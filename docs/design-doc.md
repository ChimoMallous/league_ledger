# League Ledger: Design Doc

Oct 14, 2026 · @Chimo

## Overview

A FastAPI service that syncs an ESPN fantasy football league into Postgres and serves its history through SQL. You give it a league ID (plus `espn_s2` and `SWID` for a private league), it pulls every season, and the read endpoints return standings, champions, records, head-to-head, and bench points.

The goal is a small real service with real users (my league): professional engineering practices, a live deployment, and one grounded AI feature, a weekly recap delivered to the league chat.

Out of scope: a frontend, user accounts, writing to ESPN, other sports, an ORM or migration framework, Redis, vector databases, agent frameworks, microservices, Kubernetes.

## Status

Nov 18, 2026 — step 2 done, CI green on every push (M4). Next: step 3, `espn/parse.py`.

Timeline: phases 1 and 2 by summer 2027, phase 3 live for the 2027 NFL season.

## Tech stack

| Tool | Used for |
| --- | --- |
| `fastapi[standard]` | The API (includes uvicorn and httpx) |
| `psycopg` | Running SQL against Postgres |
| PostgreSQL in Docker | The database |
| `pytest`, `ruff` | Tests, linting |
| `uv` | Dependencies, venv, loading `.env` |
| `logging` (stdlib) | Logs; no `print` in `src/` |
| GitHub Actions | CI: ruff and pytest on every push, Postgres as a service container |
| Render or Fly.io | Hosting the API |
| Neon (free tier) | Managed Postgres in production |
| One LLM API call | Writing recaps from structured data |
| Make.com | Weekly recap delivery to the league chat (glue only) |

## Architecture

Routers handle HTTP, `services/` runs the sync, `espn/` talks to ESPN, and `queries/` holds all the SQL.

&#91;embedded content: request flow · 4 layers, 1 database\]

```
league-ledger/
  .github/workflows/ci.yml
  pyproject.toml
  docker-compose.yml
  .env.example
  sql/schema.sql
  src/league_ledger/
    main.py
    config.py
    db.py
    schemas.py
    espn/        client.py, parse.py
    services/    sync.py, recap.py
    queries/
    routers/
  tests/
    fixtures/
```

## Data model

Everything is keyed by `league_id` and `season`. Loads are upserts, so re-syncing is safe.

| Table | One row per | Key columns |
| --- | --- | --- |
| `raw_payloads` | ESPN response | league\_id, season, view, fetched\_at, payload (JSONB) |
| `leagues` | League | league\_id (PK), name, first\_season, last\_synced\_at |
| `members` | ESPN user in a league | league\_id, member\_id, display\_name |
| `teams` | Team per season | league\_id, season, team\_id, member\_id, name, wins, losses, points\_for, points\_against, final\_rank |
| `matchups` | Game | league\_id, season, week, home\_team\_id, away\_team\_id, home\_score, away\_score, is\_playoff, is\_complete |
| `roster_slots` | Player per team per week | league\_id, season, week, team\_id, player\_id, player\_name, position, lineup\_slot, points |

`raw_payloads` keeps ESPN's JSON so the parser can be rerun without refetching.

`is_complete` comes from ESPN marking unplayed games `winner: "UNDECIDED"`. Future weeks
arrive with 0–0 scores, so without this flag every lowest-score and closest-game query is
wrong.

## API endpoints

| Method | Path | Returns |
| --- | --- | --- |
| GET | `/health` | Service and database status |
| POST | `/leagues/{league_id}/sync` | Pulls all seasons from ESPN and loads them; cookies in `X-ESPN-S2` and `X-ESPN-SWID` headers |
| GET | `/leagues/{league_id}` | League name, seasons available, last sync time |
| GET | `/leagues/{league_id}/seasons/{season}/standings` | Final standings for a season |
| GET | `/leagues/{league_id}/seasons/{season}/matchups` | Games, filterable by `?week=` |
| GET | `/leagues/{league_id}/champions` | Champion and last place per season |
| GET | `/leagues/{league_id}/records` | All-time highs and lows (top score, biggest blowout) |
| GET | `/leagues/{league_id}/head-to-head` | Record between two members, `?a=&b=` |
| GET | `/leagues/{league_id}/seasons/{season}/bench-points` | Points left on the bench per team |
| GET | `/leagues/{league_id}/recap/{season}/{week}` | LLM-written recap of one week |
| GET | `/leagues/{league_id}/recap/{season}` | Season-in-review recap, works in the offseason |

## Security

ESPN cookies come in as request headers on `POST /sync`, or from environment variables for the scheduled sync of my league. They are passed to ESPN and never stored or logged. Secrets (`DATABASE_URL`, cookies, LLM API key) live in `.env` locally, which is gitignored, and in the host's environment settings in production.

## Decisions

| Decision | Choice | Why |
| --- | --- | --- |
| Database | Postgres in Docker | Free, and closer to production than SQLite |
| Data access | Raw SQL with psycopg | The SQL is the point of the project |
| Migrations | None yet, one `schema.sql` | Dev data can just be re-synced |
| ESPN access | httpx, not `espn_api` | Parsing the JSON is the real work |
| Sync | On demand, plus one trigger a scheduler can call | History doesn't need a scheduler; weekly recaps need fresh data |
| Config | Environment variables (python-dotenv, or pydantic-settings if typed config is worth it) | Standard, works the same locally and in production |
| Hosting | Render or Fly.io, Postgres on Neon | Free tiers, real deployment |
| AI | One LLM call, given only structured stats from SQL | Grounding: the model never sees raw data it could misread, and numbers in its output are checked against the database |
| Delivery | Make.com calls the recap endpoint and posts to the chat | No frontend needed; the code doesn't depend on Make, so a cron job or n8n can replace it |

## Risks

- ESPN's API is undocumented and can change. All ESPN code stays in `espn/` and is tested against saved JSON.
- `status.previousSeasons` over-reports. League 2127 lists 2016–2025, but 2016 and 2017 return 404 and 2018 returns 401 — only 2019 onward fetch. Treat it as a list of candidates and record which seasons actually loaded.
- 401 does not only mean expired cookies. A public league returns 401 for seasons that require auth. Pass the status through and name the season that failed.
- The `leagueHistory` fallback for pre-2018 seasons is **unverified**. It returned 404 for every year tried on league 2127, including years the seasons endpoint serves fine. Test it against a private league with cookies before building that branch.
- Roster data is fetched per week, so one league is roughly 17 requests a season. A full sync of eight seasons is ~140 calls, which may be too slow for a synchronous `POST /sync`.
- The LLM can invent or change numbers. Recaps are validated: every number in the output must match the database, or the recap is rejected.
- Make.com credits expire March 11, 2027, before the 2027 season. Prototype the scenario before then, and keep delivery swappable.
- No live weeks until September 2027. Season-in-review and rivalry recaps cover the offseason.
- Still open: whether to allow deleting a synced league.

## Milestones

| # | Milestone | Steps | Done when |
| --- | --- | --- | --- |
| M1 | Offline ETL | 2–3 | Fetching and parsing are tested against fixtures, no network |
| M2 | League in Postgres | 4 | League 2127 syncs into Postgres; syncing twice changes nothing |
| M3 | v1 API | 5–6 | Every read endpoint works on a league synced from an empty database |
| M4 | Green CI | 7 | Every push runs ruff and pytest on GitHub Actions |
| M5 | Live | 8–10 | Public URL backed by Neon, secrets only in environment variables |
| M6 | Hands-off sync | 11 | A scheduler syncs the league with no manual step |
| M7 | First grounded recap | 12 | A recap whose numbers all match the database |
| M8 | In the group chat | 13 | Make posts a recap to the league chat (before March 11, 2027) |
| M9 | Launched | 14 | Week 1 of the 2027 season recapped for the league; README shows real usage |

## Build order

Roughly ETL, then serve. The parsing is the hard part and the riskiest, so it goes first.
The database shows up at step 4, once there are rows to put in it and the shape is known.

**Phase 1: v1 core**

### 1. Skeleton and exploration

Repo, `uv init --package`, httpx. Hit ESPN and write down what comes back.

- `scratch/explore.py`, findings in `espn-api-notes.md`
- Check what `teams` actually holds under `mTeam` vs `mRoster`
- Save real responses to `tests/fixtures/` for a good season (401 and 404 cases are faked in tests)

Done when the fixtures are saved and parsing can be worked on with the wifi off.

### 2. Extract

`espn/client.py` — fetch one season for a given view.

- Build the URL, pass repeated `view` params
- 401 and 404 raise something catchable, not a crash
- Cookies accepted as arguments, never stored
- `tests/test_client.py`: one test per error case, no network

Done when fetching a good season returns JSON, a bad one raises cleanly, and the tests pass offline.

### 3. Transform

`espn/parse.py` — JSON into flat rows. Teams first, matchups second.

- `parse_teams`: one row per team per season
- `parse_matchups`: one row per game, with `is_complete`
- Tested against fixtures, no network

Done when the parser tests pass offline and the team records match what ESPN shows.

### 4. Load

The shape is known now, so the schema can be written.

- `docker-compose.yml`, `sql/schema.sql`, `db.py`
- `raw_payloads` first, so reparsing never needs a refetch
- Upsert one season, then walk `previousSeasons` for the rest
- Per-season failures are recorded and skipped, never fatal

Done when loading twice leaves identical row counts and a league with dead seasons still finishes.

### 5. Serve

FastAPI on top of something that already works.

- `/health`, then `POST /sync`
- `standings`, then the matchups-backed reads: `champions`, `records`, `head-to-head`

Done when a league can be synced from an empty database and read back.

### 6. Rosters

Bench points. Separated because roster data is per week, not per season — roughly 17 requests
a season, so this is where sync speed becomes a real question.

**Phase 2: production basics**

### 7. CI

GitHub Actions runs ruff and pytest on every push, with Postgres as a service container. Can start right after step 2.

### 8. Config and secrets

Settings (database URL, `espn_s2`, `SWID`, LLM key) from environment variables. `.env.example` committed, `.env` never.

### 9. Logging

Standard `logging` with useful messages, e.g. "season 2018 skipped: private". No `print` in `src/`.

### 10. Deploy

API on Render or Fly.io, Postgres on Neon. Live URL in the README.

### 11. Scheduled sync

One sync endpoint or CLI command that a scheduler can trigger.

**Phase 3: real users and AI**

### 12. Recap endpoint

Pull a week's stats with SQL, pass only that structured data to one LLM call, and return a recap. Check that every number in the output matches the database. Offseason: season-in-review and all-time rivalry recaps.

### 13. Delivery with Make.com

A weekly Make scenario calls the recap endpoint and posts the result to the league chat. Make is glue only; all logic stays in Python. Prototype before March 2027.

### 14. README with a real metric

E.g. "Used by a 12-person league, 8 seasons and X matchups synced."

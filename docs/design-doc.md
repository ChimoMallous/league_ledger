# League Ledger: Design Doc

Oct 14, 2026 · @Chimo

## Overview

A FastAPI service that syncs an ESPN fantasy football league into Postgres and serves its history through SQL. You give it a league ID (plus `espn_s2` and `SWID` for a private league), it pulls every season, and the read endpoints return standings, champions, records, head-to-head, and bench points.

Not in v1: a frontend, user accounts, writing to ESPN, other sports, hosting.

## Status

Oct 18, 2026 — step 1. Packaging scaffolded, ESPN responses explored and written up in
`espn-api-notes.md`. Left to do: compare `teams` across `mTeam` and `mRoster`, save the
fixtures, declare httpx in `pyproject.toml`.

## Tech stack

| Tool | Used for |
| --- | --- |
| `fastapi[standard]` | The API (includes uvicorn and httpx) |
| `psycopg` | Running SQL against Postgres |
| PostgreSQL in Docker | The database |
| `pytest`, `ruff` | Tests, linting |
| `uv` | Dependencies, venv, loading `.env` |

## Architecture

Routers handle HTTP, `services/` runs the sync, `espn/` talks to ESPN, and `queries/` holds all the SQL.

&#91;embedded content: request flow · 4 layers, 1 database\]

```
league-ledger/
  pyproject.toml
  docker-compose.yml
  .env.example
  sql/schema.sql
  src/league_ledger/
    main.py
    db.py
    schemas.py
    espn/        client.py, parse.py
    services/    sync.py
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

## Security

ESPN cookies come in as request headers, get passed to ESPN for that sync, and are never stored or logged. `.env` only holds `DATABASE_URL` and is gitignored.

## Decisions

| Decision | Choice | Why |
| --- | --- | --- |
| Database | Postgres in Docker | Free, and closer to production than SQLite |
| Data access | Raw SQL with psycopg | The SQL is the point of the project |
| Migrations | None yet, one `schema.sql` | Dev data can just be re-synced |
| ESPN access | httpx, not `espn_api` | Parsing the JSON is the real work |
| Sync | On demand | League history doesn't need a scheduler |

## Risks

- ESPN's API is undocumented and can change. All ESPN code stays in `espn/` and is tested against saved JSON.
- `status.previousSeasons` over-reports. League 2127 lists 2016–2025, but 2016 and 2017 return 404 and 2018 returns 401 — only 2019 onward fetch. Treat it as a list of candidates and record which seasons actually loaded.
- 401 does not only mean expired cookies. A public league returns 401 for seasons that require auth. Pass the status through and name the season that failed.
- The `leagueHistory` fallback for pre-2018 seasons is **unverified**. It returned 404 for every year tried on league 2127, including years the seasons endpoint serves fine. Test it against a private league with cookies before building that branch.
- Roster data is fetched per week, so one league is roughly 17 requests a season. A full sync of eight seasons is ~140 calls, which may be too slow for a synchronous `POST /sync`.
- Still open: whether to allow deleting a synced league.

## Build order

Roughly ETL, then serve. The parsing is the hard part and the riskiest, so it goes first.
The database shows up at step 4, once there are rows to put in it and the shape is known.

### 1. Skeleton and exploration

Repo, `uv init --package`, httpx. Hit ESPN and write down what comes back.

- `scratch/explore.py`, findings in `espn-api-notes.md`
- Check what `teams` actually holds under `mTeam` vs `mRoster`
- Save real responses to `tests/fixtures/`: a good season, a 401 season, a 404 season

Done when the fixtures are saved and parsing can be worked on with the wifi off.

### 2. Extract

`espn/client.py` — fetch one season for a given view.

- Build the URL, pass repeated `view` params
- 401 and 404 raise something catchable, not a crash
- Cookies accepted as arguments, never stored

Done when fetching a good season returns JSON and a bad one raises cleanly.

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

### 7. Polish

README, CI, error messages that name the season that failed, app Dockerfile, hosting.

Later: frontend.

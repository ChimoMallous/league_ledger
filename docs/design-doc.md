# League Ledger: Design Doc

Oct 14, 2026 · @Chimo

## Overview

A FastAPI service that syncs an ESPN fantasy football league into Postgres and serves its history through SQL. You give it a league ID (plus `espn_s2` and `SWID` for a private league), it pulls every season, and the read endpoints return standings, champions, records, head-to-head, and bench points.

Not in v1: a frontend, user accounts, writing to ESPN, other sports, hosting.

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
| `matchups` | Game | league\_id, season, week, home\_team\_id, away\_team\_id, home\_score, away\_score, is\_playoff |
| `roster_slots` | Player per team per week | league\_id, season, week, team\_id, player\_id, player\_name, position, lineup\_slot, points |

`raw_payloads` keeps ESPN's JSON so the parser can be rerun without refetching.

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
- Seasons before 2018 use a different endpoint (`leagueHistory`).
- Expired cookies return 401. Pass that through instead of a 500.
- Still open: the final name, and whether to allow deleting a synced league.

## Milestones

Each one is a GitHub milestone, and its tasks are issues.

1. Explore: hit ESPN for one season, save the JSON to `tests/fixtures/`.
2. Skeleton: `uv init --package`, ruff, pytest, `/health`.
3. Database: `docker-compose.yml`, `schema.sql`, `db.py`.
4. Ingest: client, parser, loader, `POST /sync`. Syncing twice should give the same row counts.
5. Read endpoints, one test each.
6. CI: GitHub Actions runs ruff and pytest.

Later: app Dockerfile, hosting, frontend.

# Checklist

Steps match the build order in `design-doc.md`. Finish a step before starting the next.

## 1. Skeleton and exploration

- [x] Create repo with `uv init --package`
- [x] Write design doc
- [x] Write ESPN API notes
- [x] Write `scratch/explore.py`
- [x] Compare `teams` in `mTeam` and `mRoster`
- [x] Save 2025 fixtures for each view
- [x] `uv add httpx`
- [x] `uv add --dev pytest ruff`
- [x] Add `.env`, `.pytest_cache/`, `.ruff_cache/` to `.gitignore`
- [x] Remove `[project.scripts]` from `pyproject.toml`
- [x] Commit `uv.lock`

## 2. Extract: `espn/client.py`

- [ ] Add error classes: `ESPNError`, `LeagueNotFound`, `LeagueIsPrivate`, `ESPNUnavailable`
- [ ] Write `fetch_season(league_id, season, views, cookies=None)`
- [ ] Send repeated `view` params
- [ ] Set a timeout
- [ ] Raise on 401, 403, 404, 5xx, timeouts, and bad JSON
- [ ] Test each case with `httpx.MockTransport`

**Done when:** a good season returns JSON and a bad one raises the right error.

## 3. Transform: `espn/parse.py`

- [ ] Write `parse_teams`: one row per team per season
- [ ] Write `parse_matchups`: one row per game, with `is_complete`
- [ ] Set `is_complete` false if `winner` is `UNDECIDED` or the score is 0-0 (ESPN marks some unplayed games as decided)
- [ ] Skip bye weeks
- [ ] Test against fixtures with no network

**Done when:** tests pass offline and team records match ESPN.

## 4. Load

- [ ] Write `docker-compose.yml`
- [ ] Write `sql/schema.sql`
- [ ] Write `db.py`
- [ ] Save to `raw_payloads` first
- [ ] Upsert one season
- [ ] Loop over `previousSeasons`
- [ ] Record failed seasons and keep going

**Done when:** loading twice gives the same row counts and a league with dead seasons still finishes.

## 5. Serve

- [ ] `GET /health`
- [ ] `POST /leagues/{league_id}/sync`
- [ ] `GET /leagues/{league_id}`
- [ ] Standings
- [ ] Matchups
- [ ] Champions
- [ ] Records
- [ ] Head-to-head
- [ ] Merge duplicate accounts so one person isn't split across seasons

**Done when:** a league can be synced from an empty database and read back.

## 6. Rosters

- [ ] Fetch `mRoster` per week
- [ ] Load `roster_slots`
- [ ] Add the bench points endpoint
- [ ] Decide if `POST /sync` is still fast enough

**Done when:** bench points match ESPN for a known week.

## 7. Polish

- [ ] README
- [ ] CI
- [ ] Error messages name the season that failed
- [ ] App Dockerfile
- [ ] Hosting

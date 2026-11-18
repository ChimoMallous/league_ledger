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

- [x] Add error classes: `ESPNError`, `LeagueNotFound`, `LeagueIsPrivate`, `ESPNUnavailable`
- [x] Write `fetch_season(league_id, season, views, cookies=None)`
- [x] Send repeated `view` params
- [x] Set a timeout
- [x] Raise on 401, 403, 404, 5xx, timeouts, and bad JSON
- [x] Choose how tests fake HTTP: `monkeypatch` (add a client parameter later only if step 6 needs connection reuse)
- [x] Test: 200 returns JSON
- [x] Test: 404 raises `LeagueNotFound`
- [x] Test: 401 and 403 raise `LeagueIsPrivate`
- [x] Test: 500 raises `ESPNUnavailable`
- [x] Test: network error raises `ESPNUnavailable`
- [x] Test: invalid JSON raises `ESPNUnavailable`

**Done when:** all tests pass offline and ruff is clean.

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

## 7. CI

- [ ] GitHub Actions: ruff and pytest on every push
- [ ] Postgres service container (once step 4 exists)

## 8. Config and secrets

- [ ] Settings from environment variables
- [ ] `.env.example` committed

## 9. Logging

- [ ] `logging` set up, no `print` in `src/`
- [ ] Failed seasons logged with the reason

## 10. Deploy

- [ ] Postgres on Neon
- [ ] API on Render or Fly.io
- [ ] Live URL in README

## 11. Scheduled sync

- [ ] One endpoint or CLI command a scheduler can trigger

## 12. Recap endpoint

- [ ] SQL for one week's stats
- [ ] One LLM call with only that data
- [ ] Reject recaps with numbers that don't match the database
- [ ] Offseason recaps: season-in-review, rivalries

## 13. Delivery with Make.com

- [ ] Weekly scenario: call the recap endpoint, post to the league chat
- [ ] Prototype before March 11, 2027

## 14. README

- [ ] Real usage metric

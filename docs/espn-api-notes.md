# ESPN API Notes

## Full ESPN request URL
https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2026/segments/0/leagues/1380768854?rosterForTeamId=8&view=mDraftDetail&view=mLiveScoring&view=mMatchupScore&view=mPendingTransactions&view=mPositionalRatings&view=mRoster&view=mSettings&view=mTeam&view=modular&view=mNav&platformVersion=7411ee0540f4d3fa37ae9b9b557490bbb512f9d8

## URL broken up
| Part | Value | Changes? |
| --- | --- | --- |
| Host | `lm-api-reads.fantasy.espn.com` | No |
| API version | `apis/v3` | No |
| Game | `games/ffl` | No (ffl = football) |
| Season | `seasons/2026` | Yes, per year |
| Segment | `segments/0` | Unknown, note it |
| League | `leagues/1380768854` | Yes, per league |
| Params | `view=...` (repeatable) | Yes |

## Views shown
-mDraftDetail -mLiveScoring -mMatchupScore -mPendingTransactions -mPositionalRatings -mRoster -mSettings -mTeam -modular -mNav

## Views to verify
-mTeam -mRoster -mMatchupScore -mSettings

## Response keys by view (verified 2026-10-15, public league 2127)

### mTeam
`draftDetail`, `gameId`, `id`, `members`, `scoringPeriodId`, `seasonId`, `segmentId`, `status`, `teams`

### mRoster
`draftDetail`, `gameId`, `id`, `scoringPeriodId`, `seasonId`, `segmentId`, `status`, `teams`

### mMatchupScore
`draftDetail`, `gameId`, `id`, `schedule`, `scoringPeriodId`, `seasonId`, `segmentId`, `status`

### mSettings
`draftDetail`, `gameId`, `id`, `scoringPeriodId`, `seasonId`, `segmentId`, `settings`, `status`

### Base keys (every view) 
`draftDetail`, `gameId`, `id`, `scoringPeriodId`, `seasonId`, `segmentId`, `status`

| View | Added keys |
| --- | --- |
| `mTeam` | `members`, `teams` |
| `mRoster` | `teams` |
| `mMatchupScore` | `schedule` |
| `mSettings` | `settings` |

Note that `mTeam` and `mRoster` both return `teams`, but only `id` matches: `mTeam` has the season record (name, owners, W/L, points, rank), `mRoster` has only the 15-player roster and each player's points.

### mRoster is weekly
Rosters change during a season, so one request gives one week, not a season. With no
`scoringPeriodId` you get the latest week. Pass it to pick one:

    ?view=mRoster&scoringPeriodId=5 (will return for week 5)

A full season is a loop over weeks 1-17, so about 17 requests. Only bench points needs this.
Standings, champions, records, and head-to-head all come from mTeam and mMatchupScore.

Note that `appliedStatTotal` is that week's points, but `player.stats` also carries season
totals under `scoringPeriodId: 0`.

### Field notes
`lineupSlotId` is where a player sat that week. 20 = bench, 23 = flex.

`playoffTierType` is NONE, WINNERS_BRACKET, LOSERS_CONSOLATION_LADDER, or
WINNERS_CONSOLATION_LADDER, so `!= "NONE"` counts consolation games as playoffs.

`winner` is HOME, AWAY, or UNDECIDED. The 2025 fixture has no UNDECIDED because that season
finished. Need a 2026 fixture to cover it.

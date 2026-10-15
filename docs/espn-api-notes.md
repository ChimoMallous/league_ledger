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

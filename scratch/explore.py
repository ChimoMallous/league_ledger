import httpx

TEST_LEAGUE_ID = 2127
URL = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2026/segments/0/leagues/{TEST_LEAGUE_ID}"

views = ["mTeam", "mRoster", "mMatchupScore", "mSettings"]


def fetch_league(view: str):
    try:
        response = httpx.get(URL, params={"view": view})
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        print(f"An error occurred while fetching the league data: {e}")
        return None


if __name__ == "__main__":
    for view in views:
        league_data = fetch_league(view)
        if league_data:
            print(f"League Data Successfully Retrieved for {view}\nAvailable Keys for {view}: {league_data.keys()}")
        else:
            print("Error")

# Output 10/15/2026 w/ League ID 2127

# League Data Successfully Retrieved for mTeam
# Available Keys for mTeam: dict_keys(['draftDetail', 'gameId', 'id', 'members', 'scoringPeriodId', 'seasonId', 'segmentId', 'status', 'teams'])
# League Data Successfully Retrieved for mRoster
# Available Keys for mRoster: dict_keys(['draftDetail', 'gameId', 'id', 'scoringPeriodId', 'seasonId', 'segmentId', 'status', 'teams'])
# League Data Successfully Retrieved for mMatchupScore
# Available Keys for mMatchupScore: dict_keys(['draftDetail', 'gameId', 'id', 'schedule', 'scoringPeriodId', 'seasonId', 'segmentId', 'status'])
# League Data Successfully Retrieved for mSettings
# Available Keys for mSettings: dict_keys(['draftDetail', 'gameId', 'id', 'scoringPeriodId', 'seasonId', 'segmentId', 'settings', 'status'])   
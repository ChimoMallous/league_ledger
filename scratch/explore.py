import httpx
import json 

from pathlib import Path


TEST_LEAGUE_ID = 2127
TEST_SEASON = 2025

URL = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{TEST_SEASON}/segments/0/leagues/{TEST_LEAGUE_ID}"

views = ["mTeam", "mRoster", "mMatchupScore", "mSettings"]


current_dir = Path(__file__).parent.parent
target_dir = current_dir / "tests" / "fixtures"
target_dir.mkdir(parents=True, exist_ok=True)


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
            for i, team in enumerate(league_data.get("teams", []), 1):
                if "name" in team:
                    team["name"] = f"Team {i}"
                    team["abbrev"] = f"T{i}"
            file_path = target_dir / f"{TEST_SEASON}_{view}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(league_data, f, ensure_ascii=False, indent=2)
            print(f"League Data Successfully Retrieved for {view}\nAvailable Keys for {view}: {league_data.keys()}")
        else:
            print("Error")


# Output 10/18/2026 w/ League ID 2127 for Season 2025

# League Data Successfully Retrieved for mTeam
# Available Keys for mTeam: dict_keys(['draftDetail', 'gameId', 'id', 'members', 'scoringPeriodId', 'seasonId', 'segmentId', 'status', 'teams'])
# League Data Successfully Retrieved for mRoster
# Available Keys for mRoster: dict_keys(['draftDetail', 'gameId', 'id', 'scoringPeriodId', 'seasonId', 'segmentId', 'status', 'teams'])
# League Data Successfully Retrieved for mMatchupScore
# Available Keys for mMatchupScore: dict_keys(['draftDetail', 'gameId', 'id', 'schedule', 'scoringPeriodId', 'seasonId', 'segmentId', 'status'])
# League Data Successfully Retrieved for mSettings
# Available Keys for mSettings: dict_keys(['draftDetail', 'gameId', 'id', 'scoringPeriodId', 'seasonId', 'segmentId', 'settings', 'status'])

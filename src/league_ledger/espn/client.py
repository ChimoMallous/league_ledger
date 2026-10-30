import httpx


BASE_URL = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl"

class ESPNError(Exception):
    pass

class LeagueNotFound(ESPNError):
    pass

class LeagueIsPrivate(ESPNError):
    pass

class ESPNUnavailable(ESPNError):
    pass


def fetch_season(league_id: int, season: int, views: list[str], cookies: dict[str, str] | None = None) -> dict:
    url = f"{BASE_URL}/seasons/{season}/segments/0/leagues/{league_id}"
    try:
        response = httpx.get(url, params={"view": views}, cookies=cookies, timeout=10)
    except httpx.HTTPError as exc:
        raise ESPNUnavailable("Could not reach ESPN") from exc

    if response.status_code == 404:
        raise LeagueNotFound(f"League {league_id} has no {season} season")
    if response.status_code in (401, 403):
        raise LeagueIsPrivate(f"League {league_id} requires login for {season}")
    if not response.is_success:
        raise ESPNUnavailable(f"ESPN returned {response.status_code}")

    try:
        return response.json()
    except ValueError as exc:
        raise ESPNUnavailable("ESPN returned invalid JSON") from exc
import httpx
import pytest

from league_ledger.espn.client import (
    ESPNUnavailable,
    LeagueIsPrivate,
    LeagueNotFound,
    fetch_season,
)


def test_fetch_season_returns_json(monkeypatch):
    fake_response = httpx.Response(200, json={"seasonId": 2025})
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: fake_response)
    assert fetch_season(2127, 2025, ["mTeam"]) == {"seasonId": 2025}


def test_404_raises_league_not_found(monkeypatch):
    fake_response = httpx.Response(404)
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: fake_response)
    with pytest.raises(LeagueNotFound):
        fetch_season(2127, 2025, ["mTeam"])


@pytest.mark.parametrize("status_code", [401, 403])
def test_401_403_raises_league_is_private(monkeypatch, status_code):
    fake_response = httpx.Response(status_code)
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: fake_response)
    with pytest.raises(LeagueIsPrivate):
        fetch_season(2127, 2025, ["mTeam"])


def test_500_raises_espn_unavailable(monkeypatch):
    fake_response = httpx.Response(500)
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: fake_response)
    with pytest.raises(ESPNUnavailable):
        fetch_season(2127, 2025, ["mTeam"])


def test_network_error_raises_espn_unavailable(monkeypatch):
    def fake_get(*args, **kwargs):
        raise httpx.ConnectError("connection failed")

    monkeypatch.setattr(httpx, "get", fake_get)
    with pytest.raises(ESPNUnavailable):
        fetch_season(2127, 2025, ["mTeam"])


def test_invalid_json_raises_espn_unavailable(monkeypatch):
    fake_response = httpx.Response(200, text="test")
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: fake_response)
    with pytest.raises(ESPNUnavailable):
        fetch_season(2127, 2025, ["mTeam"])

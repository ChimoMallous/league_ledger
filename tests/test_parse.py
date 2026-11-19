import json
from pathlib import Path

import pytest

from league_ledger.espn.parse import parse_teams

TEAM_FIXTURE = Path(__file__).parent / "fixtures" / "2025_mTeam.json"


@pytest.fixture
def rows():
    data = json.loads(TEAM_FIXTURE.read_text(encoding="utf-8"))
    return parse_teams(data)


def test_parse_teams_returns_one_row_per_team(rows):
    assert len(rows) == 10


def test_parse_teams_team_1_values(rows):
    team1 = next(row for row in rows if row["team_id"] == 1)
    assert team1["wins"] == 10
    assert team1["losses"] == 5
    assert team1["final_rank"] == 3
    assert team1["points_for"] == 1638.48

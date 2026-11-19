def parse_teams(data: dict) -> list[dict]:
    rows = []
    for team in data["teams"]:
        overall = team["record"]["overall"]
        rows.append(
            {
                "season": data["seasonId"],
                "team_id": team["id"],
                "member_id": team["primaryOwner"],
                "name": team["name"],
                "wins": overall["wins"],
                "losses": overall["losses"],
                "ties": overall["ties"],
                "final_rank": team["rankCalculatedFinal"],
                "points_for": round(overall["pointsFor"], 2),
                "points_against": round(overall["pointsAgainst"], 2),
            }
        )
    return rows

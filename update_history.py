import json
import os
import requests
from datetime import datetime, timezone

LEAGUE_ID = "90156758"
SEASONS = [2022, 2023, 2024, 2025]

ESPN_S2 = os.environ["ESPN_S2"]
ESPN_SWID = os.environ["ESPN_SWID"]

cookies = {
    "espn_s2": ESPN_S2,
    "SWID": ESPN_SWID
}

history = {
    "leagueId": LEAGUE_ID,
    "lastUpdated": datetime.now(timezone.utc).isoformat(),
    "seasons": {}
}

for season in SEASONS:

    print(f"Pulling {season}...")

    url = (
        f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/"
        f"seasons/{season}/segments/0/leagues/{LEAGUE_ID}"
    )

    params = [
        ("view", "mTeam"),
        ("view", "mStandings"),
        ("view", "mMatchupScore"),
        ("view", "mStatus"),
        ("view", "mSettings")
    ]

    response = requests.get(
        url,
        params=params,
        cookies=cookies,
        timeout=30
    )

    if response.status_code != 200:
        print(
            f"Could not pull {season}: "
            f"HTTP {response.status_code}"
        )
        history["seasons"][str(season)] = {
            "error": f"HTTP {response.status_code}"
        }
        continue

    data = response.json()

    teams = []

    for team in data.get("teams", []):

        record = (
            team.get("record", {})
            .get("overall", {})
        )

        teams.append({
            "teamId": team.get("id"),
            "teamName": (
                team.get("name")
                or f"{team.get('location', '')} "
                   f"{team.get('nickname', '')}".strip()
            ),
            "wins": record.get("wins", 0),
            "losses": record.get("losses", 0),
            "ties": record.get("ties", 0),
            "pointsFor": round(
                record.get("pointsFor", 0),
                2
            ),
            "pointsAgainst": round(
                record.get("pointsAgainst", 0),
                2
            )
        })

    matchups = []

    for matchup in data.get("schedule", []):

        home = matchup.get("home", {})
        away = matchup.get("away", {})

        matchups.append({
            "matchupPeriodId": matchup.get(
                "matchupPeriodId"
            ),
            "playoffTierType": matchup.get(
                "playoffTierType"
            ),
            "winner": matchup.get(
                "winner",
                "UNDECIDED"
            ),
            "homeTeamId": home.get(
                "teamId"
            ),
            "homeScore": round(
                home.get("totalPoints", 0),
                2
            ),
            "awayTeamId": away.get(
                "teamId"
            ),
            "awayScore": round(
                away.get("totalPoints", 0),
                2
            )
        })

    history["seasons"][str(season)] = {
        "teams": teams,
        "matchups": matchups,
        "status": data.get("status", {}),
        "settings": data.get("settings", {})
    }

    print(
        f"{season}: "
        f"{len(teams)} teams, "
        f"{len(matchups)} matchups"
    )

with open(
    "league-history.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        history,
        f,
        indent=2
    )

print("")
print("Historical pull complete.")
print("Created league-history.json")

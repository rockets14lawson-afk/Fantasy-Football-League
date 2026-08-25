import json
import os
import requests
from datetime import datetime, timezone

LEAGUE_ID = "90156758"
SEASON = "2026"

ESPN_S2 = os.environ["ESPN_S2"]
ESPN_SWID = os.environ["ESPN_SWID"]

url = (
    f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/"
    f"seasons/{SEASON}/segments/0/leagues/{LEAGUE_ID}"
)

params = [
    ("view", "mTeam"),
    ("view", "mStandings"),
    ("view", "mMatchupScore")
]

cookies = {
    "espn_s2": ESPN_S2,
    "SWID": ESPN_SWID
}

response = requests.get(
    url,
    params=params,
    cookies=cookies,
    timeout=30
)

response.raise_for_status()

data = response.json()


# -----------------------------
# TEAMS / STANDINGS
# -----------------------------

teams = []

for team in data.get("teams", []):

    record = team.get("record", {}).get("overall", {})

    teams.append({
        "teamId": team.get("id"),
        "teamName": (
            team.get("name")
            or
            f"{team.get('location', '')} "
            f"{team.get('nickname', '')}".strip()
        ),
        "wins": record.get("wins", 0),
        "losses": record.get("losses", 0),
        "ties": record.get("ties", 0),
        "pointsFor": round(record.get("pointsFor", 0), 2),
        "pointsAgainst": round(record.get("pointsAgainst", 0), 2),
        "percentage": record.get("percentage", 0)
    })


teams.sort(
    key=lambda x: (
        -x["wins"],
        x["losses"],
        -x["pointsFor"]
    )
)


# -----------------------------
# WEEKLY MATCHUPS
# -----------------------------

schedule = []

for matchup in data.get("schedule", []):

    home = matchup.get("home", {})
    away = matchup.get("away", {})

    schedule.append({
        "matchupPeriodId": matchup.get("matchupPeriodId"),
        "homeTeamId": home.get("teamId"),
        "homeScore": round(home.get("totalPoints", 0), 2),
        "awayTeamId": away.get("teamId"),
        "awayScore": round(away.get("totalPoints", 0), 2),
        "winner": matchup.get("winner", "UNDECIDED")
    })


# -----------------------------
# OUTPUT
# -----------------------------

output = {
    "leagueId": LEAGUE_ID,
    "season": SEASON,
    "lastUpdated": datetime.now(timezone.utc).isoformat(),
    "teams": teams,
    "schedule": schedule
}


with open(
    "league-data.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        output,
        f,
        indent=2
    )


print(
    f"league-data.json updated: "
    f"{len(teams)} teams, "
    f"{len(schedule)} matchups"
)

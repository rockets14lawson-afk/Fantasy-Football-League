import json
import os
import requests
from datetime import datetime, timezone

LEAGUE_ID = "90156758"
SEASON = 2026

ESPN_S2 = os.environ["ESPN_S2"]
ESPN_SWID = os.environ["ESPN_SWID"]

url = (
    f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/"
    f"seasons/{SEASON}/segments/0/leagues/{LEAGUE_ID}"
)

params = [
    ("view", "mTeam"),
    ("view", "mStandings"),
    ("view", "mMatchupScore"),
    ("view", "mStatus")
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

manager_map = {
    1: "Devin",
    2: "Hunter",
    3: "Mike",
    4: "Tom",
    5: "Steve P.",
    6: "Steve H.",
    7: "Matt",
    8: "Toby",
    9: "Josh",
    10: "Philip"
}

teams = []

for team in data.get("teams", []):

    record = team.get("record", {}).get("overall", {})

    teams.append({
        "teamId": team.get("id"),
        "teamName": (
            team.get("name")
            or f"{team.get('location', '')} {team.get('nickname', '')}".strip()
        ),
        "wins": record.get("wins", 0),
        "losses": record.get("losses", 0),
        "ties": record.get("ties", 0),
        "pointsFor": round(record.get("pointsFor", 0), 2),
        "pointsAgainst": round(record.get("pointsAgainst", 0), 2),
        "percentage": record.get("percentage", 0)
    })

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

featured_games = {
    1: ("Matt", "Philip"),
    2: ("Tom", "Josh"),
    3: ("Devin", "Hunter"),
    4: ("Toby", "Tom"),
    5: ("Devin", "Josh"),
    6: ("Steve H.", "Steve P."),
    7: ("Devin", "Matt"),
    8: ("Devin", "Tom"),
    9: ("Devin", "Toby"),
    10: ("Toby", "Mike"),
    11: ("Toby", "Philip"),
    12: ("Devin", "Matt"),
    13: ("Devin", "Tom"),
    14: ("Devin", "Toby")
}

recaps = {}

for week in range(1, 15):

    games = [
        g for g in schedule
        if g["matchupPeriodId"] == week
    ]

    completed = [
        g for g in games
        if g["winner"] != "UNDECIDED"
    ]

    if not completed:
        recaps[str(week)] = None
        continue

    performances = []

    for game in completed:

        performances.append({
            "teamId": game["homeTeamId"],
            "score": game["homeScore"]
        })

        performances.append({
            "teamId": game["awayTeamId"],
            "score": game["awayScore"]
        })

    highest = max(
        performances,
        key=lambda x: x["score"]
    )

    lowest = min(
        performances,
        key=lambda x: x["score"]
    )

    margins = []

    for game in completed:

        margin = abs(
            game["homeScore"] - game["awayScore"]
        )

        winner_id = (
            game["homeTeamId"]
            if game["homeScore"] > game["awayScore"]
            else game["awayTeamId"]
        )

        loser_id = (
            game["awayTeamId"]
            if winner_id == game["homeTeamId"]
            else game["homeTeamId"]
        )

        margins.append({
            "margin": margin,
            "winnerId": winner_id,
            "loserId": loser_id,
            "winnerScore": max(game["homeScore"], game["awayScore"]),
            "loserScore": min(game["homeScore"], game["awayScore"])
        })

    biggest = max(
        margins,
        key=lambda x: x["margin"]
    )

    closest = min(
        margins,
        key=lambda x: x["margin"]
    )

    gotw_text = "Not found"

    featured_pair = featured_games.get(week)

    if featured_pair:

        team1, team2 = featured_pair

        team1_id = next(
            (tid for tid, name in manager_map.items() if name == team1),
            None
        )

        team2_id = next(
            (tid for tid, name in manager_map.items() if name == team2),
            None
        )

        for game in completed:

            ids = {
                game["homeTeamId"],
                game["awayTeamId"]
            }

            if ids == {team1_id, team2_id}:

                gotw_text = (
                    f"{team1} {game['homeScore'] if game['homeTeamId'] == team1_id else game['awayScore']:.2f}"
                    f" - "
                    f"{team2} {game['homeScore'] if game['homeTeamId'] == team2_id else game['awayScore']:.2f}"
                )

                break

    recaps[str(week)] = {
        "highestScorer": (
            f"{manager_map.get(highest['teamId'], 'Unknown')} — "
            f"{highest['score']:.2f}"
        ),
        "lowestScorer": (
            f"{manager_map.get(lowest['teamId'], 'Unknown')} — "
            f"{lowest['score']:.2f}"
        ),
        "biggestBlowout": (
            f"{manager_map.get(biggest['winnerId'], 'Unknown')} over "
            f"{manager_map.get(biggest['loserId'], 'Unknown')} by "
            f"{biggest['margin']:.2f}"
        ),
        "closestGame": (
            f"{manager_map.get(closest['winnerId'], 'Unknown')} over "
            f"{manager_map.get(closest['loserId'], 'Unknown')} by "
            f"{closest['margin']:.2f}"
        ),
        "gameOfWeek": gotw_text
    }

output = {
    "leagueId": LEAGUE_ID,
    "season": SEASON,
    "lastUpdated": datetime.now(timezone.utc).isoformat(),
    "teams": teams,
    "schedule": schedule,
    "recaps": recaps
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

print("league-data.json updated successfully")

import json
import os
import requests
from datetime import datetime, timezone


# =========================================================
# JDC DEGENERATES - ESPN DATA UPDATER
# 2026 SEASON
# =========================================================

LEAGUE_ID = "90156758"
SEASON = 2026


# =========================================================
# ESPN LOGIN SECRETS
# =========================================================

ESPN_S2 = os.environ["ESPN_S2"]
ESPN_SWID = os.environ["ESPN_SWID"]


# =========================================================
# ESPN API
# =========================================================

url = (
    f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/"
    f"seasons/{SEASON}/segments/0/leagues/{LEAGUE_ID}"
)

params = [
    ("view", "mTeam"),
    ("view", "mStandings"),
    ("view", "mMatchupScore"),
    ("view", "mStatus"),
    ("view", "mDraftDetail")
]

cookies = {
    "espn_s2": ESPN_S2,
    "SWID": ESPN_SWID
}


# =========================================================
# GET ESPN DATA
# =========================================================

print("Connecting to ESPN...")

response = requests.get(
    url,
    params=params,
    cookies=cookies,
    timeout=30
)

response.raise_for_status()

data = response.json()

print("ESPN data received.")


# =========================================================
# MANAGER MAPPING
# =========================================================

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

manager_id_map = {
    name: team_id
    for team_id, name in manager_map.items()
}


# =========================================================
# TEAM / STANDINGS DATA
# =========================================================

teams = []

for team in data.get("teams", []):

    record = (
        team
        .get("record", {})
        .get("overall", {})
    )

    team_name = team.get("name")

    if not team_name:

        location = team.get(
            "location",
            ""
        )

        nickname = team.get(
            "nickname",
            ""
        )

        team_name = (
            f"{location} {nickname}"
        ).strip()

    teams.append({
        "teamId": team.get("id"),
        "teamName": team_name,
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
        ),
        "percentage": record.get(
            "percentage",
            0
        )
    })


teams.sort(
    key=lambda team: (
        -team["wins"],
        team["losses"],
        -team["pointsFor"]
    )
)


# =========================================================
# SCHEDULE / SCORES
# =========================================================

schedule = []

for matchup in data.get("schedule", []):

    home = matchup.get("home", {})
    away = matchup.get("away", {})

    schedule.append({
        "matchupPeriodId":
            matchup.get(
                "matchupPeriodId"
            ),
        "homeTeamId":
            home.get("teamId"),
        "homeScore":
            round(
                home.get(
                    "totalPoints",
                    0
                ),
                2
            ),
        "awayTeamId":
            away.get("teamId"),
        "awayScore":
            round(
                away.get(
                    "totalPoints",
                    0
                ),
                2
            ),
        "winner":
            matchup.get(
                "winner",
                "UNDECIDED"
            )
    })


# =========================================================
# DRAFT DATA
# =========================================================

draft = {
    "drafted": False,
    "picks": []
}

draft_detail = data.get(
    "draftDetail",
    {}
)

picks = draft_detail.get(
    "picks",
    []
)

if picks:

    draft["drafted"] = True

    for pick in picks:

        team_id = pick.get("teamId")

        draft["picks"].append({
            "roundId":
                pick.get("roundId"),
            "roundPickNumber":
                pick.get(
                    "roundPickNumber"
                ),
            "overallPickNumber":
                pick.get(
                    "overallPickNumber"
                ),
            "teamId":
                team_id,
            "manager":
                manager_map.get(
                    team_id,
                    "Unknown"
                ),
            "playerId":
                pick.get("playerId"),
            "bidAmount":
                pick.get(
                    "bidAmount"
                ),
            "keeper":
                pick.get(
                    "keeper",
                    False
                )
        })


# =========================================================
# GAME OF THE WEEK
# =========================================================

featured_games = {

    1: {
        "team1": "Matt",
        "team2": "Philip",
        "story":
            "2025 Championship Rematch"
    },

    2: {
        "team1": "Tom",
        "team2": "Josh",
        "story":
            "Featured Matchup"
    },

    3: {
        "team1": "Devin",
        "team2": "Hunter",
        "story":
            "Veteran vs Rookie"
    },

    4: {
        "team1": "Toby",
        "team2": "Tom",
        "story":
            "Featured Matchup"
    },

    5: {
        "team1": "Devin",
        "team2": "Josh",
        "story":
            "Featured Matchup"
    },

    6: {
        "team1": "Steve H.",
        "team2": "Steve P.",
        "story":
            "Battle of the Steves"
    },

    7: {
        "team1": "Devin",
        "team2": "Matt",
        "story":
            "Commissioner vs Defending Champion"
    },

    8: {
        "team1": "Devin",
        "team2": "Tom",
        "story":
            "Featured Matchup"
    },

    9: {
        "team1": "Devin",
        "team2": "Toby",
        "story":
            "Rivalry Preview"
    },

    10: {
        "team1": "Toby",
        "team2": "Mike",
        "story":
            "Battle of Former Champions"
    },

    11: {
        "team1": "Toby",
        "team2": "Philip",
        "story":
            "Featured Matchup"
    },

    12: {
        "team1": "Devin",
        "team2": "Matt",
        "story":
            "Playoff Push"
    },

    13: {
        "team1": "Devin",
        "team2": "Tom",
        "story":
            "Final Tune-Up"
    },

    14: {
        "team1": "Devin",
        "team2": "Toby",
        "story":
            "Rivalry Week"
    }
}


# =========================================================
# WEEKLY RECAP GENERATOR
# =========================================================

recaps = {}

for week in range(1, 15):

    week_games = [
        game
        for game in schedule
        if game["matchupPeriodId"] == week
    ]

    completed_games = [
        game
        for game in week_games
        if game["winner"] != "UNDECIDED"
    ]

    if len(completed_games) < 5:

        recaps[str(week)] = None
        continue

    performances = []

    for game in completed_games:

        performances.append({
            "teamId":
                game["homeTeamId"],
            "score":
                game["homeScore"]
        })

        performances.append({
            "teamId":
                game["awayTeamId"],
            "score":
                game["awayScore"]
        })

    highest = max(
        performances,
        key=lambda team:
            team["score"]
    )

    lowest = min(
        performances,
        key=lambda team:
            team["score"]
    )

    margins = []

    for game in completed_games:

        home_score = (
            game["homeScore"]
        )

        away_score = (
            game["awayScore"]
        )

        margin = abs(
            home_score -
            away_score
        )

        if home_score > away_score:

            winner_id = (
                game["homeTeamId"]
            )

            loser_id = (
                game["awayTeamId"]
            )

        elif away_score > home_score:

            winner_id = (
                game["awayTeamId"]
            )

            loser_id = (
                game["homeTeamId"]
            )

        else:

            winner_id = (
                game["homeTeamId"]
            )

            loser_id = (
                game["awayTeamId"]
            )

        margins.append({
            "margin":
                margin,
            "winnerId":
                winner_id,
            "loserId":
                loser_id
        })

    biggest = max(
        margins,
        key=lambda game:
            game["margin"]
    )

    closest = min(
        margins,
        key=lambda game:
            game["margin"]
    )

    game_of_week_text = (
        "Game not found"
    )

    featured = (
        featured_games.get(
            week
        )
    )

    if featured:

        team1_name = (
            featured["team1"]
        )

        team2_name = (
            featured["team2"]
        )

        team1_id = (
            manager_id_map.get(
                team1_name
            )
        )

        team2_id = (
            manager_id_map.get(
                team2_name
            )
        )

        for game in completed_games:

            game_team_ids = {
                game["homeTeamId"],
                game["awayTeamId"]
            }

            featured_ids = {
                team1_id,
                team2_id
            }

            if (
                game_team_ids
                ==
                featured_ids
            ):

                if (
                    game["homeTeamId"]
                    ==
                    team1_id
                ):

                    team1_score = (
                        game["homeScore"]
                    )

                    team2_score = (
                        game["awayScore"]
                    )

                else:

                    team1_score = (
                        game["awayScore"]
                    )

                    team2_score = (
                        game["homeScore"]
                    )

                game_of_week_text = (
                    f"{team1_name} "
                    f"{team1_score:.2f}"
                    f" — "
                    f"{team2_name} "
                    f"{team2_score:.2f}"
                )

                break

    highest_name = (
        manager_map.get(
            highest["teamId"],
            "Unknown"
        )
    )

    lowest_name = (
        manager_map.get(
            lowest["teamId"],
            "Unknown"
        )
    )

    biggest_winner = (
        manager_map.get(
            biggest["winnerId"],
            "Unknown"
        )
    )

    biggest_loser = (
        manager_map.get(
            biggest["loserId"],
            "Unknown"
        )
    )

    closest_winner = (
        manager_map.get(
            closest["winnerId"],
            "Unknown"
        )
    )

    closest_loser = (
        manager_map.get(
            closest["loserId"],
            "Unknown"
        )
    )

    recaps[str(week)] = {

        "highestScorer": (
            f"{highest_name} — "
            f"{highest['score']:.2f} pts"
        ),

        "lowestScorer": (
            f"{lowest_name} — "
            f"{lowest['score']:.2f} pts"
        ),

        "biggestBlowout": (
            f"{biggest_winner} defeated "
            f"{biggest_loser} by "
            f"{biggest['margin']:.2f}"
        ),

        "closestGame": (
            f"{closest_winner} defeated "
            f"{closest_loser} by "
            f"{closest['margin']:.2f}"
        ),

        "gameOfWeek":
            game_of_week_text
    }


# =========================================================
# ESPN STATUS
# =========================================================

status = data.get(
    "status",
    {}
)

current_matchup_period = (
    status.get(
        "currentMatchupPeriod",
        1
    )
)

current_scoring_period = (
    status.get(
        "currentScoringPeriod",
        1
    )
)


# =========================================================
# FINAL JSON OUTPUT
# =========================================================

output = {

    "leagueId":
        LEAGUE_ID,

    "season":
        SEASON,

    "lastUpdated":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "currentMatchupPeriod":
        current_matchup_period,

    "currentScoringPeriod":
        current_scoring_period,

    "teams":
        teams,

    "schedule":
        schedule,

    "draft":
        draft,

    "recaps":
        recaps
}


# =========================================================
# WRITE league-data.json
# =========================================================

with open(
    "league-data.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        output,
        file,
        indent=2
    )


# =========================================================
# COMPLETE
# =========================================================

print("")
print("=====================================")
print("JDC DEGENERATES ESPN UPDATE COMPLETE")
print("=====================================")

print(
    f"Teams loaded: "
    f"{len(teams)}"
)

print(
    f"Schedule matchups loaded: "
    f"{len(schedule)}"
)

print(
    f"Draft picks loaded: "
    f"{len(draft['picks'])}"
)

print("")
print(
    "league-data.json updated successfully."
)

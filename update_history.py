import json
import os
import requests
from datetime import datetime, timezone


# =========================================================
# JDC DEGENERATES - HISTORICAL ESPN DATA
# =========================================================

LEAGUE_ID = "90156758"
SEASONS = [2022, 2023, 2024, 2025]


# =========================================================
# ESPN SECRETS
# =========================================================

ESPN_S2 = os.environ["ESPN_S2"]
ESPN_SWID = os.environ["ESPN_SWID"]

cookies = {
    "espn_s2": ESPN_S2,
    "SWID": ESPN_SWID
}


# =========================================================
# TEAM NAME -> MANAGER
# =========================================================

manager_maps = {

    2022: {
        "Soup Kitchen Mike + The Boys": "Brian Weesner",
        "89 and a Wake Up": "Josh",
        "Hanging with Aaron Hernandez": "Devin",
        "OH AshBash": "Ashley Ellsworth",
        "Cincy Katherine": "Cynthia Reeves",
        "Let's Go Muskies!": "Tom",
        "Riley Reid Option": "Brian Roush",
        "Work Dream Team": "Jacob",
        "Ohio RiffRaff26": "John Rafferty",
        "Team H00ch": "Toby",
        "The Brady Bunch": "Alyssa Whalen",
        "The back alley Ball fondlers": "Dylan Rinck"
    },

    2023: {
        "WhoDey n the Blowfish": "Cynthia Reeves",
        "THE BENCHWARMERS": "Devin",
        "Buck Nuts": "Chad Nort",
        "89 and a Wake Up": "Josh",
        "Team H00ch": "Toby",
        "Pigskin Pirates": "Jacob",
        "Breeced Lightning": "Matt",
        "Locker Room Cowboy": "Brian Weesner",
        "Mean Machine": "Chad Marshall",
        "Let's Go Muskies!": "Tom"
    },

    2024: {
        "Whiskey no Chaser": "Philip",
        "Spitters Are Quitters": "Devin",
        "Buck Nuts": "Chad Nort",
        "89 and a Wake Up": "Josh",
        "Team H00ch": "Toby",
        "Chaser Justin Time": "Mike",
        "Breeced Lightning": "Matt",
        "Bang My Nabers": "Jake Deatley",
        "Mean Machine": "Chad Marshall",
        "Let's Go Muskies!": "Tom"
    },

    2025: {
        "Olave's Neurologist": "Jake Deatley",
        "Spitters Are Quitters": "Devin",
        "89 and a Wake Up": "Josh",
        "Let's Go Muskies!": "Tom",
        "Mean Machine": "Chad Marshall",
        "Turn Your Head and Goff": "Matt",
        "They Hit The Second Bower": "Mike",
        "Unsolicited Dak Pics": "Philip",
        "Buck Nuts": "Chad Nort",
        "Team H00ch": "Toby",
        "First Down Syndrome": "Chelsea Sumner",
        "OnlyFans": "Danielle Widmeyer",
        "Rowdy Rodney Pipers": "Rodney Hall",
        "Premature Ejeantylation": "Andrew Higgins"
    }
}


# =========================================================
# TEAM ID FALLBACK
#
# These IDs come directly from the historical ESPN data.
# They are used if ESPN's team-name formatting prevents
# the normal name match.
# =========================================================

team_id_fallback = {

    2022: {
        1: "Devin",
        2: "Alyssa Whalen",
        3: "Brian Roush",
        9: "Josh",
        11: "Brian Weesner"
    },

    2023: {
        2: "Chad Nort",
        9: "Josh"
    },

    2024: {
        2: "Chad Nort",
        9: "Josh"
    },

    2025: {
        2: "Chad Nort",
        9: "Josh",
        13: "Danielle Widmeyer"
    }
}


# =========================================================
# NORMALIZE TEAM NAMES
# =========================================================

def normalize_name(name):

    if not name:
        return ""

    name = str(name)

    name = (
        name
        .strip()
        .lower()
        .replace("’", "'")
        .replace("`", "'")
    )

    # Remove ESPN's strange spacing
    name = " ".join(name.split())

    return name


# =========================================================
# NORMALIZED NAME MAPS
# =========================================================

normalized_manager_maps = {}

for season, mapping in manager_maps.items():

    normalized_manager_maps[season] = {}

    for team_name, manager in mapping.items():

        clean_name = normalize_name(team_name)

        normalized_manager_maps[season][clean_name] = manager


# =========================================================
# FINAL HISTORY DATA
# =========================================================

history = {
    "leagueId": LEAGUE_ID,
    "lastUpdated": datetime.now(timezone.utc).isoformat(),
    "seasons": {}
}


# =========================================================
# PULL EACH SEASON
# =========================================================

for season in SEASONS:

    print("")
    print("=====================================")
    print(f"Pulling ESPN season {season}")
    print("=====================================")

    url = (
        "https://lm-api-reads.fantasy.espn.com/"
        "apis/v3/games/ffl/"
        f"seasons/{season}/segments/0/"
        f"leagues/{LEAGUE_ID}"
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
            f"ERROR: {season} returned "
            f"HTTP {response.status_code}"
        )

        history["seasons"][str(season)] = {
            "error": f"HTTP {response.status_code}"
        }

        continue

    data = response.json()


    # =====================================================
    # TEAMS
    # =====================================================

    teams = []
    team_id_lookup = {}


    for team in data.get("teams", []):

        team_id = team.get("id")

        team_name = team.get("name")


        # -------------------------------------------------
        # FALLBACK TEAM NAME
        # -------------------------------------------------

        if not team_name:

            location = team.get("location", "")
            nickname = team.get("nickname", "")

            team_name = (
                f"{location} {nickname}"
            ).strip()


        # -------------------------------------------------
        # TRY NAME MATCH FIRST
        # -------------------------------------------------

        clean_team_name = normalize_name(team_name)

        manager = (
            normalized_manager_maps
            .get(season, {})
            .get(clean_team_name)
        )


        # -------------------------------------------------
        # FALL BACK TO ESPN TEAM ID
        # -------------------------------------------------

        if not manager:

            manager = (
                team_id_fallback
                .get(season, {})
                .get(team_id)
            )


        # -------------------------------------------------
        # STILL NOT FOUND
        # -------------------------------------------------

        if not manager:

            manager = "UNKNOWN"


        # -------------------------------------------------
        # RECORD
        # -------------------------------------------------

        record = (
            team
            .get("record", {})
            .get("overall", {})
        )


        # -------------------------------------------------
        # LOOKUP TABLE
        # -------------------------------------------------

        team_id_lookup[team_id] = {
            "teamName": team_name,
            "manager": manager
        }


        # -------------------------------------------------
        # SAVE TEAM
        # -------------------------------------------------

        teams.append({
            "teamId": team_id,
            "teamName": team_name,
            "manager": manager,

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


    # =====================================================
    # MATCHUPS
    # =====================================================

    matchups = []


    for matchup in data.get("schedule", []):

        home = matchup.get("home", {})
        away = matchup.get("away", {})

        home_team_id = home.get("teamId")
        away_team_id = away.get("teamId")

        home_info = team_id_lookup.get(
            home_team_id,
            {}
        )

        away_info = team_id_lookup.get(
            away_team_id,
            {}
        )

        home_score = round(
            home.get("totalPoints", 0),
            2
        )

        away_score = round(
            away.get("totalPoints", 0),
            2
        )

        winner = matchup.get(
            "winner",
            "UNDECIDED"
        )

        margin = round(
            abs(home_score - away_score),
            2
        )


        # -------------------------------------------------
        # WINNER / LOSER MANAGER
        # -------------------------------------------------

        winner_manager = None
        loser_manager = None


        if winner == "HOME":

            winner_manager = home_info.get(
                "manager",
                "UNKNOWN"
            )

            loser_manager = away_info.get(
                "manager",
                "UNKNOWN"
            )


        elif winner == "AWAY":

            winner_manager = away_info.get(
                "manager",
                "UNKNOWN"
            )

            loser_manager = home_info.get(
                "manager",
                "UNKNOWN"
            )


        elif winner == "TIE":

            winner_manager = "TIE"
            loser_manager = "TIE"


        # -------------------------------------------------
        # SAVE MATCHUP
        # -------------------------------------------------

        matchups.append({

            "season": season,

            "week": matchup.get(
                "matchupPeriodId"
            ),

            "matchupPeriodId": matchup.get(
                "matchupPeriodId"
            ),

            "playoffTierType": matchup.get(
                "playoffTierType",
                "NONE"
            ),

            "winner": winner,

            "winnerManager": winner_manager,

            "loserManager": loser_manager,

            "margin": margin,


            # AWAY

            "awayTeamId": away_team_id,

            "awayTeamName": away_info.get(
                "teamName"
            ),

            "awayManager": away_info.get(
                "manager",
                "UNKNOWN"
            ),

            "awayScore": away_score,


            # HOME

            "homeTeamId": home_team_id,

            "homeTeamName": home_info.get(
                "teamName"
            ),

            "homeManager": home_info.get(
                "manager",
                "UNKNOWN"
            ),

            "homeScore": home_score
        })


    # =====================================================
    # CHECK MAPPINGS
    # =====================================================

    unknown_teams = [
        team
        for team in teams
        if team["manager"] == "UNKNOWN"
    ]


    if unknown_teams:

        print("")
        print(
            f"WARNING: {season} has "
            f"{len(unknown_teams)} unmapped team(s):"
        )

        for team in unknown_teams:

            print(
                f"  Team ID {team['teamId']} — "
                f"{team['teamName']}"
            )

    else:

        print(
            f"{season}: all teams mapped to managers."
        )


    # =====================================================
    # SAVE SEASON
    # =====================================================

    history["seasons"][str(season)] = {

        "teams": teams,

        "matchups": matchups,

        "status": data.get(
            "status",
            {}
        ),

        "settings": data.get(
            "settings",
            {}
        )
    }


    print(
        f"{season}: "
        f"{len(teams)} teams, "
        f"{len(matchups)} matchups"
    )


# =========================================================
# FINAL VALIDATION
# =========================================================

total_unknown = 0

for season_data in history["seasons"].values():

    for team in season_data.get("teams", []):

        if team.get("manager") == "UNKNOWN":

            total_unknown += 1


# =========================================================
# WRITE FILE
# =========================================================

with open(
    "league-history.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        history,
        file,
        indent=2
    )


# =========================================================
# COMPLETE
# =========================================================

print("")
print("=====================================")
print("JDC DEGENERATES HISTORY COMPLETE")
print("=====================================")

print("Created league-history.json")

print(
    f"Total unmapped teams: {total_unknown}"
)

if total_unknown == 0:

    print("")
    print(
        "SUCCESS: Every historical team "
        "has been mapped to a manager."
    )

else:

    print("")
    print(
        "WARNING: Some historical teams "
        "still need manager mappings."
    )

print("")

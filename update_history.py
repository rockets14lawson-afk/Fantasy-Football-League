import json
import os
import requests
from datetime import datetime, timezone


# =========================================================
# JDC DEGENERATES - HISTORICAL ESPN DATA
# =========================================================

LEAGUE_ID = "90156758"

SEASONS = [
    2022,
    2023,
    2024,
    2025
]


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
# HISTORICAL TEAM -> MANAGER MAPPING
#
# Based on the ESPN screenshots:
# Pic 1 = 2022
# Pic 2 = 2023
# Pic 3 = 2024
# Pic 4 = 2025
# =========================================================

manager_maps = {


    # -----------------------------------------------------
    # 2022
    # -----------------------------------------------------

    2022: {

        "Soup Kitchen Mike + The Boys":
            "Brian Weesner",

        "89 and a Wake Up":
            "Josh",

        "Hanging with Aaron Hernandez":
            "Devin",

        "OH AshBash":
            "Ashley Ellsworth",

        "Cincy Katherine":
            "Cynthia Reeves",

        "Let's Go Muskies!":
            "Tom",

        "Riley Reid Option":
            "Brian Roush",

        "Work Dream Team":
            "Jacob",

        "Ohio RiffRaff26":
            "John Rafferty",

        "Team H00ch":
            "Toby",

        "The Brady Bunch":
            "Alyssa Whalen",

        "The back alley Ball fondlers":
            "Dylan Rinck"

    },


    # -----------------------------------------------------
    # 2023
    # -----------------------------------------------------

    2023: {

        "WhoDey n the Blowfish":
            "Cynthia Reeves",

        "THE BENCHWARMERS":
            "Devin",

        "Buck Nuts":
            "Chad Nort",

        "89 and a Wake Up":
            "Josh",

        "Team H00ch":
            "Toby",

        "Pigskin Pirates":
            "Jacob",

        "Breeced Lightning":
            "Matt",

        "Locker Room Cowboy":
            "Brian Weesner",

        "Mean Machine":
            "Chad Marshall",

        "Let's Go Muskies!":
            "Tom"

    },


    # -----------------------------------------------------
    # 2024
    # -----------------------------------------------------

    2024: {

        "Whiskey no Chaser":
            "Philip",

        "Spitters Are Quitters":
            "Devin",

        "Buck Nuts":
            "Chad Nort",

        "89 and a Wake Up":
            "Josh",

        "Team H00ch":
            "Toby",

        "Chaser Justin Time":
            "Mike",

        "Breeced Lightning":
            "Matt",

        "Bang My Nabers":
            "Jake Deatley",

        "Mean Machine":
            "Chad Marshall",

        "Let's Go Muskies!":
            "Tom"

    },


    # -----------------------------------------------------
    # 2025
    # -----------------------------------------------------

    2025: {

        "Olave's Neurologist":
            "Jake Deatley",

        "Spitters Are Quitters":
            "Devin",

        "89 and a Wake Up":
            "Josh",

        "Let's Go Muskies!":
            "Tom",

        "Mean Machine":
            "Chad Marshall",

        "Turn Your Head and Goff":
            "Matt",

        "They Hit The Second Bower":
            "Mike",

        "Unsolicited Dak Pics":
            "Philip",

        "Buck Nuts":
            "Chad Nort",

        "Team H00ch":
            "Toby",

        "First Down Syndrome":
            "Chelsea Sumner",

        "OnlyFans":
            "Danielle Widmeyer",

        "Rowdy Rodney Pipers":
            "Rodney Hall",

        "Premature Ejeantylation":
            "Andrew Higgins"

    }

}


# =========================================================
# HELPER - NORMALIZE TEAM NAMES
# =========================================================

def normalize_name(name):

    if not name:
        return ""

    return (
        str(name)
        .strip()
        .lower()
        .replace("’", "'")
    )


# =========================================================
# BUILD NORMALIZED MANAGER MAPS
# =========================================================

normalized_manager_maps = {}

for season, mapping in manager_maps.items():

    normalized_manager_maps[season] = {

        normalize_name(team_name):
            manager

        for team_name, manager
        in mapping.items()

    }


# =========================================================
# FINAL HISTORY OBJECT
# =========================================================

history = {

    "leagueId":
        LEAGUE_ID,

    "lastUpdated":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "seasons":
        {}

}


# =========================================================
# LOOP THROUGH EACH SEASON
# =========================================================

for season in SEASONS:

    print("")
    print(
        "====================================="
    )

    print(
        f"Pulling ESPN season {season}"
    )

    print(
        "====================================="
    )


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


    # -----------------------------------------------------
    # HANDLE FAILED SEASON
    # -----------------------------------------------------

    if response.status_code != 200:

        print(
            f"ERROR: {season} returned "
            f"HTTP {response.status_code}"
        )

        history["seasons"][
            str(season)
        ] = {

            "error":
                f"HTTP {response.status_code}"

        }

        continue


    data = response.json()


    # =====================================================
    # TEAM ID LOOKUP
    # =====================================================

    team_id_lookup = {}

    teams = []


    for team in data.get(
        "teams",
        []
    ):


        team_id = (
            team.get("id")
        )


        team_name = (
            team.get("name")
        )


        if not team_name:

            location = (
                team.get(
                    "location",
                    ""
                )
            )

            nickname = (
                team.get(
                    "nickname",
                    ""
                )
            )

            team_name = (

                f"{location} "
                f"{nickname}"

            ).strip()


        normalized_team_name = (
            normalize_name(
                team_name
            )
        )


        manager = (

            normalized_manager_maps
            .get(
                season,
                {}
            )
            .get(
                normalized_team_name
            )

        )


        if not manager:

            manager = "UNKNOWN"


        record = (

            team
            .get(
                "record",
                {}
            )
            .get(
                "overall",
                {}
            )

        )


        # Save lookup for matchups

        team_id_lookup[
            team_id
        ] = {

            "teamName":
                team_name,

            "manager":
                manager

        }


        # Save team history

        teams.append({

            "teamId":
                team_id,

            "teamName":
                team_name,

            "manager":
                manager,

            "wins":
                record.get(
                    "wins",
                    0
                ),

            "losses":
                record.get(
                    "losses",
                    0
                ),

            "ties":
                record.get(
                    "ties",
                    0
                ),

            "pointsFor":
                round(
                    record.get(
                        "pointsFor",
                        0
                    ),
                    2
                ),

            "pointsAgainst":
                round(
                    record.get(
                        "pointsAgainst",
                        0
                    ),
                    2
                )

        })


    # =====================================================
    # MATCHUPS
    # =====================================================

    matchups = []


    for matchup in data.get(
        "schedule",
        []
    ):


        home = matchup.get(
            "home",
            {}
        )


        away = matchup.get(
            "away",
            {}
        )


        home_team_id = (
            home.get(
                "teamId"
            )
        )


        away_team_id = (
            away.get(
                "teamId"
            )
        )


        home_lookup = (

            team_id_lookup.get(
                home_team_id,
                {}
            )

        )


        away_lookup = (

            team_id_lookup.get(
                away_team_id,
                {}
            )

        )


        home_score = round(

            home.get(
                "totalPoints",
                0
            ),

            2

        )


        away_score = round(

            away.get(
                "totalPoints",
                0
            ),

            2

        )


        winner = matchup.get(
            "winner",
            "UNDECIDED"
        )


        # -------------------------------------------------
        # CALCULATE MARGIN
        # -------------------------------------------------

        margin = round(

            abs(
                home_score
                -
                away_score
            ),

            2

        )


        # -------------------------------------------------
        # WINNER MANAGER
        # -------------------------------------------------

        winner_manager = None


        if winner == "HOME":

            winner_manager = (
                home_lookup.get(
                    "manager"
                )
            )


        elif winner == "AWAY":

            winner_manager = (
                away_lookup.get(
                    "manager"
                )
            )


        elif winner == "TIE":

            winner_manager = "TIE"


        # -------------------------------------------------
        # SAVE MATCHUP
        # -------------------------------------------------

        matchups.append({

            "week":
                matchup.get(
                    "matchupPeriodId"
                ),

            "matchupPeriodId":
                matchup.get(
                    "matchupPeriodId"
                ),

            "playoffTierType":
                matchup.get(
                    "playoffTierType",
                    "NONE"
                ),

            "winner":
                winner,

            "winnerManager":
                winner_manager,

            "margin":
                margin,


            # -------------------------
            # AWAY
            # -------------------------

            "awayTeamId":
                away_team_id,

            "awayTeamName":
                away_lookup.get(
                    "teamName"
                ),

            "awayManager":
                away_lookup.get(
                    "manager",
                    "UNKNOWN"
                ),

            "awayScore":
                away_score,


            # -------------------------
            # HOME
            # -------------------------

            "homeTeamId":
                home_team_id,

            "homeTeamName":
                home_lookup.get(
                    "teamName"
                ),

            "homeManager":
                home_lookup.get(
                    "manager",
                    "UNKNOWN"
                ),

            "homeScore":
                home_score

        })


    # =====================================================
    # FIND UNKNOWN MANAGERS
    # =====================================================

    unknown_teams = [

        team

        for team in teams

        if team["manager"]
        ==
        "UNKNOWN"

    ]


    if unknown_teams:

        print("")
        print(
            f"WARNING: {season} has "
            f"{len(unknown_teams)} "
            "unmapped team(s):"
        )


        for team in unknown_teams:

            print(

                f"  Team ID "
                f"{team['teamId']} — "
                f"{team['teamName']}"

            )


    else:

        print(
            f"{season}: all teams mapped "
            "to managers."
        )


    # =====================================================
    # SAVE SEASON
    # =====================================================

    history[
        "seasons"
    ][
        str(season)
    ] = {

        "teams":
            teams,

        "matchups":
            matchups,

        "status":
            data.get(
                "status",
                {}
            ),

        "settings":
            data.get(
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
# WRITE league-history.json
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
print(
    "====================================="
)

print(
    "JDC DEGENERATES HISTORY COMPLETE"
)

print(
    "====================================="
)

print(
    "Created league-history.json"
)

print("")

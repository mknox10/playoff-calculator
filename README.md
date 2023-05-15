# Playoff Calculator

Python script that calculates all possible and relevant scenarios where a team will make the playoffs fantasy football playoffs.

# Installation

```bash
pip install -r /path/to/requirements.txt
```

# Usage

Arguments:
    league_type: 'espn', 'yahoo', 'sleeper' (Currently ESPN is the only supported platform).
    league_id: League ID from fantasy football platform.
        ex. https://fantasy.espn.com/football/team?leagueId=58391695&teamId=1&seasonId=2023 league_id = 58391695
    year: Which fantasy football season to load.
    week: Current NFL/Fantasy Football week.

```bash
    python playoff_calculator.py league_id  
```

# Output Structure

The output is a json structure in list form. Each value in the list contains different possible scenarios that a team will make the playoffs. The 'value' contains each individual matchup outcome that is needed.
An outcome will contain the team as the key and the win or loss result as the value. Where a one represents a needed win and zero represents a needed loss. The 'next' contains a list of the needed results for 
the following week's matchups. This will be a nested structure as deep as the weeks remaining. The deepest part of the structure will contain the 'tiebreaker' which is a true or false marking whether or not the
tiebreaker is needed for the given team to make the playoffs.

```json
[
  {
    "value": {
      "Zeke and Destroy": 1
    },
    "next": [
      {
        "value": {
          "TuAnon Believer": 0,
          "Game of Mahomes": 0,
          "Zeke and Destroy": 1
        },
        "tiebreaker": true
      }
    ]
  },
  {
    "value": {
      "Zeke and Destroy": 1,
      "TuAnon Believer": 0,
      "Game of Mahomes": 1
    },
    "next": [
      {
        "value": {
          "TuAnon Believer": 1,
          "Game of Mahomes": 0,
          "Zeke and Destroy": 1
        },
        "tiebreaker": true
      }
    ]
  },
  {
    "value": {
      "Zeke and Destroy": 1,
      "TuAnon Believer": 0
    },
    "next": [
      {
        "value": {
          "Game of Mahomes": 0,
          "Zeke and Destroy": 1
        },
        "tiebreaker": true
      }
    ]
  }
]
```

In the example above is the playoff scenarios for 'Zeke and Destroy' to make the playoffs with two weeks left in the season and the following standings:
``` python
    Team('Calvin Ridely\'s Parlays', 11),
    Team('Kyler\'s Study Zone', 9),
    Team('Hooked on a Thielen', 8),
    Team('Scam Akers', 8),
    Team('Hurts Doughnut', 8),
    Team('TuAnon Believer', 6),
    Team('Game of Mahomes', 6),
    Team(ZEKE_AND_DESTROY, 5),
    Team(THE_ADAMS_FAMILY, 5),
    Team('Mixon It Up', 3),
    Team('Breece Mode', 2),
    Team('Olave Garden', 1)
```
In the first scenario, if 'Zeke and Destroy' wins their upcoming matchup. In the last week of the season they must win again, but 'Game of Mahomes' and 'TuAnon Believer' must also lose. 
In the second scenario, if 'Zeke and Destroy' wins the upcoming matchup along with 'Game of Mahomes' while 'TuAnon Believer' loses. In the following week 'Zeke and Destroy' must win again
    along with 'TuAnon Believer' while 'Game of Mahomes' must lose.
In the third/final scenario, if 'Zeke and Destroy' wins their upcoming matchup while 'TuAnon Believer' loses. In the following week 'Zeke and Destroy' must win again, while 'Game of Mahomes'
    must lose.

# Limitations

- Does not handle tie games in any capacity.
- Does not identify which teams must be beat in a tiebreaker scenario.
- Scenarios are some times repetitive. As with the above scenario 'Zeke and Destroy' must win both remaining games while 'TuAnon Believer' and 'Game of Mahomes' must each lose at least one of 
    their remaining games. The playoff calculator currently will calculate every scenario in which that happens instead of diagnosing that.
- Any playoff scenarios larger than twelve teams and two weeks remaining are incredibly slow. This algorithm grows exponentially slower with additional teams or weeks.

# Future Work

- Refactor code (It's messy and hard to read)

# Reasoning 

Used an extensive use of dictionaries in this project in order to make exporting to json easier. In my opinion this makes the code harder to understand but makes reading the output file easier.
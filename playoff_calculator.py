from distutils.command.build_scripts import first_line_re
from re import match
from turtle import pos
# from espn_api.football import League
from itertools import product
import pandas as pd
import json
import espn_api.football as espn
import copy

# Definitions
# Outcome - Result of a matchup between two teams.
# Scenario - Combination of outcomes for a given week.
# Sequence - List of scenarios.

class Node:
    def __init__(self, value=None, week=None):
        self.value = value   # dict of team's win counts
        self.week = week     # fantasy football week
        self.next = None     # list of next weeks nodes
        self.previous = None # TODO: previous week node if needed

    def __str__(self):
        return (str(self.week) + " - " if self.week != None else "") + str(self.value)

    def copy(self):
        copy = Node(self.value)
        copy.next = self.next.copy() if len(self.next) > 0 else None
        copy.previous = self.previous.copy() if self.previous else None
        return copy

class League:
    def __init__(self, teams, remaining_schedule, playoff_team_count, regular_season_game_count):
        self.teams = teams
        self.remaining_schedule = remaining_schedule
        self.weeks_remaining = len(remaining_schedule)
        self.playoff_team_count = playoff_team_count
        self.regular_season_game_count = regular_season_game_count

class Team:
    def __init__(self, team_name, wins):
        self.team_name = team_name
        self.wins = wins





def main():
    # parameters 
    # league_type = sys[argv[1]] # espn
    # league_id = int(sys.argv[2]) # 1307984
    # year = int(sys.argv[3]) # 2021
    # week = (int(sys.argv[4]))
    league_type = 'espn'
    league_id = 1307984
    year = 2021
    week = 12

    match league_type:
        case 'espn':
            league = import_espn_league(league_id, year, week)
        case 'sleeper':
            league = import_sleeper_league()
        case 'yahoo':
            league = import_yahoo_league()
        case _:
            raise Exception('Platform: {} not found.'.format(league_type))

    results = run(league)
    for team, json_dict in results.items():
        with open('playoff scenarios {}.json'.format(team), 'w') as outfile:
            json.dump(json_dict, outfile)

    
def run(league):
    """ Calculate Playoff Scenarios. """
    standings = build_standings(league.teams)

    # create a list of base nodes, one for each team
    scenarios = {}
    for team in league.teams:
        scenarios[team.team_name] = Node(standings)
        scenarios[team.team_name].next = build_node_tree(league)

    for team, node in scenarios.items():
        calculate_playoff_scenarios(team, node, league)
    
    results = {}
    for team, node in scenarios.items():
        # Convert node structure into straight list
        scenario_list = compile_scenario_list(node, [])

        json_dict = {}
        if len(scenario_list[0]) <= 1:
            print('{} has been eliminated from playoff contention.'.format(team))
            json_dict = { 'value': 'eliminated'}
        else:
            remove_irrelevant_outcomes(scenario_list, team, league.playoff_team_count, league.remaining_schedule)

            json_dict = build_readable_json_structure({}, scenario_list)['next'][0]
            clinched = True
            loop_json = json_dict.copy()['next']

            while loop_json and clinched:
                if len(loop_json) > 1 or bool(loop_json[0]['value']):
                    clinched = False
                else:
                    loop_json = loop_json[0]['next']

            if clinched:
                print('{} has been clinched a playoff birth.'.format(team))
                json_dict = { 'value': 'clinched' }
        
        results[team] = json_dict

    return results


def import_espn_league(league_id, year, week):
    """ Import league data from espn and store in local data structure. """

    print('Importing ESPN league: {}'.format(str(league_id)))
    espn_league = espn.League(league_id=league_id, year=year)

    regular_season_games = espn_league.settings.reg_season_count
    weeks_remaining = regular_season_games - week + 1

    # Create 'Team' objects.
    teams = []
    for espn_team in espn_league.teams:
        teams.append(Team(espn_team.team_name, sum(outcome == 'W' for outcome in espn_team.outcomes)))

    # Construct remaining schedule.
    remaining_schedule = []
    for x in range(weeks_remaining):
        matchups = []
        for matchup in espn_league.scoreboard(regular_season_games - x):
            matchups.append((matchup.away_team.team_name, matchup.home_team.team_name))
        remaining_schedule.append(matchups)

    return League(teams, remaining_schedule, espn_league.settings.playoff_team_count, espn_league.settings.reg_season_count)



def import_sleeper_league():
    """ Import league data from sleeper and store in local data structure. """
    raise Exception('Sleeper is not yet a supported platform.')

def import_yahoo_league():
    """ Import data from espn and store in local data structure. """
    raise Exception('Yahoo is not yet a supported platform.')

def build_standings(teams):
    """ Build a dictionary with each teams win count. """
    return dict((team.team_name, team.wins) for team in teams)



def build_readable_json_structure(json, scenario_list):
    """ Convert list of scenarios into readable json structure. """
    next_list = []

    for scenario in scenario_list:
        if len(scenario) > 0:
            string_dict = scenario[0]
            val = next((sc for sc in next_list if sc['value'] == string_dict), None)
            if val is not None:
                val['next'].append(scenario[1:])
            else:
                scenario = {
                    'value': scenario[0],
                    'next': [scenario[1:]] # Remove first element from list and add remaining to next list.
                }
                next_list.append(scenario)
    
    for val in next_list:
        build_readable_json_structure(val, val['next'])

    json['next'] = next_list
    return json
        

def remove_irrelevant_outcomes(sequences, team, num_playoff_teams, remaining_schedule):
    """ 
    Remove outcomes that do not effect playoff scenarios for the given team. 
      sequences -         List of sequences. (See Definitions)
      team -              The team whos playoff scenarios are being evaluated.
      num_playoff_teams - The number of teams that make the playoffs.
    """
    
    print("Info: Filtering Unique Results: ", team)
    if team ==  'TuAnon Believer':
        for sequence in sequences:
            # The first value in each sequence is the current standings - skip this in the following loop.
            for idx, scenario in enumerate(sequence[1:].copy()):
                scenario_copy = scenario.copy()
                for key, value in scenario_copy.items():
                    sequence_modified = sequence.copy()
                    scenario_modified = scenario_copy.copy()

                    # TODO: not working on second loop on 2+ weeks
                    #Somthing must be wrong with ccopying somewhere, first iteration works as expected.


                    # Change the result of a single matchup.
                    matchup = next(matchup for matchup in remaining_schedule[idx] if key in matchup)
                    opposing_team = matchup[1] if matchup[0] == key else matchup[0] 
                    if value == 1:
                        scenario_modified[key] = 0
                        scenario_modified[opposing_team] = 1
                    else:
                        scenario_modified[key] = 1
                        scenario_modified[opposing_team] = 0

                    sequence_modified[idx+1] = scenario_modified

                    # TODO: Do I need to loop through every result and see if the alternate matchup out come changes playoff scenario before removing? I think yes...
                    # For each other team assume they win out.

                    # Build standings objecect with changed result.
                    standings = sequence[0].copy()
                    for x in sequence_modified[1:]:
                        for team2, result in x.items():
                            standings[team2] += result

                    # If this does not change whether the team makes the playoffs or not, the outcome is irrelevant and should be removed.
                    if standings[team] >= wins_needed(standings, 0, num_playoff_teams, False):
                        sequence[idx+1].pop(key, None)

                #TODO: Mark if playoff it is a tie for the playoffs.



def wins_needed(standings, weeks_remaining, num_playoff_teams, without_tiebreaker):
    """ Calculates the minimum number of wins a team needs to make the playoffs assuming they will win out. """

    without_tiebreaker = True
    standings = dict(sorted(standings.items(), key=lambda item: item[1], reverse=True))
    min_playoff_wins = 0
    teams_included = 0
    for team in standings:
        if num_playoff_teams > teams_included:
            min_playoff_wins = standings[team]
            teams_included += 1
        elif min_playoff_wins == standings[team] and without_tiebreaker:
            min_playoff_wins += 1
    
    return min_playoff_wins + weeks_remaining



def calculate_playoff_scenarios(team, node, league):
    """  """
    # TODO: clean function.
    weeks_remaining = league.weeks_remaining
    num_playoff_teams = league.playoff_team_count

    for scenario in node.next.copy():
        x = scenario.value.copy()
        for key, value in node.value.items():
            x[key] += value
        wins = wins_needed(x, weeks_remaining, num_playoff_teams, False)
        # assume the team will win out, we will handle the situation in which they don't in future iterations.
        scenario.value = get_unique_scenarios(scenario)
        if x[team] + weeks_remaining < wins:
            node.next.remove(scenario)
        if not scenario.next:
            calculate_playoff_scenarios(team, scenario, league)



def check_non_exclusive_scenario(scenario1, scenario2, team):
    """   """
    # The number of game out comes that don't match, for a non-exclusive scenario there must be less than 2.
    for key, value in scenario1.value.items():
        if scenario1.value[key] != scenario2.value[key] and key != team:
            return False
    return True
        



# TODO: I don't think this does anything
def get_unique_scenarios(node):
    """ 
    remove results that aren't exclusively needed
    example: a player wins last week of the season all the other outcomes of the other games do not matter. 
    """

    unique = {}
    for scenario in node.next:
        for key, value in scenario.value.items():
            if key not in unique:
                unique[key] = value
            else:
                if unique[key] != value:
                    unique[key] = -1
    unique_scenario = False
    for key, value in unique.copy().items():
        if value != -1:
            unique_scenario = True
    if unique_scenario:
        return unique
    else:
        return node.value



def build_node_tree(league):
    """" 
    Build the Node tree. 
      remaining_schedule:
      reg_season_count: Number of games in the regular season
    """
    #TODO: clean up function
    remaining_schedule = league.remaining_schedule.copy()
    reg_season_count = league.regular_season_game_count

    previous_week_outcomes = []
    first_week_outcomes = []
    while len(remaining_schedule) > 0:
        matchups = remaining_schedule.pop()
        outcomes = calculate_weekly_outcomes(matchups, reg_season_count - len(remaining_schedule))
        if len(previous_week_outcomes) > 0:
            for outcome in previous_week_outcomes:
                outcome.next = outcomes
        else:
            first_week_outcomes = outcomes
        previous_week_outcomes = outcomes

    return first_week_outcomes



def calculate_weekly_outcomes(matchups, week_number):
    """ Returns a list of all possible outcomes of a given week. """

    case = ['W', 'L']
    outcomes = []
    for permutation in product(case, repeat=len(matchups)):
        scenario = {}
        for x in range(len(matchups)):
            matchup = matchups[x]
            outcome = permutation[x]
            scenario[matchup[0]] = 1 if outcome == 'W' else 0
            scenario[matchup[1]] = 0 if outcome == 'W' else 1
        node = Node(scenario, week_number)
        node.next = []
        outcomes.append(node)
    return outcomes



def compile_scenario_list(node, path):
    """ 
    Transforms node tree structure into an iterable list.
      node - ...
      path - list of matchups in current recursive set.
    """
    scenarios = []
    if not node.next:
        outcome = {}
        for team, value in node.value.items():
            outcome.update({team: value})

        next_path = path.copy()
        next_path.append(outcome)
        scenarios.append(next_path)
    else:
        next_path = path.copy()
        next_path.append(node.value)
        for next in node.next:
            for scenario in compile_scenario_list(next, next_path):
                scenarios.append(copy.deepcopy(scenario))
    return scenarios



def print_scenarios(team, node, string_builder):
    """ Print Scenarios as a readable list. """

    if not string_builder:
        print(team.team_name)
        # if len(node.next) > 0:
        #     print(node.value)
    if len(node.next) > 0:
        for v in node.next.copy():
            child_string = string_builder + str(v) +'\n'
            print_scenarios(team, v, child_string)
    else:
        print(string_builder)


def export_data_to_csv(scenarios, teams):
    """ 
    Exports the results to a csv file for easier debugging.
      scenarios: Dictionary containing a list of playoff scenarios for each team.
      teams: List of team names to be used as column headers.
    """
    print("DEBUG: Building CSV")
    column_headers = ['Week']
    for team in teams:
        column_headers.append(team)

    for team, value in scenarios.items():
        # build_csv_rows(key, value, [])
        results = build_csv_rows(team, value, [], teams)
        

        playoff_scenarios = pd.DataFrame(results, columns=column_headers)
        playoff_scenarios.to_csv('playoff_scenarios_{}.csv'.format(team.team_name))




def build_csv_rows(team, node, results, teams):
    """
    
      results: list of csv rows.
    """
    if len(node.next) > 0:
        for next in node.next.copy():
            build_csv_rows(team, next, results, teams)
        return results
    else:
        row = [node.week]
        for team in teams:
            row.append('W') if node.value[team.team_name] else row.append('L')
            results.append(row)
        # return row



if __name__ == "__main__":
    main()

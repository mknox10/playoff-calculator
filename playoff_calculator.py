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
        self.tiebreaker = False # Does this scenario require a tiebreaker win to make the playoffs.
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
        calculate_playoff_scenarios(team, node, league.weeks_remaining, league.playoff_team_count, node.value)
    
    results = {}
    for team, node in scenarios.items():
        # Convert node structure into straight list
        scenario_data = compile_scenario_list(node, [])
        # Why is this double nested
        scenario_list = scenario_data

        json_dict = {}
        if len(scenario_list) <= 1:
            print('{} has been eliminated from playoff contention.'.format(team))
            json_dict = { 'value': 'eliminated'}
        else:
            remove_irrelevant_outcomes(scenario_list, team, league)

            json_dict = build_readable_json_structure({}, scenario_list)['next'][0]

            clinched = True
            loop_json = json_dict.copy()['next']

            while loop_json and clinched:
                if len(loop_json) > 1 or bool(loop_json[0]['value']):
                    clinched = False
                else:
                    if 'next' in loop_json:
                        loop_json = loop_json[0]['next']
                    else:
                        loop_json = False

            if clinched:
                print('{} has clinched a playoff birth.'.format(team))
                json_dict = {'value': 'clinched'}
        
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
        if len(scenario['scenarios']) > 1:
            string_dict = scenario['scenarios'][0]
            val = next((sc for sc in next_list if sc['value'] == string_dict), None)
            if val is not None:
                val['next'].append({'scenarios': scenario['scenarios'][1:], 'tiebreaker': scenario['tiebreaker']})
            else:
                scenario_data = {
                    'value': scenario['scenarios'][0],
                    'next': [{'scenarios': scenario['scenarios'][1:], 'tiebreaker': scenario['tiebreaker']}] # Remove first element from list and add remaining to next list.
                }
                next_list.append(scenario_data)
        elif len(scenario['scenarios']) > 0:
            string_dict = scenario['scenarios'][0]
            val = next((sc for sc in next_list if sc['value'] == string_dict), None)
            if val is not None and scenario['tiebreaker'] != val['tiebreaker']:
                raise Exception("Yooo WTF!")
            elif val is None:
                scenario_data = {
                    'value': scenario['scenarios'][0],
                    'tiebreaker': scenario['tiebreaker'] # Remove first element from list and add remaining to next list.
                }
                next_list.append(scenario_data)
    
    json['next'] = next_list
    for val in next_list:
        if 'next' in val:
            build_readable_json_structure(val, val['next'])

    return json



def remove_irrelevant_outcomes_from_json(json, team, num_playoff_teams, remaining_schedule):


    print("Info: Filtering Unique Results")

    
        

def remove_irrelevant_outcomes_old(sequences, team, num_playoff_teams, remaining_schedule):
    """ 
    Remove outcomes that do not effect playoff scenarios for the given team. 
      sequences -         List of sequences. (See Definitions)
      team -              The team whos playoff scenarios are being evaluated.
      num_playoff_teams - The number of teams that make the playoffs.
    """
    
    print("Info: Filtering Unique Results: ", team)
    if team == 'TuAnon Believer':
    # if True:
        for sequence in sequences:
            # The first value in each sequence is the current standings - skip this in the following loop.
            for idx, scenario in enumerate(sequence['scenarios'][1:].copy()):
                scenario_copy = scenario.copy()
                irrelevant = False
                for key, value in scenario_copy.items():

                    #TODO: key should instead be the matchup both results of the matchup should be kept
                    sequence_modified = copy.deepcopy(sequence['scenarios'])
                    scenario_modified = scenario_copy.copy()


                    # Change the result of a single matchup.
                    # matchup = next(matchup for matchup in remaining_schedule[idx] if key in matchup)
                    # opposing_team = matchup[1] if matchup[0] == key else matchup[0] 
                    # if value == 1:
                    #     scenario_modified[key] = 0
                    #     scenario_modified[opposing_team] = 1
                    # else:
                    #     scenario_modified[key] = 1
                    #     scenario_modified[opposing_team] = 0

                    # sequence_modified[idx+1] = scenario_modified

                    # TODO: Do I need to loop through every result and see if the alternate matchup out come changes playoff scenario before removing? I think yes...
                    # For each other team assume they win out. I need to do this for every possible combination... fuck!
                    # For each other possible outcome... use wins_needed to check if 'team' has made playoffs.
                    # If and only if the 'team' makes the playoffs in every scenario then remove the key from the sequence['scenarios']

                    # Do something like this...
                    # case = ['W', 'L']
                    # outcomes = []
                    # for permutation in product(case, repeat=len(matchups)):
                    #     scenario = {}
                    #     for x in range(len(matchups)):
                    #         matchup = matchups[x]
                    #         outcome = permutation[x]
                    #         scenario[matchup[0]] = 1 if outcome == 'W' else 0
                    #         scenario[matchup[1]] = 0 if outcome == 'W' else 1
                    #     node = Node(scenario, week_number)
                    #     node.next = []
                    #     outcomes.append(node)
                    # return outcomes
                    case = ['W', 'L']
                    base_standings = sequence['scenarios'][0]


    # I don't think we can do all permutations... we've already eliminated permutations in which a team misses the playoffs. I can't bring that back into the fold here.
    # Retry the original design, does the opposite outcome for 'key' impact the playoff chances for 'team' for this specific scenario.
    # Does the opposite outcome for key have impacts on future weeks?


                    permutations = product(case, repeat=len(remaining_schedule[idx]))

                    for permutation in permutations:
                        updated_standings = copy.deepcopy(base_standings)
                        for x in range(len(remaining_schedule[idx])):
                            case_matchup = remaining_schedule[idx][x]
                            if case_matchup[0] == key or case_matchup[1] == key:
                                #TODO: this does not need to be in loop. Could then decrease permutation length by 1...
                                if case_matchup[0] == key:
                                    updated_standings[case_matchup[0]] += value
                                    updated_standings[case_matchup[1]] += 0 if value == 1 else 1
                                elif case_matchup[1] == key:
                                    updated_standings[case_matchup[0]] += 0 if value == 1 else 1
                                    updated_standings[case_matchup[1]] += value
                            else:
                                outcome = permutation[x]
                                updated_standings[case_matchup[0]] += 1 if outcome == 'W' else 0
                                updated_standings[case_matchup[1]] += 0 if outcome == 'W' else 1

                        initial_update = copy.deepcopy(updated_standings)
                
                        for i, x in enumerate(sequence_modified):
                            # Don't do week of permutations
                            if i != 0 and i != idx+1:
                                for team2, result in x.items():
                                    updated_standings[team2] += result
                        
                        #TODO: what conditions should the outcome be marked as irrelevant? - Should only be removed if all permutations lead to this same outcome
                        wins_data = wins_needed(updated_standings, 0, num_playoff_teams, team)

                        # Doesn't seem like the cleanest solution. If the below if statement is True for every permutation then the scenario is irrelevant
                        if updated_standings[team] >= wins_data['wins'] and wins_data['tiebreaker'] == sequence['tiebreaker']:
                            irrelevant = True
                        else:
                            # Outcome (key) is relevant to playoff scenarios
                            irrelevant = False
                            break
                    if irrelevant:
                        sequence['scenarios'][idx+1].pop(key, None)

                # Build standings objecect with changed result.

                # If this does not change whether the team makes the playoffs or not, the outcome is irrelevant and should be removed.

            #TODO: Mark if playoff it is a tie for the playoffs.




def remove_irrelevant_outcomes(playoff_scenarios, team, league):


    print("Info: Filtering Unique Results: ", team)
    testing_team =  'Hooked on a Thielen'

    if team == testing_team:
        print(testing_team)
    if True:
        for scenario in playoff_scenarios:
            scenario_copy = copy.deepcopy(scenario)

            base_standings = scenario['scenarios'][0]
            irrelevant_events = []

            team_total_wins = base_standings[team] #TODO: I don't think this is needed.

            # The first value in each sequence is the current standings - skip this in the following loop.
            for idx1, event in enumerate(scenario['scenarios'][1:].copy()):
                team_total_wins += event[team]

                irrelevant_teams = []
                # Loop through each matchup for the given week.
                for matchup in league.remaining_schedule[idx1]:

                    # Temp variables
                    modified_standings = copy.deepcopy(base_standings)
                    full_standings = copy.deepcopy(base_standings)
                    event_copy = event.copy()
                    away_team = matchup[0]
                    home_team = matchup[1]

                    # Change outcome of the matchup to check if it is irrelevant
                    event_copy[away_team] = 0 if event[away_team] else 1 #TODO: This conditional could be a funciton.
                    event_copy[home_team] = 0 if event[home_team] else 1 

                    for idx2, updated_event in enumerate(scenario['scenarios'][1:]):
                        event_outcomes = event_copy if idx1 == idx2 else updated_event # This is the modified value so use the modified variable
                        for event_team, event_outcome in event_outcomes.items():
                            modified_standings[event_team] += event_outcome
                            full_standings[event_team] += updated_event[event_team]
                        

                    wins_data = wins_needed(modified_standings, 0, league.playoff_team_count, team)
                    if modified_standings[team] >= wins_data['wins'] and wins_data['tiebreaker'] == scenario['tiebreaker']:
                        irrelevant_teams.append(matchup[0])
                        irrelevant_teams.append(matchup[1])
            
                irrelevant_events.append(irrelevant_teams)

            for irrelevant_team in league.teams:
                irrelevant_weeks = 0
                team_has_potential_irrelevant_outcomes = False
                # wins_needed - league_team add weeks remaining to win count.
                for irrelevant_week in irrelevant_events:
                    if irrelevant_team.team_name in irrelevant_week:
                        irrelevant_weeks += 1
                        team_has_potential_irrelevant_outcomes = True

                total_irrelevant_matchups_allowed = irrelevant_outcomes_allowed(team, irrelevant_team.team_name, copy.deepcopy(full_standings), scenario['tiebreaker'], league, scenario['scenarios'][1:])

                if team_has_potential_irrelevant_outcomes:
                    if irrelevant_weeks > total_irrelevant_matchups_allowed:
                        if team == testing_team:
                            # Both Mixon It Up and Hooked on a Thielen lost in week 13, while Scam Akers and The Adams Family both won... Interesting... scenarios are defs out of order...
                            huh = irrelevant_outcomes_allowed(team, irrelevant_team.team_name, copy.deepcopy(full_standings), scenario['tiebreaker'], league, scenario['scenarios'][1:])
                    else:
                        # This teams outcomes are indeed irrelevant. Go forward with removing them.
                        for idx, event in enumerate(irrelevant_events):
                            if irrelevant_team.team_name in irrelevant_events[idx]:
                                scenario['scenarios'][idx+1].pop(irrelevant_team.team_name, None)
                else: 
                    temp = 'huh'

                    
def irrelevant_outcomes_allowed(playoff_team, irrelevant_team, standings, tiebreaker, league, remaining_outcomes):
    """ Determines the maximum number of games a team's matchup can be marked as irrelevant. """
    # TODO: When calculating which teams a team must outscore when calculating tiebreakers this function will need to be adjusted.
    #           This function only accounts for whether or not a tiebreaker is needed, not which teams the tiebreaker is need for.

    # TODO: This might need to be looped by matchup...

    max_irrelevant_games = 0
    no_changes = True
    x = 0
    while no_changes and x < len(remaining_outcomes):

        matchup = next(matchup for matchup in league.remaining_schedule[x] if irrelevant_team in matchup)
        irrelevant_team_opponent = matchup[1] if matchup[0] == irrelevant_team else matchup[0] 
        standings[irrelevant_team] += 0 if remaining_outcomes[x][irrelevant_team] else 1
        standings[irrelevant_team_opponent] -= 0 if remaining_outcomes[x][irrelevant_team] else 1

        wins_data = wins_needed(standings, 0, league.playoff_team_count, playoff_team)
        if wins_data['tiebreaker'] == tiebreaker and standings[playoff_team] >= wins_data['wins']:
            max_irrelevant_games += 1
        else:
            no_changes = False
        x += 1
    
    return max_irrelevant_games





def wins_needed(standings, weeks_remaining, num_playoff_teams, playoff_team):
    """ Calculates the minimum number of wins a team needs to make the playoffs assuming they will win out. """

    standings = dict(sorted(standings.items(), key=lambda item: item[1], reverse=True))
    min_playoff_wins = 0
    teams_included = 0
    tiebreaker_needed = False
    for team in standings:
        if num_playoff_teams > teams_included:
            min_playoff_wins = standings[team]
            teams_included += 1
        elif min_playoff_wins == standings[team]:
            tiebreaker_needed = True

    
    
    playoff_status = {}
    playoff_status['tiebreaker'] = tiebreaker_needed and standings[playoff_team] == min_playoff_wins
    playoff_status['wins'] = min_playoff_wins + weeks_remaining
    return playoff_status



def calculate_playoff_scenarios(team, node, weeks_remaining, num_playoff_teams, standings):
    """  """

    for scenario in node.next.copy():
        standings_copy = copy.deepcopy(standings) # Do I need a deep copy here
        # if scenario.value['Calvin Ridely\'s Parlays'] == 1 and scenario.value['Kyler\'s Study Zone'] == 0 and scenario.value['Hooked on a Thielen'] == 1 and scenario.value['Scam Akers'] == 0 and scenario.value['Hurts Doughnut'] == 0 and scenario.value['TuAnon Believer'] == 1 and scenario.value['Game of Mahomes'] == 0 and scenario.value['Zeke and Destroy'] == 1 and scenario.value['Mixon It Up'] == 0 and scenario.value['Breece Mode'] == 1 and scenario.value['The Adams Family'] == 1 and scenario.value['Olave Garden'] == 0:
        #     print('here')
        for key, value in scenario.value.items():
            standings_copy[key] += value
        playoff_status = wins_needed(standings_copy, weeks_remaining-1, num_playoff_teams, team)
        wins = playoff_status['wins']
        # assume the team will win out, we will handle the situation in which they don't in future iterations.
        scenario.value = scenario.value
        if standings_copy[team] + weeks_remaining-1 < wins:
            node.next.remove(scenario)
        elif scenario.next:
            # Remove irrelevant outcomes could be here
            # Then build scenerio list directly from here, a list for each child node that matches the playoff condition.

            calculate_playoff_scenarios(team, scenario, weeks_remaining-1, num_playoff_teams, standings_copy)
        elif playoff_status['tiebreaker']:
            # Only need to mark the last week
            scenario.tiebreaker = True



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
        matchups = remaining_schedule.pop(0)
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
    #TODO: something has to be wrong here...
    """ 
    Transforms node tree structure into an iterable list.
      node - ...
      path - list of matchups in current recursive set.
    """
    scenarios = []
    if not node.next:
        scenario_data = {}
        outcome = {}
        for team, value in node.value.items():
            outcome.update({team: value})

        next_path = copy.deepcopy(path)
        next_path.append(outcome)
        scenarios.append(next_path)

        scenario_data['tiebreaker'] = node.tiebreaker
        scenario_data['scenarios'] = scenarios[0]
        return [scenario_data]
    else:
        next_path = path.copy()
        next_path.append(node.value)
        for next in node.next:
            scenario_data = compile_scenario_list(next, next_path)
            # for scenario in scenario_data['scenarios']:
            for scenario in scenario_data:
                # data = { 'scenarios': copy.deepcopy(scenario) }
                # if 'tiebreaker' in scenario_data and scenario_data['tiebreaker']:
                #     data['tiebreaker'] = True
                # elif len(scenario_data['scenarios']) == 1:
                #     data['tierbreaker'] = False
                scenarios.append(copy.deepcopy(scenario))
                
        # scenario_data = { 'scenarios': scenarios }
        # if not path:
        #     return scenario_data['scenarios']
        return scenarios
        #TODO: If this is parent return call only return scenario_list (scenarios)



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

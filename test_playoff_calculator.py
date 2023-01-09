import unittest

from playoff_calculator import League, Team, Node, run, build_node_tree, calculate_playoff_scenarios, compile_scenario_list, wins_needed

import json

# https://realpython.com/python-testing/#automated-vs-manual-testing

ELIMINATED = { 'value': 'eliminated' }
CLINCHED = { 'value': 'clinched' }

class TestPlayoffCalculator(unittest.TestCase):

    def test_run(self):

        teams = [
            Team('Calvin Ridely\'s Parlays', 11),
            Team('Kyler\'s Study Zone', 9),
            Team('Hooked on a Thielen', 8),
            Team('Scam Akers', 8),
            Team('Hurts Doughnut', 8),
            Team('TuAnon Believer', 6),
            Team('Game of Mahomes', 6),
            Team('Zeke and Destroy', 5),
            Team('The Adams Family', 5),
            Team('Mixon It Up', 3),
            Team('Breece Mode', 2),
            Team('Olave Garden', 1),
        ]

        # Use a 14 week regular season schedule.

        week_13 = [
            ('Calvin Ridely\'s Parlays', 'Olave Garden'),
            ('Kyler\'s Study Zone', 'Breece Mode'),
            ('Hooked on a Thielen', 'Mixon It Up'),
            ('Scam Akers', 'The Adams Family'),
            ('Hurts Doughnut', 'Zeke and Destroy'),
            ('TuAnon Believer', 'Game of Mahomes')
        ]

        # Test two weeks remaining
        week_14 = [
            ('Calvin Ridely\'s Parlays', 'Kyler\'s Study Zone'),
            ('Hooked on a Thielen', 'Scam Akers'),
            ('Hurts Doughnut', 'TuAnon Believer'),
            ('Game of Mahomes', 'Zeke and Destroy'),
            ('The Adams Family', 'Mixon It Up'),
            ('Breece Mode', 'Olave Garden')
        ]


        # Test one week remaining.
        league = League(teams, [week_13], 6, 13)

        taunon_believer_expected_results = {'TuAnon Believer': 1, 'Game of Mahomes': 0}
        game_of_mahomes_expected_results = {'Game of Mahomes': 1, 'TuAnon Believer': 0}

        results = run(league)

        self.assertEqual(results['Calvin Ridely\'s Parlays'], CLINCHED)
        self.assertEqual(results['Kyler\'s Study Zone'], CLINCHED)
        self.assertEqual(results['Hooked on a Thielen'], CLINCHED)
        self.assertEqual(results['Scam Akers'], CLINCHED)
        self.assertEqual(results['Hurts Doughnut'], CLINCHED)
        self.assertEqual(results['Zeke and Destroy'], ELIMINATED)
        self.assertEqual(results['The Adams Family'], ELIMINATED)
        self.assertEqual(results['Mixon It Up'], ELIMINATED)
        self.assertEqual(results['Breece Mode'], ELIMINATED)
        self.assertEqual(results['Olave Garden'], ELIMINATED)

        tuanon_believer_results = results['TuAnon Believer']
        game_of_mahomes_results = results['Game of Mahomes']

        self.assertEqual(len(tuanon_believer_results['next']), 1)
        self.assertEqual(len(game_of_mahomes_results['next']), 1)
        self.assertEqual(tuanon_believer_results['next'][0]['value'], taunon_believer_expected_results)
        self.assertEqual(game_of_mahomes_results['next'][0]['value'], game_of_mahomes_expected_results)

        league = League(teams, [week_13, week_14], 6, 14)

        standings = {}
        for team in teams:
            standings[team.team_name] = team.wins

        node = Node(standings)
        node.next = build_node_tree(league)

        # calculate_playoff_scenarios('TuAnon Believer', node, league.weeks_remaining, league.playoff_team_count, node.value)
        # scenario_list = compile_scenario_list(node, [])

        # results = []
        # for scenario in scenario_list:
        #     scenario_standings = scenario[0]
        #     for week in scenario[1:]:
        #         for key, value in week.items():
        #             scenario_standings[key] += value
        #     results.append(scenario_standings)
        #     if scenario_standings['TuAnon Believer'] < wins_needed(scenario_standings, 0, league.playoff_team_count, False):
        #         print('uh oh')

            

        results = run(league)

        self.assertEqual(results['Calvin Ridely\'s Parlays'], CLINCHED)
        self.assertEqual(results['Kyler\'s Study Zone'], CLINCHED)
        self.assertEqual(results['Hooked on a Thielen'], CLINCHED)
        self.assertEqual(results['Scam Akers'], CLINCHED)
        self.assertEqual(results['Hurts Doughnut'], CLINCHED)

        with open('playoff_scenarios_tuanon_believer.json'.format(team), 'w') as outfile:
            json.dump(results['TuAnon Believer'], outfile)

        # with open('playoff_scenarios_game_of_mahomes.json'.format(team), 'w') as outfile:
            json.dump(results['Game of Mahomes'], outfile)

        with open('playoff_scenarios_zeke_and_destroy.json'.format(team), 'w') as outfile:
            json.dump(results['Zeke and Destroy'], outfile)

        with open('playoff_scenarios_the_adams_family.json'.format(team), 'w') as outfile:
            json.dump(results['The Adams Family'], outfile)

        self.assertEqual(results['Mixon It Up'], ELIMINATED)
        self.assertEqual(results['Breece Mode'], ELIMINATED)
        self.assertEqual(results['Olave Garden'], ELIMINATED)



if __name__ == '__main__':
    unittest.main()
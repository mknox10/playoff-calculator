import filecmp
import unittest

from playoff_calculator import League, Team, ScenarioStructure, run_playoff_calculator, calculate_all_possible_scenarios, calculate_all_playoff_scenarios, compile_scenario_list, wins_needed

import json

# https://realpython.com/python-testing/#automated-vs-manual-testing

# Team Names
THE_ADAMS_FAMILY = 'The Adams Family'
ZEKE_AND_DESTROY = 'Zeke and Destroy'

# Constants
CLINCHED = { 'value': 'clinched' }
ELIMINATED = { 'value': 'eliminated' }
NEXT = 'next'
ACTUAL_OUTPUT_DIRECTORY = 'actual-outputs'
GOAL_OUTPUT_DIRECTORY = 'goal-outputs'


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
            Team(ZEKE_AND_DESTROY, 5),
            Team(THE_ADAMS_FAMILY, 5),
            Team('Mixon It Up', 3),
            Team('Breece Mode', 2),
            Team('Olave Garden', 1),
        ]

        week_13 = [
            ('Calvin Ridely\'s Parlays', 'Olave Garden'),
            ('Kyler\'s Study Zone', 'Breece Mode'),
            ('Hooked on a Thielen', 'Mixon It Up'),
            ('Scam Akers', 'The Adams Family'),
            ('Hurts Doughnut', 'Zeke and Destroy'),
            ('TuAnon Believer', 'Game of Mahomes')
        ]

        week_14 = [
            ('Calvin Ridely\'s Parlays', 'Kyler\'s Study Zone'),
            ('Hooked on a Thielen', 'Scam Akers'),
            ('Hurts Doughnut', 'TuAnon Believer'),
            ('Game of Mahomes', 'Zeke and Destroy'),
            ('The Adams Family', 'Mixon It Up'),
            ('Breece Mode', 'Olave Garden')
        ]



        # Test one week remaining.
        results = run_playoff_calculator(League(teams, [week_13], 6, 13), )

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

        taunon_believer_expected_results = {'TuAnon Believer': 1, 'Game of Mahomes': 0}
        tuanon_believer_results = results['TuAnon Believer']
        self.assertEqual(len(tuanon_believer_results['next']), 1)
        self.assertEqual(tuanon_believer_results['next'][0]['value'], taunon_believer_expected_results)

        game_of_mahomes_expected_results = {'Game of Mahomes': 1, 'TuAnon Believer': 0}
        game_of_mahomes_results = results['Game of Mahomes']
        self.assertEqual(len(game_of_mahomes_results['next']), 1)
        self.assertEqual(game_of_mahomes_results['next'][0]['value'], game_of_mahomes_expected_results)



        # Test for two weeks remaining
        results = run_playoff_calculator(League(teams, [week_13, week_14], 6, 12))

        self.assertEqual(results['Calvin Ridely\'s Parlays'], CLINCHED)
        self.assertEqual(results['Kyler\'s Study Zone'], CLINCHED)
        self.assertEqual(results['Hooked on a Thielen'], CLINCHED)
        self.assertEqual(results['Scam Akers'], CLINCHED)
        self.assertEqual(results['Hurts Doughnut'], CLINCHED)
        self.assertEqual(results['Mixon It Up'], ELIMINATED)
        self.assertEqual(results['Breece Mode'], ELIMINATED)
        self.assertEqual(results['Olave Garden'], ELIMINATED)

        with open('{}/playoff_scenarios_tuanon_believer.json'.format(ACTUAL_OUTPUT_DIRECTORY), 'w') as outfile:
            json.dump(results['TuAnon Believer'], outfile)

        with open('{}/playoff_scenarios_game_of_mahomes.json'.format(ACTUAL_OUTPUT_DIRECTORY), 'w') as outfile:
            json.dump(results['Game of Mahomes'], outfile)

        """ There are 2 possible playoff scenarios for 'Zeke and Destroy'. Each require 'Zeke and Destroy' must win out. 
            1.) 'TuAnon Believer' and 'Game of Mahomes' both lose week 14.
            2.) 'TuAnon Believer' loses in week 13 or 14. """
        zeke_and_destroy_results = results[ZEKE_AND_DESTROY][NEXT]
        zeke_and_destroy_output_file_name = '{}/playoff_scenarios_zeke_and_destroy.json'
        with open(zeke_and_destroy_output_file_name.format(ACTUAL_OUTPUT_DIRECTORY), 'w') as outfile:
            json.dump(zeke_and_destroy_results, outfile)

        self.assertTrue(filecmp.cmp(zeke_and_destroy_output_file_name.format(ACTUAL_OUTPUT_DIRECTORY), zeke_and_destroy_output_file_name.format(GOAL_OUTPUT_DIRECTORY), shallow=False))

        """ There are 2 possible playoff scenarios for 'The Adams Family'. Each require 'The Adams Family' must win out. 
            1.) 'TuAnon Believer' wins in week 13 and 'Game of Mahomes' loses in week 14.
            2.) 'Game of Mahomes' wins in week 13 and 'TuAnon Believer' loses in week 14. """
        the_adams_family_results = results[THE_ADAMS_FAMILY][NEXT]
        the_adams_family_output_file_name = '{}/playoff_scenarios_the_adams_family.json'
        with open(the_adams_family_output_file_name.format(ACTUAL_OUTPUT_DIRECTORY), 'w') as outfile:
            json.dump(the_adams_family_results, outfile)

        #TODO: Still some issues identifying irrelevant outcomes for 'The Adams Family' calculation.
        self.assertTrue(filecmp.cmp(the_adams_family_output_file_name.format(ACTUAL_OUTPUT_DIRECTORY), the_adams_family_output_file_name.format(GOAL_OUTPUT_DIRECTORY), shallow=False))

if __name__ == '__main__':
    unittest.main()
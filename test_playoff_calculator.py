import unittest

from playoff_calculator import League, Team, run

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


        # Test one week remaining.
        league = League(teams, [week_13], 6, 13)

        taunon_believer_expected_results = {'TuAnon Believer': 1, 'Game of Mahomes': 0}
        game_of_mahomes_expected_results = {'Game of Mahomes': 1, 'TuAnon Believer': 0}

        results = run(league)

        # self.assertEqual(results['Calvin Ridely\'s Parlays'], CLINCHED)
        # self.assertEqual(results['Kyler\'s Study Zone'], CLINCHED)
        # self.assertEqual(results['Hooked on a Thielen'], CLINCHED)
        # self.assertEqual(results['Scam Akers'], CLINCHED)
        # self.assertEqual(results['Hurts Doughnut'], CLINCHED)
        # self.assertEqual(results['Zeke and Destroy'], ELIMINATED)
        # self.assertEqual(results['The Adams Family'], ELIMINATED)
        # self.assertEqual(results['Mixon It Up'], ELIMINATED)
        # self.assertEqual(results['Breece Mode'], ELIMINATED)
        # self.assertEqual(results['Olave Garden'], ELIMINATED)

        # tuanon_believer_results = results['TuAnon Believer']
        # game_of_mahomes_results = results['Game of Mahomes']

        # self.assertEqual(len(tuanon_believer_results['next']), 1)
        # self.assertEqual(len(game_of_mahomes_results['next']), 1)
        # self.assertEqual(tuanon_believer_results['next'][0]['value'], taunon_believer_expected_results)
        # self.assertEqual(game_of_mahomes_results['next'][0]['value'], game_of_mahomes_expected_results)


        # Test two weeks remaining
        week_14 = [
            ('Calvin Ridely\'s Parlays', 'Kyler\'s Study Zone'),
            ('Hooked on a Thielen', 'Scam Akers'),
            ('Hurts Doughnut', 'TuAnon Believer'),
            ('Game of Mahomes', 'Zeke and Destroy'),
            ('The Adams Family', 'Mixon It Up'),
            ('Breece Mode', 'Olave Garden')
        ]

        league = League(teams, [week_13, week_14], 6, 13)

        results = run(league)

        # self.assertEqual(results['Calvin Ridely\'s Parlays'], CLINCHED)
        # self.assertEqual(results['Kyler\'s Study Zone'], CLINCHED)
        # self.assertEqual(results['Hooked on a Thielen'], CLINCHED)
        # self.assertEqual(results['Scam Akers'], CLINCHED)
        # self.assertEqual(results['Hurts Doughnut'], CLINCHED)
        # self.assertEqual(results['Zeke and Destroy'], ELIMINATED)
        # self.assertEqual(results['The Adams Family'], ELIMINATED)
        # self.assertEqual(results['Mixon It Up'], ELIMINATED)
        # self.assertEqual(results['Breece Mode'], ELIMINATED)
        # self.assertEqual(results['Olave Garden'], ELIMINATED)

        tuanon_believer_results = results['TuAnon Believer']
        game_of_mahomes_results = results['Game of Mahomes']



if __name__ == '__main__':
    unittest.main()
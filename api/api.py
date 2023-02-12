from flask import Flask
from playoff_calculator import League, run, import_espn_league


app = Flask(__name__)

@app.route('/calculate_playoff_scenarios')
def calculate_playoff_scenarios():
    print('INFO: calculate_playoff_scenarios')
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
    return {'results': 'run'}
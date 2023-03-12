from flask import Flask, jsonify
from playoff_calculator import *

YEAR = 2021
ERROR = 'error'


app = Flask(__name__)

@app.route('/calculate_playoff_scenarios/<league_id>/<team_id>')
def calculate_playoff_scenarios(league_id, team_id):
    print('INFO: calculate_playoff_scenarios: ', team_id)
    league_type = 'espn'

    league = get_league(league_type, int(league_id), YEAR)

    team_to_calculate = next((team for team in league.teams if team.source_id == int(team_id)), None)

    results = run(league, team_to_calculate)
    weeks_remaining = 2
    return {
        'status': 'in the hunt' if 'next' in results[team_to_calculate.team_name] else results[team_to_calculate.team_name]['value'],
        'scenarios': results[team_to_calculate.team_name]['next'] if 'next' in results[team_to_calculate.team_name] else [],
        'weeks_remaining': weeks_remaining,
        'team': team_to_calculate.team_name
    }


@app.route('/load_teams/<type>/<id>')
def get_teams(type, id):
    try:
        league = get_league(type, int(id), YEAR)
    except LeagueDoesNotExistException as exception:
        return {ERROR: str(exception)}

    teams = []
    for team in league.teams:
        teams.append({'name': team.team_name, 'id': team.source_id})
    return jsonify({'teams': teams})
    

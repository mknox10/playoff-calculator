from flask import Flask, jsonify
from playoff_calculator import *


app = Flask(__name__)

@app.route('/calculate_playoff_scenarios/<league_id>/<team_id>')
def calculate_playoff_scenarios(league_id, team_id):
    print('INFO: calculate_playoff_scenarios: ', team_id)
    league_type = 'espn'
    #TODO: determine year
    year = 2021
    week = 12

    league = get_league(league_type, int(league_id), year)

    team_to_calculate = next((team for team in league.teams if team.source_id == int(team_id)), None)

    results = run(league, team_to_calculate)
    weeks_remaining = 2
    return {
        'scenarios': results[team_to_calculate.team_name],
        'weeks_remaining': weeks_remaining
    }


@app.route('/load_teams/<type>/<id>/<year>')
def get_teams(type, id, year):
    teams = []
    for team in get_league(type, int(id), int(year)).teams:
        teams.append({'name': team.team_name, 'id': team.source_id})
        # teamsData = json.loads(teamsJson)
        # teams.append(teamsData)
    return jsonify({'teams': teams})
    

import axios from 'axios';
import React, { Component, useEffect, useState,  } from "react";
import '../App.css';
import Scenario from './Scenario.js';

class App extends Component {

  constructor(props) {
    super(props);
    this.state = {
      leagueId: '',
      teams: [],
      teamId: '',
      scenarios: [],
      testScenarios: [1, 2, 3, 4, 5]
    };
    this.handleChange = this.handleChange.bind(this);
    this.handleTeamSelect = this.handleTeamSelect.bind(this);
    this.loadTeams = this.loadTeams.bind(this);
    this.calculatePlayoffScenarios = this.calculatePlayoffScenarios.bind(this);
  }

  handleChange(event) {
    this.setState({leagueId: event.target.value});
  }
  

  handleTeamSelect(event) {
    this.setState({teamId: event.target.value})
  }

  loadTeams = (event) => {
    event.preventDefault();
    axios.get(`load_teams/espn/${this.state.leagueId}/2022`).then(response => {
      this.setState(({
        teams: response.data.teams
      }));
    }).catch((error) => {
      if (error.response) {
        console.log(error.response);
      }
    });
  };

  calculatePlayoffScenarios = (event) => {
    event.preventDefault();
    axios.get(`calculate_playoff_scenarios/${this.state.leagueId}/${this.state.teamId}`).then(response => {
      this.setState({
        scenarios: response.data.next
      });
    }).catch((error) => {
      if (error.response) {
        console.log(error.response);
      }
    });
  };

  render() {
    return (
      <div className="App">
        <form onSubmit={this.loadTeams}>
          <label>
            League Id:
            <input type="text" value={this.state.leagueId} onChange={this.handleChange} />
          </label>
          <input type="submit" value="Load League" />
        </form>
        <br/>
        { this.state.teams.length > 0 &&
          <form onSubmit={this.calculatePlayoffScenarios}>
            <label>
              Select Team
              <select value={this.state.teamId} onChange={this.handleTeamSelect}>
                {this.state.teams.map(team => <option key={team.id} value={team.id}>{team.name}</option>)}
              </select>
            </label>
            <input type="submit" value="Calculate Playoff Scenarios" />
          </form>
        }
        <br/>
        { this.state.scenarios.map(scenario => <Scenario name='Scenario' data={scenario} />)}
      </div>
    );
  }
}

export default App;

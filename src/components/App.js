import axios from 'axios';
import React, { Component  } from "react";
import '../App.css';
import Scenario from './Scenario.js';
import BackgroundImage from '../img/background.jpeg';

let sectionStyle = {
  backgroundImage: `url(${BackgroundImage})`,
  backgroundPosition: 'center',
  backgroundSize: 'cover',
  backgroundRepeat: 'no-repeat',
  height: '20vh'
}

class App extends Component {

  constructor(props) {
    super(props);
    this.state = {
      leagueURL: '',
      teams: [],
      teamId: '',
      scenarios: [],
      testScenarios: [1, 2, 3, 4, 5],
      weeksRemaining: 0
    };
    this.handleLeagueURLChange = this.handleLeagueURLChange.bind(this);
    this.handleTeamSelect = this.handleTeamSelect.bind(this);
    this.loadLeague = this.loadLeague.bind(this);
    this.calculatePlayoffScenarios = this.calculatePlayoffScenarios.bind(this);
    this.calculatePlayoffScenariosDefault = this.calculatePlayoffScenariosDefault.bind(this);
  }

  handleLeagueURLChange(event) {
    this.setState({leagueURL: event.target.value});
  }
  

  handleTeamSelect(event) {
    this.setState({teamId: event.target.value})
  }

  loadLeague = (event) => {
    event.preventDefault();
    let leagueId;
    if (this.state.leagueURL.includes('espn.com')) {
      leagueId = this.state.leagueURL.split("leagueId=")[1].split("&")[0];
    }

    if (!leagueId) {
      alert('Platform not supported')
    } else {
      axios.get(`load_teams/espn/${leagueId}/2022`).then(response => {
        this.setState(({
          teams: response.data.teams,
          leagueId: leagueId
        }));
      }).catch((error) => {
        if (error.response) {
          console.log(error.response);
        }
      });
    }
  };

  calculatePlayoffScenarios = (event) => {
    event.preventDefault();
    axios.get(`calculate_playoff_scenarios/${this.state.leagueId}/${this.state.teamId}`).then(response => {
      this.setState({
        scenarios: response.data.scenarios.next,
        weeksRemaining: response.data.weeks_remaining
      });
    }).catch((error) => {
      if (error.response) {
        console.log(error.response);
      }
    });
  };

  calculatePlayoffScenariosDefault = (event) => {
    event.preventDefault();
    axios.get(`calculate_playoff_scenarios/1307984/3`).then(response => {
      this.setState({
        scenarios: response.data.scenarios.next,
        weeksRemaining: response.data.weeks_remaining
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
        <nav class="navbar navbar-expand-lg bg-body-tertiary">
          <div class="container-fluid">
            <a class="navbar-brand" href="#">Playoff Calculator</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
              <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
              <ul class="navbar-nav">
                <li class="nav-item">
                  <a class="nav-link active" aria-current="page" href="#">Home</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" href="#">Features</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" href="#">Pricing</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link disabled">Disabled</a>
                </li>
              </ul>
            </div>
          </div>
        </nav>
        <div class="bg-image" style={sectionStyle}>
          <div class="container-fluid">
            <form onSubmit={this.loadLeague}>
              <div class="row form-row justify-content-md-center align-items-center">
                <div class="col col-lg-2">
                  <label class="text-white">Enter Fantasy league URL:</label>
                </div>
                <div class="col col-lg-4">
                  <input class="form-control" type="text" value={this.state.leagueURL} onChange={this.handleLeagueURLChange} />
                </div>
                <div class="col col-lg-2">
                  <input class="btn btn-outline-purple" type="submit" value="Load League" />
                </div>
              </div>
            </form>
            { this.state.teams.length > 0 &&
              <form onSubmit={this.calculatePlayoffScenarios}>
                <div class="row form-row justify-content-md-center align-items-center">
                  <div class="col col-lg-2">
                    <label class="text-white ">Select Team:</label>
                  </div>
                  <div class="col col-lg-2">
                    <select class="form-select" value={this.state.teamId} onChange={this.handleTeamSelect}>
                      {this.state.teams.map(team => <option key={team.id} value={team.id}>{team.name}</option>)}
                    </select>
                  </div>
                  <div class="col col-lg-2">
                    <input class="btn btn-outline-purple" type="submit" value="Calculate Playoff Scenarios" />
                  </div>
                </div>
              </form>
            }
          </div>
        </div>
        <button onClick={this.calculatePlayoffScenariosDefault}>Default</button>
      </div>
    );
  }
}

export default App;

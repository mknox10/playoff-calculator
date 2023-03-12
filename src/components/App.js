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
      teamName: '',
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
    this.setState({
      teamId: event.target.value
    });
  }

  loadLeague = (event) => {
    event.preventDefault();
    let leagueId;
    if (this.state.leagueURL.includes('espn.com')) {
      leagueId = this.state.leagueURL.split("leagueId=")[1].split("&")[0];
    } else {
      alert('Platform not supported')
    }

    if (!leagueId) {
      alert('Invalid URL')
    } else {
      axios.get(`load_teams/espn/${leagueId}`).then(response => {
        if (response.data.error) {
          alert(response.data.error)
        } else {
          this.setState(({
            teams: response.data.teams,
            leagueId: leagueId,
            teamId: response.data.teams[0].id
          }));
        }
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
      if (response.data.error) {
        alert(response.data.error)
      } else {
        this.setState({
          status: response.data.status,
          scenarios: response.data.scenarios,
          weeksRemaining: response.data.weeks_remaining,
          teamName: response.data.team
        });
      }
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
        status: response.data.status,
        scenarios: response.data.scenarios,
        weeksRemaining: response.data.weeks_remaining,
        teamName: response.data.team
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
            <a class="navbar-brand" href="#">Fantasy Football Playoff Machine</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
              <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
              <ul class="navbar-nav">
                <li class="nav-item">
                  <a class="nav-link disabled">About</a>
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
                  <button class="btn btn-outline-purple" onClick={this.calculatePlayoffScenariosDefault}>Default</button>
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
        
        { this.state.teamName && 
          <h2>'{this.state.teamName}' is {this.state.status}</h2>
        }
        { this.state.scenarios.map((scenario, i) => <Scenario key={i} name='Scenario' data={scenario} weeksRemaining={this.state.weeksRemaining} depth={0}/>)}
      </div>
    );
  }
}

export default App;

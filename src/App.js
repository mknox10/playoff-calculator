import axios from 'axios';
import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';

function App() {
  const [results, setResults] = useState(0);

  let myParameter = 'skol vikings';

  useEffect(() => {
    axios.get(`/calculate_playoff_scenarios/${myParameter}`).then(response => {
      setResults(response.data.results);
    });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
        <p>Playoff Scenarios: {results}</p>
      </header>
    </div>
  );
}

export default App;

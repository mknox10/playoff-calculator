import React, { Component } from 'react';

class Scenario extends Component {

  constructor(props) {
    super(props);
    this.state = {
      viewDetails: false
    };
    this.toggleDetails = this.toggleDetails.bind(this);
  }

  toggleDetails(event) {
    this.setState({viewDetails: !this.state.viewDetails});
  }

  render() {
    return (
      <div>
        <button onClick={this.toggleDetails}>{this.props.name}</button>
        { this.props.data.next && this.state.viewDetails && 
            this.props.data.next.map(scenario => <Scenario name='Detail' data={scenario} />)
        }
      </div>
    );    
  }
}

export default Scenario;
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
      <div class="scenario">
        <div class="row" onClick={this.toggleDetails}>
          {[...Array(this.props.weeksRemaining)].map((value, idx1) => 
            <div class="col">
              { this.props.depth === idx1 &&
                <div class="card">
                    <ol>
                      {
                        Object.keys(this.props.data.value).map((key, idx2) => ( 
                          <li key={idx2}> {key} - { this.props.data.value[key] ? 'WIN' : 'Loss'}</li> 
                        ))
                      }
                    </ol>
                </div>
              }
            </div>
          )}
        </div>
        { this.props.data.next && this.state.viewDetails && 
            this.props.data.next.map(scenario => <Scenario name='Detail' data={scenario} weeksRemaining={this.props.weeksRemaining} depth={this.props.depth+1} />)
        }
      </div>
    );    
  }
}

export default Scenario;
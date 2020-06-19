import React, { Component } from 'react'
import { photos } from './UserFunctions'

class Photo extends Component {
  constructor() {
    super()
    this.state = {
      first_name: '',
      last_name: '',
      username: '',
      errors: {},
      image_div: []
    }
  }

  componentDidMount() {
        const user = {
          first_name: localStorage.first_name,
          last_name: localStorage.last_name,
          username: localStorage.username,
          password: localStorage.password
        }
        
        photos(user).then( response => {
              const urls = response.data
              console.log(urls)
              var renderedOutput=[]
              urls.forEach(function(item, index){
                renderedOutput.push(item)
              });
              this.setState({image_div: renderedOutput});

          }
        )
  }

    render() {
      

      return (
        <div className="container">
          <div className="jumbotron mt-5">
            <div className="col-sm-8 mx-auto">
              <h1 className="text-center">Photos</h1>
            </div>
          </div>

          <div className="row">
                {this.state.image_div.map(item=> (
                  <div className="col-md-4">
                    <img src={item.url}></img><br></br>
                    {item.date}, {item.location}
                  </div>    
                  )
                )}
          </div>
            
          </div>
      )
      
    }

  }

export default Photo
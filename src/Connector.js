import React from 'react'
import './App.css'
import firebase from 'firebase/app'
import 'firebase/database'
import config from './config'
import { Button, } from '@mantine/core'
import axios from 'axios'

class Connector extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      isCorrect: true,
      statusMsg: '',
      database: null,
      isConnected: false,
      myId: 'receiverId1',
      receiverId: '',
      message: '',
      messages: [],
      messagesLayer0: [],
      messagesLayer1: [],
      messagesLayer2: [],
      messagesLayer3: [],
      messagesLayer4: [],
      layer: 4,
    }
  }

  componentDidMount = async () => {
    firebase.initializeApp(config)

    this.setState({
      database: firebase.database()
    })
  }

  shouldComponentUpdate(nextProps, nextState) {
    if (this.state.database !== nextState.database) {
      return false
    }

    return true
  }

  connect = async () => {
    try {
      const { database, myId } = this.state

      await database.ref('/notifs/' + myId).remove()

      await database.ref('/notifs/' + myId).on('value', snapshot => {
        if (snapshot.exists()) {
          const notif = snapshot.val()
          // this.setState({
          //   messages: [...this.state.messages, notif]
          // })
          this.addMessage(notif)
          console.log(notif)
        }
      })
      this.setState({
        isConnected: true
      })
      this.checkMessage()
    } catch (e) {
      console.error(e)
    }
  }


  runPythonScript = async () => {
    try {
      const response = await axios.post('http://localhost:8000/run-python-script');
      console.log(response.data.output); // Output from the Python script
    } catch (error) {
      console.error(error);
    }
  };

  addMessage = (message) => {
    this.setState((prevState) => {
      const updatedMessages = [...prevState.messages, message];
      if(message.layer === 4){
        this.runPythonScript();
        return {
          messages: updatedMessages,
          messagesLayer4: [...prevState.messagesLayer4, message],
        };
        
      }
      if (message.layer === 3) {
        const updatedMessagesLayer4 = prevState.messagesLayer4.filter((msg) => msg.from !== message.from);
        return {
          messages: updatedMessages,
          messagesLayer3: [...prevState.messagesLayer3, message],
          messagesLayer4: updatedMessagesLayer4,
        };
      }

      if (message.layer === 2) {
        const updatedMessagesLayer3 = prevState.messagesLayer3.filter((msg) => msg.from !== message.from);
        return {
          messages: updatedMessages,
          messagesLayer2: [...prevState.messagesLayer2, message],
          messagesLayer3: updatedMessagesLayer3,
        };
      }

      if (message.layer === 1) {
        const updatedMessagesLayer2 = prevState.messagesLayer2.filter((msg) => msg.from !== message.from);
        return {
          messages: updatedMessages,
          messagesLayer1: [...prevState.messagesLayer1, message],
          messagesLayer2: updatedMessagesLayer2,
        };
      }

      if (message.layer === 0) {
        const updatedMessagesLayer1 = prevState.messagesLayer1.filter((msg) => msg.from !== message.from);
        return {
          messages: updatedMessages,
          messagesLayer0: [...prevState.messagesLayer0, message],
          messagesLayer1: updatedMessagesLayer1,
        };
      }

      return { messages: updatedMessages };
    });
  };

  sendMessage = async () => {
    try {
      const { database, receiverId, myId, layer } = this.state
      await database.ref('/notifs/' + receiverId).set({
        // message,
        from: myId,
        layer: layer,
      })
      this.setState({
        message: '',
        statusMsg: '',
        isCorrect: true,
        layer: layer - 1
      })
    } catch (e) {
      console.error(e)
    }
  }

  renderRank = (value, key) => {
    const newKey = key += 1;
    return <tr key={newKey}>
      {/* <td>{key}</td> */}
      <td>{value.from}</td>
    </tr>
  }

  render() {

const tableStyle = {
  flex: 1,
  margin: '10px',
  width: '20%'
};


    return <div style={{ width: '70vw' }}>
      {this.state.isConnected ? (<center>
        <div>
        </div>
        <div>
          <div style={{ display: 'flex', width: '100%' }}>
          <div style={tableStyle}>
              <h2>Entry</h2>
              <table>
                <tbody>
                  {this.state.messagesLayer4.map(this.renderRank)}
                </tbody>
              </table>
            </div>
            <div style={tableStyle}>
              <h2>Layer 3</h2>
              <table>
                <tbody>
                  {this.state.messagesLayer3.map(this.renderRank)}
                </tbody>
              </table>
            </div>
            <div style={tableStyle}>
              <h2>Layer 2</h2>
              <table>
                <tbody>
                  {this.state.messagesLayer2.map(this.renderRank)}
                </tbody>
              </table>
            </div>
            <div style={tableStyle}>
              <h2>Layer 1</h2>
              <table>
                <tbody>
                  {this.state.messagesLayer1.map(this.renderRank)}
                </tbody>
              </table>
            </div>
            <div style={tableStyle}>
              <h2>Winner</h2>
              <table>
                <tbody>
                  {this.state.messagesLayer0.map(this.renderRank)}
                </tbody>
              </table>
            </div>
          </div>
        </div></center>
      ) : (
        <div>
          <center>
            <h2>Click me to join network as host</h2>
            <Button onClick={this.connect}>Connect</Button>
          </center>
        </div>
      )}
    </div>
  }
}

export default Connector

import { useEffect, useState } from 'react';
import './App.css';

const wsEndpoint = "ws://localhost:8000/ws";

function App()  {
  const [subMessage, setSubMessage] = useState('');
  const [pubMessage, setPubMessage] = useState('');
  const [websckt, setWebsckt] = useState(null);

  useEffect(() => {
    const ws = new WebSocket(wsEndpoint);

    ws.onopen = (event) => {
      ws.send("Connected to ws server");
    };

    // recieve message every start page
    ws.onmessage = (e) => {
      const message = JSON.parse(e.data);
      setSubMessage(message);
    };

    setWebsckt(ws);

    // Close the socket when the component unmounts
    return () => ws.close();
  }, []);

  const onInputChange = (e) => {
    setPubMessage(e.target.value);
  }

  const publishMessage = () => {
    websckt.send(pubMessage);

    // recieve message every send message
    websckt.onmessage = (e) => {
      const message = JSON.parse(e.data);
      setSubMessage(message);
    };
  };

  return (
    <div className="App">
      <header className="App-header">
        <div>
          <br />
          <div className="mb-3">
            <label 
              htmlFor="incoming_messages" 
              className="form-label"
            >
              Incoming messages from AWS IoT Core
            </label>
            <div 
              id="incoming_messages_help" 
              className="form-text"
            >
              Subscribed to the topic AWS_IOT_THING_NAME/publish
            </div>
            <textarea 
              disabled 
              rows="5" 
              className="form-control" 
              id="incomingMessages" 
              name="incomingMessages" 
              aria-describedby="incoming_messages_help" 
              value={subMessage} 
            />
          </div>
          <div className="mb-3">
            <label 
              htmlFor="publish_string" 
              className="form-label"
            >
              Publish a message to AWS IoT Core
            </label>
            <div 
              id="publishHelp" 
              className="form-text"
            >
              Published to the topic AWS_IOT_THING_NAME/subscribe
            </div>
            <input 
              id="publishString" 
              name="publishString" 
              placeholder="String to publish"
              type="text" 
              className="form-control" 
              value={pubMessage} 
              onChange={onInputChange}
            />
          </div>
          <button 
            className="btn btn-success"
            onClick={publishMessage}
          >
            Publish
          </button>
        </div>
      </header>
    </div>
  );
}

export default App;

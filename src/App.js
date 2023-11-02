import React from 'react'
import './App.css'
import Connector from './Connector'
import { MantineProvider } from '@mantine/core';
// export NODE_OPTIONS=--openssl-legacy-provider

function App () {
  // runPythonScript();

  return (
    <MantineProvider>
    <div className='app'>
      <img src="Tor-Emblem.png" alt="Onion Routing Logo" width="150" height="150"/>
      <h1>Onion Routing App</h1>
      <Connector/>
      {/* <Live /> */}
    </div>
    </MantineProvider>
  )
}

export default App

const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const app = express();
app.use(cors());
app.use(express.json());

const port = 8000; // Port of this server.js not the fking node.js 

//Shit u needa touch only -- run this script to run the entire shiet. start node_server.js first manually
let PUBLIC_IP = '192.168.68.106';

// const server_script = spawn('python3', ['onionRouter/server.py']);
// if (server_script.pid !== null) {
//   console.log('Server is currently running.');
// } else {
//   console.log('Server has already exited.');
// }

let counter = 6100;
app.post('/run-python-script', (req, res) => {
  // const scriptPath = 'onionRouter/node.py';
  // console.log(args);
  const scriptPath = 'onionRouter/node.py';
  const node_script = spawn('python3', [scriptPath, counter.toString()]);
  if (node_script.pid !== null) {
    console.log('Node child process is currently running.');
  } else {
    console.log('Node child process has already exited.');
  }
  
  if (typeof PUBLIC_IP === 'string') {
    node_script.stdin.write(`${PUBLIC_IP}\n`);
    node_script.stdin.end(); 
  } else {
    console.error('PUBLIC_IP is not defined or is not a string.');
  }

  counter++;
  node_script.on('exit', (code) => {
    if (code === 0) {
      console.log("node.py exited successfully");
    } else {
      console.log("node.py exited with error");
    }
  });
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
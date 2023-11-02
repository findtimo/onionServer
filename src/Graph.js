import React, { useEffect } from 'react';
import G6 from '@antv/g6'; // Import G6 library

const Graph = () => {
  useEffect(() => {
    const server_ip = "192.168.50.179";
    const client_ip = "192.168.50.179";
    const data = {
      nodes: [
        {
          img: "https://cunhuahk.oss-cn-hongkong.aliyuncs.com/web_server.png",
          id: `${server_ip}:9999`,
          label: `${server_ip}:9999`,
        },
      ],
      edges: [],
    };

    const container = document.getElementById("mountNode");
    const width = container.scrollWidth;
    const height = container.scrollHeight || 500;

    const graph = new G6.Graph({
      container: "mountNode",
      width,
      height,
      modes: {
        default: ["zoom-canvas", "drag-canvas", "drag-node"],
      },
      layout: {
        type: "grid",
        begin: [20, 20],
        width: width - 20,
        height: height - 20,
      },
      animate: true,
      defaultNode: {
        type: "image",
        img: "https://cunhuahk.oss-cn-hongkong.aliyuncs.com/servericon.png",
        size: [50],
        style: {
          fill: "#FF6A00",
          stroke: "#FF6A00",
          lineWidth: 3,
        },
      },
      edgeStateStyles: {
        active: {
          stroke: "#F6BD16",
          lineWidth: 10,
        },
      },
    });

    graph.data(data);
    graph.render();

    async function InitNodes() {
      const response = await fetch(`http://${server_ip}:8888/get_nodes`);
      const res = await response.json();
      console.log(res.data);
      for (let i = 0; i < res.data.length; i++) {
        data.nodes.push({
          id: `${res.data[i][1]}:${res.data[i][2]}`,
          label: `${res.data[i][1]}:${res.data[i][2]}`,
        });
      }
      graph.data(data);
      graph.render();
    }

    InitNodes();
    data.nodes.push({
      img: "https://static.vecteezy.com/system/resources/previews/007/296/447/original/user-icon-in-flat-style-person-icon-client-symbol-vector.jpg",
      id: `${client_ip}:8889`,
      label: `${client_ip}:8889`,
    });

    var intervalId = window.setInterval(async function () {
      let response = await fetch(`http://${server_ip}:8888/get_new_node`);
      let res = await response.json();
      if (res.data != "") {
        console.log("yyyyyessss  found it");
        data.nodes.push({
          id: `${res.data[1]}:${res.data[2]}`,
          label: `${res.data[1]}:${res.data[2]}`,
        });
        graph.data(data);
        graph.render();
      }

      response = await fetch(`http://${server_ip}:8888/get_new_link`);
      res = await response.json();
      if (res.data != "") {
        console.log("yyyyyessss  found link it");
        const newEdge = res.data; // Define newEdge here
        newEdge.style = {
          stroke: "#F6BD16",
          lineWidth: 10,
          endArrow: {
            path: G6.Arrow.triangle(),
          },
        };
        data.edges = [newEdge];
        graph.data(data);
        graph.render();
      }
    }, 1000);

    return () => {
      clearInterval(intervalId); // Cleanup logic when unmounting the component
    };
  }, []); // An empty dependency array ensures this effect runs only once

  return <div id="mountNode"></div>;
};

export default Graph;

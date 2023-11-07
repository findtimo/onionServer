import json

import requests
import random
from layer import Layer
from util import Util
import socket

server = ""
node_server = ""
layer = Layer()
util = Util()


def get_nodes():
    response = requests.get(node_server + "/get_nodes")
    # print_green(response.json())
    return response.json()


def generate_node_list():
    nodes_list = get_nodes()
    list_of_random_node = random.sample(nodes_list['data'], 3)
    return list_of_random_node


def send_msg(message):
    # generate node list
    node_list = generate_node_list()

    # create onion
    body, keys_list, request_id = layer.client_encrypt_all(node_list, message, server)
    util.print_green("sending the onion to enter node and waiting for sever's response")
    util.print_red("your request ID:{}".format(request_id[0:5]))

    # init the socket
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect and sent to entry node
    clientSocket.connect((node_list[0][1], int(node_list[0][2])))

    # get local machine ip address
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    message = "forward:{}:{}:{}".format(ip_address, '8889', body).encode()
    clientSocket.send(message)
    requests.post(node_server + "/report_link", json={
        "label": "forward:" + request_id[0:5],
        "source": ip_address + ":8889",
        "target": node_list[0][1] + ":" + str(node_list[0][2])
    })
    clientSocket.close()

    # listen for response
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.bind(('0.0.0.0', 8889))
    clientSocket.listen(1)

    connectionSocket, addr = clientSocket.accept()
    response = connectionSocket.recv(10240)


    data = response.decode()
    response_data = data.split(":")

    encrypted_data = json.loads(bytes.fromhex(response_data[1]).decode())
    response_message = layer.client_decrypt_all(keys_list, encrypted_data['data'])
    util.print_blue("response from server: {}".format(response_message))

    clientSocket.close()

    # print_green(body)
    # response = requests.post(node_list[0][1] + node_list[0][2], body)


if __name__ == '__main__':
    util.print_red("WELCOME to THE KILLER")
    util.print_yellow("Please input the server's IP address [x.x.x.x]:")
    server_address = input().strip()
    server = server_address+":9999"

    util.print_yellow("Please input the NODE server's IP address [x.x.x.x]:")
    node_server_address = input().strip()
    node_server = "http://" + server_address + ":8888"
    while True:
        # input
        util.print_green("Who do you want to kill today:")
        message = input()
        send_msg(message)

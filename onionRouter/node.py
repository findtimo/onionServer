import base64
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import requests
import sys
import socket
from Crypto.Random import get_random_bytes
from time import sleep
from layer import Layer
from util import Util
import os

util = Util()
layer = Layer()
aes_key = get_random_bytes(16)
backward_table = {}
    
script_dir = os.path.dirname(__file__) 
file_path = os.path.join(script_dir, f'keys')

def gen_key():
    print("arg: "+sys.argv[1])
    rsa_key = RSA.generate(2048)
    print(file_path)
    with open(file_path+"/{}private.key".format(sys.argv[1]), 'wb') as content_file:
        # chmod("/tmp/private.key", 0o600)
        content_file.write(rsa_key.export_key(format='PEM', passphrase=None, pkcs=1, protection=None, randfunc=None))

    with open(file_path+"/{}public.key".format(sys.argv[1]), 'wb') as content_file:
        content_file.write(
            rsa_key.public_key().export_key(format='PEM', passphrase=None, pkcs=1, protection=None, randfunc=None))


def get_public_key():
    # key = RSA.import_key(open('./keys/public.key').read())
    with open(file_path+"/{}public.key".format(sys.argv[1]), 'r') as content_file:
        return content_file.read()

def get_private_key():
    # key = RSA.import_key(open('./keys/public.key').read())
    with open(file_path+"/{}private.key".format(sys.argv[1]), 'r') as content_file:
        return content_file.read()

def sign_message(message):
    h = SHA256.new(message)
    key = RSA.import_key(open(file_path+'/{}private.key'.format(sys.argv[1])).read())
    signature = pkcs1_15.new(key).sign(h)
    return signature


def register_node(my_address, server_address):
    # sys.argv[1] is the port number
    host = ip_address + ":" + sys.argv[1]
    body = {
        "public_key": get_public_key(),
        "host": host,
         # use signature to verify ownership of public key
        "signature": base64.b64encode(sign_message(bytes(host, 'utf-8'))).decode()
    }
    response = requests.post("http://"+server_address+":8888"+"/register_node", json=body)
    if response.status_code == 200:
        print("Node Registered")
        print("assigned position: " + str(response.json()['position']))


if __name__ == '__main__':
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    gen_key()

    util.print_yellow("Please input the node server address [x.x.x.x]:")
    server_ip = input().strip()
    register_node(ip_address, server_ip)
    serverPort = int(sys.argv[1])
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind(('0.0.0.0', serverPort))
    serverSocket.listen(1)

    print('Your node is registered and listening at {}:{}'.format(ip_address, serverPort))
    while True:
        connectionSocket, addr = serverSocket.accept()
        message = connectionSocket.recv(10240)
        # print("data received: {} from {}".format(message, addr))
        data = message.decode()
        data = data.split(":")

        if data[0] == "request_AES":
            connectionSocket.send(aes_key)

        if data[0] == "forward":
            my_address = ip_address + ":" + sys.argv[1]

            # decrypt data
            layer_data = layer.layer_decrypt(aes_key, get_private_key(), data[3])

            if layer_data['is_server'] == 1:  # if the next hop is the server
                util.print_green("Forwarding onion from {},sending data to server: {}".format(addr, layer_data['next']))

                # this is to report exit node
                body = {
                    "label": "forward:{}".format(layer_data['request_id'][0:5]),
                    "source": my_address,
                    "target": layer_data['next']
                }
                response = requests.post("http://" + server_ip + ":8888" + "/report_link", json=body)
                server_response = requests.post("http://"+layer_data['next'], layer_data['data'])

                # this is to report exit node receive response
                body = {
                    "label": "backward:{}".format(layer_data['request_id'][0:5]),
                    "source": layer_data['next'],
                    "target": my_address
                }
                response = requests.post("http://" + server_ip + ":8888" + "/report_link", json=body)



                final_data = {
                    'request_id': layer_data['request_id'],
                    'data': layer.encrypt_layer(server_response.text, aes_key)
                }
                host = (data[1], int(data[2]))

                message = "backward:{}".format(json.dumps(final_data).encode().hex()).encode()
                util.print_blue("Backward onion from server,sending data to server: {}:{}".format(host[0], host[1]))

                # this is to report exit node send back the onion
                body = {
                    "label": "backward:{}".format(layer_data['request_id'][0:5]),
                    "source": my_address,
                    "target": "{}:{}".format(host[0], host[1])
                }
                response = requests.post("http://" + server_ip + ":8888" + "/report_link", json=body)


            else:  # when next hop is another router
                util.print_green("Forwarding onion from {}, sending to next hop: {}".format(addr, layer_data['next']))
                sleep(1)
                host = layer_data['next'].split(":")

                # save the request to backward table
                backward_table[layer_data['request_id']] = {
                    "from": (data[1], int(data[2])),
                    "to": layer_data['next']
                }
                message = "forward:{}:{}:{}".format(ip_address, serverPort, layer_data['data']).encode()

                # this is to report forward to next node
                body = {
                    "label": "forward:{}".format(layer_data['request_id'][0:5]),
                    "source": my_address,
                    "target": "{}:{}".format(host[0], host[1])
                }
                response = requests.post("http://" + server_ip + ":8888" + "/report_link", json=body)


            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.connect((host[0], int(host[1])))
            clientSocket.send(message)
            clientSocket.close()

        if data[0] == "backward":
            final_data = json.loads(bytes.fromhex(data[1]).decode())
            # add another layer of encryption
            final_data['data'] = layer.encrypt_layer(final_data['data'], aes_key)

            message = "backward:{}".format(json.dumps(final_data).encode().hex()).encode()

            host = backward_table[final_data['request_id']]['from']

            sleep(1)
            util.print_blue("Backward onion from {},sending data to server: {}:{}".format(addr, host[0], host[1]))

            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.connect((host[0], int(host[1])))
            clientSocket.send(message)
            clientSocket.close()

            my_address = ip_address + ":" + sys.argv[1]
            # report to node_server for visualisation!!! this should not be implemented
            body = {
                "label": "backward:{}".format(final_data['request_id'][0:5]),
                "source": my_address,
                "target": "{}:{}".format(host[0], host[1])
            }
            response = requests.post("http://" + server_ip + ":8888" + "/report_link", json=body)

            del backward_table[final_data['request_id']]


        connectionSocket.close()



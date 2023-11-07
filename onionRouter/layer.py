import rsa
import base64
import json
import socket
from time import sleep
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from util import Util
import uuid

util = Util()


class Layer:
    def rsa_encrypt(self, public_key, data):
        public_key = rsa.PublicKey.load_pkcs1_openssl_pem(public_key)
        encrypted_data = rsa.encrypt(data, public_key)
        return encrypted_data

    def rsa_decrypt(self, private_key, data):
        decrypted_data = rsa.decrypt(private_key, data)
        return decrypted_data

    def layer_decrypt(self, aes_key, private_key, data):
        private_key = rsa.PrivateKey.load_pkcs1(private_key)
        cipher = AES.new(aes_key, AES.MODE_ECB)
        padded = cipher.decrypt(bytes.fromhex(data))
        result = unpad(padded, 16, 'pkcs7')
        layer_json = json.loads(result.decode())
        layer_json['next'] = rsa.decrypt(bytes.fromhex(layer_json['next']), private_key)
        layer_json['next'] = layer_json['next'].decode()
        return layer_json

    def test_decrypt(self, aes_key, data):

        cipher = AES.new(aes_key, AES.MODE_ECB)

        padded = cipher.decrypt(bytes.fromhex(data))
        result = unpad(padded, 16, 'pkcs7')
        print("Decrypted data : {}".format(padded))

        print("TEST decrypt result {}".format(result.decode()))

    def get_aes(self, node_host, node_port):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # udp_socket.connect((node_host, node_port))
        print("sending to {}:{}".format(node_host, node_port))
        clientSocket.connect((node_host, node_port))
        clientSocket.send("request_AES:".encode())
        key = clientSocket.recv(1024)
        clientSocket.close()
        return key

    def encrypt_layer(self, data, aes_key):
        cipher = AES.new(aes_key, AES.MODE_ECB)
        encrypted = cipher.encrypt(pad(data.encode(), 16, 'pkcs7'))
        return encrypted.hex()

    def client_encrypt_all(self, node_list, message, server, final_data=None):
        processing_list = node_list[::-1]
        server_node_list = []
        request_id = uuid.uuid1().hex

        keys_list = []

        for item in processing_list:
            server_node_list.append([item[0], item[1], item[2]])

        for i in range(len(processing_list)):
            if i == 0:
                # then encrypt the layer of last node
                data = {
                    "next": self.rsa_encrypt(processing_list[i][3], server.encode()).hex(),
                    "request_id": request_id,
                    "is_server": 1,
                    "data": message
                }
            else:
                next_hop = processing_list[i - 1][1] + ":" + str(processing_list[i - 1][2])
                data = {
                    # node[1] = host; node[2] = port
                    "next": self.rsa_encrypt(processing_list[i][3], next_hop.encode()).hex(),
                    "request_id": request_id,
                    "is_server": 0,
                    "data": final_data
                }
            print("Encoding data at layer {} ".format(str(len(processing_list) - i)))

            aes_key = self.get_aes(processing_list[i][1], processing_list[i][2])
            keys_list.append(aes_key)
            cipher = AES.new(aes_key, AES.MODE_ECB)

            encrypted = cipher.encrypt(pad(json.dumps(data).encode(), 16, 'pkcs7'))
            final_data = encrypted.hex()
            # self.test_decrypt(aes_key, final_data)

        return final_data, keys_list, request_id

    def client_decrypt_all(self, key_list, data):
        temp_list = key_list[::-1]

        for key in temp_list:
            cipher = AES.new(key, AES.MODE_ECB)
            data = cipher.decrypt(bytes.fromhex(data))
            data = unpad(data, 16, 'pkcs7').decode()
        return data

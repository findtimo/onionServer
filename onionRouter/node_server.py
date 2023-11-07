import base64
import socketserver
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from typing import Tuple
import sqlite3
import socket
import signal
from flask import Flask, request, jsonify, render_template

host = ('localhost', 8888)


def db_run(sql, data=None):
    if data is None:
        data = []
    connection = sqlite3.connect('./node_server/nodes.db')
    cursor = connection.cursor()
    cursor.execute(sql)
    if "SELECT" in sql:
        for row in cursor:
            data.append(row)
        return data
    connection.commit()
    connection.close()
    if "INSERT" in sql:
        return cursor.lastrowid

    if "UPDATE" in sql:
        return cursor.lastrowid

    if "SELECT" in sql:
        return data


app = Flask(__name__)


def get_all_nodes():
    return db_run("""SELECT * FROM NODE WHERE STATUS = 1""")


new_node = []
new_link = []


@app.route("/get_nodes", methods=['GET'])
def get_nodes():
    response = jsonify({'data': get_all_nodes()})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route("/get_new_node", methods=['GET'])
def get_new_node():
    try:
        new = new_node.pop(0)
        response = jsonify({'data': new})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except:
        response = jsonify({'data': ""})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

# for nodes to report the next hop
@app.route("/report_link", methods=['POST'])
def report_link():
    data = request.json
    new_link.append(data)
    return jsonify({'data': "ok"})


@app.route("/get_new_link", methods=['GET'])
def get_new_link():
    try:
        new = new_link.pop(0)
        response = jsonify({'data': new})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except:
        response = jsonify({'data': ""})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@app.route("/register_node", methods=['POST'])
def register_node():
    body = request.json
    key = RSA.import_key(body['public_key'])
    h = SHA256.new(bytes(body['host'], 'utf-8'))
    print("Received node registration request from " + body['host'] + ", Verifying signature ......")

    try:
        pkcs1_15.new(key).verify(h, base64.b64decode(body['signature']))
        print("The signature is valid. Inserting new record to database")
        host_with_port = str(body['host']).split(":")

        check_exist = db_run('''
        SELECT * FROM NODE WHERE HOST='{}' AND PORT = {} 
        '''.format(host_with_port[0], host_with_port[1]))

        if len(check_exist) == 0:
            inserted_id = db_run('''
                INSERT INTO NODE (HOST,PORT,PUBLIC_KEY,STATUS) VALUES ('{}', {}, '{}', 1)
            '''.format(host_with_port[0], int(host_with_port[1]), body['public_key']))
        else:
            db_run('''
               UPDATE NODE
               SET PUBLIC_KEY = '{}', STATUS = 1
               WHERE HOST = '{}' AND PORT = {};
            '''.format(body['public_key'], host_with_port[0], host_with_port[1]))
            inserted_id = check_exist[0][0]

        new_node.append([inserted_id, host_with_port[0], int(host_with_port[1])])
        res = {'position': inserted_id}

    except (ValueError, TypeError):
        print("The signature is not valid. Rejected")
        res = {'err': 'signature invalid'}

    return res

def handler(sig, frame):
    db_run('''DROP TABLE IF EXISTS NODE''')
    exit(1)

if __name__ == '__main__':
    db_run('''CREATE TABLE IF NOT EXISTS NODE
           (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
           HOST           TEXT    NOT NULL,
           PORT            INT     NOT NULL,
           PUBLIC_KEY      TEXT  NOT NULL,
           STATUS          BIT);''')

    signal.signal(signal.SIGINT, handler)
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    app.run(host='0.0.0.0', port=8888)

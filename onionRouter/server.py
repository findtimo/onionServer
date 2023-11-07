from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from util import Util
import socket

util = Util()


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self._set_headers()
        data_string = self.rfile.read(int(self.headers['Content-Length']))
        body = data_string
        util.print_blue("Sender: {}".format(body.decode()))
        util.print_red("Please input your response:")
        response_message = input()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(response_message.encode())
        util.print_yellow("response sent")
        return

    def _set_headers(self):
        pass

    def log_message(self, format, *args):
        return


if __name__ == '__main__':
    httpd = HTTPServer(('0.0.0.0', 9999), RequestHandler)
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print("Server is up, listening at: {}:{}".format(ip_address, 9999))
    httpd.serve_forever()

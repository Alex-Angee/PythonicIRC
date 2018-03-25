import socket
import sys
import json

class Client:
    def __init__(self):
        self.isClientConnected = False

    def connect(self, host='', port=50000):
        try:
            self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.clientSocket.connect((host, port))
            self.isClientConnected = True
        except socket.error as errorMessage:
            if errorMessage.errno == socket.error.errno:
                sys.stderr.write('Connection refused to ' + str(host) + ' on port ' + str(port))
            else:
                sys.stderr.write('Failed to create a client socket: Error - %s\n', errorMessage[1])

    def disconnect(self):
        if self.isClientConnected:
            self.clientSocket.close()
            self.isClientConnected = False

    def send(self, data):
        if not self.isClientConnected:
            return

        self.clientSocket.send(data.encode('utf8'))

    def receive(self, size=4096):
        if not self.isClientConnected:
            return ""

        string = self.clientSocket.recv(size).decode('utf8')
        if '~%c%h%a%n%n%e%l%s%~' in string:
            string = string.replace('~%c%h%a%n%n%e%l%s%~', '')
            ser_dict = json.loads(string)
            return ["channels", ser_dict]
        if '~%m%e%s%s%a%g%e%s%~' in string:
            string = string.replace('~%m%e%s%s%a%g%e%s%~', '')
            ser_dict = json.loads(string)
            return ["messages", ser_dict]
        else:
            return [string, None]

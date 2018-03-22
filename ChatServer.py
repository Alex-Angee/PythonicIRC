import socket
import sys
import threading
import User as user
import Commands
from pathlib import Path
from argparse import ArgumentParser
import platform
from datetime import datetime
import time
import json


class Server:
    SERVER_CONFIG = {"BACKLOG": 15}
    channel = None
    command = None
    config = "Client_Server/Config/chatserver.conf"

    def __init__(self,port=None,db=None,config=None,host=socket.gethostbyname('localhost'), allowReuseAddress=True):
        self.serverTime = self.createdTime()
        self.host = host
        self.dbpath = self.path()
        if port is None:
            self.port = self.port()
        else:
            self.port = port
        self.allowReuseAddress = allowReuseAddress
        self.additionalPorts = self.additionalPorts()
        self.address = (self.host, self.port)
        self.clients = {}
        self.clientThreadList = []
        self.channelName = "MainChannel"

        # Dictionary of a dictionary with unique channel id to list of public or private channels
        self.allChannels = {"Public": {self.channelName: list(self.clients.values())}, "Private": {}, "All Channels": {}}
        self.userStatus = {}
        self.userPrivileges = {"SysOP": [], "Admin": []}

        self.startserver()

        if db is None:
            pass
        else:
            if self.dbpath != None:
                print("The dbpath is: '" + self.dbpath + "'")
            else:
                self.dbpath = self.path()
                print("The dbpath is: '" + self.dbpath + "'")
        if config is None:
            pass
        else:
            print("The location of the server config file is: '" + self.config + "'")

    def port(self):
        filepath = Path(self.config).resolve()
        with open(filepath) as file_handle:
            data = file_handle.readlines()
        port = data[0]
        port = port.split(" ")
        port = port[1]
        port = int(port)
        return port

    def path(self):
        filepath = Path(self.config).resolve()
        with open(filepath) as file_handle:
            data = file_handle.readlines()
        path = data[1].replace('\n', '')
        path = path[3:]
        path = path.strip()
        return path

    def additionalPorts(self):
        filepath = Path(self.config).resolve()
        with open(filepath) as file_handle:
            data = file_handle.readlines()
        ports = data[2].replace(',', '')
        ports = ports.replace('\n', '')
        ports = ports.split(" ")
        ports = ports[2:]
        return ports

    def listen_thread(self, defaultGreeting="\n> Welcome to our chat app!!! What is your name?\n"):
        while True:
            print("Waiting for a client to establish a connection\n")
            clientSocket, clientAddress = self.serverSocket.accept()
            print(
                "Connection established with IP address {0} and port {1}\n".format(clientAddress[0], clientAddress[1]))
            clientSocket.send(defaultGreeting.encode('utf8'))
            clientThread = threading.Thread(target=self.client_thread, args=(clientSocket, clientAddress))
            self.clientThreadList.append(clientThread)
            clientThread.start()

        for thread in self.clientThreadList:
            if thread.is_alive():
                thread.join()

    def start_listening(self):
        self.serverSocket.listen(Server.SERVER_CONFIG["BACKLOG"])
        listenerThread = threading.Thread(target=self.listen_thread)
        listenerThread.start()
        listenerThread.join()

    def client_thread(self, clientSocket, clientAddress, size=4096):
        self.command = Commands.Commands()
        response = self.getName(clientSocket, size)
        name = response[0]
        isReturnUser = response[1]
        if isReturnUser is True:
            realName = self.command.returnUser(name).realName
            password = self.command.returnUser(name).password
        else:
            clientSocket.send("> What's your real name?\n".encode('utf8'))
            realName = clientSocket.recv(size).decode('utf8')
            clientSocket.send("> What's your password?\n".encode('utf8'))
            password = clientSocket.recv(size).decode('utf8')
        newUser = user.User(name, realName, password, clientSocket, clientAddress, size, "ACTIVE", "AVAILABLE")

        self.command.serverCreatedTime = self.serverTime
        self.command.serverSocket = self.serverSocket
        self.command.host = self.host
        self.command.port = self.port
        self.command.server = "localhost"
        self.command.serverplatform = platform.release()
        self.command.allowReuseAddress = self.allowReuseAddress
        self.command.serverself = self
        self.clients[clientSocket] = newUser
        self.command.allUsers[newUser] = newUser.name
        if len(self.clients) == 1:
            self.channel = self.command.createChannel(self.channelName, self.allChannels, newUser, False)
            self.channel.allChannels = dict(self.allChannels["Public"])
            self.userPrivileges["Admin"].append(newUser)
            newUser.isAdmin = True
            newUser.currentChannel = self.channel
            self.command.ChannelOP.append(newUser)
        else:
            self.channel.allUsers[newUser.socket] = newUser
            self.channel.allChannels = dict(self.allChannels["Public"])
            newUser.currentChannel = self.channel
            self.command.joinPublic(self.channel, newUser)
        self.allChannels["All Channels"][self.channelName] = self.channel
        self.command.allChannels = dict(self.allChannels["All Channels"])
        self.command.Admins = self.userPrivileges["Admin"]
        self.command.SysOP = self.userPrivileges["SysOP"]
        newUser.allChannels = self.allChannels["Public"].copy()
        self.channel.start(newUser)
        self.command.start(newUser)

    def getName(self, clientSocket, size):
        isReturnUser = False
        name = clientSocket.recv(size).decode('utf8')
        if self.command.returnUser(name) is not None:
            if self.isUserOn(self.command.returnUser(name)) is False:
                if self.command.returnUser(name):
                    clientSocket.send("> What is the password for this account?\n".encode('utf8'))
                    attempts = 3
                    while attempts > 0:
                        password = clientSocket.recv(size).decode('utf8')
                        serverMessage = "> Password Incorrect. You have " + str(attempts) + " attempts left.\n"
                        if password != self.command.returnUser(name).password:
                            clientSocket.send(serverMessage.encode('utf8'))
                        else:
                            isReturnUser = True
                            break
                        attempts = attempts - 1
                else:
                    while self.command.returnUser(name) is not None:
                        clientSocket.send("> Please input another name. A user with that name exists in this server\n".encode('utf8'))
                        name = clientSocket.recv(size).decode('utf8')
            else:
                clientSocket.send(("A user with the name of " + name + " already exists.").encode('utf8'))
                while self.command.returnUser(name) is not None:
                    clientSocket.send("> Please input another name. A user with that name exists in this server\n".encode('utf8'))
                    name = clientSocket.recv(size).decode('utf8')
        if ' ' in name:
            name = name.replace(' ', '')
        if ',' in name:
            name = name.replace(',', '')
        return [name, isReturnUser]

    def createdTime(self):
        ts = time.time()
        localTime = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        newTime = localTime
        return newTime

    # Checks if user is online
    def isUserOn(self, user):
        if user.socket.fileno() != -1:
            return False
        else:
            return True

    # Start server
    def startserver(self):
        try:
            self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as errorMessage:
            sys.stderr.write("Failed to initialize the server. Error - %s\n", errorMessage[1])
            raise

        if self.allowReuseAddress:
            self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.serverSocket.bind(self.address)
        except socket.error as errorMessage:
            sys.stderr.write('Failed to bind to ' + self.address + '. Error - %s\n', errorMessage[1])
            raise

    # Server shutdown function
    def server_shutdown(self):
        print("Shutting down chat server.\n")
        self.serverSocket.shutdown(2)
        self.serverSocket.close()

def main():
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", metavar = '', help="Allows you to change the port this application is hosted on", type=int)
    parser.add_argument("-d", "--db", help="Displays the file path for the db", action="store_true")
    parser.add_argument("-c", "--config", help="Displays the server configuration path", action="store_true")
    args = parser.parse_args()

    port = None
    db = None
    config = None
    if args.port:
        port = args.port
    if args.db:
        db = args.db
    if args.config:
        config = args.config
    chatServer = Server(port, db, config)

    print("\nListening on port " + str(chatServer.port))
    print("Waiting for connections...\n")

    chatServer.start_listening()
    chatServer.server_shutdown()


if __name__ == "__main__":
    main()

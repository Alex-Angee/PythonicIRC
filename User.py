import socket
import sys


class User:

    def __init__(self, name, realname, password, socket, address, size, status, statusMessage):
        self.name = name
        self.realName = realname
        self.password = password
        self.socket = socket
        self.address = address
        self.size = size
        self.status = status
        self.statusMessage = statusMessage
        self.isAdmin = False
        self.isSysOP = False
        self.allChannels = {}
        self.currentChannel = None
        self.isInvisible = False
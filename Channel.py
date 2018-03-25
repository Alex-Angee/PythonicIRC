class Channel:

    def __init__(self, name, channeltopic, user, isPrivate=False, channelPassword=None, sysops=[], admins=[], helpMessage='', allChannels={}):
        self.RegUsers = []
        self.ChannelOP = []
        self.ChannelOP.append(user)
        self.SysOP = sysops
        self.Admins = admins
        self.allUsers = {}
        self.channelName = name
        self.isPrivate = isPrivate
        self.channelPassword = ""
        self.allChannels = allChannels.copy()
        self.channelTopic = channeltopic
        self.messages = []

        if isPrivate:
            self.channelPassword = channelPassword
        self.allUsers[user.socket] = user

    def start(self, user):
        # Do not allow to make another name
        if self.isPrivate:
            passwordCorrect = False
            user.socket.send("> Please input the channel password.".encode('utf8'))
            for x in range (0,3):
                channelPassword = user.socket.recv(user.size).decode('utf8')
                if channelPassword == self.channelPassword:
                    self.RegUsers.append(user)
                    welcomeMessage = "> Welcome " + user.name + " to the " + self.channelName + ", type /help for a list of helpful commands.\n\n"
                    user.socket.send(welcomeMessage.encode('utf-8'))
                    chatMessage = '\n> %s has joined the chat!\n' % user.name
                    for person in self.allUsers.values():
                        person.socket.send(chatMessage.encode('utf8'))
                    if user.socket not in self.allUsers:
                        self.allUsers[user.socket] = user
                    passwordCorrect = True
                    break
                else:
                    user.socket.send("> Password incorrect please try again".encode('utf8'))
            if passwordCorrect == False:
                user.socket.send("> You did not enter the password correct. You will not be added to the channel.".encode('utf8'))
                return
        else:
            welcomeMessage = "> Welcome " + user.name + " to the " + self.channelName + ", type /help for a list of helpful commands.\n\n"
            user.socket.send(welcomeMessage.encode('utf-8'))
            chatMessage = '\n> %s has joined the chat!\n' % user.name
            for person in self.allUsers.values():
                person.socket.send(chatMessage.encode('utf8'))
            if user not in (self.ChannelOP, self.SysOP, self.Admins):
                self.RegUsers.append(user)

import Channel
from datetime import datetime
import time
from pathlib import Path
import ChatServer
import json
import asyncio


class Commands:
    allChannels = {}
    serverSocket = None
    allUsers = {}
    bannedusers = {}
    host = ""
    port = ""
    server = ""
    serverplatform = ""
    allowReuseAddress = None
    serverself = None
    serverCreatedTime = None
    silenced = []
    HELP_MESSAGE = """> The list of commands available are:
    /away - [message] Sets the status to away if passed a parameter, otherwise sets the status to active
    /die - Shuts down the server
    /info - Displays server information
    /invite - <user> <channel> [i] Invite a user to a channel. For private channels, ChannelOP must invite with mode i
    /ison - <user> <user>Provide a space separated user list and will output the users that are online.
    /join - <PrivateChannelName>, <PublicChannelName> [password] Allows the user to a public channel. If the channel you wish to join is private, add a password for it. Only add a password if the channel already exists.
    /kick - <user>, <user> 	Kicks a user or users from a channel.
    /kill - <user> Kill command disconnects a user from the server with a provided message.
    /knock - <channel> [message] Sends a notice to all Channel OP or Admin/SYSOP to send an invite to a private channel.
    /list - Lists all the channels with their topics, also including the number of users in each one.
    /nick - <nickname> Change nickname
    /notice - <user> <message> Similarly send a message to specified users, but if the status of a user is set to away, the message is not sent an automatic reply.
    /operwall - <message> Send a message to all Channel OP in your current channel.
    /part - <channel>, <channel> [message] User can leave a channel or comma separated channels with an optional parting response.
    /ping - Checks to see if the server is alive.
    /pong - Return to a ping message.
    /privmsg - <user>, <user> <message> Sends a private message to user(s) separated by commas
    /promote - <user> <d> <c> <s> <a> Allows a Channel OP/ Sys OP/ Admin to promote/demote with -d (demote to regular user) -c (channel OP) -s (Sys OP) -a (Admin)
    /quit - Exits the program.
    /restart - Allows the Admins to restart the server
    /rules - Displays the rules of the server
    /setname - <name> Change real name
    /silence - <user> <+> <-> Prevents a user from speaking if + is given. Allows the user to speak if - is given. If nothing is given, displays all users who cannot speak.
    /switch - <channel> Allows you to switch to the specified channel if you're a member of it.
    /time - Returns the local time of the server.
    /topic - <channel> [topic]If no message is provided, displays the channel's topic. If a message is passed, it changes the channel's topic.
    /user - Returns the real name and nick name of a user.
    /userhost - Returns information of up to 5 users separated by a space character.
    /userip - Returns the user ip of a given name.
    /users - List all users in the server.
    /version - Displays server version
    /wallops - <message> Sends a message to every channel op, SysOP, and Admin in the server
    /who - <user> [o] Returns information about a user is a name is provided. -o returns information for all channel ops. Nothing provided provides information about everyone if they are not invisible.
    /whois - <user> Returns the real name for the nickname provided.\n\n""".encode('utf8')

    RULES_MESSAGE = """> The list of the rules are as followed:
    1) Be respectful to others.
    2) No foul language.
    3) I'm better than Dr. Ortega @ Fifa.\n\n
    """.encode('utf8')

    def __init__(self):
        self.RegUsers = []
        self.ChannelOP = []
        self.SysOP = None
        self.Admins = None
        self.HELP_MESSAGE = self.HELP_MESSAGE


    # List of commands
    # Invite command
    def invite(self, newUser, args):
        if len(args) > 0:
            user = args[0]
            del args[0]
            if len(args) > 0:
                channel = args[0]
                del args[0]

                serverMessage = "> You have been added to " + channel + ", by " + newUser.name + ".\n"
                serverPrivilegeErrorMessage = "> You do not have the privileges to add " + newUser.name + " to " + channel + ".\n"
                serverErrorMessage = "> The channel you have tried to add " + user + " to does not exist.\n"

                if self.returnUser(user) is not None:
                    addUser = self.returnUser(user)
                else:
                    newUser.socket.send("> The given user does not exist.\n".encode('utf8'))
                    return

                if self.doesChannelExist(channel):
                    inviteChannel = Commands.allChannels["All Channels"][channel]
                else:
                    newUser.socket.send(serverErrorMessage.encode('utf8'))
                    return

                # Invite with higher privileges
                if (len(args) == 1) and (args[0] == "i"):
                    if (newUser in inviteChannel.ChannelOP) or newUser.isAdmin or newUser.isSysOP:
                        if inviteChannel.isPrivate is False:
                            if addUser not in inviteChannel.allUsers.keys():
                                self.joinPublic(inviteChannel, addUser)
                                addUser.currentChannel = inviteChannel
                                addUser.socket.send(serverMessage.encode('utf8'))
                                newUser.socket.send(( "> You have successfully added " + addUser.name + " to " + inviteChannel.channelName + ".\n").encode('utf8'))
                            else:
                                newUser.socket.send(("> " + addUser.name + " is already in this channel.").encode())
                        else:
                            if addUser not in inviteChannel.allUsers.keys():
                                self.joinPrivate(inviteChannel, addUser)
                                addUser.currentChannel = inviteChannel
                                addUser.socket.send(serverMessage.encode('utf8'))
                                newUser.socket.send(("> You have successfully added " + addUser.name + " to " + inviteChannel.channelName + ".\n").encode('utf8'))
                            else:
                                newUser.socket.send(("> " + addUser.name + " is already in this channel.").encode())
                    else:
                        newUser.socket.send(serverPrivilegeErrorMessage.encode('utf8'))
                else:
                    if inviteChannel.isPrivate is False:
                        if addUser not in inviteChannel.allUsers.keys():
                            inviteChannel.allUsers[addUser] = addUser.name
                            addUser.socket.send(serverMessage.encode('utf8'))
                            newUser.socket.send(("> You have successfully added " + addUser.name + " to " + inviteChannel.channelName + ".\n").encode('utf8'))
                        else:
                            newUser.socket.send(("> " + addUser.name + " is already in this channel.").encode())
                    else:
                        newUser.socket.send("> To invite a user to a private channel, please pass the 'i' flag.\n".encode('utf8'))
            else:
                newUser.socket.send("> You did not provide a channel name.\n".encode('utf8'))
        else:
            newUser.socket.send("> You did not provide any users.\n".encode('utf8'))

    # Away command
    def away(self, user, args=[]):
        if len(args) > 0:
            user.status = "AWAY"
            user.statusMessage = "AWAY " +  " ".join(args)
            serverMessage = "> You have successfully changed to AWAY status and set changed your status message.\n"
            user.socket.send(serverMessage.encode('utf8'))
        else:
            user.status = "ACTIVE"
            user.statusMessage = "AVAILABLE"
            serverMessage = "> You have successfully changed to ACTIVE status and set changed your status message.\n"
            user.socket.send(serverMessage.encode('utf8'))

    # Private Message command
    def private_message(self, newUser, args=[]):
        if len(args) > 0:
            users = [newUser]
            breakpoint = 0
            privmessage = ""
            tempUser = None

            # Sends the message to users listed
            for x in range(0, len(args)):
                user = ""
                if ',' in args[x]:
                    user = args[x].replace(',', '')
                else:
                    user = args[x]

                tempUser = self.returnUser(user)
                if tempUser != None:
                    users.append(tempUser)
                else:
                    breakpoint = x
                    break

            message = args[(breakpoint):]
            if len(message) <= 1:
                privmessage = "".join(message)
            else:
                privmessage = " ".join(message)

            # Got the list, now get the message
            for x in range(0, len(users)):
                if newUser.name != users[x].name:
                    if users[x].status == "AWAY":
                        message = users[x].statusMessage + "\n"
                        newUser.socket.send((users[x].name + ": " + message).encode('utf8'))
                        self.log(newUser, message)
                    else:
                        message = "PRIVMSG " + newUser.name + ": " + privmessage + "\n"
                        users[x].socket.send((message).encode('utf8'))
                        self.log(newUser, message)
                else:
                    message = 'PRIVMSG You: ' + privmessage + "\n"
                    newUser.socket.send((message).encode('utf8'))
                    self.log(newUser, message)
        else:
            newUser.socket.send("> You did not provide any users or a message.".encode('utf8'))

    # Change nickname command
    def nick(self, user, args=[]):
        if len(args) > 0:
            oldName = user.name
            serverMessage = ""
            listOfUsers = []
            for person in Commands.allUsers.keys():
                listOfUsers.append(person.name)
            if len(args) > 1:
                name = "".join(args)
                if name not in listOfUsers:
                    tempUser = self.returnUser(user.name)
                    tempUser.name = name
                    serverMessage = "> You have successfully changed your nickname to " + name + "\n"
                    self.broadcast_message(
                        "For everyone in the chat to be aware, I have changed my name from " + oldName + " to " + name + "." + '\n',
                        tempUser)
                    return tempUser
                else:
                    serverMessage = "> Someone else with that name already exists."
            else:
                name = args[0]
                if name not in listOfUsers:
                    tempUser = self.returnUser(user.name)
                    tempUser.name = name
                    serverMessage = "> You have successfully changed your nickname to " + name + "\n"
                    self.broadcast_message(
                        "For everyone in the chat to be aware, I have changed my name from " + oldName + " to " + name + "." + '\n',
                        tempUser)
                    return tempUser
                else:
                    serverMessage = "> Someone else with that name already exists.\n"
            user.socket.send(serverMessage.encode('utf8'))
        else:
            user.socker.send("> You did not provide a nickname.\n".encode('utf8'))

    # Restart server command
    def restart(self, user):
        if user in self.Admins:
            self.broadcast_all(user, "I have restarted the server.")
            for key in Commands.allUsers.keys():
                key.socket.close()
        else:
            user.socket.send("> You do not have permissions to restart the server.\n".encode('utf8'))

    # Quit command
    def quit(self, user):
        self.broadcast_message(('\n> %s has left the chat room.\n' % user.name), user)
        del Commands.allUsers[user.socket]
        user.socket.close()
        print("Connection with IP address {0} has been removed.\n".format(user.address))

    # Users command
    def list_all_users(self, user):
        message = "> The users in the chat room are: "
        users_list = []
        for person in Commands.allUsers.values():
            if person == user:
                users_list.append("You")
            else:
                users_list.append(person)
        message = message + ", ".join(users_list) + "\n"
        user.socket.send(message.encode('utf8'))

    # Help command
    def help(self, user):
        user.socket.send(self.HELP_MESSAGE)

    # Broadcast message command
    def broadcast_message(self, message, user):
        channelObject = user.currentChannel

        if user.name not in Commands.silenced:
            # Gets channel user is in
            for users in channelObject.allUsers.values():
                if users.currentChannel == channelObject:
                    if user.name != users.name:
                        users.socket.send((user.name + ": " + message).encode('utf8'))
                    else:
                        user.socket.send(('You: ' + message).encode('utf8'))
            channelObject.messages.append((user.name + ": " + message))

    def joinChannel(self, user, listofargs):
        listOfPasswords = []
        listOfChannels = {}
        start = False
        end = False
        if isinstance(listofargs, str):
            channel = listofargs
            listOfChannels[channel] = None
        else:
            for string in listofargs:
                if '[' in string:
                    start = True
                    string.replace('[', '')
                    if ',' in string:
                        string.replace(',', '')
                    if ']' in string:
                        end = True
                        string.replace(']', '')
                    listOfPasswords.append(string)
                elif ']' in string:
                    end = True
                    string.replace(']', '')
                    listOfPasswords.append(string)
                else:
                    if start is False and end is False:
                        if ',' in string:
                            string.replace(',', '')
                        listOfChannels[string] = None
                    else:
                        listOfPasswords.append(string)

        for key, value in listOfChannels.items():
            if self.doesChannelExist(key) is True:
                channelObj = Commands.allChannels["All Channels"][key]
                if channelObj.isPrivate is True:
                    if len(listOfPasswords) > 0:
                        listOfChannels[key] = listOfPasswords[0]
                        listOfPasswords = listOfPasswords[1:]
                    else:
                        listOfChannels[key] = "Password"
                else:
                    listOfChannels[key] = "exists"
            else:
                listOfChannels[key] = "does not exist"

        for key, value in listOfChannels.items():
            if value == "exists":
                    self.joinPublic(key, user)
            elif value == "does not exist":
                    user.currentChannel = self.create(user, key)
                    serverMessage = "> " + user.name + " has joined channel " + user.currentChannel.channelName + ".\n"
                    self.broadcast_channel(serverMessage, user)
            else:
                if Commands.allChannels["All Channels"][key].channelPassword == value:
                        self.joinPrivate(key, user)
                elif len(listOfPasswords) == 0:
                    user.socket.send(("> What's the password for " + key + "\n").encode('utf8'))
                    password = user.socket.recv(user.size).decode('utf8')
                    if Commands.allChannels["All Channels"][key].channelPassword == password:
                        self.joinPrivate(key, user)
                    else:
                        error = "> The password is incorrect for " + key + " .\n"
                        user.socket.send(error.encode('utf8'))
                else:
                    error = "> The password is incorrect for " + key + " .\n"
                    user.socket.send(error.encode('utf8'))

    # Create channel command
    def createChannel(self, channelName, allChannels, user, isPrivate=False):
        if isPrivate == True:
            user.socket.send("> What's the channel topic?\n".encode('utf8'))
            channelTopic = user.socket.recv(user.size).decode('utf8')
            user.socket.send("> Please make a password for the channel.\n".encode('utf8'))
            channelPassword = user.socket.recv(user.size).decode('utf8')
            newChannel = Channel.Channel(channelName, channelTopic, user, isPrivate, channelPassword, self.SysOP,self.Admins)
            newChannel.allUsers[user.socket] = user
            Commands.allChannels["All Channels"][channelName] = newChannel
            self.newChannel(newChannel)
            return newChannel
        else:
            user.socket.send("> What's the channel topic?\n".encode('utf8'))
            channelTopic = user.socket.recv(user.size).decode('utf8')
            newChannel = Channel.Channel(channelName, channelTopic, user, isPrivate, None, self.SysOP,self.Admins)
            Commands.allChannels = allChannels
            newChannel.allUsers[user.socket] = user
            Commands.allChannels["All Channels"][channelName] = newChannel
            self.newChannel(newChannel)
            return newChannel

    # Kick command
    def kickFromChannel(self, user, lisofPeopleToKick):
        if len(lisofPeopleToKick) > 0:
            users = []
            if user in (self.ChannelOP) or user.isAdmin or user.isSysOP:
                for x in range(0, len(lisofPeopleToKick)):
                    tempUser = ""
                    if ',' in lisofPeopleToKick[x]:
                        tempUser = lisofPeopleToKick[x].replace(',', '')
                    else:
                        tempUser = lisofPeopleToKick[x]

                    if tempUser not in users:
                        if self.returnUser(tempUser) in Commands.allUsers.values():
                            users.append(tempUser)
                        else:
                            breakpoint = x
                            break

                for x in range(0, len(users)):
                    if users[x].currentChannel == self.allChannels["All Channels"]["MainChannel"]:
                        user.socket.send("> The user appears to be in the Main Channel. "
                                         "Use the /kill command instead.\n".encode('utf8'))
                        return

                if len(users) > 1:
                    for x in range(0, len(users)):
                        self.removeFromChannel(user, users[x])
                else:
                    self.removeFromChannel(user, lisofPeopleToKick)
            else:
                user.socket.send("> You do not have sufficient permissions to kick someone from this channel.\n".encode('utf8'))
        else:
            user.socket.send("> You did not provide a user to kick.\n".encode('utf8'))

    # UserIP command
    def userip(self, name, user):
        if user is not None:
            newUser = self.returnUser("".join(name))
            if newUser != None:
                ip = str(newUser.address[0])
                message = "> " + newUser.name + "'s ip address is " + ip + ".\n"
                user.socket.send(message.encode('utf8'))
            else:
                user.socket.send("> The given user does not exist.\n".encode('utf8'))
        else:
            user.socket.send("> You did not provide a username.\n".encode('utf8'))

    # List command
    def list(self, user):
        returnMessage = ""
        channels = Commands.allChannels["All Channels"]
        for channel in channels.values():
            listOfUsers = channels[channel.channelName].allUsers.values()
            if channel.isPrivate is False:
                if len(listOfUsers) == 0:
                    returnMessage += "> The " + channel.channelName + "'s topic is: " + channel.channelTopic + "and " \
                                                                                "currently does not have any users.\n"
                elif len(listOfUsers) == 1:
                    returnMessage += "> The " + channel.channelName + "'s topic is: " + channel.channelTopic + \
                                     " and currently has 1 user.\n"
                else:
                    returnMessage += "> The " + channel.channelName + "'s topic is: " + channel.channelTopic + \
                                     " and currently has " + str(len(listOfUsers)) + " users.\n"
            else:
                if len(listOfUsers) == 0:
                    returnMessage += "> The " + channel.channelName + " currently does not have any users. "
                elif len(listOfUsers) == 1:
                    returnMessage += "> The " + channel.channelName + " currently has 1 user.\n"
                else:
                    returnMessage += "> The " + channel.channelName + " currently has " + str(len(listOfUsers)) + " users.\n"
        user.socket.send(returnMessage.encode('utf8'))

    # Promotes someone to Channel OP or SYSOPS
    def promote(self, user, listofArgs):
        isAdmin = user.isAdmin
        isSysOP = user.isSysOP
        isChannelOP = False
        name = listofArgs[0]
        promoteUser = self.returnUser(name)
        listofArgs = listofArgs[1:]
        currentChannel = user.currentChannel
        if user in user.currentChannel.ChannelOP:
            isChannelOP = True

        if promoteUser is not None:
            if listofArgs[0] == "d":
                if isChannelOP or isSysOP or isAdmin:
                    promoteUser.isAdmin = False
                    promoteUser.isSysOP = False
                    for x in range(0, len(currentChannel.ChannelOP)):
                        if currentChannel.ChannelOP[x]  == promoteUser:
                            del user.currentChannel.ChannelOP [x]
                            message = "> The user: " + name + " has been successfully demoted."
                            user.socket.send(message.encode('utf8'))
                            otherMessage = "> " + user.name + " has demoted you."
                            promoteUser.socket.send(otherMessage.encode('utf8'))
                else:
                    user.socket.send("> You do not have the permissions for this action".encode('utf8'))
            elif listofArgs[0] == "c":
                if isChannelOP or isSysOP or isAdmin:
                    if promoteUser not in currentChannel.ChannelOP:
                        currentChannel.ChannelOP.append(promoteUser)
                        message = "> The user: " + name + " has been successfully promoted to Channel OP."
                        user.socket.send(message.encode('utf8'))
                        otherMessage = "> " + user.name + " has promoted you to ChannelOP."
                        promoteUser.socket.send(otherMessage.encode('utf8'))
                        self.newUserOldChannel(user, currentChannel.channelName)
                else:
                    user.socket.send("> You do not have the permissions for this action".encode('utf8'))
            elif listofArgs[0] == "s":
                if isSysOP or isAdmin:
                    if promoteUser.isSysOP is False:
                        promoteUser.isSysOP = True
                        message = "> The user: " + name + " has been successfully promoted to SYS OP."
                        user.socket.send(message.encode('utf8'))
                        otherMessage = "> " + user.name + " has promoted you to Sys OP."
                        promoteUser.socket.send(otherMessage.encode('utf8'))
                    else:
                        message = "> The user: " + name + " is already a SYS OP."
                        user.socket.send(message.encode('utf8'))
                else:
                    user.socket.send("> You do not have the permissions for this action".encode('utf8'))
            elif listofArgs[0] == "a":
                if isAdmin:
                    if promoteUser.isAdmin is False:
                        promoteUser.isAdmin = True
                        message = "> The user: " + name + " has been successfully promoted to Admin."
                        user.socket.send(message.encode('utf8'))
                        otherMessage = "> " + user.name + " has promoted you to Admin."
                        promoteUser.socket.send(otherMessage.encode('utf8'))
                    else:
                        message = "> The user: " + name + " is already an Admin."
                        user.socket.send(message.encode('utf8'))
                else:
                    user.socket.send("> You do not have the permissions for this action".encode('utf8'))
            else:
                user.socket.send("> That command does not exist.\n".encode('utf8'))

    # Setname command
    def setname(self, user):
        user.socket.send("> What do you want to set your real name to?\n".encode('utf8'))
        user.realName = user.socket.recv(user.size).decode('utf8')
        serverMessage = "> You have successfully changed your real name to " + user.realName +".\n"
        user.socket.send(serverMessage.encode('utf8'))

    # Time message
    def time(self, user):
        ts = time.time()
        localTime = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        newTime = "> " + localTime + "\n"
        user.socket.send(newTime.encode('utf8'))

    # Topic message
    def topic(self, user, listOfArgs):
        channel = user.currentChannel
        if len(listOfArgs) == 0:
            message = "> The channel's topic: " + channel.channelTopic + "\n"
            user.socket.send(message.encode('utf8'))
        else:
            newTopic = " ".join(listOfArgs)
            channel.channelTopic = newTopic
            user.socket.send("> You have successfully changed the channel's topic.\n".encode('utf8'))

    # Operwall command
    def operWall(self, user, listOfArgs):
        if len(listOfArgs) > 0:
            message = " ".join(listOfArgs)
            currentChannel = user.currentChannel
            for users in currentChannel.ChannelOP:
                users.socket.send(("OPERWALL " + user.name + ": " + message + "\n").encode('utf8'))
        else:
            user.socket.send("> You did not provide a message\n".encode('utf8'))

    # Who command
    def who(self, user, listOfArgs):
        returnMessage = ""
        currentChannel = user.currentChannel
        if len(listOfArgs) == 0:
            for users in self.allUsers.values():
                if users not in currentChannel.allUsers.values():
                    if users.isInvisible is False:
                        returnMessage += "> " + users.name + "\n" + users.realName + "\n" + users.status + " " +users.statusMessage + "\n"
        elif listOfArgs[0] == 'o':
            for users in currentChannel.ChannelOP:
                returnMessage += "> " + users.name + "\n" + users.realName + "\n" + users.status + " " + users.statusMessage + "\n"
        else:
            returnUser = self.returnUser(listOfArgs[0])
            if returnUser is not None:
                returnMessage += "> " + returnUser.name + "\n" + returnUser.realName + "\n" + returnUser.status + " " + returnUser.statusMessage + "\n"
            else:
                returnMessage += "> The given user does not exist"
        user.socket.send(returnMessage.encode('utf8'))

    # Whois command
    def whois(self, user, listOfArgs):
        if len(listOfArgs) > 0:
            name = listOfArgs[0]
            returnUser = self.returnUser(name)
            currentChannel = user.currentChannel
            returnMessage = ""
            if returnUser is not None:
                if user.isAdmin or user.isSysOP or (currentChannel == returnUser.currentChannel and user in currentChannel.ChannelOP):
                    returnMessage += "> " + returnUser.name + "\n" + returnUser.realName + "\n" + returnUser.address[0]
                else:
                    returnMessage += "> " + returnUser.name + "\n" + returnUser.realName
            else:
                returnMessage += "> The given user does not exist.\n"
            user.socket.send((returnMessage + "\n").encode('utf8'))
        else:
            user.socket.send("> You did not provide a name.\n".encode('utf8'))

    # Switch command allows user to speak make passed channel the current channel
    def switch(self, user, listOfArgs):
        channelName = "".join(listOfArgs)
        message = ""
        switch = "No"
        channels = Commands.allChannels["All Channels"]
        for key, value in channels.items():
            if channelName == key:
                if user in value.allUsers.values():
                    if user.currentChannel == value:
                        message = "> You are currently in this channel.\n"
                        switch = "Mem"
                        break
                    else:
                        switch = "Yes"
                        user.currentChannel = value
                        message += "> You have switched to " + channelName + ".\n"
                        break
                else:
                    switch = "NotM"
                    message += "> You are not a member of " + channelName + ".\n"
                    break
        if switch == "No":
            message += "> The channel does not exist.\n"
            user.socket.send(message.encode('utf8'))
        elif switch == "Mem":
            user.socket.send(message.encode('utf8'))
        elif switch == "Yes":
            user.socket.send(message.encode('utf8'))
        else:
            self.joinChannel(user, channelName)

    # Ping message
    def ping(self, user):
        print("> Server at " + self.host + ": " + str(self.port) + " Status: Active\n")
        user.socket.send("> Please use the pong command if you wish to see if the server is active.\n".encode())

    # Pong message
    def pong(self, user):
        user.socket.send(("> Server at " + self.host + ": " + str(self.port) + " Status: Active\n").encode('utf8'))

    # Users command
    def usercommand(self, user, listOfArgs):
        if len(listOfArgs) == 0:
            user.socket.send("Please pass a user name.\n".encode('utf8'))
        else:
            returnUser = self.returnUser(listOfArgs[0])
            if returnUser is not None:
                user.socket.send(("> " + returnUser.name + " " + returnUser.realName + "\n").encode('utf8'))
            else:
                user.socket.send(("> The user " + listOfArgs[0] + " does not exist\n").encode('utf8'))

    # Rules command
    def rules(self, user):
        user.socket.send(self.RULES_MESSAGE)

    # Kill command
    def kill(self, user, listOfArgs):
        if len(listOfArgs) > 0:
            returnUser = self.returnUser(listOfArgs[0])
            if returnUser is not None:
                listOfArgs = listOfArgs[1:]
                serverMessage = "> Your connection has been killed by " + user.name + ".\n"
                if len(listOfArgs) > 0:
                    serverMessage += "> The user's message is provided: " + " ".join(listOfArgs) + "\n"
                    returnUser.socket.send(serverMessage.encode('utf8'))
                    returnUser.socket.close()
                else:
                    returnUser.socket.send(serverMessage.encode('utf8'))
                    returnUser.socket.close()
            else:
                user.socket.send("> The user you provided does not exist.\n".encode('utf8'))
        else:
            user.socket.send("> You did not provide a user or message.\n".encode('utf8'))

    # Notice command
    def notice(self, newUser, args):
        if len(args) > 0:
            users = [newUser]
            breakpoint = 0
            noticemessage = ""
            tempUser = None

            # Sends the message to users listed
            for x in range(0, len(args)):
                user = ""
                if ',' in args[x]:
                    user = args[x].replace(',', '')
                else:
                    user = args[x]

                tempUser = self.returnUser(user)
                if tempUser != None:
                    users.append(tempUser)
                else:
                    breakpoint = x
                    break

            message = args[(breakpoint):]
            if len(message) <= 1:
                noticemessage = "".join(message)
            else:
                noticemessage = " ".join(message)

            # Got the list, now get the message
            for x in range(0, len(users)):
                if newUser.name != users[x].name:
                    if users[x].status == "AWAY":
                        pass
                    else:
                        message = "NOTICE " + newUser.name + ": " + noticemessage + "\n"
                        users[x].socket.send((message).encode('utf8'))
                        self.log(newUser, message)
                else:
                    message = 'NOTICE You: ' + noticemessage + "\n"
                    newUser.socket.send((message).encode('utf8'))
                    self.log(newUser, message)
        else:
            newUser.socket.send("> You did not provide any users or a message.".encode('utf8'))

    # Version command
    def version(self, user):
        serverMessage = "> Server: " + self.server + "\n> Server Version: " + self.serverplatform + ".\n"
        user.socket.send(serverMessage.encode('utf8'))

    # Ison command
    def ison(self, user, listOfArgs):
        if len(listOfArgs) > 0:
            users = []
            for username in listOfArgs:
                if self.returnUser(username) is not None:
                    users.append(self.returnUser(username))
            online = []
            for isUserOnline in users:
                if isUserOnline.socket.fileno() == -1:
                    pass
                else:
                    online.append(isUserOnline.name)

            if len(online) > 0:
                message = "> The list of online users are: " + " ".join(online) + "\n"
                user.socket.send(message.encode('utf8'))
            else:
                message = "> There are no users online.\n"
                user.socket.send(message.encode('utf8'))
        else:
            user.socket.send("> You did not provide any users.\n".encode('utf8'))

    # Knock command
    def knock(self, user, listOfArgs):
        if len(listOfArgs) > 0:
            channelName = listOfArgs[0]
            del listOfArgs[0]
            if len(listOfArgs) > 0:
                message = "KNOCK to " + channelName + " " + user.name + ": " + " ".join(listOfArgs) + "\n"
            else:
                message = "KNOCK to " + channelName + " " + user.name + ": May I please receive an invite to the " + channelName + " channel?\n"

            if self.doesChannelExist(channelName) is True:
                channels = Commands.allChannels["All Channels"]
                for key, value in channels.items():
                    if key == channelName:
                        if value.isPrivate is True:
                            if len(value.ChannelOP) > 0:
                                for users in value.ChannelOP:
                                    users.socket.send(message.encode('utf8'))
                            else:
                                for userobject, username in Commands.allUsers.items():
                                    if userobject.isAdmin or userobject.isSysOP:
                                        userobject.socket.send(message.encode('utf8'))
                        else:
                            user.socket.send("This channel is public. Join it with the /join command.\n".encode('utf8'))
            else:
                user.socket.send("> The channel provided does not exist.\n".encode('utf8'))
        else:
            user.socket.send("> You did not provide a channel.\n".encode('utf8'))

    # Die command
    def die(self, user):
        if user.isSysOP or user.isAdmin:
            user.socket.send("> You have shutdown the server.\n".encode('utf8'))
            ChatServer.Server.server_shutdown(self.serverself)
        else:
            user.socket.send("> You do not have the permissions to access this command.\n".encode('utf8'))

    # Userhost command
    def userhost(self, user, listOfArgs):
        if len(listOfArgs) > 0:
            userslist = []
            for users in listOfArgs:
                if self.returnUser(users) is not None:
                    returnUser = self.returnUser(users)
                    userslist.append(returnUser)
            for checkusers in userslist:
                user.socket.send(("> " + returnUser.name + "\n" + returnUser.realName + "\n").encode('utf8'))
        else:
            user.socket.send("> Please provide a username.\n".encode('utf8'))

    # Info command
    def info(self, user):
        # Displays the server version and the time the server was created
        serverMessage = "> Server: " + self.server + "\n> Server Version: " + self.serverplatform + ".\n" \
                        "> Server Created Time: " + self.serverCreatedTime + ".\n"
        user.socket.send(serverMessage.encode('utf8'))

    # Part command
    def part(self, user, listOfArgs):
        if len(listOfArgs) > 0:
            channels = []
            message = ""
            breakpoint = 0
            for x in range(0, len(listOfArgs)):
                if ',' in listOfArgs[x]:
                    listOfArgs[x] = listOfArgs[x].replace(',', '')
                if self.doesChannelExist(listOfArgs[x]) is True:
                    if listOfArgs[x] != "MainChannel":
                        channels.append(Commands.allChannels["All Channels"][listOfArgs[x]])
                        user.socket.send(("> You have been removed from " + Commands.allChannels["All Channels"][listOfArgs[x]].channelName + ".\n").encode('utf8'))
                    else:
                        user.socket.send("> You cannot leave MainChannel. If you wish to leave, please exit the server.\n".encode('utf8'))
                else:
                    breakpoint = x
                    break
            listOfArgs = listOfArgs[breakpoint:]
            if len(listOfArgs) > 0:
                message = " ".join(listOfArgs)
                for channel in channels:
                    user.currentChannel = channel
                    self.broadcast_channel((user.name + ": " + message), user)
                    del channel.allUsers[user.socket]
                user.currentChannel = Commands.allChannels["All Channels"]["MainChannel"]
            else:
                message = "I am leaving the channel."
                for channel in channels:
                    user.currentChannel = channel
                    self.broadcast_channel((user.name + ": " + message), user)
                    del channel.allUsers[user.socket]
                user.currentChannel = Commands.allChannels["All Channels"]["MainChannel"]
        else:
            user.socket.send("> You did not provide a channel to leave.\n".encode('utf8'))

    # Mode command
    def mode(self, user):
        pass

    # Channelmodes command
    def channelModes(self, user):
        pass

    # Usermodes command
    def userModes(self, user):
        pass

    # Oper command
    def oper(self, user):
        pass

    # Pass command
    def passcommand(self, user):
        pass

    # Wallops command
    def wallops(self, user, listOfArgs):
        if len(listOfArgs) > 0:
            ChannelOP = []
            channels = Commands.allChannels["All Channels"].values()
            for channel in channels:
                for users in channel.ChannelOP:
                    if users not in ChannelOP:
                        ChannelOP.append(users)
                for users in channel.allUsers.values():
                    if users.isAdmin and users not in ChannelOP:
                        ChannelOP.append(users)

            for users in ChannelOP:
                users.socket.send(("WALLOPS " + user.name + ": " + " ".join(listOfArgs) + "\n").encode('utf8'))
        else:
            user.socket.send("> There was no message given.\n".encode('utf8'))

    # Password command
    def password(self, user, listOfArgs):
        if len(listOfArgs) > 0:
            if user.currentChannel.isPrivate is True:
                password = listOfArgs[0]
                del listOfArgs[0]
                user.currentChannel.channelPassword = password
                self.broadcast_channel(("I have changed the channel password to " + password + "."), user)
            else:
                user.socket.send("> The current channel you're in is public.\n".encode('utf8'))
        else:
            user.socket.send("> You did not provide a password.\n".encode('utf8'))

    # Silence command
    def silence(self, user, listOfArgs):
        if user.isAdmin or user.isSysOP or (user in user.currentChannel.ChannelOP):
            if len(listOfArgs) > 0:
                returnUser = self.returnUser(listOfArgs[0])
                if returnUser is None:
                    user.socket.send("> The provided user does not exist.\n".encode('utf8'))
                    return
                else:
                    del listOfArgs[0]
                    if len(listOfArgs) > 0:
                        addOrRemove = listOfArgs[0]
                        del listOfArgs[0]
                        if addOrRemove == '+':
                            if returnUser.name not in Commands.silenced:
                                Commands.silenced.append(returnUser.name)
                                user.socket.send(("> " + returnUser.name + " has been silenced.\n").encode('utf8'))
                                returnUser.socket.send("> You have been silenced.\n".encode('utf8'))
                                return
                            else:
                                user.socket.send("> The given user is already silenced.\n".encode('utf8'))
                                return
                        elif addOrRemove == '-':
                            if returnUser.name not in Commands.silenced:
                                user.socket.send("> The given user is not silenced.\n".encode('utf8'))
                                return
                            else:
                                Commands.silenced.remove(returnUser.name)
                                user.socket.send(("> " + returnUser.name + " has been unsilenced.\n").encode('utf8'))
                                returnUser.socket.send("> You have been unsilenced.\n".encode('utf8'))
                                return
                        else:
                            if returnUser.name in Commands.silenced:
                                user.socket.send("> The user is currently silenced.\n".encode('utf8'))
                                return
                            else:
                                user.socket.send("> The user is not currently silenced.\n".encode('utf8'))
                                return
                    else:
                        if len(Commands.silenced) > 0:
                            user.socket.send(("> These are all the users that are silenced in the server" + ", ".join(Commands.silenced) + ".\n").encode('utf8'))
                        else:
                            user.socket.send("> There are no users silenced.\n".encode('utf8'))
            else:
                if len(Commands.silenced) > 0:
                    user.socket.send(("> These are all the users that are silenced in the server" + ", ".join(
                        Commands.silenced) + ".\n").encode('utf8'))
                else:
                    user.socket.send("> There are no users silenced.\n").encode('utf8')
        else:
            user.socket.send("> You do not have the permissions to use this command.\n".encode('utf8'))

    # Helper functions
    # Remove from channel function
    def removeFromChannel(self, user, name):
        kickedUser = self.returnUser(name)
        if kickedUser is not None and kickedUser.currentChannel == user.currentChannel:
            del Commands.allChannels["All Channels"][kickedUser.currentChannel.channelName][kickedUser.socket]
            kickedUser.currentChannel = self.allChannels["MainChannel"]
        if kickedUser is not None and kickedUser.currentChannel != user.currentChannel:
            del Commands.allChannels["All Channels"][user.currentChannel.channelName][kickedUser.socket]

    # Return User given name function
    def returnUser(self, name):
        user = None
        for key, value in self.allUsers.items():
            if name == value:
                user = key
                return user

    # Join public channel function
    def joinPublic(self, channel, user):
        if isinstance(channel, str):
            if user not in Commands.allChannels["All Channels"][channel].allUsers.values():
                Commands.allChannels["All Channels"][channel].allUsers[user.socket] = user
                serverMessage = "> " + user.name + " has joined channel " + user.currentChannel.channelName + ".\n"
                self.broadcast_channel(serverMessage, user)
            else:
                if user.currentChannel != Commands.allChannels["All Channels"][channel]:
                    self.switch(user, channel)
        else:
            if user not in Commands.allChannels["All Channels"][channel.channelName].allUsers.values():
                Commands.allChannels["All Channels"][channel.channelName].allUsers[user.socket] = user
                serverMessage = "> " + user.name + " has joined channel " + user.currentChannel.channelName + ".\n"
                self.broadcast_channel(serverMessage, user)
            else:
                if user.currentChannel != Commands.allChannels["All Channels"][channel.channelName]:
                    self.switch(user, channel.channelName)

    # Join private channel
    def joinPrivate(self, channel, user):
        if isinstance(channel, str):
            if user not in Commands.allChannels["All Channels"][channel].allUsers.values():
                Commands.allChannels["All Channels"][channel].allUsers[user.socket] = user
                serverMessage = "> " + user.name + " has joined channel " + user.currentChannel.channelName + ".\n"
                self.broadcast_channel(serverMessage, user)
            else:
                if user.currentChannel != Commands.allChannels["All Channels"][channel]:
                    self.switch(user, channel)
        else:
            if user not in Commands.allChannels["All Channels"][channel.channelName].allUsers.values():
                Commands.allChannels["All Channels"][channel.channelName].allUsers[user.socket] = user
                serverMessage = "> " + user.name + " has joined channel " + user.currentChannel.channelName + ".\n"
                self.broadcast_channel(serverMessage, user)
            else:
                if user.currentChannel != Commands.allChannels["All Channels"][channel.channelName]:
                    self.switch(user, channel.channelName)

    # Create Channel function
    def create(self, user, channelName):
        isPrivate = False
        channelPassword = None
        channel = None
        user.socket.send("> Would you like to make this channel private?\n".encode('utf8'))
        answer = user.socket.recv(user.size).decode('utf8')
        answer = answer.lower()
        if answer[0] == 'y':
            isPrivate = True
            channel = self.createChannel(channelName, Commands.allChannels, user, isPrivate)
            self.joinPrivate(channel, user)
            return channel
        else:
            channel = self.createChannel(channelName, Commands.allChannels, user, isPrivate)
            self.joinPublic(channel, user)
            return channel

    def relay(self, user, listOfArgs):
        if len(listOfArgs) > 0:
            message = " ".join(listOfArgs)
            user.socket.send((message + "\n").encode('utf8'))
        else:
            user.socket.send("> You did not provide a message.\n".encode('utf8'))

    # Broadcast message to channel
    def broadcast_channel(self, message, user):
        channelObject = user.currentChannel

        # Gets channel user is in
        for users in channelObject.allUsers.values():
            users.socket.send((message + "\n").encode('utf8'))

    # Braodcast whole server
    def broadcast_all(self, user, message):
        for key, value in self.allUsers.items():
            if value == user:
                user.socket.send(("You: " + message + "\n").encode('utf8'))
            else:
                key.socket.send((user.name + ": " + message + "\n").encode('utf8'))

    # Validates if channel exists
    def doesChannelExist(self, channelName):
        returnValue = False
        channels = Commands.allChannels["All Channels"]
        for key, value in channels.items():
            if key == channelName:
                returnValue = True

        return returnValue

    # Logs to file
    def log(self, user, message):
        filepath = Path("Client_Server/logs/messages.txt").resolve()
        with open(filepath, 'a') as out:
            out.write(user.currentChannel.channelName + " " + user.name + ": " +message + "\n")

    # File of all users
    def newUser(self, user):
        userPassword = user.password
        isBan = False
        if user.name in self.bannedusers.keys():
            isBan = True
        channels = self.allChannels.values()
        privilege = ""
        for channel in channels:
            if user in channel.ChannelOP:
                privilege = "Channel OP"
        if user.isAdmin:
            privilege = "Admin"
        elif user.isSysOP:
            privilege = "SysOP"
        elif len(privilege) != 0:
            privilege = "Channel OP"
        else:
            privilege = "User"
        if len(userPassword.strip()) == 0:
            userPassword = "@"
        filepath = Path("Client_Server/db/users.txt").resolve()
        with open(filepath, 'a') as out:
            out.write(user.name + " " + userPassword + " " + privilege + " " + str(isBan) +"\n")

    # File of all channels
    def newChannel(self, channel):
        ChannelOP = []
        channelPassword = "@"
        channelTopic = ""
        listOfOPs = ""
        if len(channel.ChannelOP) > 0:
            for user in channel.ChannelOP:
                ChannelOP.append(user.name)
        else:
            for user in self.allUsers.values():
                if user.isSysOP:
                    ChannelOP.append(user.name)
        if channel.isPrivate:
            channelPassword = channel.channelPassword
        for x in range(0, len(ChannelOP)):
            if x == 0:
                if len(ChannelOP) == 1:
                    listOfOPs += "[" + ChannelOP[x] + "]"
                else:
                    listOfOPs += "[" + ChannelOP[x] + ", "
            elif x == len(ChannelOP) -1 :
                listOfOPs += ChannelOP[x] + "]"
            else:
                listOfOPs +=ChannelOP[x] + ", "
        channelTopic = channel.channelTopic
        filepath = Path("Client_Server/db/channels.txt").resolve()
        with open(filepath, 'a') as out:
            out.write(channel.channelName + " " + channelTopic + " " + channelPassword + " " + listOfOPs + '\n')

    # Add user to existing channel
    def newUserOldChannel(self, user, channelName):
        filepath = Path("Client_Server/db/channels.txt").resolve()
        with open(filepath) as file_handle:
            data = file_handle.readlines()

        for x in range(0, len(data)):
            if channelName in data[x]:
                count = x
                newList = data[x].split()
                for line in newList:
                    if ']' in line:
                        line.replace(']', '')
                        line += user.name + "]"
                data[x] = " ".join(newList)

    # Action to ban users and log
    def banUser(self, user, name):
        returnUser = self.returnUser(name)
        filepath = Path("Client_Server/db/banusers.txt").resolve()
        if returnUser is not None:
            with open(filepath, 'a') as out:
                out.write(name + " " + returnUser.address[0] + "\n")
            returnUser.socket.disconnect()
        else:
            user.socket.send("> The given user name does not exist.\n")

    # Function to load ban users
    def loadBanUser(self):
        filepath = Path("Client_Server/db/banusers.txt").resolve()
        with open(filepath) as file_handle:
            for line in file_handle:
                newLine = line.split(" ")
                self.bannedusers[newLine[0]] = newLine[1]

    async def ser_obj(self):
        channels = Commands.allChannels["All Channels"]
        ser_channels = {}
        for key, value in channels.items():
            list = []
            users = value.allUsers.values()
            for name in users:
                list.append(name.name)
            if value.isPrivate is False:
                ser_channels["+" + key] = list
            else:
                ser_channels["-" + key] = list
        sync = json.dumps(ser_channels).encode('utf8')
        await asyncio.sleep(0.05)
        return sync

    async def ser_chan_messages_(self):
        channels = Commands.allChannels["All Channels"]
        ser_channels = {}
        for key, value in channels.items():
            list_messages = value.messages
            ser_channels[key] = list_messages
        sync = json.dumps(ser_channels).encode('utf8')
        await asyncio.sleep(0.05)
        return sync

    def serialize_messages(self):
        loop = asyncio.new_event_loop()
        done = loop.run_until_complete(self.ser_chan_messages_())
        sync = "~%m%e%s%s%a%g%e%s%~".encode('utf8') + done
        loop.close()
        return sync

    def serialize_channels(self):
        loop = asyncio.new_event_loop()
        done = loop.run_until_complete(self.ser_obj())
        sync = "~%c%h%a%n%n%e%l%s%~".encode('utf8') + done
        loop.close()
        return sync

    def refresh(self):
        users = Commands.allUsers.keys()
        channels = self.serialize_channels()
        for user in users:
            user.socket.send(channels)

    def refresh_messages(self):
        users = Commands.allUsers.keys()
        messages = self.serialize_messages()
        for user in users:
            user.socket.send(messages)

    def start(self, user):
        self.newUser(user)
        self.loadBanUser()
        isBan = False
        for key, value in self.bannedusers.items():
            if key == user.name or value == user.address[0]:
                isBan = True
        if isBan is True:
            user.socket.send("> You are ban form this server.".encode('utf8'))
            user.socket.disconnect()
        else:
            while True:
                if user.socket.fileno() != -1:
                    self.refresh()
                    #self.refresh_messages()
                    chatMessage = user.socket.recv(user.size).decode('utf8')
                    args = chatMessage.split(" ")

                    # Accepts case insensitive
                    headofargs = list(args[0])
                    headofargs = headofargs[1:]
                    arg1 = '/' + ''.join(headofargs).lower()
                    listofargs = args[1:]

                    if arg1 == '/quit':
                        print("User " + user.name + ", has disconnected.\n" + user.address[0] + " " + str(user.address[1]))
                        break
                    elif arg1 == '/users':
                        self.list_all_users(user)
                    elif arg1 == '/help':
                        self.help(user)
                    elif arg1 == '/nick':
                        userobject = self.nick(user, listofargs)
                        Commands.allUsers[userobject] = userobject.name
                    elif arg1 == '/privmsg':
                        self.private_message(user, listofargs)
                    elif arg1 == '/away':
                        self.away(user, listofargs)
                    elif arg1 == '/invite':
                        self.invite(user, listofargs)
                    elif arg1 == '/restart':
                        self.restart(user)
                    elif arg1 == '/join':
                        self.joinChannel(user, listofargs)
                    elif arg1 == '/kick':
                        self.kickFromChannel(user, listofargs)
                    elif arg1 == '/userip':
                        self.userip(listofargs, user)
                    elif arg1 == '/setname':
                        self.setname(user)
                    elif arg1 == '/list':
                        self.list(user)
                    elif arg1 == '/promote':
                        self.promote(user, listofargs)
                    elif arg1 == '/topic':
                        self.topic(user, listofargs)
                    elif arg1 == '/who':
                        self.who(user, listofargs)
                    elif arg1 == '/whois':
                        self.whois(user, listofargs)
                    elif arg1 == '/time':
                        self.time(user)
                    elif arg1 == '/switch':
                        self.switch(user, listofargs)
                    elif arg1 == '/operwall':
                        self.operWall(user, listofargs)
                    elif arg1 == '/user':
                        self.usercommand(user, listofargs)
                    elif arg1 == '/ping':
                        self.ping(user)
                    elif arg1 == '/pong':
                        self.pong(user)
                    elif arg1 == '/rules':
                        self.rules(user)
                    elif arg1 == '/userhost':
                        self.userhost(user, listofargs)
                    elif arg1 == '/kill':
                        self.kill(user, listofargs)
                    elif arg1 == '/version':
                        self.version(user)
                    elif arg1 == '/notice':
                        self.notice(user, listofargs)
                    elif arg1 == '/knock':
                        self.knock(user, listofargs)
                    elif arg1 == '/die':
                        self.die(user)
                    elif arg1 == '/ison':
                        self.ison(user, listofargs)
                    elif arg1 == '/info':
                        self.info(user)
                    elif arg1 == '/part':
                        self.part(user, listofargs)
                    elif arg1 == '/wallops':
                        self.wallops(user, listofargs)
                    elif arg1 == '/silence':
                        self.silence(user, listofargs)
                    elif arg1 == '/relaytouser':
                        self.relay(user, listofargs)
                    # not done yet
                    elif arg1 == '/channelmodes':
                        self.channelModes(user)
                    elif arg1 == '/mode':
                        self.mode(user)
                    elif arg1 == '/oper':
                        self.oper(user)
                    elif arg1 == '/pass':
                        self.passcommand(user)
                    else:
                        self.broadcast_message(chatMessage + '\n', user)
                        self.log(user, chatMessage)

                else:
                    break
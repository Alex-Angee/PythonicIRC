***********************************************************************************************
WELCOME TO THE CHATAPP!!!
***********************************************************************************************
IMPORTANT INFORMATION ABOUT THE ASSIGNMENT:

- Commands that are missing:
			  CONNECT
			  MODE
			  PASS
                        OPER

- I did not create a test file.

- I did not finish parsing the command line for Main.py and did not finish the config file for that
as well.
 
- The ChatServer.py is parsed on the command line and the config file is set for it located in "./Client_Server/config/chatserver.conf".

- When starting up a new connection, you will be asked for a nickname(everything is allowed except spaces and commas), then enter your Real name(First and Last), then enter your server name(localhost). 
Your user information will now be stored in the "./Client_Server/db/users.txt".

- After registering, you will be able to join a channel. You may create a new channel or
view a list of open channels. When creating a new channel, you will be asked to set
the topic and if you would like to set a password(Enter Y or N), after completion the channel will be 
logged in the channels.txt file located in the "db" folder inside of the "clientserver" folder. Once joining or creating a channel,
you can type /help to see all of the available commands and you are ready to start 
chatting with your friends!

- Messages broadcasted to all channel users, as well as private messages and notice messages will
be logged in the "./Client_Server/logs/messages.txt".

- For this assignment, I implemented a way for the users to join multiple channels, speak to one at a time, and send private messages/notice to one or many users.

- You will find the list of implemented commands at the bottom of the file and how to run them in Main.py.

***********************************************************************************************
How to Run the Application:
	- Open the terminal and Navigate to the folder in which the python files are found.
	- The Chat Server usage includes
		-p or --port Port Number where the chat server will run. Default is found
		 in configuration file (-port 10500)
		-c or --config config file path
		–d or --db user file path
	- The locations for configurations for the chat server are located at "./Client_Server/config/chatserver.conf"
	- Start the server by running the command 
	  python ChatServer.py --port 8500 -c --db
	  which specifies a port number of 8500, and with the option commands -s and --db it prints the path to the chatserver.conf and "./db/".
	- Start a new connection by running 
	  python Main.py
	- Click connect at the top and type in localhost and 8500 in the host and port fields.

***********************************************************************************************
Rules of the Server:
	1) Be respectful to others.
    2) No foul language.
    3) I'm better than Dr. Ortega @ Fifa.

***********************************************************************************************
The list of commands implemented are:

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
/whois - <user> Returns the real name for the nickname provided

***********************************************************************************************

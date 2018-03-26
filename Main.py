import tkinter as tk
from tkinter import messagebox
import ChatClient as client
import BaseDialog as dialog
import BaseEntry as entry
import threading
from tkinter import END

class SocketThreadedTask(threading.Thread):
    def __init__(self, socket, callback):
        threading.Thread.__init__(self)
        self.socket = socket
        self.callback = callback
        self.allChannels = None
        self.privateChannels = {}
        self.publicChannels = {}
        self.channelMessages = {}

    def run(self):
        channels = None
        messages = None
        while True:
            try:
                message = self.socket.receive()
                if message[0] == "channels":
                    self.allChannels = message[1]
                    for key, value in self.allChannels.items():
                        if key[0] == '+':
                            oldKey = key
                            newKey = key[1:]
                            self.allChannels[newKey] = value
                            del self.allChannels[oldKey]
                            self.publicChannels[key] = value
                        elif key[0] == '-':
                            oldKey = key
                            newKey = key[1:]
                            self.allChannels[newKey] = value
                            del self.allChannels[oldKey]
                            self.privateChannels[key] = value
                    message = message[0]
                    self.callback(None, self.allChannels, None)
                elif message[0] == "messages":
                    self.channelMessages = messages = message[1]
                    message = message[0]
                    self.callback(message, None, messages)
                else:
                    message = message[0]
                    self.callback(message, None, None)
                if message == '/quit':
                    self.callback('> You have been disconnected from the chat room.')
                    self.socket.disconnect()
                    break
            except OSError:
                break

class ChatDialog(dialog.BaseDialog):
    def body(self, master):
        tk.Label(master, text="Enter host:").grid(row=0, sticky="w")
        tk.Label(master, text="Enter port:").grid(row=1, sticky="w")

        self.hostEntryField = tk.Entry(master)
        self.portEntryField = tk.Entry(master)

        self.hostEntryField.grid(row=0, column=1)
        self.portEntryField.grid(row=1, column=1)
        return self.hostEntryField

    def validate(self):
        host = str(self.hostEntryField.get())

        try:
            port = int(self.portEntryField.get())

            if(port >= 0 and port < 65536):
                self.result = (host, port)
                return True
            else:
                tk.messagebox.showwarning("Error", "The port number has to be between 0 and 65535. Both values are inclusive.")
                return False
        except ValueError:
            tk.messagebox.showwarning("Error", "The port number has to be an integer.")
            return False

class ChatWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.initUI(parent)

    def initUI(self, parent):
        self.messageScrollbar = tk.Scrollbar(parent, orient=tk.VERTICAL)
        self.messageScrollbar.grid(row=0, column=3, sticky="ns")

        self.messageTextArea = tk.Text(parent, bg="white", state=tk.DISABLED, yscrollcommand=self.messageScrollbar.set, wrap=tk.WORD)
        self.messageTextArea.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # list of users
        self.usersListBox = tk.Listbox(parent, bg="white")
        self.usersListBox.grid(row=0, column=4, padx=5, sticky="nsew")

        self.entryField = entry.BaseEntry(parent, placeholder="Enter message.", width=80)
        self.entryField.grid(row=1, column=0, padx=5, pady=10, sticky="we")

        self.send_message_button = tk.Button(parent, text="Send", width=10, bg="#CACACA", activebackground="#CACACA")
        self.send_message_button.grid(row=1, column=1, padx=5, sticky="we")

    def update_window(self, message, channels, messages):
        if (message is None) and (messages is None):
            self.refresh_users(channels)
        elif (channels is None) and (message is None):
            self.refresh_messages(messages)
        elif (channels is None) and (messages is None):
            self.update_chat_window(message)

    def refresh_messages(self, messages):
        for key, value in messages.items():
            for message in value:
                print(message)

    def refresh_users(self, channels={}):
        self.usersListBox.delete(0, END)
        if bool(channels) is True:
            count = 2
            for key, value in channels.items():
                self.usersListBox.insert(count, key)
                for users in value:
                    self.usersListBox.insert(count, ("\t" + users))
                    count += 1
                count += 1
        else:
            self.usersListBox.insert(0, " ")

    def switch(self, event, **callbacks):
        widget = event.widget
        selection = widget.curselection()
        value = widget.get(selection[0])
        if "\t" in value:
            message = "/relayToUser This is a user."
            callbacks['send_message_to_server'](message)
        else:
            switch = "/switch " + value
            self.messageTextArea.configure(state='normal')
            self.messageTextArea.delete(1.0, END)
            self.messageTextArea.configure(state='disabled')
            callbacks['send_message_to_server'](switch)

    def update_chat_window(self, message):
        self.messageTextArea.configure(state='normal')
        self.messageTextArea.insert(tk.END, message)
        self.messageTextArea.configure(state='disabled')

    def send_message(self, **callbacks):
        message = self.entryField.get()
        self.set_message("")

        callbacks['send_message_to_server'](message)

    def set_message(self, message):
        self.entryField.delete(0, tk.END)
        self.entryField.insert(0, message)

    def bind_widgets(self, callback):
        self.send_message_button['command'] = lambda sendCallback = callback : self.send_message(send_message_to_server=sendCallback)
        self.usersListBox.bind("<<ListboxSelect>>", lambda event, sendCallback = callback : self.switch(event, send_message_to_server=sendCallback))
        self.entryField.bind("<Return>", lambda event, sendCallback = callback : self.send_message(send_message_to_server=sendCallback))
        self.messageTextArea.bind("<1>", lambda event: self.messageTextArea.focus_set())

class ChatGUI(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.initUI(parent)

        self.ChatWindow = ChatWindow(self.parent)

        self.clientSocket = client.Client()

        self.ChatWindow.bind_widgets(self.clientSocket.send)
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

    def initUI(self, parent):
        self.parent = parent
        self.parent.title("ChatApp")

        screenSizeX = self.parent.winfo_screenwidth()
        screenSizeY = self.parent.winfo_screenheight()

        frameSizeX = 800
        frameSizeY = 600

        framePosX = (screenSizeX - frameSizeX) / 2
        framePosY = (screenSizeY - frameSizeY) / 2

        self.parent.geometry('%dx%d+%d+%d' % (frameSizeX, frameSizeY, framePosX, framePosY))
        self.parent.resizable(True, True)

        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)

        self.mainMenu = tk.Menu(self.parent)
        self.parent.config(menu=self.mainMenu)

        self.subMenu = tk.Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label='File', menu=self.subMenu)
        self.subMenu.add_command(label='Connect', command=self.connect_to_server)
        self.subMenu.add_command(label='Exit', command=self.on_closing)

    def connect_to_server(self):
        if self.clientSocket.isClientConnected:
            return

        dialogResult = ChatDialog(self.parent).result

        if dialogResult:
            self.clientSocket.connect(dialogResult[0], dialogResult[1])

            if self.clientSocket.isClientConnected:
                SocketThreadedTask(self.clientSocket, self.ChatWindow.update_window).start()
            else:
                tk.messagebox.showwarning("Error", "Unable to connect to the server.")

    def on_closing(self):
        if self.clientSocket.isClientConnected:
            self.clientSocket.send('/quit')

        self.parent.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    chatGUI = ChatGUI(root)
    root.mainloop()

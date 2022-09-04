import threading
import simpleaudio
from requests import get
from bs4 import BeautifulSoup
from datetime import datetime
import json
from time import sleep


class Config:
    def __init__(self):
        self.players = []
        self.servers = []
        self.interval = 60

    #Prompts user to add values to config and creates config.json file with those values
    def initialize(self):
        create_config()
        self.add_player()
        self.add_server()
        update_config(self.__dict__)

    #reinitialize all values for config file
    def start_new(self):
        warning = input("This will erase your previous config file, are you sure? 'y' to continue.")
        if not (warning == 'y'):
            return
        self.players = []
        self.servers = []
        self.add_player()
        self.add_server()

    #loads config.json values / Initializes a config.json file if one is not found
    def load_config(self):
        try:
            playerlist_file = open('config.json', 'r')
        except FileNotFoundError:
            print ("No config.json file found.")
            self.initialize()
        except Exception:
            print ("Other error occurred.")
        else:
            json_file = json.load(playerlist_file)
            self.players = json_file["players"]
            self.servers = json_file["servers"]
            playerlist_file.close()

    #remove specified player from checking list in config
    def delete_player(self):
        while True:
            del_player = input("Enter player name (case sensitive) enter 'x' when finished:    ")
            if (del_player == "x"):
                break
            if (del_player in self.players):
                self.players.remove(del_player)
            else:
                print ("Player is not in list")
        update_config(self.__dict__)

    #prints config values to console
    def print_values(self):
        print (f"Number of Servers checking:  {len(self.servers)}")
        print (f"Checking on Server IP: {self.servers} \n")
        print(f"Number of Players checking: {len(self.players)}")
        print (f"Checking for players: {self.players} \n")

    #append new players to players list
    def add_player(self):
        while True:
            new_player = input("Enter player name (enter 'x' when finished):    ")
            if (new_player == "x"):
                break
            self.players.append(new_player)
        update_config(self.__dict__)

    #change server ip to be checked
    def add_server(self):
        while True:
            new_server = input("Enter Server IP (enter 'x' when finished):   ")
            if (new_server == "x"):
                break
            if (server_is_valid(new_server)):
                self.servers.append(new_server)
                update_config(self.__dict__)

    #delete specified player from checking list in config
    def delete_server(self):
        while True:
            del_server = input("Enter server name (case sensitive) enter 'x' when finished:    ")
            if (del_server == "x"):
                break
            if (del_server in self.servers):
                self.servers.remove(del_server)
            else:
                print ("Server is not in list")
        update_config(self.__dict__)

    #change interval between each GET request
    def change_interval(self):
        while True:
            try:
                self.interval = int(input("Enter an interval in seconds between each fetch (must be at least 30 with no decimals:   "))
                if (self.interval < 30): raise ValueError
            except ValueError:
                print ("Input Error")
            else:
                break

#Prints help manual to console
def print_manual():
    manual = open('help.txt', 'r')
    print (manual.read())
    manual.close()

#create config.json file / no return variable
def create_config():
    print("Creating new config.json file.")
    new_file = open('config.json', 'x')
    new_file.close()

#update config.json file / takes dictionary argument from Config object instance
def update_config(dict_object):
    new_file = open('config.json', 'w')
    json_object = json.dumps(dict_object, indent=2)
    new_file.write(json_object)
    new_file.close()

#Returns InnerHTML string of given HTML elements/class
def get_innerHTML(element):
    return element.string

#checks validity of server IP / returns False if HTTP error code given or if blank
def server_is_valid(server):
    if (server == ""):
        print ("No Server IP given")
        return False
    try:
        get("https://minecraftlist.com/servers/" + server).ok
    except Exception:
        print ("Invalid server")
        return False
    else:
        return True

#update time interval between each refresh (not in use, troubleshoot)
# def refresh_interval(string, server):
#     global interval_dict
#     if any(character.isdigit() for character in string):
#         string = string.replace("We last checked this server ", "")
#         string = string.replace(" minutes ago.", "")
#         interval_dict[server] = 920 - (int(string) * 60)
#     else:
#         interval_dict[server] = 0

#return list object with currently online players / makes GET request to URL
def get_online_list(server):
    if not (server_is_valid(server)): #Return None if HTTP response code is not valid
        print ("Error making HTTP request.")
        return None
    new_request = get("https://minecraftlist.com/servers/" + server)
    html_doc = BeautifulSoup(new_request.text, "html.parser")
    player_elements = html_doc.find_all("a", class_="block no-underline hover:bg-gray-200 px-2 py-1 flex items-center text-gray-800")
    #last_checked = html_doc.find("p", class_="text-center text-gray-500").text
    player_list = []
    for each_element in player_elements:
        player = each_element.find("span", class_="truncate")
        player_list.append(player)
    online_list = list(map(get_innerHTML, player_list))
    return online_list

#quick command function that displays to users all online players in config servers
def check_online_list():
    for each_server in config.servers:
        online_list = get_online_list(each_server)
        sleep(2)
        if (online_list == None):
            return
        elif (len(online_list) == 0):
            print (f"Nobody is online on Server: {each_server}")
        else:
            for each_player in online_list:
                print(f"> {each_player} seen online at {datetime.now().strftime('%D  %H:%M:%S')} on Server: {each_server}")

#play notification sound for login
def sound_login():
    audio_object = simpleaudio.WaveObject.from_wave_file("./login.wav")
    play_attempts = 0
    while True:
        try:
            play_attempts += 1
            play = audio_object.play()
            play.wait_done()
        except Exception:
            if (play_attempts == 3):
                print ("Error with playing notification audio.")
                break
            else:
                sleep(1)
        else:
            break

#play notification sound for logout
def sound_logout():
    audio_object = simpleaudio.WaveObject.from_wave_file("./logoff.wav")
    play_attempts = 0
    while True:
        try:
            play_attempts += 1
            play = audio_object.play()
            play.wait_done()
        except Exception:
            if (play_attempts == 3):
                print ("Error with playing notification audio.")
                break
            else:
                sleep(1)
        else:
            break

#checks for newly joined players and players who have logged
def checker():
    global currently_online_list
    for server in config.servers:
        online_list = get_online_list(server)
        if (not online_list or online_list == None):
            for each_player in currently_online_list[server]:
                print(f"> {each_player} logged off at {datetime.now().strftime('%D  %H:%M:%S')} on Server: {server}")
                currently_online_list[server].remove(each_player)
                sound_logout()
            return
        found_list = list(set(config.players).intersection(online_list))
        for each_player in found_list:
            if (each_player not in currently_online_list[server]):
                print(f"> {each_player} seen online at {datetime.now().strftime('%D  %H:%M:%S')} on Server: {server}")
                currently_online_list[server].append(each_player)
                sound_login()
        for each_player in currently_online_list[server]:
            if (each_player not in online_list):
                print (f"> {each_player} logged off at {datetime.now().strftime('%D  %H:%M:%S')} on Server: {server}")
                currently_online_list[server].remove(each_player)
                sound_logout()

#iterative function, continues if user has not stopped
def looper():
    global continue_condition
    global interval_dict
    while continue_condition:
        config.load_config()
        checker()
        for timer in range (config.interval):
            if continue_condition:
                sleep(1)
            else:
                break

#start application
def start():
    if (threading.active_count() > 1):
        print("Checker already running. \n")
        return
    print ("Starting checker \n")
    global continue_condition
    continue_condition = True
    process = threading.Thread(target=looper)
    process.start()

#stop application
def stop():
    if (threading.active_count() == 1):
        print ("Checker not running.\n")
        return
    print ("Stopping checker.\n")
    global continue_condition
    global currently_online_list
    continue_condition = False
    currently_online_list = []

def main():
    command_dict = {"addplayer": config.add_player,
                    "delplayer": config.delete_player,
                    "addserver": config.add_server,
                    "delserver": config.delete_server,
                    "onlinenow": check_online_list,
                    "checkconfig": config.print_values,
                    "fresh": config.start_new,
                    "start": start,
                    "stop": stop,
                    "help": print_manual}

    while True:
        print ("-------------------------")
        user_input = input()
        print ("-------------------------")
        if (user_input in command_dict.keys()):
            command_dict[user_input]()
        elif (user_input == "exit"):
            stop()
            print("Program exiting.")
            break
        elif (user_input == ""):
            print ("")
        else:
            print ("Unknown command.")

if __name__ == '__main__':
    print ("Welcome to the Minecraft Java Edition Playerlist Pinger. Type 'help' to see list of commands.\n-------------------------------------------")
    global continue_condition
    global currently_online_list
    global interval_dict
    config = Config()
    config.load_config()
    config.print_values()
    currently_online_list = dict()
    interval_dict = dict()
    for each_server in config.servers:
        currently_online_list[each_server] = []
        interval_dict[each_server] = 0
    main()

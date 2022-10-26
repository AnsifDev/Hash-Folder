from ast import While
import os
import sys
from numpy import False_

import pexpect

aptInit = """type -p curl >/dev/null || sudo apt install curl -y
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
&& sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update \
&& sudo apt install gh -y"""

def init():
    if os.system("git --version") != 0:
        print("==========Installing git==========")
        os.system("sudo apt update")
        os.system("sudo apt-get install git")
    
    if os.system("gh --version") != 0:
        print("==========Installing gh==========")
        os.system("sudo apt update")
        if os.system("sudo apt-get install gh") != 0: os.system(aptInit)
    print()

def is_valid_filename(filename):
    for letter in filename:
        if letter not in "-abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789.": return False
    return True

def generateSSH():
    if sys.argv[1] == "ssh-keygen":
        if len(sys.argv) > 2: filename = os.path.expanduser(sys.argv[2])
        else: filename = input("Enter a filename for the key (min length is 5): ")

        if (len(filename) < 5): print("Error: File name must have a length of minimum 5!!!")
        elif "/" in filename: print("Error: Only file name is allowed not path!!!")
        elif not is_valid_filename(filename): print("Error: Not a valid filename!!!")
        else:
            keyname = input("Enter a key name: ")
            os.system("ssh-keygen -t ed25519 -C \""+keyname+"\" -f "+filename)
            return
        
        exit(1)
        

    while True:
        filename = input("Enter a filename for the key (min length is 5): ")
        if (len(filename) < 5): print("Error: File name must have a length of minimum 5!!!\n")
        elif "/" in filename: print("Error: Only file name is allowed not path!!!\n")
        elif not is_valid_filename(filename): print("Error: Not a valid filename!!!\n")
        else: break
    
    keyname = input("Enter a key name: ")
    os.system("ssh-keygen -t ed25519 -C \""+keyname+"\" -f "+filename)
    

def help():
    print("\nclone\t\tTo clone a repo\n\t\tpython3 git-client.py clone <repo> [<destination>]")
    print("ch-port-config\tTo set port configuration for github to 443")
    print("rm-port-config\tTo undo port configuration")
    print("ssh-keygen\tTo create ssh key for ssh connections\n\t\tpython3 git-client.py ssh-keygen <filename>")
    
def main():
    argLen = len(sys.argv)

    if argLen < 2:
        print("Invalid syntax:")
        help()
        exit(1)

    cmd = sys.argv[1]

    if cmd == "--help": help()
    elif cmd == "clone":
        print("Log: In")
        init()
        
        if argLen < 3: 
            print("Invalid syntax:")
            help()
            exit(1)
        
        userIn = input("Do you want to generate new ssh key? (y/n): ")
        if userIn in ["y", "Y"]: generateSSH()

        os.system("gh auth login")
        name = input("Enter github username: ")
        email = input("Enter the github email id: ")

        repo = sys.argv[2]
        if argLen > 3: repo_dir = os.path.abspath(os.path.expanduser(sys.argv[3]))
        os.system("gh repo clone "+repo+" \""+repo_dir+"\"")
        os.chdir(repo_dir)
        os.system("git config user.name "+name)
        os.system("git config user.email "+email)
        print("\nGit repo clone sucessfull")
    elif cmd == "ssh-keygen": generateSSH()
    elif cmd == "ch-port-config": ch_port()
    elif cmd == "rm-port-config": rm_port()
    else: 
        print("Invalid syntax:")
        help()
        exit(1)

def getConfigs() -> dict:
    configStrCodes = []
    
    #Retriving line based array from config string
    if os.path.exists(os.path.expanduser("~/.ssh/config")):
        file = open(os.path.expanduser("~/.ssh/config"), "r")
        configStrCodes = file.readlines()
        file.close()
    else: print("Log: File not exists")

    #Removing unwanted spaces and empty lines
    i = 0
    while i < len(configStrCodes):
        configStrCodes[i] = configStrCodes[i].strip() #Space removal
        if configStrCodes[i] == "": configStrCodes.pop(i) #Empty line removal
        else: i += 1

    #Grouping configurations
    groups = []
    group = {}
    for line in configStrCodes:
        key = ""
        for character in line:
            if character == " " and key != "":
                value = str(line).replace(key, "").strip()
                if key.strip() == "Host" and len(group) != 0:
                    groups.append(group)
                    group = {}
                if value != "": group[key] = value
                break
            else: key = key + character
    if len(group) != 0: groups.append(group)
    
    #Building configuration dict
    configs = {}
    for group in groups:
        configId = group.pop("Host")
        if "Host" in group:
            print("found")
            group.pop("Host")
        configs[configId] = dict(group).copy()

    return configs

def saveConfig(configs):
    String = ""
    for Host in configs:
        String = String+"Host "+Host+"\n"
        for Label in configs[Host]:
            String = String+"\t"+Label+" "+configs[Host][Label]+"\n"
        String = String+"\n"
    
    file = open(os.path.expanduser("~/.ssh/config"), "w")
    file.write(String.strip())
    file.close()

def ch_port():
    configurations = getConfigs()

    if "github.com" in configurations: configurations["github.com"].update([("HostName", "ssh.github.com"), ("Port", "443")])
    else: configurations["github.com"] = {
        "HostName": "ssh.github.com",
        "Port": "443"
    }

    saveConfig(configurations)

def rm_port():
    configurations = getConfigs()
    if "github.com" in configurations:
        if "Port" in configurations["github.com"]:
            configurations["github.com"].pop("Port")
            configurations["github.com"].pop("HostName")
        if len(configurations["github.com"]) == 0: configurations.pop("github.com")

    saveConfig(configurations)

main()
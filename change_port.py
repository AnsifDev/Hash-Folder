import os
import sys

def getConfigs() -> dict:
    configStrCodes = []
    
    #Retriving line based array from config string
    if os.path.exists(os.path.expanduser("~/.ssh/config")):
        print("Log: File exists")
        

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

def main():
    configurations = getConfigs()

    removeOk = False
    if len(sys.argv) > 1:
        if sys.argv[1] == "-r": removeOk = True
    
    if removeOk:
        if "github.com" in configurations:
            configurations["github.com"].pop("Port")
            configurations["github.com"]["HostName"] = "github.com"
    else:
        if "github.com" in configurations: configurations["github.com"].update([("HostName", "ssh.github.com"), ("Port", "443")])
        else: configurations["github.com"] = {
            "HostName": "ssh.github.com",
            "Port": "443"
        }
        

    saveConfig(configurations)

main()
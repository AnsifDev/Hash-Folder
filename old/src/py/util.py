from .portConfig import getConfigs, saveConfig

def parse_yml_file(filename):
    file = open(filename)
    lines = file.readlines()
    file.close()
    
    dictData = {}
    prevTabs = 0
    stack = [dictData]
    stackTop = 0
    for line in lines:
        if len(line.strip()) == 0: continue

        tabs = 0
        for character in line:
            if (character != "\t"): break
            tabs += 1
        
        diff = prevTabs - tabs
        if diff > 1 or diff < -1: print("Err in yml script")

        result = line.strip().split(':')
        key = result[0].strip()
        if len(result) > 1: value = result[1].strip()
        else: value = ""

        if prevTabs > tabs:
            stackTop -= prevTabs-tabs
        
        if value == "":
            value = {}
            stack[stackTop][key] = value
            stackTop += 1
            stack.append(value)
        else: stack[stackTop][key] = value

        prevTabs = tabs
        
    return dictData

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

# class A:
#     pass

# class B:
#     pass

# inp = input(">>")
# class C(A if inp == "A" else B):
#     pass

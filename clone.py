from subprocess import PIPE
import os
import subprocess
import apt

import pexpect

aptInit = """type -p curl >/dev/null || sudo apt install curl -y
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
&& sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update \
&& sudo apt install gh -y"""


def test():
    #process = subprocess.Popen("ssh-keygen -t ed25519 -C \"Test\"", stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)

    analyzer = pexpect.spawn("ssh-keygen -t ed25519 -C \"Test\"", encoding='utf-8')
    analyzer.expect(":")
    print(analyzer.before)
    analyzer.send("testKey\n")
    ex = analyzer.expect([":", "(y/n)"])
    print(ex)
    if ex == 1:
        analyzer.send("y\n")
        analyzer.expect(":")
    analyzer.send("shamsu123\n")
    analyzer.expect(":")
    analyzer.send("shamsu123\n")
    analyzer.wait()

def main():
    print("==========Initializing==========")
    if os.system("git --version") != 0:
        print("==========Installing git==========")
        os.system("sudo apt update")
        os.system("sudo apt-get install git")
    
    if os.system("gh --version") != 0:
        print("==========Installing gh==========")
        os.system("sudo apt update")
        if os.system("sudo apt-get install gh") != 0: os.system(aptInit)
    print("================================")

    ssh_init()

    if os.system("gh auth status") != 0:
        if os.system("gh auth login") != 0: return
        print("====== Login complete ======")
    
    repo = input("\n>> gh repo clone ")
    chdir(os.path.dirname(os.getcwd()))
    os.system("gh repo clone "+repo)

def getPassPhrase():
    password1 = input("Enter pass phrase (Empty for no pass phrase): ")
    if password1 == "": return password1
    password2 = input("Confirm pass phrase: ")
    if password1 == password2: return password1
    print("Pass pharse mismatched!!!")
    return getPassPhrase()

def generateSSH(fileName, KeyName):
    password = getPassPhrase()
    analyzer = pexpect.spawn("ssh-keygen -t ed25519 -C \""+KeyName+"\"", encoding='utf-8')
    analyzer.send(os.path.expanduser("~/.ssh/"+fileName)+"\n")
    analyzer.send(password+"\n")
    if password != "": analyzer.send(password+"\n")
    exitCode = analyzer.wait()
    if exitCode != 0: print("Log: SSH Key Generation Failed\n    ExitCode: "+exitCode)

def ssh_init():
    option = input("Do you want to create new SSH Key (y/Y): ")
    fileName = ""
    if not option in ["y", "Y"]: return
        
    while True:
        fileName = input("Enter the SSH File Name (min length 5): ")
        if len(fileName) < 5: print("Bad SSH File Name!!!")
        elif "/" in fileName: print("No / symbol allowed")
        elif "~" in fileName: print("No ~ symbol allowed")
        else:
            generateSSH(fileName, input("Enter the key name: ")) 
            return
        if fileName == "": return ssh_init()
        elif os.path.exists(os.path.expanduser("~/.ssh/"+fileName)):
            print("File Name not available!!!")
            fileName = ""
        
main()

import os
from gi.repository import Adw
from gi.repository import Gtk
from .LoginPage import LoginPage
from .HomePage import HomePage
from ..util import parse_yml_file, ExtTerminal

cmds="""#!/bin/bash
type -p curl >/dev/null || (sudo apt update && sudo apt install curl -y)
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh -y
"""

@Gtk.Template(filename='ui/gtk4app_window.ui')
class AppWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'AppWindow'

    base_connector = Gtk.Template.Child()
    logout = Gtk.Template.Child()

    def getBuilderForBase(self, name):
        return Gtk.Builder.new_from_resource('/hashtag/linux/linuxapp1/'+name+'.ui')

    def on_dialog_response(self, widget, response):
        if response == "cancel": self.close()
        elif response == "login": 
            self.connect_login_page()
            os.system("gh auth logout -h github.com")
        elif response == "install":
            self.open_install_app_file()
            filename = self.cache_location+"app-install"
            self.install_task.run("bash "+filename, False, self.on_terminal_task_performed)
        
    def on_terminal_task_performed(self, widget, response, userdata):
        if widget == self.install_task:
            self.close_install_app_file()
            if response == 0: self.on_apps_ready()
            else:
                dg = Adw.MessageDialog.new(self, "App Install Failed", "Installation failed. Please retry or install the gh pacakage manually.\nErr code: "+str(response))
                dg.add_response("cancel", "Quit")
                dg.add_response("install", "Retry")
                dg.set_response_appearance("install", 1)
                dg.set_response_appearance("cancel", 2)
                dg.connect("response", self.on_dialog_response)
                dg.present()

    def on_apps_ready(self):
        yml_path = os.path.expanduser("~/.config/gh/hosts.yml")
        if os.path.exists(yml_path):
            usrDat = parse_yml_file(yml_path)
        else: usrDat = {}
        
        if "github.com" in usrDat:
            if usrDat["github.com"]["git_protocol"] == "ssh":
                self.connect_home_page(usrDat["github.com"]["user"])
            else:
                dg = Adw.MessageDialog.new(self, "Unsupported Protocol", "Currently logged in method is in not ssh protocol. Please re-login with ssh protocol")
                dg.add_response("cancel", "Cancel")
                dg.add_response("login", "Re Login")
                dg.set_response_appearance("login", 1)
                dg.set_response_appearance("cancel", 2)
                dg.connect("response", self.on_dialog_response)
                dg.present()
        else: self.connect_login_page()
    
    @Gtk.Template.Callback()
    def on_visible(self, widget):
        appsReady = os.system("gh --version") == 0
        if appsReady: self.on_apps_ready()
        else:
            dg = Adw.MessageDialog.new(self, "App Installs Required", "Some apps required to run this program is not present in this system. Please proceed to install all dependency apps.\nApp required: git client (package: gh)")
            dg.add_response("cancel", "Cancel")
            dg.add_response("install", "Install All")
            dg.set_response_appearance("install", 1)
            dg.set_response_appearance("cancel", 2)
            dg.connect("response", self.on_dialog_response)
            dg.present()
        
    def connect_login_page(self):
        self.base_connector.set_child(self.login_page)
        self.destroy_callback = self.login_page.on_window_destroy
    
    def connect_home_page(self, username):
        self.base_connector.set_child(self.home_page)
        self.home_page.refresh(username)
        self.destroy_callback = self.home_page.on_window_destroy

    def open_install_app_file(self):
        filename = self.cache_location+"app-install"
        file = open(filename, "w")
        file.write(cmds)
        file.close()
        os.system("chmod +x "+filename)
    
    def close_install_app_file(self):
        filename = self.cache_location+"app-install"
        os.system("rm "+filename)

    def on_window_destroy(self, window):
        if self.destroy_callback: self.destroy_callback(window)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.login_page = LoginPage(self)
        self.home_page = HomePage(self)
        self.logout.set_visible(False)
        self.cache_location = os.path.expanduser("~/.cache/hashtag-gitcloner/")
        self.config_location = os.path.expanduser("~/.config/hashtag-gitcloner/")
        if not os.path.exists(self.cache_location): os.mkdir(self.cache_location)
        if not os.path.exists(self.config_location): os.mkdir(self.config_location)
        self.connect("close-request", self.on_window_destroy)
        self.destroy_callback = None
        self.install_task = ExtTerminal(self)
        
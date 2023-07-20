# window.py
#
# Copyright 2023 Ansif
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from gi.repository import Gtk
from .LoginPage import LoginPage
from .HomePage import HomePage
from .util import parse_yml_file
from .. import Htg, runtime_env, get_ui_file_path, app_cache_path, app_config, update_app_config

if runtime_env >= 22.04:
    from gi.repository import Adw

cmds="""#!/bin/bash
set -e
type -p curl >/dev/null || (sudo apt update && sudo apt install curl -y)
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh -y
"""

@Gtk.Template(filename=get_ui_file_path("window.ui"))
class Linuxapp1Window(Adw.ApplicationWindow if runtime_env >= 22.04 else Gtk.ApplicationWindow):
    __gtype_name__ = 'Linuxapp1Window'

    base_connector = Gtk.Template.Child()
    logout = Gtk.Template.Child()

    __registered_tasks = 0

    def lock(self): 
        self.__registered_tasks += 1
        if self.__registered_tasks > 0:
            self.set_sensitive(False)

    def release(self):
        self.__registered_tasks -= 1
        if self.__registered_tasks <= 0:
            self.set_sensitive(True)

    def getBuilderForBase(self, name):
        return Gtk.Builder.new_from_resource('/Htg/linux/linuxapp1/'+name+'.ui')

    def on_dialog_response(self, widget, response):
        if response == "cancel": self.close()
        elif response == "login": 
            self.connect_login_page()
            os.system("gh auth logout -h github.com")
        elif response == "install":
            self.open_install_app_file()
            filename = os.path.join(app_cache_path, "app-install")
            self.install_task.run("bash "+filename, False, self.on_terminal_task_performed)
        
    def on_terminal_task_performed(self, widget, response, userdata):
        if widget == self.install_task:
            self.close_install_app_file()
            if response == 0: self.on_apps_ready()
            else:
                dg = Htg.MessageDialog(self, "App Install Failed", "Installation failed. Please retry or install the gh pacakage manually.\nErr code: "+str(response))
                dg.add_response("cancel", "Quit")
                dg.add_response("install", "Retry")
                if runtime_env >= 23.04:
                    dg.set_response_appearance("install", 1)
                    dg.set_response_appearance("cancel", 2)
                dg.connect("response", self.on_dialog_response)
                dg.present()

    def on_apps_ready(self):
        if app_config["current_runtime_env"] != app_config["detected_runtime_env"]:
            if runtime_env >= 22.04: self.add_css_class("devel")
            else: self.get_style_context().add_class("devel")
            dg = Htg.MessageDialog(self, "Debug Mode Activated", "Turn the debug mode off for better and updated experience")
            dg.add_response("ok", "OK")
            dg.present()

        yml_path = os.path.expanduser("~/.config/gh/hosts.yml")
        if os.path.exists(yml_path):
            usrDat = parse_yml_file(yml_path)
        else: usrDat = {}
        
        if "github.com" in usrDat:
            if usrDat["github.com"]["git_protocol"] == "ssh":
                self.connect_home_page(usrDat["github.com"]["user"])
            else:
                dg = Htg.MessageDialog(self, "Unsupported Protocol", "Currently logged in method is in not ssh protocol. Please re-login with ssh protocol")
                dg.add_response("cancel", "Cancel")
                dg.add_response("login", "Re Login")
                if runtime_env >= 23.04:
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
            dg = Htg.MessageDialog(self, "App Installs Required", "Some apps required to run this program is not present in this system. Please proceed to install all dependency apps.\nApp required: git client (package: gh)")
            dg.add_response("cancel", "Cancel")
            dg.add_response("install", "Install All")
            if runtime_env >= 23.04:
                dg.set_response_appearance("install", 1)
                dg.set_response_appearance("cancel", 2)
            dg.connect("response", self.on_dialog_response)
            dg.present()
        
    def connect_login_page(self):
        self.base_connector.set_child(self.login_page)
        self.destroy_callback = self.login_page.on_window_destroy

        if not app_config["version_warning_shown"]:
            if runtime_env == 20.04: 
                dg = Htg.MessageDialog(self, "Outdated Ubuntu Detected", "Seriously bro? Its Ubuntu 20.04, Its will lose its support so soon. Also I am not implementing new features to this version. Update ubuntu asap bro, new LTS version is way too beautiful than this version")
                dg.add_response("ok", "OK")
                dg.present()
            elif runtime_env == 22.04:
                dg = Htg.MessageDialog(self, "Keep Updating Ubuntu", "Update your ubuntu to 24.04 LTS when it is available. This version misses some built in features which the next LTS version will have. You are currently running Ubuntu 22.04 LTS")
                dg.add_response("ok", "OK")
                dg.present()
                app_config["version_warning_shown"] = True
                update_app_config()
            else:
                if runtime_env < 24.04:
                    dg = Htg.MessageDialog(self, "Keep Ubuntu in a LTS version", "Intermediate version of ubuntu is not recomended as it lose its support very soon. Update to the next and latest (Ubuntu 24.04) LTS version when it is available")
                    dg.add_response("ok", "OK")
                    dg.present()
                    app_config["version_warning_shown"] = True
                    update_app_config()
    
    def connect_home_page(self, username):
        self.base_connector.set_child(self.home_page)
        self.home_page.refresh(username)
        self.destroy_callback = self.home_page.on_window_destroy

    def open_install_app_file(self):
        filename = os.path.join(app_cache_path, "app-install")
        file = open(filename, "w")
        file.write(cmds)
        file.close()
        os.system("chmod +x "+filename)
    
    def close_install_app_file(self):
        filename = os.path.join(app_cache_path, "app-install")
        os.system("rm "+filename)

    def on_window_destroy(self, window, *args):
        if self.destroy_callback: self.destroy_callback(window)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.login_page = LoginPage(self)
        self.home_page = HomePage(self)
        if runtime_env >= 22.04: self.connect("close-request", self.on_window_destroy)
        else: self.connect("delete-event", self.on_window_destroy)
        self.destroy_callback = None
        self.install_task = Htg.ExtTerminal(self)
        
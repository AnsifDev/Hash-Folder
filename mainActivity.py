import os
from threading import Thread
from time import sleep
from InstallDialog import InstallDialog
from darwin.house.linux.utils import Activity
from ErrDialog import ErrorDialog
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

class MainActivity(Activity):
    Destiny_file = None

    def onCreate(self):
        self.setContentView("MainUI.glade")

        self.ssh_ok = self.findViewById("check_ssh")
        self.ssh_ok.connect("toggled", self.checkbox_toggled)
        self.relogin = self.findViewById("check_relogin")
        

        self.ssh_tools = self.findViewById("ssh_tools")

        self.ssh_file = self.findViewById("entry_ssh_file")
        self.ssh_key = self.findViewById("entry_ssh_key")
        self.ssh_pass = self.findViewById("entry_ssh_pass")
        self.ssh_cpass = self.findViewById("entry_ssh_cpass")

        self.git_user = self.findViewById("entry_git_name")
        self.git_email = self.findViewById("entry_git_email")
        self.git_repo = self.findViewById("entry_git_repo")

        self.btn_clone = self.findViewById("btn_clone")
        self.btn_clone.connect("clicked", self.btn_clicked)

        return super().onCreate()

    def checkbox_toggled(self, checkbox):
        if checkbox == self.ssh_ok:
            self.ssh_tools.set_sensitive(checkbox.get_active())
            self.relogin.set_sensitive(not checkbox.get_active())
            if checkbox.get_active(): self.relogin.set_active(True)
    
    def btn_clicked(self, btn):
        if btn == self.btn_clone:
            dialog = Gtk.FileChooserDialog("Please choose a file", self.getWindow(),
                Gtk.FileChooserAction.SELECT_FOLDER,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                print("Ok")
                self.Destiny_file = dialog.get_filename()
                dialog.destroy()
            else:
                dialog.destroy()
                ErrorDialog("Destination folder is not selected").show()
                return

            ssh_opted = self.ssh_ok.get_active()
            self.username = self.git_user.get_text()
            self.email = self.git_email.get_text()
            self.repo = self.git_repo.get_text()
            filename = self.ssh_file.get_text()
            keyname = self.ssh_key.get_text()
            password = self.ssh_pass.get_text()
            cpassword = self.ssh_cpass.get_text()
            
            if ssh_opted and len(filename) < 5: ErrorDialog("SSH File name minimum 5 characters required").show()
            elif ssh_opted and "/" in filename: ErrorDialog("Only file name is allowed not directory").show()
            elif ssh_opted and "~" in filename: ErrorDialog("Only file name is allowed not directory").show()
            elif ssh_opted and os.path.exists(os.path.expanduser("~/.ssh/")+filename): ErrorDialog("Filename not available").show()
            elif ssh_opted and len(keyname) == 0: ErrorDialog("SSH Key name cannot be empty").show()
            elif ssh_opted and len(password) < 8: ErrorDialog("SSH password minimum 8 characters required").show()
            elif ssh_opted and cpassword != password: ErrorDialog("SSH passwords not matching").show()
            elif len(self.username) == 0: ErrorDialog("User name cannot be empty").show()
            elif "/" in self.username: ErrorDialog("Only user name is allowed not directory").show()
            elif len(self.email) == 0: ErrorDialog("Email ID cannot be empty").show()
            elif len(self.repo) == 0: ErrorDialog("Repository name cannot be empty").show()
            elif "/" in self.repo: ErrorDialog("Only repository name is allowed no need of user name along it").show()
            else:
                self.window.set_sensitive(False)
                if ssh_opted: self.ssh_gen(filename, keyname, password)
                if os.system("git --version") != 0: InstallDialog("Git is not installed", 1, self.onInstallPromptExit).show()
                elif os.system("gh --version") != 0: InstallDialog("Github CLI is not installed", 2, self.onInstallPromptExit).show()
                else:
                    Thread(target=self.clone).start()

    def ssh_gen(self, filename, keyname, password):
        os.system("ssh-keygen -t ed25519 -C \""+keyname+"\" -f ~/.ssh/"+filename.replace(" ", "\\ ")+" -N \""+password+"\"")

    def onInstallPromptExit(self, request, result):
        if request == 1:
            if result:
                if os.system("gnome-terminal --wait -- bash -c \"./aptInit.sh git\"") != 0: GLib.idle_add(self.showError, "Installation of git failed!!!")
                elif os.system("gh --version") != 0: GLib.idle_add(self.installDg, "Github CLI is not installed", 2, self.onInstallPromptExit)
                else: self.clone()
            else: GLib.idle_add(self.showError, "git install request rejected!!!\nCloning failed. Try after installing git")
        elif request == 2:
            if result:
                if os.system("gnome-terminal --wait -- bash -c \"./aptInit.sh gh\"") != 0:
                    if os.system("gnome-terminal --wait -- bash -c \"./aptInit.sh repo\"") != 0: GLib.idle_add(self.showError, "Installation of gh (GitHub CLI) failed!!!")
                    else: self.clone()
                else: self.clone()
            else: GLib.idle_add(self.showError, "Github CLI install request rejected!!!\nCloning failed. Try after installing gh")
    
    def clone(self):
        GLib.idle_add(self.ssh_ok.set_active, False)

        if os.system("gh auth status") != 0:
            if os.system("gnome-terminal --wait -- gh auth login") != 0:
                GLib.idle_add(self.showError, "Git login failed")
                return

        elif self.relogin.get_active():
            if os.system("gnome-terminal --wait -- gh auth login") != 0:
                GLib.idle_add(self.showError, "Git login failed")
                return
        
        GLib.idle_add(self.relogin.set_active, False)

        if os.system("gnome-terminal --wait -- gh repo clone "+self.username+"/"+self.repo+" "+self.Destiny_file.replace(" ", "\\ ")) != 0:
            GLib.idle_add(self.showError, "Git clone failed")
            return
        
        GLib.idle_add(self._finish)
        os.system("cd "+self.Destiny_file.replace(" ", "\\ ")+"&& git config user.name \""+self.username+"\" && git config user.email "+self.email)
        os.system("gnome-terminal -- nautilus "+self.Destiny_file.replace(" ", "\\ "))
        
    def showError(self, msg):
        ErrorDialog(msg).show()
        self.window.set_sensitive(True)
    
    def installDg(self, msg, reqId, callback):
        InstallDialog(msg, reqId, callback).show()
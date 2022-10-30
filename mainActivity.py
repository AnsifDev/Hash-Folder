import os
from InstallDialog import InstallDialog
from darwin.house.linux.utils import Activity
from ErrDialog import ErrorDialog
import gi

gi.require_version("Gtk", "3.0")

gh_install_cmd = """type -p curl >/dev/null || sudo apt install curl -y
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \\
&& sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \\
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update \\
&& sudo apt install gh -y"""

class MainActivity(Activity):
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

        self.btn_chooser = self.findViewById("btn_choose_file")

        return super().onCreate()

    def checkbox_toggled(self, checkbox):
        if checkbox == self.ssh_ok:
            self.ssh_tools.set_sensitive(checkbox.get_active())
            self.relogin.set_sensitive(not checkbox.get_active())
            if checkbox.get_active(): self.relogin.set_active(True)
    
    def btn_clicked(self, btn):
        if btn == self.btn_clone:

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
            elif self.btn_chooser.get_filename() == None: ErrorDialog("Destination folder is not selected").show()
            else:
                if ssh_opted: self.ssh_gen(filename, keyname, password)
                if os.system("git --version") != 0: InstallDialog("Git is not installed", 1, self.onInstallPromptExit).show()
                elif os.system("gh --version") != 0: InstallDialog("Github CLI is not installed", 2, self.onInstallPromptExit).show()
                else: self.clone()

    def ssh_gen(self, filename, keyname, password):
        os.system("ssh-keygen -t ed25519 -C \""+keyname+"\" -f ~/.ssh/"+filename.replace(" ", "\\ ")+" -N \""+password+"\"")

    def onInstallPromptExit(self, request, result): 
        if request == 1:
            if result:
                if os.system("gnome-terminal --wait -- sudo apt update && sudo apt install git") != 0: ErrorDialog("Installation of git failed!!!").show()
                elif os.system("gh --version") != 0: InstallDialog("Github CLI is not installed", 2, self.onInstallPromptExit).show()
                else: self.clone()
            else: ErrorDialog("git install request rejected!!!\nCloning failed. Try after installing git").show()
        elif request == 2:
            if result:
                if os.system("gnome-terminal --wait -- sudo apt update && sudo apt install gh") != 0:
                    if os.system("gnome-terminal --wait -- "+gh_install_cmd) != 0: ErrorDialog("Installation of gh (GitHub CLI) failed!!!").show()
                    else: self.clone()
                else: self.clone()
            else: ErrorDialog("Github CLI install request rejected!!!\nCloning failed. Try after installing gh").show()

    def clone(self):
        self.ssh_ok.set_active(False)

        if os.system("gh auth status") != 0:
            if os.system("gnome-terminal --wait -- gh auth login") != 0:
                ErrorDialog("Git login failed").show()
                return
        elif self.relogin.get_active():
            if os.system("gnome-terminal --wait -- gh auth login") != 0:
                ErrorDialog("Git login failed").show()
                return
        
        self.relogin.set_active(False)
        
        if os.system("gh repo clone "+self.username+"/"+self.repo+" "+self.btn_chooser.get_filename().replace(" ", "\\ ")) != 0:
            ErrorDialog("Git clone failed\n").show()
            return

        os.system("cd "+self.btn_chooser.get_filename().replace(" ", "\\ ")+"&& git config user.name \""+self.username+"\" && git config user.email "+self.email)
        os.system("nautilus "+self.btn_chooser.get_filename().replace(" ", "\\ "))
        self._finish()

import os
from gi.repository import Adw, Gtk
from .DialogSSH import DialogSSH
from .util import ExtTerminal, parse_yml_file
from .HomePage import HomePage

@Gtk.Template(filename='ui/login_page.ui')
class LoginPage(Gtk.Box):
    __gtype_name__ = 'LoginPage'

    login_git = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def on_button_clicked(self, widget):
        if (widget == self.login_git):
            if os.system("gh auth status -h github.com") != 0:
                self.login_task.run("gh auth login -h github.com -p ssh -s admin:public_key -w", False, self.on_terminal_task_performed)
            else: self.on_terminal_task_performed(1, 0)

    def on_terminal_task_performed(self, widget, response, userdata):
        if widget == self.login_task:
            if response == 0:
                usrDat = parse_yml_file(os.path.expanduser("~/.config/gh/hosts.yml"))
                username = usrDat["github.com"]["user"]
                if os.path.exists(os.path.expanduser("~/.ssh/"+username)):
                    self.complete_login(username)
                else:
                    dg = DialogSSH(self.window, username, self.on_ssh_key_done)
                    dg.present()
            else:
                dg = Adw.MessageDialog.new(self.window, "Login Failed", "Login attempt got failed. Please retry\nErr code:"+str(response))
                dg.add_response("ok", "OK")
                dg.present()
        elif widget == self.ssh_load_task:
            if response == 0: self.window.connect_home_page(userdata)
            else:
                dg = Adw.MessageDialog.new(self.window, "Login Failed", "SSH Key Upload Failed. Please retry\nErr code:"+str(response))
                dg.add_response("ok", "OK")
                dg.present()
                filename = userdata.replace(" ","\\ ")
                os.system("rm -f ~/.ssh/"+filename+".pub ~/.ssh/"+filename)
                os.system("gh auth logout -h github.com")

    def on_ssh_key_done(self, dialog, keyname):
        cmd = "gh ssh-key add ~/.ssh/"+dialog.keyname.replace(" ","\\ ")+".pub -t \""+keyname+"\""
        self.ssh_load_task.run(cmd, True, self.on_terminal_task_performed, keyname)
    
    def on_window_destroy(self, window):
        pass

    def __init__(self, window) -> None:
        super().__init__()
        self.window = window
        self.login_task = ExtTerminal(window)
        self.ssh_load_task = ExtTerminal(window)

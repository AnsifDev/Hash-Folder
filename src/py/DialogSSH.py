import os
from gi.repository import Gtk
from .. import Htg, runtime_env, get_ui_file_path

if runtime_env >= 22.04:
    from gi.repository import Adw

@Gtk.Template(filename=get_ui_file_path("dg_ssh.ui"))
class DialogSSH(Adw.Window if runtime_env >= 22.04 else Gtk.Window):
    __gtype_name__ = 'DialogSSH'

    create = Gtk.Template.Child()
    cancel = Gtk.Template.Child()
    en_keyname = Gtk.Template.Child()
    en_pass = Gtk.Template.Child()
    en_repass = Gtk.Template.Child()
    warning_layout = Gtk.Template.Child()
    warning_label = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def on_button_clicked(self, widget):
        if (widget == self.create):
            self.ssh_gen(self.keyname, self.en_pass.get_text(), self.en_keyname.get_text()) 
        self.close()

    def on_terminal_task_complete(self, widget, response, userdata):
        self.callback(self, userdata)

    def ssh_gen(self, keyname, password, keylabel):
        cmd = "ssh-keygen -t ed25519 -C \""+keyname+"\" -f ~/.ssh/"+keyname.replace(" ", "\\ ")+" -N \""+password+"\""
        Htg.ExtTerminal(self.get_transient_for()).run(cmd, True, self.on_terminal_task_complete, keylabel)

    def troubleshoot(self):
        if (len(str(self.en_keyname.get_text())) < 5): return "Keyname must have atleast 5 characters"
        if (len(str(self.en_pass.get_text())) < 8): return "Password must have atleast 8 characters"
        if (self.en_pass.get_text() != self.en_repass.get_text()): return "Passwords isn't matching"
        return None

    @Gtk.Template.Callback()
    def on_text_changed(self, widget):
        response = self.troubleshoot()
        self.create.set_sensitive(response == None)
        self.warning_layout.set_visible(response != None)
        
        if (response != None): self.warning_label.set_text(response)

    def __init__(self, parent, keyname, callback, **kwargs):
        super().__init__(**kwargs)

        self.keyname = keyname
        self.callback = callback
        self.set_transient_for(parent)

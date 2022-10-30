import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class InstallDialog:
    def __init__(self, msg, reqId, onExit) -> None:
        self.onExit = onExit
        self.reqId = reqId
        builder = Gtk.Builder()
        builder.add_from_file("MainUI.glade")
        self.dg = builder.get_object("install_dg")
        dg_msg = builder.get_object("install_dg_msg")
        dg_msg.set_text(msg)
        self.ok = builder.get_object("install_dg_ok")
        self.ok.connect("clicked", self.btn_clicked)
        self.cancel = builder.get_object("install_dg_cancel")
        self.cancel.connect("clicked", self.btn_clicked)
    
    def btn_clicked(self, btn):
        self.onExit(self.reqId, btn == self.ok)
        self.dg.destroy()

    def show(self):
        self.dg.show()


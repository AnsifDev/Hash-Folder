import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

class ErrorDialog:
    def __init__(self, msg) -> None:
        file = "MainUI.glade"
        id = "err_dg"
        builder = Gtk.Builder()
        builder.add_from_file(file)
        self.dg = builder.get_object(id)
        dg_msg = builder.get_object("err_dg_msg")
        dg_msg.set_text(msg)
        ok = builder.get_object("err_dg_ok")
        ok.connect("clicked", self.btn_clicked)

    def btn_clicked(self, btn):
        self.dg.destroy()

    def show(self):
        self.dg.run()


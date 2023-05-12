import os
import shlex
import sys
from threading import Thread
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk, Gio, GLib, Gdk

screen = Gdk.Screen.get_default()
provider = Gtk.CssProvider()
provider.load_from_path("py/gtk3/styles.css")
Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

class Linuxapp1Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='hashtag.linux.gitcloner',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        self.win = self.props.active_window
        if not self.win:
            builder = Gtk.Builder.new_from_file("py/gtk3/test.ui")
            self.win = builder.get_object("window")
            # self.win = Gtk.Window()
            # self.win.set_default_size(600, 450)
            self.win.set_application(self)

        self.win.present()
        self.win.show_all()

    def on_btn_clicked(self, widget):
        if widget == self.btn:
            pass
        

def main():
    """The application's entry point."""
    app = Linuxapp1Application()
    return app.run(sys.argv)

main()

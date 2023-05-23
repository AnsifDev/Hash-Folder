import gi

# gi.require_version('Gtk', '3.0')
# gi.require_version('Vte', '2.91')

from gi.repository import Gtk, Gio
from .window import Linuxapp1Window
from .. import version_code

if version_code >= 22.04:
    from gi.repository import Adw

class Application(Adw.Application if version_code >= 22.04 else Gtk.Application):
    """The main application singleton class."""

    def __init__(self):
        flags = Gio.ApplicationFlags.FLAGS_NONE if version_code < 23.04 else Gio.ApplicationFlags.DEFAULT_FLAGS
        super().__init__(application_id='hashtag.linux.gitcloner',
                         flags=flags)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        self.win = self.props.active_window
        if not self.win:
            self.win = Linuxapp1Window(application=self)

        self.win.present()
        self.win.show()
        #self.win.logout.set_visible(False)

    # def on_button_clicked(self, widget):
    #     pass

    # def on_about_action(self, widget, _):
    #     """Callback for the app.about action."""
    #     about = Gtk.AboutWindow(transient_for=self.props.active_window,
    #                             application_name='Repo Cloner',
    #                             application_icon='hashtag.linux.linuxapp1',
    #                             developer_name='Ansif',
    #                             version='0.1.0',
    #                             developers=['Ansif'],
    #                             copyright='© 2023 Ansif')
    #     about.present()

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

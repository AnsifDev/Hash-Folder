#!/bin/python3

import sys
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gio
from .AppWindow import AppWindow


class GitCloner(Gtk.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='hashtag.linux.gitcloner',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        self.win = self.props.active_window
        if not self.win:
            self.win = AppWindow(application=self)
        self.win.present()


    # def on_about_action(self, widget, _):
    #     """Callback for the app.about action."""
    #     about = Adw.AboutWindow(transient_for=self.props.active_window,
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

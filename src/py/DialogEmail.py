import os
from gi.repository import Gtk
from .. import version_code, get_ui_file_path

if version_code >= 22.04:
    from gi.repository import Adw

@Gtk.Template(filename=get_ui_file_path("dg_email.ui"))
class DialogEmail(Adw.Window if version_code >= 22.04 else Gtk.Window):
    __gtype_name__ = 'DialogEmail'

    create = Gtk.Template.Child()
    cancel = Gtk.Template.Child()
    en_email = Gtk.Template.Child()
    warning_layout = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def on_button_clicked(self, widget, *args):
        if (widget != self.create): self.callback(self, None)
        else: self.callback(self, self.en_email.get_text())
        self.close()

    @Gtk.Template.Callback()
    def on_text_changed(self, widget):
        email = self.en_email.get_text().strip()
        response = "@" in email and not " " in email
        self.create.set_sensitive(response)
        self.warning_layout.set_visible(not response)

    def __init__(self, parent, callback, **kwargs):
        super().__init__(**kwargs)

        self.callback = callback
        self.set_transient_for(parent)
        self.positive_return = False
        if version_code >= 22.04: self.connect("close-request", self.on_button_clicked)
        else: self.connect("delete-event", self.on_button_clicked)
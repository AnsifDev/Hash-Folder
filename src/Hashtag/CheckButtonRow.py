from gi.repository import Gtk
from . import ActionRow
from .. import runtime_env

class CheckButtonRow(ActionRow):
    __gtype_name__ = 'HashtagCheckButtonRow'

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.check_button = Gtk.CheckButton()
        if runtime_env < 22.04:
            self.check_button.show()
            self.check_button.set_margin_start(8)
        self.add_prefix(self.check_button)
        self.set_activatable_widget(self.check_button)
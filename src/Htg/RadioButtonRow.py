from gi.repository import Gtk
from . import ActionRow

class RadioButtonRow(ActionRow):
    __gtype_name__ = 'HtgRadioButtonRow'

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.check_button = Gtk.RadioButton()
        self.check_button.show()
        self.check_button.set_margin_start(8)
        self.add_prefix(self.check_button)
        self.set_activatable_widget(self.check_button)
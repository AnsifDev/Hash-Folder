from gi.repository import Gtk, Adw, GObject
from . import EntryRow

class PasswordEntryRow(EntryRow):
    __gtype_name__ = "HtgPasswordEntryRow"

    __password_shown = False
    __keyboard = None

    def _on_password_btn_clicked(self, *args):
        self.__password_shown = not self.__password_shown
        self._en_entry.set_visibility(self.__password_shown)
        if self.__password_shown: self._password_btn.set_icon_name("view-conceal-symbolic")
        else: self._password_btn.set_icon_name("view-reveal-symbolic")

    def _caps_update(self, *args):
        self._img_caps.set_visible(not self._en_entry.get_visibility() and self.__keyboard.get_caps_lock_state())

    def _focus_changed(self, *args):
        activate = self._en_entry.has_focus()
        if activate: self._caps_update()
        else: self._img_caps.set_visible(False)
        return super()._focus_changed(*args)

    def do_realize(self):
        display = self.get_display()
        seat = display.get_default_seat()
        if seat: self.__keyboard = seat.get_keyboard()
        if self.__keyboard:
            self.__keyboard.connect("notify::caps-lock-state", self._caps_update)
            self._caps_update()
        EntryRow.do_realize(self)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._img_caps = Gtk.Image()
        self._img_caps.set_from_icon_name("caps-lock-symbolic")
        self._img_caps.add_css_class("indicator")
        self._img_caps.set_visible(False)
        self._main_box.append(self._img_caps)

        self._password_btn = Gtk.Button()
        self._password_btn.set_icon_name("view-reveal-symbolic")
        self._password_btn.set_focusable(False)
        self._password_btn.add_css_class("flat")
        self._password_btn.connect("clicked", self._on_password_btn_clicked)
        self._en_entry.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        self._en_entry.set_visibility(False)
        self._main_box.append(self._password_btn)

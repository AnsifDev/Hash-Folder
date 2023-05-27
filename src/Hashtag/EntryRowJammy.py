from gi.repository import Gtk, Adw, GObject
from . import get_ui_file_path

class EntryRow(Adw.PreferencesRow, Gtk.Editable):
    __gtype_name__ = "HashtagEntryRow"
    __gsignals__ = {
        'apply': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
    }

    __parent = None
    __parent_handler_id = None
    __apply_button_shown = False

    _show_apply_button = False

    @GObject.Property(type=int, default=0)
    def cursor_position(self):
        return self._en_entry.get_property("cursor-position")

    @GObject.Property(type=bool, default=True)
    def editable(self):
        return self._en_entry.get_property("editable")

    @editable.setter
    def editable(self, value):
        self._en_entry.set_property("editable", value)

    @GObject.Property(type=bool, default=True)
    def enable_undo(self):
        return self._en_entry.get_property("enable-undo")

    @enable_undo.setter
    def enable_undo(self, value):
        self._en_entry.set_property("enable-undo", value)

    @GObject.Property(type=int, default=-1)
    def max_width_chars(self):
        return self._en_entry.get_property("max-width-chars")

    @max_width_chars.setter
    def max_width_chars(self, value):
        self._en_entry.set_property("max-width-chars", value)

    @GObject.Property(type=int, default=0)
    def selection_bound(self):
        return self._en_entry.get_property("selection-bound")

    @GObject.Property(type=str, default="")
    def text(self):
        return self._en_entry.get_property("text")

    @text.setter
    def text(self, value):
        self._en_entry.set_property("text", value)

    @GObject.Property(type=int, default=-1)
    def width_chars(self):
        return self._en_entry.get_property("width-chars")

    @width_chars.setter
    def width_chars(self, value):
        self._en_entry.set_property("width-chars", value)

    @GObject.Property(type=float, default=0.0)
    def xalign(self):
        return self._en_entry.get_property("xalign")

    @xalign.setter
    def xalign(self, value):
        self._en_entry.set_property("xalign", value)

    @GObject.Property(type=bool, default=False)
    def show_apply_button(self):
        return self._show_apply_button

    @show_apply_button.setter
    def show_apply_button(self, value):
        self._show_apply_button = value

    def do_get_delegate(self):
        return self._en_entry
    
    def do_dispose(self):
        self.finish_delegate()
        Adw.PreferencesRow.do_dispose(self)

    def do_focus(self, *args):
        self._en_entry.grab_focus()
        return False
    
    def _focus_changed(self, *args):
        activate = self._en_entry.has_focus()

        self.__apply_button_shown = False
        if activate: self.add_css_class("focused")
        else:
            self.remove_css_class("focused")
            self._btn_apply.set_visible(False)
        self._img_edit.set_visible(not activate)
        if self._en_entry.get_text() == "":
            self._empty_title.set_visible(not activate)
            self._en_entry.set_visible(activate)
            self._title_viewer.set_visible(activate)
            

    def _parent_changed(self, *args):
        current_parent = self.get_parent()
        if current_parent == self.__parent: return
        if self.__parent: self.__parent.disconnect(self.__parent_handler_id)
        self.__parent_handler_id = current_parent.connect("row-activated", self.__row_activated)
        self.__parent = current_parent

    def __row_activated(self, widget, row): 
        if self == row:
            self._en_entry.grab_focus()

    def _title_prop_changed(self, *args):
        title = self.get_title()
        self._title_viewer.set_text(title)
        self._empty_title.set_text(title)
    
    def _en_activate(self, *args):
        if self._show_apply_button and self.__apply_button_shown:
            self.__apply_button_shown = False
            self._btn_apply.set_visible(False)
            self.emit("apply")
    
    def do_changed(self, *args):
        if self._show_apply_button:
            self.__apply_button_shown = True
            self._btn_apply.set_visible(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        builder = Gtk.Builder.new_from_file(get_ui_file_path("entry_row.ui"))
        self._en_entry = builder.get_object("_en_entry")
        self._title_viewer = builder.get_object("_title_viewer")
        self._empty_title = builder.get_object("_empty_title")
        self._img_edit = builder.get_object("_img_edit")
        self._btn_apply = builder.get_object("_btn_apply")
        self._main_box = builder.get_object("_main_box")

        self.set_child(self._main_box)

        self._en_entry.connect("notify::has-focus", self._focus_changed)
        self._en_entry.connect("activate", self._en_activate)
        self._btn_apply.connect("clicked", self._en_activate)
        self.connect("notify::parent", self._parent_changed)
        self.connect("notify::title", self._title_prop_changed)
        self.set_size_request(-1, 56)
        self.add_css_class("entry")

        self.init_delegate()

GObject.type_register(EntryRow)
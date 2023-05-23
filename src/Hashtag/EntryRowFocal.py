from gi.repository import Gtk, GObject
from . import get_ui_file_path

class EntryRow(Gtk.ListBoxRow, Gtk.Editable):
    __gtype_name__ = "HashtagEntryRow"

    __parent_handler_id = None
    __parent = None

    @GObject.Property(type=str)
    def title(self):
        return self.get_title()
    
    @title.setter
    def title(self, value):
        self.set_title(value)

    def set_title(self, value): self._en_edit.set_placeholder_text(value)

    def get_title(self): return self._en_edit.get_placeholder_text()

    def set_text(self, value): self._en_edit.set_text(value)

    def get_text(self): return self._en_edit.get_text()
  
    def __row_activated(self, widget, row): 
        if self == row:
            print("Activating")
            self._en_edit.mnemonic_activate(False)

    def _parent_changed(self, *args):
        current_parent = self.get_parent()
        if current_parent == self.__parent: return
        if self.__parent: self.__parent.disconnect(self.__parent_handler_id)
        self.__parent_handler_id = current_parent.connect("row-activated", self.__row_activated)

    def _on_focused(self, *args):
        self._title_helper.set_visible(True)
        self._title_helper.set_label(self.get_title())
        self._edit_icon.set_visible(False)

    def _on_focus_finished(self, *args):
        self._edit_icon.set_visible(True)
        if self._en_edit.get_text() == "":  
            self._title_helper.set_visible(False)

    def _on_en_activated(self, *args):
        self.emit("apply")

    #Editable Implementation
    def do_do_delete_text(self, *args):
        return self._en_edit.do_delete_text(*args)

    def do_do_insert_text(self, *args):
        return self._en_edit.do_insert_text(*args)
    
    def do_get_chars(self, *args):
        return self._en_edit.get_chars(*args)

    def do_get_position(self, *args):
        return self._en_edit.get_position(*args)

    def do_get_selection_bounds(self, *args):
        return self._en_edit.get_selection_bounds(*args)

    def do_set_position(self, *args):
        return self._en_edit.set_position(*args)

    def do_set_selection_bounds(self, *args):
        return self._en_edit.set_selection_bounds(*args)

    def connect(self, name, handler, *args):
        if name in ["changed", "delete-text", "insert-text"]:
            self._en_edit.connect(name, handler, *args)
        else: super().connect(name, handler, *args)

    def __init__(self) -> None:
        super().__init__()

        builder = Gtk.Builder.new_from_file(get_ui_file_path("entry_row.ui"))
        widget1 = builder.get_object("widget1")
        self._title_helper = builder.get_object("_title_helper")
        self._en_edit = builder.get_object("_en_edit")
        self._edit_icon = builder.get_object("_edit_icon")
        self.add(widget1)

        self.connect("notify::parent", self._parent_changed)
        self._en_edit.connect("focus-in-event", self._on_focused)
        self._en_edit.connect("focus-out-event", self._on_focus_finished)
        self._en_edit.connect("activate", self._on_en_activated)

GObject.type_register(EntryRow)
GObject.signal_new("apply", EntryRow, GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, [])
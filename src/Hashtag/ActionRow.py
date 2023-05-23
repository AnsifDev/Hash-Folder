from gi.repository import Gtk, GObject
from . import get_ui_file_path

class ActionRow(Gtk.ListBoxRow):
    __gtype_name__ = "HashtagActionRow"

    _title_widget = None
    _subtitle_widget = None
    _prefix_box = None
    _suffix_box = None

    __activatable_widget = None
    __parent_handler_id = None
    __parent = None
    __widget_ready = False

    @GObject.Property(type=str)
    def subtitle(self):
        return self.get_subtitle()
    
    @subtitle.setter
    def subtitle(self, value):
        self.set_subtitle(value)

    @GObject.Property(type=str)
    def title(self):
        return self.get_title()
    
    @title.setter
    def title(self, value):
        self.set_title(value)

    def add_prefix(self, widget): self._prefix_box.add(widget)

    def remove_prefix(self, widget): self._prefix_box.remove(widget)

    def add_suffix(self, widget): self._suffix_box.add(widget)

    def remove_suffix(self, widget): self._suffix_box.remove(widget)

    def set_title(self, value): self._title_widget.set_label(value)

    def get_title(self): return self._title_widget.get_label()

    def set_subtitle(self, value): 
        self._subtitle_widget.set_visible(True)
        self._subtitle_widget.set_label(value)

    def get_subtitle(self): return self._subtitle_widget.get_label()
    
    def set_activatable_widget(self, widget): self.__activatable_widget = widget

    def get_activatable_widget(self): return self.__activatable_widget
    
    def __row_activated(self, widget, row): 
        if self == row:
            if self.__activatable_widget:
                self.__activatable_widget.mnemonic_activate(False)

    def _parent_changed(self, *args):
        current_parent = self.get_parent()
        if current_parent == self.__parent: return
        if self.__parent: self.__parent.disconnect(self.__parent_handler_id)
        self.__parent_handler_id = current_parent.connect("row-activated", self.__row_activated)

    def do_add(self, widget):
        if self.__widget_ready: self._suffix_box.add(widget)
        else: Gtk.ListBoxRow.do_add(self, widget)

    def __init__(self) -> None:
        super().__init__()

        builder = Gtk.Builder.new_from_file(get_ui_file_path("action_row.ui"))
        widget1 = builder.get_object("widget1")
        self._title_widget = builder.get_object("_title_widget")
        self._subtitle_widget = builder.get_object("_subtitle_widget")
        self._prefix_box = builder.get_object("_prefix_box")
        self._suffix_box = builder.get_object("_suffix_box")
        self.add(widget1)

        self.connect("notify::parent", self._parent_changed)
        self.__widget_ready = True
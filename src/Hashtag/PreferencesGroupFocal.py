import gi
from gi.repository import Gtk, GObject
from . import ListViewAdapter, get_ui_file_path

class PreferencesGroup(Gtk.Box):
    __gtype_name__ = "HashtagPreferencesGroup"

    __header_suffix_widget = None

    _listview_adapter = None
    _children = None
    _view_holders = None
    _recycle_bin = None

    @GObject.Property(type=Gtk.Widget)
    def header_suffix(self):
        return self.get_header_suffix()
    
    @header_suffix.setter
    def header_suffix(self, value):
        self.set_header_suffix(value)

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

    def set_header_suffix(self, widget):
        if self.__header_suffix_widget: 
            self._header_prefix_box.remove(self.__header_suffix_widget)
        if widget:
            self._header_suffix_box.add(widget)
        self.__header_suffix_widget = widget

    def get_header_suffix(self, widget): self.__header_suffix_widget

    def set_title(self, value): self._title_widget.set_label(value)

    def get_title(self): return self._title_widget.get_label()

    def set_subtitle(self, value): self._subtitle_widget.set_label(value)

    def get_subtitle(self): return self._subtitle_widget.get_label()

    def do_add(self, widget):
        self._listbox.add(widget)
        self._children.append(widget)

    def set_listview_adapter(self, listview_adapter: ListViewAdapter):
        self._listview_adapter = listview_adapter

        self._view_holders.clear()
        self._recycle_bin.clear()

        while len(self._children) > 0:
            self.remove(self._children[0])

        items = listview_adapter.get_item_count()
        for i in range(items):
            view_holder = listview_adapter.get_view_holder()
            self._view_holders.append(view_holder)

            widget = listview_adapter.get_widget(view_holder, i)
            self.add(widget)

    def notify_data_changed(self, position: int = -1):
        item_count = self._listview_adapter.get_item_count()
        removed = len(self._view_holders) - item_count
        if removed > 0:
            for i in range(removed):
                self._recycle_bin.append(self._view_holders.pop())
                self.remove(self._children[-1])

        if position < 0: i = 0
        elif removed != 0: i = position
        else:
            self._listview_adapter.get_widget(self._view_holders[position], position)
            return
        
        while i < item_count:
            if not i < len(self._view_holders):
                if len(self._recycle_bin) > 0: view_holder = self._recycle_bin.pop(0)
                else: view_holder = self._listview_adapter.get_view_holder()
                self._view_holders.append(view_holder)
            view_holder = self._view_holders[i]
            new_widget = self._listview_adapter.get_widget(view_holder, i)
            old_widget = self._children[i] if i < len(self._children) else None
            if not i < len(self._children): self.add(new_widget)
            if old_widget and not old_widget == new_widget:
                print("Not equal err")
            i += 1
                    
    def remove(self, widget):
        self._children.remove(widget)
        self._listbox.remove(widget)
    
    def do_realize(self):
        Gtk.Box.do_add(self, self._title_layout)
        Gtk.Box.do_add(self, self._listbox)
        Gtk.Box.do_realize(self)

    def __init__(self) -> None:
        super().__init__()
        builder = Gtk.Builder.new_from_file(get_ui_file_path("preferences_group.ui"))
        self._title_widget = builder.get_object("_title_widget")
        self._subtitle_widget = builder.get_object("_subtitle_widget")
        self._header_suffix_box = builder.get_object("_header_suffix_box")
        self._listbox = builder.get_object("_listbox")
        self._title_layout = builder.get_object("title_layout")
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self._children = []
        self._recycle_bin = []
        self._view_holders = []
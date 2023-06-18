from . import ListViewAdapter
from gi.repository import Adw

class PreferencesGroup(Adw.PreferencesGroup):
    __gtype_name__ = 'HtgPreferencesGroup'

    _listview_adapter = None
    _children = []
    _view_holders = []
    _recycle_bin = []

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
                    
    def add(self, widget):
        self._children.append(widget)
        super().add(widget)
    
    def remove(self, widget):
        self._children.remove(widget)
        super().remove(widget)

from gi.repository import Gtk
from . import ViewHolder

class ListViewAdapter:
    def get_view_holder(self) -> ViewHolder:
        raise Exception("Function Not Implemented")
    
    def get_widget(self, view_holder: ViewHolder, position: int) -> Gtk.Widget:
        raise Exception("Function Not Implemented")
    
    def get_item_count(self) -> int:
        raise Exception("Function Not Implemented")

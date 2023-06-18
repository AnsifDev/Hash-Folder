from gi.repository import Gtk

class Bin(Gtk.Bin):
    __gtype_name__ = "HtgBin"
    _child = None

    def set_child(self, widget):
        self.add(widget)
    
    def do_add(self, widget):
        if self._child:
            self.remove(self._child)
        Gtk.Bin.do_add(self, widget)
        widget.show()
        self._child = widget

    def get_child(self):
        return self._child
    
    def __init__(self) -> None:
        super().__init__()

from . import Bin

class Clamp(Bin):
    __gtype_name__ = "HtgClamp"
    max_width = 600

    def _size_allocated(self, widget, userdata):
        width = self.get_allocated_width()
        size = self.get_allocation()
        if width > 600:
            total_width = size.width
            size.width = self.max_width
            size.x = (total_width-self.max_width)/2
            self.size_allocate(size)

    def __init__(self) -> None:
        super().__init__()

        self.connect("size-allocate", self._size_allocated)
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.set_margin_start(8)
        self.set_margin_end(8)

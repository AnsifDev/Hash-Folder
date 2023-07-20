from gi.repository import Gtk
from .. import runtime_env

if runtime_env >= 22.04: from gi.repository import Adw

def AdwMsg(win, title, subtitle=None):
    return Adw.MessageDialog.new(win, title, subtitle)

class MessageDialog:
    __id_map = []
    __callback_map = {}

    def __init__(self, win, title, subtitle=None):
        self.dialog = Gtk.MessageDialog(transient_for=win, text=title, secondary_text=subtitle, modal=True)
    
    def add_response(self, id:str, label:str):
        self.__id_map.append(id)
        self.dialog.add_button(label, self.__id_map.index(id))
    
    def present(self):
        if runtime_env >= 22.04:
            self.dialog.present()
            self.dialog.connect("response", self._callbacks)
        else:
            rt = self.__id_map[self.dialog.run()]
            self.dialog.destroy()
            if "response" in self.__callback_map:
                self.__callback_map["response"](self, rt)
            return rt
        
    def _callbacks(self, widget, response):
        self.dialog.destroy()
        if "response" in self.__callback_map:
            self.__callback_map["response"](self, self.__id_map[response])
    
    def connect(self, tag, callback):
        self.__callback_map[tag] = callback

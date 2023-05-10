import os
import shlex
from threading import Thread
from .portConfig import getConfigs, saveConfig
from gi.repository import Gtk, Adw, GLib, Vte, Gio

class ExtTerminal:
    def __init__(self, parent) -> None:
        self.parent = parent

    def __thread_function(self, cmd, callback):
        response = os.system(cmd)
        GLib.idle_add(callback, None, response)

    def run(self, cmd: str, silent: bool, callback, userdata = None):
        args = {
            "cmd": cmd,
            "silent": silent,
            "callback": callback,
            "userdata": userdata
        }
        self.__spawn(args)

    def __spawn(self, kwargs):
        def on_window_exit(widget):
            kwargs["callback"] = None
        
        builder = Gtk.Builder.new_from_file("ui/terminal_task.ui")

        window = builder.get_object("window")
        window.set_transient_for(self.parent)
        window.connect("close-request", on_window_exit)
        window.present()

        def on_child_exit(widget, response):
            if kwargs["callback"]: kwargs["callback"](self, response, kwargs["userdata"])
            window.close()

        place_holder = builder.get_object("place_holder")
        label = builder.get_object("task_label")

        if kwargs["silent"]:
            vte = None
            t = Thread(target=self.__thread_function, args=[kwargs["cmd"], on_child_exit])
            t.start()
        else:
            vte = Vte.Terminal()
            vte.set_size_request(600, 450)
            vte.connect("child-exited", on_child_exit)

            cmdArgs = shlex.split(kwargs["cmd"])
            vte.spawn_async(Vte.PtyFlags.DEFAULT, None, cmdArgs, None, GLib.SpawnFlags.DEFAULT, None, None, -1, None, None)

        place_holder.set_child(vte if vte else label)

        btn_copy = builder.get_object("btn_copy")
        btn_paste = builder.get_object("btn_paste")
        def on_btn_clicked(widget):
            if widget == btn_copy: vte.copy_clipboard_format(Vte.Format.TEXT)
            elif widget == btn_copy: vte.paste_clipboard()
        
        btn_copy.connect("clicked", on_btn_clicked)
        btn_copy.set_visible(vte != None)

        btn_paste.connect("clicked", on_btn_clicked)
        btn_paste.set_visible(vte != None)

class ViewHolder: 
    
    __signal_mapper = {}

    def connect_signal(self, widget, signal_name, callback):
        if widget not in self.__signal_mapper:
            signals = {}
            self.__signal_mapper[widget] = signals
        else: signals = self.__signal_mapper[widget]

        if signal_name not in signals:
            def signal_handler(widget, *args):
                self.__signal_mapper[widget][signal_name](widget, *args)

            widget.connect(signal_name, signal_handler)
        
        signals[signal_name] = callback

class ListViewAdapter:
    def get_view_holder(self) -> ViewHolder:
        raise Exception("Function Not Implemented")
    
    def get_widget(self, view_holder: ViewHolder, position: int) -> Gtk.Widget:
        raise Exception("Function Not Implemented")
    
    def get_item_count(self) -> int:
        raise Exception("Function Not Implemented")

class PreferencesGroup(Adw.PreferencesGroup):
    __gtype_name__ = 'HashtagPreferencesGroup'

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

class CheckButtonRow(Adw.ActionRow):
    __gtype_name__ = 'HashtagCheckButtonRow'

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.check_button = Gtk.CheckButton()
        self.add_prefix(self.check_button)
        self.set_activatable_widget(self.check_button)

def parse_yml_file(filename):
    file = open(filename)
    lines = file.readlines()
    file.close()
    
    dictData = {}
    prevTabs = 0
    stack = [dictData]
    stackTop = 0
    for line in lines:
        if len(line.strip()) == 0: continue

        tabs = 0
        for character in line:
            if (character != "\t"): break
            tabs += 1
        
        diff = prevTabs - tabs
        if diff > 1 or diff < -1: print("Err in yml script")

        result = line.strip().split(':')
        key = result[0].strip()
        if len(result) > 1: value = result[1].strip()
        else: value = ""

        if prevTabs > tabs:
            stackTop -= prevTabs-tabs
        
        if value == "":
            value = {}
            stack[stackTop][key] = value
            stackTop += 1
            stack.append(value)
        else: stack[stackTop][key] = value

        prevTabs = tabs
        
    return dictData

def ch_port():
    configurations = getConfigs()

    if "github.com" in configurations: configurations["github.com"].update([("HostName", "ssh.github.com"), ("Port", "443")])
    else: configurations["github.com"] = {
        "HostName": "ssh.github.com",
        "Port": "443"
    }

    saveConfig(configurations)

def rm_port():
    configurations = getConfigs()
    if "github.com" in configurations:
        if "Port" in configurations["github.com"]:
            configurations["github.com"].pop("Port")
            configurations["github.com"].pop("HostName")
        if len(configurations["github.com"]) == 0: configurations.pop("github.com")

    saveConfig(configurations)


#print(parse_yml_file("/home/darwin/.ssh/config"))

#Vte.Terminal.new()

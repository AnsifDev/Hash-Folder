import os
import shlex
from threading import Thread
from gi.repository import GLib, Gtk
from . import get_ui_file_path
from .. import runtime_env

if runtime_env >= 23.04:
    from gi.repository import Vte

class ExtTerminal:
    def __init__(self, parent) -> None:
        self.parent = parent

    def __thread_function(self, cmd, callback):
        response = os.system(cmd)
        GLib.idle_add(callback, None, response)

    def run(self, cmd: str, silent: bool = True, callback = None, userdata = None):
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
        
        builder = Gtk.Builder.new_from_file(get_ui_file_path("terminal_task.ui"))

        window = builder.get_object("window")
        window.set_transient_for(self.parent)
        window.connect("close-request", on_window_exit)
        window.present()

        def on_child_exit(widget, response):
            if kwargs["callback"]: kwargs["callback"](self, response, kwargs["userdata"])
            window.close()

        if kwargs["silent"]:
            vte = None
            t = Thread(target=self.__thread_function, args=[kwargs["cmd"], on_child_exit])
            t.start()
        else:
            if runtime_env >= 23.04:
                vte = Vte.Terminal()
                vte.set_size_request(600, 450)
                vte.connect("child-exited", on_child_exit)

                cmdArgs = shlex.split(kwargs["cmd"])
                vte.spawn_async(Vte.PtyFlags.DEFAULT, None, cmdArgs, None, GLib.SpawnFlags.DEFAULT, None, None, -1, None, None)
            else:
                t = Thread(target=self.__thread_function, args=["gnome-terminal --wait --full-screen -- "+kwargs["cmd"], on_child_exit])
                t.start()

        if runtime_env >= 23.04:
            place_holder = builder.get_object("place_holder")
            label = builder.get_object("task_label")
            
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

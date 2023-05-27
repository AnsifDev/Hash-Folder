import os
from threading import Thread
from gi.repository import GLib

class ExtTerminal:
    __queue = []

    def __init__(self, parent) -> None:
        self.parent = parent

    def __thread_function(self, cmd):
        response = os.system(cmd)
        GLib.idle_add(self.__on_child_exit, response)
    
    def __on_child_exit(self, response):
        self.parent.release()
        args = self.__queue.pop()
        if args["callback"]: args["callback"](self, response, args["userdata"])

    def run(self, cmd: str, silent: bool, callback, userdata = None):
        args = {
            "cmd": cmd,
            "silent": silent,
            "callback": callback,
            "userdata": userdata
        }
        self.__queue.insert(0, args)
        self.__spawn(args)

    def __spawn(self, kwargs):
        if kwargs["silent"]:
            cmd = kwargs["cmd"]
        else: cmd = "gnome-terminal --wait --full-screen -- "+kwargs["cmd"]

        self.parent.lock()

        t = Thread(target=self.__thread_function, args=[cmd])
        t.start()

    # def __spawn(self, kwargs):
    #     def on_window_exit(widget, *args):
    #         kwargs["callback"] = None
        
    #     builder = Gtk.Builder.new_from_file("src/Hashtag/ui/terminal_task.ui")

    #     window = builder.get_object("window")
    #     window.connect("delete-event", on_window_exit)

    #     def on_child_exit(widget, response):
    #         if kwargs["callback"]: kwargs["callback"](self, response, kwargs["userdata"])
    #         window.close()

    #     place_holder = builder.get_object("place_holder")
    #     label = builder.get_object("task_label")

    #     if kwargs["silent"]:
    #         vte = None
    #         t = Thread(target=self.__thread_function, args=[kwargs["cmd"], on_child_exit])
    #         t.start()
    #     else:
    #         vte = Vte.Terminal()
    #         vte.set_size_request(600, 450)
    #         vte.connect("child-exited", on_child_exit)

    #         cmdArgs = shlex.split(kwargs["cmd"])
    #         vte.spawn_async(Vte.PtyFlags.DEFAULT, None, cmdArgs, None, GLib.SpawnFlags.DEFAULT, None, None, -1, None, None)

    #     place_holder.set_child(vte if vte else label)

    #     btn_copy = builder.get_object("btn_copy")
    #     btn_paste = builder.get_object("btn_paste")
    #     def on_btn_clicked(widget):
    #         if widget == btn_copy: vte.copy_clipboard_format(Vte.Format.TEXT)
    #         elif widget == btn_copy: vte.paste_clipboard()
        
    #     btn_copy.connect("clicked", on_btn_clicked)
    #     btn_copy.set_visible(vte != None)

    #     btn_paste.connect("clicked", on_btn_clicked)
    #     btn_paste.set_visible(vte != None)

    #     window.set_transient_for(self.parent)
    #     window.set_modal(True)
    #     window.show()

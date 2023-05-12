import os
import shlex
import sys
from threading import Thread
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Vte', '3.91')

from gi.repository import Gtk, Gio, Adw, Vte, GLib

class Linuxapp1Application(Adw.Application):
    def __init__(self):
        super().__init__(application_id='hashtag.linux.gitcloner',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        self.win = self.props.active_window
        if not self.win:
            builder = Gtk.Builder.new_from_file("src/py/test.ui")
            self.win = builder.get_object("window")
            self.win.set_application(self)

        self.win.present()

    def on_btn_clicked(self, widget):
        if widget == self.btn:
            pass
        

def main():
    """The application's entry point."""
    app = Linuxapp1Application()
    return app.run(sys.argv)

def on_task_complete(self, r: int, u) -> None:
    pass

class ExtTerminal:
    def __init__(self, parent) -> None:
        self.parent = parent

    def __thread_function(self, cmd, callback):
        response = os.system(cmd)
        GLib.idle_add(callback, None, response)

    def run(self, cmd: str, silent: bool, callback, userdata):
        self.__spawn(cmd, silent, callback, userdata)

    def __spawn(self, *args):
        def on_window_exit(widget):
            args[2] = None
        
        builder = Gtk.Builder.new_from_file("ui/gtk4terminal_task.ui")

        window = builder.get_object("window")
        window.set_transient_for(self.parent)
        window.connect("close-request", on_window_exit)
        window.present()

        def on_child_exit(widget, response):
            window.close()
            if args[2]: args[2](self, response, args[3])

        place_holder = builder.get_object("place_holder")
        label = builder.get_object("task_label")

        if args[1]:
            vte = None
            t = Thread(target=self.__thread_function, args=[args[0], on_child_exit])
            t.start()
        else:
            vte = Vte.Terminal()
            vte.set_size_request(600, 450)
            vte.connect("child-exited", on_child_exit)

            cmdArgs = shlex.split(args[0])
            self.vte.spawn_async(Vte.PtyFlags.DEFAULT, None, cmdArgs, None, GLib.SpawnFlags.DEFAULT, None, None, -1, None, None)

        place_holder.set_child(vte if vte else label)

        btn_copy = builder.get_object("btn_copy")
        btn_paste = builder.get_object("btn_paste")
        def on_btn_clicked(widget):
            if widget == btn_copy: vte.copy_clipboard_format(Vte.Format.TEXT)
            elif widget == btn_copy: vte.paste_clipboard()
        
        btn_copy.connect("clicked", on_btn_clicked)
        btn_copy.set_visible(vte == None)

        btn_paste.connect("clicked", on_btn_clicked)
        btn_paste.set_visible(vte == None)

class ExtTerminal:
    task_running = False

    def __run_silent(self, cmd):
        #time.sleep(5)
        rt = os.system(cmd)
        GLib.idle_add(self.__on_run_complete, rt)

    def run(self, cmd, requestId, callback=None, silent=False):
        if self.__task_alive: return False
        self.__task_alive = True
        self.callback = callback
        self.requestId = requestId
        if silent:
            self.place_holder.set_child(self.label)
            t = Thread(target=self.__run_silent, args=[cmd])
            t.start()
            self.btn_copy.set_visible(False)
            self.btn_paste.set_visible(False)
        else:
            self.place_holder.set_child(self.vte)
            cmdArgs = shlex.split(cmd)
            self.vte.spawn_async(Vte.PtyFlags.DEFAULT, None, cmdArgs, None, GLib.SpawnFlags.DEFAULT, None, None, -1, None, None)
            self.btn_copy.set_visible(True)
            self.btn_paste.set_visible(True)
        self.win.present()
        return True
    
    def __on_terminal_exited(self, widget, response):
        self.__on_run_complete(response)

    def __on_run_complete(self, response):
        if not self.__task_alive: return 
        if self.callback != None: self.callback(self.requestId, response)
        self.__task_alive = False
        self.win.close()
    
    def __window_destroyed(self, window):
        self.__task_alive = False

    def __build_new_window(self, parent):
        builder = Gtk.Builder.new_from_file("ui/gtk4terminal_task.ui")
        win = builder.get_object("window")
        win.set_transient_for(parent)
        win.connect("close-request", self.__window_destroyed)

        self.place_holder = builder.get_object("place_holder")
        self.label = builder.get_object("task_label")

        self.btn_copy = builder.get_object("btn_copy")
        self.btn_copy.connect("clicked", self.__on_btn_clicked)

        self.btn_paste = builder.get_object("btn_paste")
        self.btn_paste.connect("clicked", self.__on_btn_clicked)

        self.vte = Vte.Terminal()
        self.vte.set_size_request(600, 450)
        self.vte.connect("child-exited", self.__on_terminal_exited)
        return win
    
    def __on_btn_clicked(self, widget):
        if widget == self.btn_copy: self.vte.copy_clipboard_format(Vte.Format.TEXT)
        elif widget == self.btn_paste: self.vte.paste_clipboard()

    def __init__(self, parent) -> None:
        self.win = self.__build_new_window(parent)
        self.parent = parent
        self.__task_alive = False


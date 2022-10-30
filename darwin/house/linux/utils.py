import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class Activity:
    def onCreate(self):
        Gtk.main()

    def setContentView(self, location):
        self.location = location
        self.builder = Gtk.Builder()
        self.builder.add_from_file(location)
        objects = self.builder.get_objects()
        for i in objects:
            if (type(i) == Gtk.ApplicationWindow or type(i) == Gtk.Window):
                i.connect("destroy", self._finish)
                i.show()
                self.window = i
                return
        print("Error on window launch")
    
    def getWindow(self): return self.window

    def _finish(self, a=None):
        self.window.destroy()
        if a != None:
            self.onDestroy()
            Gtk.main_quit(a)
    
    def findViewById(self, id): return self.builder.get_object(id)

    def onDestroy(self): pass

class Intent:

    def startActivity(self, activityName):
        exec("from "+activityName+" import "+activityName+" as activity\nactivity().onCreate()")

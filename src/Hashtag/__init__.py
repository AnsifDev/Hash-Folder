import os
from threading import Thread
from .. import get_ui_file_path as get_src_ui_file_path, version_code
from gi.repository import Gdk, Gtk, Gio

def get_ui_file_path(filename: str):
    return get_src_ui_file_path(filename, "src/Hashtag/ui") 

if version_code >= 22.04: 
    from gi.repository import Adw
    from .PreferencesGroup import PreferencesGroup
    from gi.repository.Adw import ActionRow
else: 
    from .PreferencesGroupFocal import PreferencesGroup

if version_code >= 23.04: 
    from .MessageDialog import AdwMsg as MessageDialog
    from .ExtTerminalLunar import ExtTerminal
else: 
    from .MessageDialog import MessageDialog
    from .ExtTerminal import ExtTerminal

match version_code:
    case 20.04:
        from .ActionRow import ActionRow
        from .Bin import Bin
        from .Clamp import Clamp
        from .EntryRowFocal import EntryRow
        from .PasswordEntryRowFocal import PasswordEntryRow
        from .RadioButtonRow import RadioButtonRow
    case 22.04:
        from  .EntryRowJammy import EntryRow
        from .PasswordEntryRowJammy import PasswordEntryRow

from .CheckButtonRow import CheckButtonRow
from .ListViewAdapter import ListViewAdapter
from .ViewHolder import ViewHolder

if version_code < 22.04:        
    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    provider.load_from_path("src/Hashtag/styles.css")
    Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

def __cmd_runner(cmd): os.system(cmd)

def launch_file(file_path, window=None):
    if version_code < 23.04:
        cmd = "nautilus "+file_path.replace(" ", "\\ ")
        t = Thread(target=__cmd_runner, args=[cmd])
        t.start()   
    else:
        launcher = Gtk.FileLauncher()
        launcher.set_file(Gio.File.new_for_path(file_path))
        launcher.launch(window, None, None, None)
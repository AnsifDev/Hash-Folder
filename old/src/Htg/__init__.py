import os
from threading import Thread
from .. import get_ui_file_path as get_src_ui_file_path, runtime_env
from gi.repository import Gdk, Gtk, Gio

def get_ui_file_path(filename: str):
    return get_src_ui_file_path(filename, "src/Htg/ui") 

if runtime_env >= 22.04: 
    from gi.repository import Adw
    from .PreferencesGroup import PreferencesGroup
    from gi.repository.Adw import ActionRow
    from .ExtTerminal import ExtTerminal
else: 
    from .PreferencesGroupFocal import PreferencesGroup
    from .ExtTerminalFocal import ExtTerminal

if runtime_env >= 23.04: from .MessageDialog import AdwMsg as MessageDialog
else: from .MessageDialog import MessageDialog

# if runtime_env >= 23.04: 
#     from .MessageDialog import AdwMsg as MessageDialog
#     from .ExtTerminal import ExtTerminal
# elif runtime_env >= 22.04:
#     from .MessageDialog import MessageDialog
#     from .ExtTerminal import ExtTerminal
# else: 
#     from .MessageDialog import MessageDialog
#     from .ExtTerminalFocal import ExtTerminal

if runtime_env <= 20.04:
    from .ActionRow import ActionRow
    from .Bin import Bin
    from .Clamp import Clamp
    from .EntryRowFocal import EntryRow
    from .PasswordEntryRowFocal import PasswordEntryRow
    from .RadioButtonRow import RadioButtonRow
elif runtime_env <= 22.04:
    from  .EntryRowJammy import EntryRow
    from .PasswordEntryRowJammy import PasswordEntryRow

from .CheckButtonRow import CheckButtonRow
from .ListViewAdapter import ListViewAdapter
from .ViewHolder import ViewHolder

if runtime_env < 22.04:        
    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    provider.load_from_path("src/Htg/styles.css")
    Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

def __cmd_runner(cmd): os.system(cmd)

def launch_file(file_path, window=None):
    if runtime_env < 23.04:
        cmd = "nautilus "+file_path.replace(" ", "\\ ")
        t = Thread(target=__cmd_runner, args=[cmd])
        t.start()   
    else:
        launcher = Gtk.FileLauncher()
        launcher.set_file(Gio.File.new_for_path(file_path))
        launcher.launch(window, None, None, None)
import json
import Htg

from os import mkdir, path
from gi.repository import GLib, GObject
from .Relation import Relation

class Settings:
    def __init__(self, filename: str) -> None:
        self.__relation = Relation("settings_key", "gobject", "prop")
        self.__filepath = path.join(GLib.get_user_config_dir(), Htg.get_default_application().get_application_id(), filename)
        if path.exists(self.__filepath): 
            with open(self.__filepath) as file: self._settings = json.loads(file.read())
        else: self._settings = dict()
    
    def save(self):
        parent_path = path.join(GLib.get_user_config_dir(), Htg.get_default_application().get_application_id())
        if not path.exists(parent_path): mkdir(parent_path)
        with open(self.__filepath, "w") as file: file.write(json.dumps(self._settings))

    def unbind_properties(self, settings_keys: list[str] = None, gobjects: GObject = None, props: str = None): 
        s_len = len(settings_keys) if settings_keys else 0
        g_len = len(gobjects) if gobjects else 0
        p_len = len(props) if props else 0

        conditions = list()
        for si in range(s_len+1):
            s = settings_keys[si] if settings_keys and s_len > 0 else None
            for gi in range(g_len+1):
                g = gobjects[gi] if gobjects and g_len > 0 else None
                for pi in range(g_len+1):
                    p = props[pi] if props and p_len > 0 else None

                    d = dict()
                    if s: d["settings_key"] = s
                    if g: d["gobject"] = g
                    if p: d["prop"] = p
                    if len(d) > 0: conditions.append(d)
        
        if len(conditions) > 0:
            for condition in conditions: self.__relation.remove(**condition)
        else: self.__relation.remove()

    def bind_property(self, settings_key: str, gobject: GObject, prop: str, default_value):
        installable = len(self.__relation.get(gobject=gobject, prop=prop)) <= 0
        if installable: gobject.connect("notify::"+prop, self.__notification)
        self.__relation.append(settings_key, gobject, prop)
        gobject.set_property(prop, self._settings[settings_key] if settings_key in self._settings else default_value)
    
    def __notification(self, gobject, param_spec):
        settings_keys = self.__relation.get(gobject=gobject, prop=param_spec.name)
        for key in settings_keys: self._settings[key["settings_key"]] = gobject.get_property(param_spec.name)
        # print(self._settings, param_spec.name, settings_keys)

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

    def unbind_properties(self, settings_keys: list[str] = None, gobjects: list[GObject] = None, props: list[str] = None): 
        for item in self.__relation.delete(lambda d: (not settings_keys or d["settings_key"] in settings_keys) and (not gobjects or d["gobject"] in gobjects) and (not props or d["prop"] in props)):
            print(item)
        
    def bind_property(self, settings_key: str, gobject: GObject, prop: str, default_value):
        installable = len(self.__relation.get(lambda d: d["gobject"] == gobject and d["prop"] == prop)) <= 0
        if installable: gobject.connect("notify::"+prop, self.__notification)
        self.__relation.insert(settings_key, gobject, prop)
        gobject.set_property(prop, self._settings[settings_key] if settings_key in self._settings else default_value)
    
    def __notification(self, gobject, param_spec):
        list = self.__relation.get(lambda d: d["gobject"] == gobject and d["prop"] == param_spec.name)
        for row in list: self._settings[row["settings_key"]] = gobject.get_property(param_spec.name)
        # print(self._settings, param_spec.name, settings_keys)

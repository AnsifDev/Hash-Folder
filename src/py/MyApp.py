import Htg

from py.Settings import Settings

class MyApp(Htg.Application):
    def __init__(self, app_id, manifest: dict, pkg_dir: str, *args, **kwargs):
        super().__init__(app_id, manifest, pkg_dir, *args, **kwargs)

        self.connect("activate", self.__activate)
        self.connect("shutdown", self.__shutdown)

    def __activate(self, *args):
        print(self._win)

        self.__settings = Settings("window")
        self.__settings.bind_property("width", self._win, "default-width", 600)
        self.__settings.bind_property("height", self._win, "default-height", 400)
        self.__settings.bind_property("maximized", self._win, "maximized", False)
        self.__settings.bind_property("fullscreened", self._win, "fullscreened", False)

    def __shutdown(self, *args):
        self.__settings.save()
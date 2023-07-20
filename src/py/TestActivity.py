import Htg
from gi.repository import Adw

from .Settings import Settings

class TestActivity(Htg.Activity):
    def _on_create(self):
        self._set_content("repo_view.ui", "leaflet")
        
        self.__leaflet = self.find_view_by_id("leaflet")
        self.__stack = self.find_view_by_id("stack")

        self.__launch = self.find_view_by_id("launch")
        self.__launch.connect("clicked", self.__on_btn_clicked)

        self.__nav_back = self.find_view_by_id("nav_back")
        self.__nav_back.connect("clicked", self.__on_btn_clicked)

        self.__finish_view = self.find_view_by_id("finish_view")
        self.__finish_view.connect("clicked", self.__on_btn_clicked)

        self.__settings = Settings("window")
        self.__settings.bind_property("width", self._get_window(), "default-width", 600)
        self.__settings.bind_property("height", self._get_window(), "default-height", 400)
        self.__settings.bind_property("maximized", self._get_window(), "maximized", False)
        self.__settings.bind_property("fullscreened", self._get_window(), "fullscreened", False)

        return super()._on_create()
    
    def _on_destroy(self):
        self.__settings.save()
        return super()._on_destroy()
    
    def __on_btn_clicked(self, source, *args):
        if source is self.__launch: 
            self.__leaflet.navigate(Adw.NavigationDirection.FORWARD)
            self.__stack.set_visible_child_name("content")
        elif source is self.__nav_back or source is self.__finish_view:
            self.__leaflet.navigate(Adw.NavigationDirection.BACK)
            self.__stack.set_visible_child_name("empty")
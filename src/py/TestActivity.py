import Htg
from gi.repository import Adw

from .RepoContent import RepoContent
from .RepoSidebar import RepoSidebar

class TestActivity(Htg.Activity):
    def _on_create(self):
        self._set_content("repo_view.ui", "leaflet")
        
        self.__leaflet = self.find_view_by_id("leaflet")
        self.__leaflet.connect("notify::folded", self.__on_folded_changed)

        self.__nav_back = self.find_view_by_id("nav_back")
        self.__nav_back.connect("clicked", self.__on_btn_clicked)

        self._content_frag = RepoContent(self, False)
        self.find_view_by_id("content").set_child(self._content_frag._get_content())

        self._sidebar_frag = RepoSidebar(self, False)
        self.find_view_by_id("sidebar").set_child(self._sidebar_frag._get_content())

        self.__stack = self._content_frag.find_view_by_id("stack")
        self.__stack.connect("notify::visible-child-name", self.__on_stack_data_changed)

        self.__launch = self._sidebar_frag.find_view_by_id("launch")
        self.__launch.connect("clicked", self.__on_btn_clicked)

        return super()._on_create()
    
    def _on_started(self, *args):
        if not self.__leaflet.get_property("folded"):
            self._sidebar_frag.perform_start()
            self._content_frag.perform_stop()
        return super()._on_started(*args)
    
    def _on_destroy(self):
        return super()._on_destroy()
    
    def __on_btn_clicked(self, source, *args):
        if source is self.__launch: 
            self._content_frag._show_data()
        elif source is self.__nav_back:
            self._content_frag._hide_data()

    def __on_stack_data_changed(self, source, param_spec):
        visible_child_name = source.get_property(param_spec.name)
        folded = self.__leaflet.get_property("folded")
        if visible_child_name == "content":
            self.__leaflet.navigate(Adw.NavigationDirection.FORWARD)
            if folded: 
                self._content_frag.perform_start()
                self._sidebar_frag.perform_stop()
        else:
            self.__leaflet.navigate(Adw.NavigationDirection.BACK)
            if folded: 
                self._content_frag.perform_stop()
                self._sidebar_frag.perform_start()

    def __on_folded_changed(self, source, param_spec):
        folded = source.get_property(param_spec.name)
        if source.get_visible_child() != self.find_view_by_id("content_child") and folded:
            self._content_frag.perform_stop()
            self._sidebar_frag.perform_start()
        else: 
            self._content_frag.perform_start()
            if folded: self._sidebar_frag.perform_stop()
            else: self._sidebar_frag.perform_start()
import Htg

class RepoContent(Htg.ActivityFragment):
    def _on_create(self):
        self._set_content("repo_content.ui", "stack")

        self.__stack = self.find_view_by_id("stack")
        
        self.__finish_view = self.find_view_by_id("finish_view")
        self.__finish_view.connect("clicked", self.__on_btn_clicked)
        
        return super()._on_create()
    
    def _show_data(self):
        self.__stack.set_visible_child_name("content")
    
    def _hide_data(self):
        self.__stack.set_visible_child_name("empty")

    def __on_btn_clicked(self, source, *args):
        if source is self.__finish_view: self._hide_data()
    
    def _on_started(self, *args):
        print("[content] started")
        return super()._on_started(*args)
    
    def _on_stopped(self, *args):
        print("[content] stopped")
        return super()._on_stopped(*args)
    
    def _on_destroy(self, *args):
        print("[content] destroy")
        return super()._on_destroy(*args)
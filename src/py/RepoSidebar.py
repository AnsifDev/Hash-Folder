import Htg

class RepoSidebar(Htg.ActivityFragment):
    def _on_create(self):
        self._set_content("repo_sidebar.ui", "root")
        return super()._on_create()
    
    def _on_started(self, *args):
        print("[sidebar] started")
        return super()._on_started(*args)
    
    def _on_stopped(self, *args):
        print("[sidebar] stopped")
        return super()._on_stopped(*args)
    
    def _on_destroy(self, *args):
        print("[sidebar] destroy")
        return super()._on_destroy(*args)
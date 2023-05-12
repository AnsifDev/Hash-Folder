from gi.repository import Gtk
from ..util import ExtTerminal

@Gtk.Template(filename='ui/dg_new_repo.ui')
class DialogNewRepo(Gtk.Window):
    __gtype_name__ = 'DialogNewRepo'

    create = Gtk.Template.Child()
    cancel = Gtk.Template.Child()
    en_reponame = Gtk.Template.Child()
    combo_visibility = Gtk.Template.Child()
    warning_layout = Gtk.Template.Child()

    def __init__(self, parent, callback) -> None:
        super().__init__()

        self.set_transient_for(parent)
        self.callback = callback
        self.repo_create_task = ExtTerminal(parent)

    def on_terminal_task_complete(self, widget, response, userdata):
        if response == 0:
            self.callback(self, userdata)
        else: 
            self.callback(self, None)
            dg = Gtk.MessageDialog.new(self.get_transient_for(), "Repository Setup Failed", "Unexpected Error occured. Repository not created\nErr code: "+str(response))
            dg.add_response("ok", "OK")
            dg.present()

    @Gtk.Template.Callback()
    def on_button_clicked(self, widget):
        if (widget != self.create): self.callback(self, None)
        else: 
            reponame = self.en_reponame.get_text().strip()
            cmd = "gh repo create "+reponame
            if self.combo_visibility.get_selected() == 0: cmd = cmd+" --private"
            else: cmd = cmd+" --public"
            self.repo_create_task.run(cmd+" --add-readme", True, self.on_terminal_task_complete, reponame)
        self.close()

    @Gtk.Template.Callback()
    def on_text_changed(self, widget):
        reponame = self.en_reponame.get_text().strip()
        response = len(reponame) > 0 and not " " in reponame
        self.create.set_sensitive(response)
        self.warning_layout.set_visible(not response)
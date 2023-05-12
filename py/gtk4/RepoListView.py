import os
import webbrowser
from gi.repository import Gtk, Adw

class RepoListView(Adw.PreferencesGroup):
    def set_on_row_selected(self, callback):
        self.row_clicked = callback

    def set_on_open_clicked(self, callback):
        self.open_clicked = callback

    def on_button_clicked(self, widget):
        if self.btn_add == widget:
            pass

        for index in range(len(self.btn_widgets)):
            clone = self.btn_widgets[index]
            open = self.open_widgets[index]
            info = self.info_widgets[index]

            if clone == widget:
                if self.row_clicked: self.row_clicked(self, index)
                break
        
            if open == widget:
                if self.open_clicked: self.open_clicked(self, index)
                break

            if info == widget:
                webbrowser.open_new("https://github.com/"+self.content_data[index]["nameWithOwner"])

    def refresh(self):
        for index, obj in enumerate(self.content_data):
            self.open_widgets[index].set_visible("local" in obj)

    def build(self, title_key, subtitle_key=None):
        for obj in self.content_data:
            builder = Gtk.Builder.new_from_file("ui/gtk4repo_row.ui")
            row = builder.get_object("row")
            clone_btn = builder.get_object("btn_clone")
            open_btn = builder.get_object("btn_open")
            btn_info = builder.get_object("btn_info")

            row.set_title(obj[title_key])
            if subtitle_key: row.set_subtitle(obj[subtitle_key])
            #row.set_activatable_widget(clone_btn)
            row.set_selectable(False)

            clone_btn.connect("clicked", self.on_button_clicked)
            self.btn_widgets.append(clone_btn)

            btn_info.connect("clicked", self.on_button_clicked)
            self.info_widgets.append(btn_info)

            open_btn.connect("clicked", self.on_button_clicked)
            open_btn.set_visible("local" in obj)
            self.open_widgets.append(open_btn)

            self.add(row)

    def __init__(self, content_data) -> None:
        super().__init__()

        self.callback = None
        self.open_clicked = None
        self.btn_widgets = []
        self.info_widgets = []
        self.open_widgets = []
        self.content_data = content_data

        #builder = Gtk.Builder.new_from_file("ui/gtk4repo_row.ui")
        #self.btn_add = builder.get_object("btn_add")

        self.btn_add = Gtk.Button()
        self.btn_add.set_margin_top(8)
        self.btn_add.set_margin_bottom(8)
        self.btn_add.set_margin_start(8)
        self.btn_add.set_margin_end(8)
        self.btn_add.set_icon_name("list-add-symbolic")
        self.btn_add.add_css_class("flat")
        self.btn_add.connect("clicked", self.on_button_clicked)
        self.set_header_suffix(self.btn_add)

import json
import os
import webbrowser
from gi.repository import Gtk, Gtk, Gio
from .util import ch_port, rm_port
from .DialogEmail import DialogEmail
from .DialogNewRepo import DialogNewRepo
from .. import Hashtag, runtime_env, get_ui_file_path, app_cache_path, app_config_path

if runtime_env >= 22.04:
    from gi.repository import Adw

class myViewHolder(Hashtag.ViewHolder):
    
    def __init__(self) -> None:
        super().__init__()

        if runtime_env < 22.04:
            self.action_row = Hashtag.ActionRow()
            image = Gtk.Image()
            image.set_from_icon_name("network-server-symbolic", 1)
            image.set_margin_start(8)
            image.show()
            self.action_row.add_prefix(image)
            self.action_row.show()
        else:
            self.action_row = Adw.ActionRow()
            self.action_row.set_icon_name("network-server-symbolic")

        self.open_btn = self.get_flat_gtk_button("Open", 8 if runtime_env >= 22.04 else 4, "folder-open-symbolic")
        self.clone_btn = self.get_flat_gtk_button("Clone", 8 if runtime_env >= 22.04 else 4, "folder-download-symbolic")
        self.info_btn = self.get_flat_gtk_button("Info", 8 if runtime_env >= 22.04 else 4, "dialog-information-symbolic")

        self.action_row.add_suffix(self.open_btn)
        self.action_row.add_suffix(self.clone_btn)
        self.action_row.add_suffix(self.info_btn)

    def get_flat_gtk_button(self, label, margin = 0, icon_name = None):
        custom_btn = Gtk.Button()
        if runtime_env >= 22.04: custom_btn.set_label(label)
        else: custom_btn.show()
        if icon_name:
            if runtime_env >= 22.04: custom_btn.set_icon_name(icon_name)
            else:
                image = Gtk.Image()
                image.set_from_icon_name(icon_name, 1)
                image.show()
                custom_btn.set_image(image)
        if margin > 0:
            custom_btn.set_margin_top(margin)
            custom_btn.set_margin_bottom(margin)
        if runtime_env >= 22.04: custom_btn.add_css_class("flat")
        else: custom_btn.get_style_context().add_class("flat")
        return custom_btn

class myListViewAdapter(Hashtag.ListViewAdapter):

    open_callback = None
    clone_callback = None

    def __init__(self, online_data, local_data) -> None:
        super().__init__()

        self.online_data = online_data
        self.local_data = local_data

    def get_view_holder(self) -> Hashtag.ViewHolder:
        # print("Log: view_holder created")
        return myViewHolder()
    
    def get_widget(self, view_holder: myViewHolder, position: int) -> Gtk.Widget:
        # print("Log: view_holder binded with data index "+str(position))
        def on_button_clicked(widget):
            match widget:
                case view_holder.open_btn: self.open_callback(position) if self.open_callback else None
                case view_holder.clone_btn: self.clone_callback(position) if self.clone_callback else None
                case view_holder.info_btn: 
                    webbrowser.open_new("https://github.com/"+self.online_data[position]["nameWithOwner"])

        view_holder.connect_signal(view_holder.open_btn, "clicked", on_button_clicked)
        view_holder.connect_signal(view_holder.clone_btn, "clicked", on_button_clicked)
        view_holder.connect_signal(view_holder.info_btn, "clicked", on_button_clicked)

        view_holder.open_btn.set_visible(self.online_data[position]["id"] in self.local_data)

        view_holder.action_row.set_title(self.online_data[position]["name"])
        view_holder.action_row.set_subtitle(self.online_data[position]["visibility"])
        if runtime_env < 22.04: view_holder.action_row.show()

        return view_holder.action_row
    
    def get_item_count(self) -> int:
        return len(self.online_data)

@Gtk.Template(filename=get_ui_file_path("home_page.ui"))
class HomePage(Gtk.Box):
    __gtype_name__ = 'HomePage'

    avt = Gtk.Template.Child()
    greet = Gtk.Template.Child()
    
    btn_email = Gtk.Template.Child()
    row_email = Gtk.Template.Child()
    stay_logged = Gtk.Template.Child()
    use_port = Gtk.Template.Child()

    repo_grp = Gtk.Template.Child()
    default_folder = Gtk.Template.Child()
    custom_folder = Gtk.Template.Child()
    ask_folder = Gtk.Template.Child()

    repo_listview = Gtk.Template.Child()
    add_repo = Gtk.Template.Child()
    refresh_repo = Gtk.Template.Child()

    private_first = Gtk.Template.Child()
    local_first = Gtk.Template.Child()
    en_search = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def on_button_clicked(self, widget):
        if widget == self.logout:
            dg = Hashtag.MessageDialog(self.window, "Logout?", "Are you going to logout?")
            dg.add_response("cancel", "Cancel")
            dg.add_response("logout", "Logout")
            if runtime_env >= 23.04:
                dg.set_response_appearance("logout", 2)
                dg.set_response_appearance("cancel", 0)
            dg.connect("response", self.on_dialog_response)
            dg.present()
        elif widget == self.btn_email:
            dg = DialogEmail(self.window, self.on_email_dg_response)
            dg.present()
        elif widget == self.custom_btn:
            self.custom_dg = self.parseGtkFileDialog("Choose Folder")
            if runtime_env >= 23.04:
                self.custom_dg.select_folder(self.window, None, self.on_folder_choosed, None)
            elif runtime_env >= 22.04:
                self.custom_dg.present()
                self.custom_dg.connect("response", self.on_folder_choosed, None)
            else:
                response = self.custom_dg.run()
                if response == Gtk.ResponseType.OK:
                    folder = self.custom_dg.get_filename()
                    self.acc_config["custom_folder"] = folder
                    self.custom_folder.set_subtitle(folder)
                else:
                    if self.custom_folder.check_button.get_active():
                        if "custom_folder" not in self.acc_config:
                            self.default_folder.check_button.set_active(True)
                self.custom_dg.destroy()
        elif widget == self.add_repo:
            dg = DialogNewRepo(self.window, self.on_repo_create)
            dg.present()
        elif widget == self.refresh_repo:
            filename = os.path.join(app_cache_path, "temp.json")
            cmd = "gh repo list --json name --json id --json visibility --json diskUsage --json nameWithOwner > "+filename.replace(" ", "\\ ")
            self.repo_fetch_task.run(cmd, True, self.on_terminal_task_complete, filename)
        elif widget == self.en_search:
            self.sort_repos()

    def on_repo_create(self, widget, reponame):
        if reponame:
            filename = os.path.join(app_cache_path, "temp.json")
            cmd = "gh repo view "+reponame+" --json name --json id --json visibility --json diskUsage --json nameWithOwner > "+filename.replace(" ", "\\ ")
            self.post_repo_create_task.run(cmd, True, self.on_terminal_task_complete, filename)

    def on_email_dg_response(self, widget, email):
        if email:
            self.row_email.set_subtitle(email)
            self.acc_config["email"] = email

    def on_dialog_response(self, widget, response):
        if response == "logout": 
            os.system("gh auth logout -h github.com")
            self.window.connect_login_page()
        elif response == "config":
            DialogEmail(self.window, self.on_email_dg_response).present()

    @Gtk.Template.Callback()
    def on_switch_state_changed(self, widget, state):
        if self.use_port == widget:
            self.acc_config["use_port"] = state
            if state: ch_port()
            else: rm_port()

    def sort_repos(self):
        local_first = self.local_first.check_button.get_active()
        private_first = self.private_first.check_button.get_active()
        search_data = self.en_search.get_text().strip().lower()
        local = []
        non_local = []

        self.repoList.clear()
        for item in self.repo_full_list:
            if search_data == "" or str(item["name"]).lower().startswith(search_data):
                if not local_first:
                    self.repoList.append(item)
                if item["id"] in self.acc_config["local_repo"]:
                    local.append(item)
                else: non_local.append(item)

        if local_first:
            if private_first:
                local.sort(key = lambda a: a["visibility"])
                non_local.sort(key = lambda a: a["visibility"])

            for item in local:
                self.repoList.append(item)
            for item in non_local:
                self.repoList.append(item)
        elif private_first:
            self.repoList.sort(key = lambda a: a["visibility"])

        self.repo_listview.notify_data_changed()

    def on_checked_changed(self, widget):
        match widget:
            case self.private_first.check_button: self.sort_repos()
            case self.local_first.check_button: self.sort_repos()
        if not widget.get_active(): return
        match widget:
            case self.default_folder.check_button: self.acc_config["folder"] = "default"
            case self.custom_folder.check_button:
                self.acc_config["folder"] = "custom"
                if "custom_folder" not in self.acc_config: 
                    self.custom_dg = self.parseGtkFileDialog("Choose Folder")
                    if runtime_env >= 23.04:
                        self.custom_dg.select_folder(self.window, None, self.on_folder_choosed, None)
                    elif runtime_env >= 22.04:
                        self.custom_dg.present()
                        self.custom_dg.connect("response", self.on_folder_choosed, None)
                    else:
                        response = self.custom_dg.run()
                        if response == Gtk.ResponseType.OK:
                            folder = self.custom_dg.get_filename()
                            self.acc_config["custom_folder"] = folder
                            self.custom_folder.set_subtitle(folder)
                        else:
                            if self.custom_folder.check_button.get_active():
                                if "custom_folder" not in self.acc_config:
                                    self.default_folder.check_button.set_active(True)
                        self.custom_dg.destroy()
            case self.ask_folder.check_button: self.acc_config["folder"] = "ask"

    def parseGtkFileDialog(self, title):
        if runtime_env >= 23.04:
            dg = Gtk.FileDialog()
            dg.set_title(title)
            dg.set_modal(True)
            dg.set_initial_folder(Gio.File.new_for_path(self.home))
        else:
            dg = Gtk.FileChooserDialog()
            dg.set_title(title)
            dg.set_transient_for(self.window)
            dg.set_modal(True)
            dg.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
            dg.add_button("Select", Gtk.ResponseType.OK)
            dg.add_button("Cancel", Gtk.ResponseType.CANCEL)
        return dg

    def refresh(self, username):
        self.username = username
        if runtime_env >= 22.04: self.avt.set_text(username)
        self.greet.set_label("Hey "+username)
        self.logout.set_visible(True)
        
        filename = os.path.join(app_cache_path, "temp.json")
        cmd = "gh repo list --json name --json id --json visibility --json diskUsage --json nameWithOwner > "+filename.replace(" ", "\\ ")
        self.repo_fetch_task.run(cmd, True, self.on_terminal_task_complete, filename)

        self.load_account_data(username)

        self.repoList = []
        self.repo_full_list = []
        self.listview_adapter = myListViewAdapter(self.repoList, self.acc_config["local_repo"])
        self.listview_adapter.clone_callback = self.on_row_selected
        self.listview_adapter.open_callback = self.on_row_open_clicked
        self.repo_listview.set_listview_adapter(self.listview_adapter)

        self.default_folder.set_subtitle(self.home+username)
        
        self.stay_logged.set_active(self.acc_config["stay_logged"])
        self.use_port.set_active(self.acc_config["use_port"])
        if "email" in self.acc_config: self.row_email.set_subtitle(self.acc_config["email"])
        match self.acc_config["folder"]:
            case "default": self.default_folder.check_button.set_active(True)
            case "custom": self.custom_folder.check_button.set_active(True)
            case "ask": self.ask_folder.check_button.set_active(True)
        if "custom_folder" in self.acc_config: self.custom_folder.set_subtitle(self.acc_config["custom_folder"])

    def load_account_data(self, username):
        filename = os.path.join(app_config_path, "accounts.json")
        if os.path.exists(filename):
            file = open(filename)
            self.accounts = json.loads(file.read())
            file.close()
        else: self.accounts = {}

        self.acc_config = None
        if username in self.accounts:
            self.acc_config = self.accounts[username]
        else:
            self.acc_config = {
                "stay_logged": False,
                "use_port": False,
                "folder": "default",
                "local_repo": {}
            }
            self.accounts[username] = self.acc_config

    def on_row_selected(self, index):
        repo = self.repoList[index]
        match self.acc_config["folder"]:
            case "default": folder = os.path.join(self.home, self.username, repo["name"])
            case "custom": folder = os.path.join(self.acc_config["custom_folder"], repo["name"])
            case "ask": folder = None
        if folder: self.start_clone(folder, index)
        else: 
            dg = self.parseGtkFileDialog("Choose Folder")
            response = dg.run()
            if response == Gtk.ResponseType.OK:
                self.start_clone(dg.get_filename(), index)
            dg.destroy()

    def on_folder_choosed(self, widget, result, index):
        if runtime_env >= 23.04:
            try:
                file = widget.select_folder_finish(result)
                folder = file.get_path()
                result_ok = True
            except: result_ok = False
        else: 
            result_ok = result == int(Gtk.ResponseType.OK)
            widget.destroy()
            folder = widget.get_file()

        if result_ok:
            if widget == self.ask_dg: self.start_clone(folder, index)
            elif widget == self.custom_dg: 
                self.acc_config["custom_folder"] = folder
                self.custom_folder.set_subtitle(folder)
        else:
            if widget == self.custom_dg:
                if self.custom_folder.check_button.get_active():
                    if "custom_folder" not in self.acc_config:
                        self.default_folder.check_button.set_active(True)
        

    def on_row_open_clicked(self, index):
        id = self.repoList[index]["id"]
        folder = self.acc_config["local_repo"][id]
        if os.path.exists(folder): Hashtag.launch_file(folder, self.window)
        else:
            dg = Hashtag.MessageDialog(self.window, "Folder Not Found")
            dg.add_response("ok", "OK")
            dg.present()
            self.acc_config["local_repo"].pop(self.repoList[index]["id"])
            self.repo_listview.notify_data_changed(index)

    def start_clone(self, folder, index):
        if "email" not in self.acc_config:
            dg = Hashtag.MessageDialog(self.window, "Error", "Git User Email is not configured")
            dg.add_response("cancel", "Cancel")
            dg.add_response("config", "Configure Now")
            if runtime_env >= 23.04:
                dg.set_response_appearance("config", 1)
                dg.set_response_appearance("cancel", 0)
            dg.connect("response", self.on_dialog_response)
            dg.present()
            return
        if not os.path.exists(folder): os.makedirs(folder)
        repo = self.repoList[index]
        self.acc_config["local_repo"][repo["id"]] = folder
        self.repo_listview.notify_data_changed(index)
        self.clone_task.run("gh repo clone "+repo["name"]+" "+folder.replace(" ", "\\ "), False, self.on_terminal_task_complete, index)

    def on_terminal_task_complete(self, widget, response, userdata):
        if widget == self.post_repo_create_task:
            if response == 0:
                file = open(userdata)
                json_str = file.read()
                file.close()
                if json_str == "": json_str = "[]"
                new_repo = json.loads(json_str)
                self.repo_full_list.append(new_repo)
                self.repo_full_list.sort(key= lambda a: a["name"])
                self.sort_repos()
            else:
                dg = Hashtag.MessageDialog(self.window, "Data Fetch Failed", "Couldn't able to read repository data. Please check the network connectivity and refetch\nErr code: "+str(response))
                dg.add_response("ok", "OK")
                dg.present()
        elif widget == self.repo_fetch_task:
            filename = os.path.join(app_cache_path, "repos.json")
            json_str = ""
            if response != 0:
                if os.path.exists(filename):
                    file = open(filename)
                    json_str = file.read()
                    file.close()
                dg = Hashtag.MessageDialog(self.window, "Data Fetch Failed", "Couldn't able to read repository data. Please check the network connectivity and refetch\nErr code: "+str(response))
                dg.add_response("ok", "OK")
                dg.present()
            else:
                file = open(userdata)
                json_str = file.read()
                file.close()
                os.system("cp "+userdata.replace(" ", "\\ ")+" "+filename.replace(" ", "\\ "))

            if json_str == "": json_str = "[]"
            repos = json.loads(json_str)
            
            self.repo_full_list.clear()
            for item in repos:
                self.repo_full_list.append(item)

            self.repo_full_list.sort(key= lambda a: a["name"])
            self.sort_repos()
            
        elif widget == self.clone_task:
            repo_id = self.repoList[userdata]["id"]
            folder = self.acc_config["local_repo"][repo_id]
            if widget == self.clone_task:
                if response == 0:
                    os.system("git config -f "+folder.replace(" ", "\\ ")+"/.git/config user.name \""+self.username+"\"")
                    os.system("git config -f "+folder.replace(" ", "\\ ")+"/.git/config user.email \""+self.acc_config["email"]+"\"") 
                    Hashtag.launch_file(folder, self.window)
                else:
                    dg = Hashtag.MessageDialog(self.window, "Clone Failed", "Err code: "+str(response))
                    dg.add_response("ok", "OK")
                    dg.present()

    def on_window_destroy(self, window):
        self.acc_config["stay_logged"] = self.stay_logged.get_state()

        if not self.stay_logged.get_state(): os.system("gh auth logout -h github.com")
        rm_port()

        filename = os.path.join(app_config_path, "accounts.json")
        file = open(filename, "w")
        file.write(json.dumps(self.accounts))
        file.close()

    def __init__(self, window) -> None:
        super().__init__()
        self.window = window
        self.logout = window.logout
        self.logout.connect("clicked", self.on_button_clicked)
        self.row_email.set_activatable_widget(self.btn_email)
        self.home = os.path.expanduser("~/")

        self.default_folder.check_button.connect("toggled", self.on_checked_changed)
        self.custom_folder.check_button.connect("toggled", self.on_checked_changed)
        self.ask_folder.check_button.connect("toggled", self.on_checked_changed)

        self.custom_btn = Gtk.Button()
        if runtime_env >= 22.04:
            self.custom_btn.set_icon_name("document-edit-symbolic")
            self.custom_btn.add_css_class("flat")
        else:
            image = Gtk.Image()
            image.set_from_icon_name("document-edit-symbolic", 1)
            image.show()
            self.custom_btn.set_image(image)
            self.custom_btn.show()
            self.custom_btn.get_style_context().add_class("flat")
        self.custom_btn.set_margin_top(8 if runtime_env >= 22.04 else 4)
        self.custom_btn.set_margin_bottom(8 if runtime_env >= 22.04 else 4)
        self.custom_btn.connect("clicked", self.on_button_clicked)
        self.custom_folder.add_suffix(self.custom_btn)
        if runtime_env >= 22.04:
            self.custom_dg = self.parseGtkFileDialog("Choose Folder")
            self.ask_dg = self.parseGtkFileDialog("Choose Folder")

        if runtime_env >= 22.04:
            self.custom_folder.check_button.set_group(self.default_folder.check_button)
            self.ask_folder.check_button.set_group(self.default_folder.check_button)
        else:
            self.custom_folder.check_button.join_group(self.default_folder.check_button)
            self.ask_folder.check_button.join_group(self.default_folder.check_button)
        self.clone_task = Hashtag.ExtTerminal(window)
        self.repo_fetch_task = Hashtag.ExtTerminal(window)
        self.post_repo_create_task = Hashtag.ExtTerminal(window)

        self.local_first.check_button.connect("toggled", self.on_checked_changed)
        self.private_first.check_button.connect("toggled", self.on_checked_changed)
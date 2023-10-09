using Gtk, Gee, Htg;

namespace HashFolder {
    public class HomeActivity: Activity {
        private ToggleButton theme_auto;
        private ToggleButton theme_light;
        private ToggleButton theme_dark;
        private int _theme = Adw.ColorScheme.DEFAULT;

        private Switch ssh_port;
        private Adw.ActionRow def_folder;
        private Button clear_folder;
        private Button open_folder;
        private Button logout;
        private ProgressBar progress;
        private Switch auto_download;
        private Switch auto_upload;
        private Switch discoverable;

        private int progress_running = 0;

        private Htg.Settings app_settings;
        private Htg.Settings user_settings;

        public int theme {
            get { return _theme; }
            set {
                var style_mgr = Adw.StyleManager.get_default ();
                style_mgr.color_scheme = (Adw.ColorScheme) (_theme = value.clamp(0, 4));
            }
        }

        internal override void on_create () {
            set_content("home_activity.ui");

            app_settings = get_application().get_settings ("app");
            var user = (string) app_settings["user"];
            user_settings = get_application().get_settings(user);

            progress = (ProgressBar) builder.get_object("progress");

            //Theme settings
            theme_auto = (ToggleButton) builder.get_object ("theme_auto");
            theme_auto.toggled.connect (update_theme);

            theme_dark = (ToggleButton) builder.get_object ("theme_dark");
            theme_dark.toggled.connect (update_theme);
            
            theme_light = (ToggleButton) builder.get_object ("theme_light");
            theme_light.toggled.connect (update_theme);

            //Visible widget setups
            ssh_port = (Switch) builder.get_object("ssh_port");
            ssh_port.sensitive = "ssh_config_old" in app_settings;
            ssh_port.notify["active"].connect(() => {
                if (ssh_port.active) {
                    var config = load_ssh_config();
                    if (!config.has_key ("github.com")) config["github.com"] = new HashMap<string, Value?>();
                    var git_host = (HashMap<string, Value?>) config["github.com"];
                    
                    git_host["Port"] = "443";
                    git_host["HostName"] = "ssh.github.com";
                    store_ssh_config(config);
                } else {
                    app_settings = get_application().get_settings ("app");
                    store_ssh_config((HashMap<string, GLib.Value?>) app_settings["ssh_config_old"]);
                }
            });

            logout = (Button) builder.get_object ("logout_btn");
            logout.clicked.connect(on_button_clicked);

            def_folder = (Adw.ActionRow) builder.get_object("def_folder");

            clear_folder = (Button) builder.get_object("clear_folder");
            clear_folder.clicked.connect(on_button_clicked);

            open_folder = (Button) builder.get_object("open_folder");
            open_folder.clicked.connect(on_button_clicked);

            var acc_name = (Label) builder.get_object("acc_name");
            acc_name.label = @"Welcome $(user_settings["disp_name"].get_string())";

            var def_path = @"$(Environment.get_home_dir())/$user";
            if (!("clone_path" in user_settings)) user_settings["clone_path"] = def_path;
            
            var current_path = user_settings["clone_path"].get_string();
            clear_folder.visible = current_path != def_path;
            def_folder.subtitle = current_path;

            auto_download = (Switch) builder.get_object("auto_download");
            user_settings.bind("auto_download", auto_download, "active", false);

            auto_upload = (Switch) builder.get_object("auto_upload");
            user_settings.bind("auto_upload", auto_upload, "active", true);

            discoverable = (Switch) builder.get_object("discoverable");
            user_settings.bind("discoverable", discoverable, "active", true);

            //Repository subpage
            var repo_page_back = (Button) builder.get_object ("repo_page_back");
            var viewstack = (Adw.ViewStack) builder.get_object ("viewstack");
            var repo_activity_frag = new RepoActivity (this, viewstack, repo_page_back);
            var repo_container = (Adw.Bin) builder.get_object ("repo_container");
            repo_container.child = repo_activity_frag.content;

            base.on_create();
        }

        protected override void on_started() {
            app_settings.bind("theme", this, "theme", Adw.ColorScheme.DEFAULT);
            app_settings.bind("ssh_port_443", ssh_port, "active", false);

            if (theme == Adw.ColorScheme.DEFAULT) theme_auto.active = true;
            if (theme == Adw.ColorScheme.FORCE_LIGHT) theme_light.active = true;
            if (theme == Adw.ColorScheme.FORCE_DARK) theme_dark.active = true;
            
            base.on_started();
        }

        protected override void on_stopped() {
            app_settings.unbind(this, "theme");
            app_settings.unbind(ssh_port, "active");
            base.on_stopped ();
        }

        public void start_progress_indetermination() {
            progress_running++;
            if (progress_running == 0) progress_running++;
            if (progress_running == 1) {
                progress.visible = true;
                Timeout.add(100, () => {
                    progress.pulse();
                    if (progress_running == 0) {
                        progress.fraction = 0;
                        progress_running = -1;
                        progress.visible = false;
                    } return progress_running > 0;
                });
            }
        }

        public void stop_progress_indetermination() {
            if (progress_running-- == 0) {
                critical("No progress indetermination exists");
                progress_running++;
            }
        }

        private void update_theme() {
            if (theme_auto.active) theme = Adw.ColorScheme.DEFAULT;
            else if (theme_light.active) theme = Adw.ColorScheme.FORCE_LIGHT;
            else if (theme_dark.active) theme = Adw.ColorScheme.FORCE_DARK;
        }

        private void on_button_clicked(Button button) {
            if (button == logout) {
                var listbox = new ListBox();
                listbox.add_css_class("boxed-list");
                //  listbox.sensitive = false;

                //  var git_logout_row = new Adw.ActionRow();
                //  git_logout_row.title = "Detach Git Account";
                //  git_logout_row.subtitle = "Logs you out and blocks further account management";
                //  git_logout_row.sensitive = false;
                //  listbox.append(git_logout_row);

                var git_auto_push_row = new Adw.ActionRow();
                git_auto_push_row.title = "Push uncommited changes";
                git_auto_push_row.subtitle = "Pushing every uncomitted changes to the account";
                git_auto_push_row.sensitive = false;
                listbox.append(git_auto_push_row);

                var git_clear_local_repos_row = new Adw.ActionRow();
                git_clear_local_repos_row.title = "Clear all downloaded repos";
                git_clear_local_repos_row.subtitle = "Deletes all downloaded repositories on logout";
                listbox.append(git_clear_local_repos_row);

                var git_clear_ssh_key_row = new Adw.ActionRow();
                git_clear_ssh_key_row.title = "Clear SSH Key";
                git_clear_ssh_key_row.subtitle = "Revoke this device's access to your account";
                git_clear_ssh_key_row.sensitive = false;
                listbox.append(git_clear_ssh_key_row);

                //  var git_logout_check = new CheckButton();
                //  git_logout_check.add_css_class("selection-mode");
                //  git_logout_check.active = true;
                //  git_logout_check.valign = Align.CENTER;
                //  git_logout_row.add_suffix(git_logout_check);
                //  git_logout_row.activatable_widget = git_logout_check;

                var git_auto_push_check = new CheckButton();
                git_auto_push_check.add_css_class("selection-mode");
                //  git_auto_push_check.active = true;
                git_auto_push_check.valign = Align.CENTER;
                git_auto_push_row.add_suffix(git_auto_push_check);
                git_auto_push_row.activatable_widget = git_auto_push_check;

                var git_clear_local_repos_check = new CheckButton();
                git_clear_local_repos_check.add_css_class("selection-mode");
                git_clear_local_repos_check.valign = Align.CENTER;
                git_clear_local_repos_row.add_suffix(git_clear_local_repos_check);
                git_clear_local_repos_row.activatable_widget = git_clear_local_repos_check;

                var git_clear_ssh_key_check = new CheckButton();
                git_clear_ssh_key_check.add_css_class("selection-mode");
                git_clear_ssh_key_check.valign = Align.CENTER;
                git_clear_ssh_key_row.add_suffix(git_clear_ssh_key_check);
                git_clear_ssh_key_row.activatable_widget = git_clear_ssh_key_check;
                git_clear_ssh_key_row.activatable_widget = git_clear_ssh_key_check;

                var dg = new Adw.MessageDialog (get_application().active_window, "Logout?", "You are going to logout from this app. Choose additional actions needed to be taken on Logout");
                dg.add_response ("cancel", "Cancel");
                dg.add_response ("logout", "Logout");
                dg.set_response_appearance ("logout", Adw.ResponseAppearance.SUGGESTED);
                dg.extra_child = listbox;
                dg.response.connect((res) => {
                    if (res == "logout") {
                        logout.sensitive = false;
                        start_progress_indetermination();

                        logout_task_handler.begin(() => {
                            if (!user_settings.contains("local_repos")) user_settings["local_repos"] = new HashMap<string, Value?>();
                            var local_repos = (HashMap<string, Value?>) user_settings["local_repos"];
                            var repo_store = (HashMap<string, Value?>) user_settings["repo_store"];

                            var rm_keys = new ArrayList<string>();
                            foreach (var repo_id in local_repos.keys) {
                                if (!repo_store.has_key(repo_id)) continue;
                                var repo_data = (HashMap<string, Value?>) repo_store[repo_id];
                                var repo_path = local_repos[repo_id].get_string();
                                //Pushing uncommited
                                //  print(@"$(repo_data["name"].get_string())\n");
                                //  foreach (var key in repo_data.keys) print(@"\t$key\n");
                                if (git_auto_push_check.active && repo_data.has_key("banner") && repo_data["banner"].get_boolean()) {
                                    Posix.system(@"git -C \"$repo_path\" add --all");
                                    Posix.system(@"git -C \"$repo_path\" commit -a -m update");
                                    Posix.system(@"git -C \"$repo_path\" push");
                                    repo_data["banner"] = false;
                                }

                                //Clearing Local Repositories
                                if (git_clear_local_repos_check.active) {
                                    Posix.system(@"rm -rf $(repo_path)");
                                    rm_keys.add(repo_id);
                                }

                                //  repo_data["banner"] = false;
                            }

                            while(rm_keys.size > 0) local_repos.unset(rm_keys.remove_at(0));

                            Posix.system("gh auth logout -h github.com");
                        }, (src, res) => {
                            stop_progress_indetermination();
                            logout.sensitive = true;
                            finish();
                        });
                    }
                });

                dg.present();
            } else if (button == open_folder) {
                var dg = new FileDialog();
                dg.title = "Select Folder";
                dg.select_folder.begin(get_application ().active_window, null, (src, res) => {
                    try {
                        var file = dg.select_folder.end(res);
                        var filepath = file.get_path();
                        user_settings["clone_path"] = filepath;
                        def_folder.subtitle = filepath;
                        clear_folder.visible = true;
                    }
                    catch (Error e) {}
                });
            } else if (button == clear_folder) {
                var user = (string) app_settings["user"];
                var filepath = @"$(Environment.get_home_dir())/$user";
                user_settings["clone_path"] = filepath;
                def_folder.subtitle = filepath;
                clear_folder.visible = false;
            }
        }

        //  private class CommandSequencer: Object {
        //      private ArrayList<string> sync_queue = new ArrayList<string>();
        //      private ArrayList<string> async_queue = new ArrayList<string>();
        //      private HashMap<string, string> cmd_store = new HashMap<string, string>();
        //      private int async_count = 0;

        //      public bool sleeping {
        //          get;
        //          private set;
        //          default = true;
        //      }

        //      public void add_task(string id, string command, bool sync = false) {
        //          sleeping = false;
        //          if (!sync) async_count++;
                
        //          cmd_store[id] = command;
        //          if (sync) sync_queue.add(id);
        //          else if (sync_queue.size == 0) Htg.run_command.begin(command, (src, res) => {
        //              async_count--;
        //              if (async_count == 0) sleeping = true;
        //          });
        //          else async_queue.add(id);

        //          if (sync_queue.size == 1) Htg.run_command.begin(cmd_store[sync_queue[0]], on_sync_task_completed);
        //      }

        //      private void on_sync_task_completed(Object? src, AsyncResult res) {
        //          //  on_task_completed(sync_queue.remove_at(0), Htg.run_command.end(res));
        //          if (sync_queue.size > 0) Htg.run_command.begin(cmd_store[sync_queue[0]], on_sync_task_completed);
        //          else {
        //              async_count += async_queue.size;
        //              while(async_queue.size > 0) Htg.run_command.begin(cmd_store[async_queue.remove_at(0)], (src, res) => {
        //                  async_count--;
        //                  if (async_count == 0) sleeping = true;
        //              });
        //          }
        //      }

        //      //  public signal void on_task_completed(string id, int status);
        //  }

        private delegate void TaskBeginCallback();

        private async void logout_task_handler(TaskBeginCallback callback) {
            var t = new Thread<void>("sub-command", () => {
                callback();
                Idle.add(logout_task_handler.callback);
            });
            yield;
            t.join();
        }
    }
}
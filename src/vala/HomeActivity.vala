using Gtk, Gee, Htg;

namespace org.htg.hashfolder {
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

            //Repository subpage
            var repo_page_back = (Button) builder.get_object ("repo_page_back");
            var viewstack = (Adw.ViewStack) builder.get_object ("viewstack");
            var repo_activity_frag = new RepoActivity (this, viewstack, repo_page_back);
            var repo_container = (Adw.Bin) builder.get_object ("repo_container");
            repo_container.child = repo_activity_frag.content;

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
            if (progress_running++ == 0) {
                Timeout.add(100, () => {
                    progress.pulse();
                    if (progress_running == 0) progress.fraction = 0;
                    return progress_running > 0;
                });
            }
        }

        public void stop_progress_indetermination() {
            if (progress_running-- == 0) {
                critical("No progress indetermination exists");
                progress_running = 0;
            }
        }

        private void update_theme() {
            if (theme_auto.active) theme = Adw.ColorScheme.DEFAULT;
            else if (theme_light.active) theme = Adw.ColorScheme.FORCE_LIGHT;
            else if (theme_dark.active) theme = Adw.ColorScheme.FORCE_DARK;
        }

        private void on_button_clicked(Button button) {
            if (button == logout) {
                var dg = new Adw.MessageDialog (get_application().active_window, "Logout?", "You are going to logout from this app. Logout will only detach the github account, will not clear your data such as cloned repositories. Would you like to clear all the data which belongs this account?");
                dg.add_response ("cancel", "Cancel");
                dg.add_response ("logout", "Logout");
                dg.set_response_appearance ("logout", Adw.ResponseAppearance.SUGGESTED);
                dg.response.connect((res) => {
                    if (res == "logout") {
                        logout.sensitive = false;

                        start_progress_indetermination();
                        run_command.begin("gh auth logout -h github.com", (src, res) => {
                            stop_progress_indetermination();
                            logout.sensitive = true;
                            run_command.end(res);
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
    }
}
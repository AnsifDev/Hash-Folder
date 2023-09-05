using Gee, Gtk, Htg;

namespace org.htg.hashfolder {
    public class LauncherActivity: Htg.Activity {
        private Htg.Settings app_settings;

        private Button login_btn;
        private ProgressBar progress;

        private ToggleButton theme_auto;
        private ToggleButton theme_light;
        private ToggleButton theme_dark;
        private int _theme = Adw.ColorScheme.DEFAULT;

        public int theme {
            get { return _theme; }
            set {
                var style_mgr = Adw.StyleManager.get_default ();
                style_mgr.color_scheme = (Adw.ColorScheme) (_theme = value.clamp(0, 4));
            }
        }
        
        internal override void on_create() {
            set_content("launcher_activity.ui");

            app_settings = get_application().get_settings("app");
            
            //Theme Settings
            theme_auto = (ToggleButton) builder.get_object ("theme_auto");
            theme_auto.toggled.connect (update_theme);

            theme_dark = (ToggleButton) builder.get_object ("theme_dark");
            theme_dark.toggled.connect (update_theme);
            
            theme_light = (ToggleButton) builder.get_object ("theme_light");
            theme_light.toggled.connect (update_theme);

            //Visible widget setup
            var intro_label = (Label) builder.get_object("introduction");
            var file = File.new_for_uri("resource:///org/htg/hashfolder/introduction.txt");
            try {
                var file_input_stream = file.read();
                var data_input_stream = new DataInputStream(file_input_stream);
                var file_str = data_input_stream.read_upto("\0", -1, null, null);
                intro_label.label = file_str;
            } catch (Error e) { error("%s\n", e.message); }

            login_btn = (Button) builder.get_object("login_btn");
            login_btn.clicked.connect(() => {
                get_application().activity_manager.start_activity(this, typeof(LoginTerm));
            });

            progress = (ProgressBar) builder.get_object("progress");

            var guest_login_btn = (Button) builder.get_object("guest_login_btn");
            guest_login_btn.clicked.connect(() => {
                finish();
            });

            //SSH State Fetching
            var ssh_config = (HashMap<string, Value?>) load_ssh_config();
            var current_port_443 = false;
            if (ssh_config.has_key("github.com")) {
                var git_config = (HashMap<string, Value?>) ssh_config["github.com"];
                if (git_config.has_key("Port")) current_port_443 = git_config["Port"].get_string() == "443";
            }
            app_settings["ssh_port_443"] = current_port_443;
            if (!app_settings["ssh_port_443"].get_boolean()) app_settings["ssh_config_old"] = ssh_config;

            auto_login();
            base.on_create();
        }

        protected override void on_started() {
            app_settings.bind("theme", this, "theme", Adw.ColorScheme.DEFAULT);

            if (theme == Adw.ColorScheme.DEFAULT) theme_auto.active = true;
            if (theme == Adw.ColorScheme.FORCE_LIGHT) theme_light.active = true;
            if (theme == Adw.ColorScheme.FORCE_DARK) theme_dark.active = true;

            base.on_started();
        }

        protected override void on_stopped() {
            app_settings.unbind(this, "theme");
            base.on_stopped();
        } 

        private void update_theme() {
            if (theme_auto.active) theme = Adw.ColorScheme.DEFAULT;
            else if (theme_light.active) theme = Adw.ColorScheme.FORCE_LIGHT;
            else if (theme_dark.active) theme = Adw.ColorScheme.FORCE_DARK;
        }

        private void auto_login() {
            var continue_pulsing = true;
            Timeout.add(100, () => {
                progress.pulse();
                if (!continue_pulsing) progress.fraction = 0;
                return continue_pulsing;
            });

            run_command.begin("gh auth status", (src, res) => {
                continue_pulsing = false;
                login_btn.sensitive = true;

                var status = run_command.end(res);
                if (status == 0) {
                    if (!("user" in app_settings)) {
                        var gh_config = new YAMLEngine().parse_file_to_hashmap(@"$(Environment.get_user_config_dir())/gh/hosts.yml");
                        app_settings["user"] = ((HashMap<string, Value?>) gh_config["github.com"])["user"].get_string();
                    }
                    get_application().activity_manager.start_activity(this, typeof(HomeActivity));
                }
            });
        }
    }
}
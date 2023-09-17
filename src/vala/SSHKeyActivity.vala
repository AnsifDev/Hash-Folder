using Gee, Gtk, Htg;

namespace HashFolder {
    public class SSHKeyActivity: Htg.Activity {private Box base_box;
        private Box bottom_box;
        private Box content_box;
        private Adw.TimedAnimation animation;
        private Htg.Breakpoint breakpoint;
        private Button create_btn;
        private bool waiting_to_change = false;
        private bool ssh_available = false;

        private Image dev_name_valid;
        private Image key_pass_valid;
        private Image key_cpass_valid;
        private Image disp_name_valid;
        private Image email_valid;
        
        private int _validation = 0;
        private int validation { 
            get { return _validation; }
            set {
                _validation = value;
                dev_name_valid.visible = (value & 1) == 0;
                key_pass_valid.visible = (value & 2) == 0;
                key_cpass_valid.visible = (value & 4) == 0;
                disp_name_valid.visible = (value & 8) == 0;
                email_valid.visible = (value & 16) == 0;
                create_btn.sensitive = validation > 30;
            }
        }

        //  private Adw.PasswordEntryRow dev_name;
        //  private Adw.PasswordEntryRow key_pass;
        //  private Adw.PasswordEntryRow key_pass_confirm;

        public override void on_create() {
            set_content("ssh_key_activity.ui");

            //  var file = File.new_for_path(Environment.get_user_config_dir());
            //  if (file.query_exists()) {
            //      var children = file.enumerate_children("", GLib.FileQueryInfoFlags.NOFOLLOW_SYMLINKS);
            //      for (FileInfo file_info; (file_info = children.next_file()) != null; ) {
            //          print("File: %s\n", file_info.get_name());
            //      }
            //  }
            //  else print("Folder not exists\n");

            base_box = (Box) builder.get_object("base_box");
            bottom_box = (Box) builder.get_object("bottom_box");
            content_box = (Box) builder.get_object("content_box");

            var animation_target = new Adw.CallbackAnimationTarget((value) => {
                base_box.opacity = value;
                //  print("%f\n", value);
                if (value <= 0.01 && waiting_to_change) {
                    base_box.valign = breakpoint.narrow? Align.FILL: Align.CENTER;
                    if (breakpoint.narrow) base_box.remove_css_class("my-frame");
                    else base_box.add_css_class("my-frame");
                    content_box.vexpand = breakpoint.narrow;
                    waiting_to_change = false;
                }
            });

            animation = new Adw.TimedAnimation(base_box, 1, 0, 150, animation_target);
            animation.repeat_count = 2;
            animation.alternate = true;

            breakpoint = (Htg.Breakpoint) builder.get_object("breakpoint");
            breakpoint.notify["narrow"].connect(() => {
                waiting_to_change = true;
                animation.play();
            });

            var app_settings = get_application().get_settings("app");
            var user = app_settings["user"].get_string();
            var user_settings = get_application().get_settings(user);
            
            var dev_name = (Adw.EntryRow) builder.get_object("dev_name");
            dev_name.changed.connect(() => {
                var text = dev_name.text.strip();
                var valid = text.length > 4;

                for (var i = 0; i < text.length && valid; i++) {
                    var c = (int) text[i];
                    if (c < 48 && c != 45 || 57 < c < 65 || 90 < c < 97 && c != 95 || 122 < c) valid = false;
                    if (i == 0 && c < 65) valid = false;
                }

                if (valid) validation |= 1;
                else validation &= ~1;
            });

            var key_pass = (Adw.PasswordEntryRow) builder.get_object("key_pass");
            key_pass.changed.connect(() => {
                var text = key_pass.text;
                var valid = text.length > 7;
                if (valid) validation |= 2;
                else validation &= ~2;
            });

            var key_cpass = (Adw.PasswordEntryRow) builder.get_object("key_cpass");
            key_cpass.changed.connect(() => {
                var text = key_cpass.text;
                var valid = key_pass.text == text;
                if (valid) validation |= 4;
                else validation &= ~4;
                
            });

            var disp_name = (Adw.EntryRow) builder.get_object("disp_name");
            disp_name.changed.connect(() => {
                var text = disp_name.text;
                var valid = text.length > 0;
                if (valid) validation |= 8;
                else validation &= ~8;
            });

            var email = (Adw.EntryRow) builder.get_object("email");
            email.changed.connect(() => {
                var text = email.text;
                var valid = text.length > 0;
                var at = false;
                var at_len_ok = false;
                for (var i = 0; i < text.length && valid; i++) {
                    var c = (int) text[i];
                    if (at) at_len_ok = true;
                    if (c == 64 && !at) at = true;
                    else if (c != 43 && c != 45 && c != 46 && c != 95 && c != 126)
                    if (c < 48 || 57 < c < 65 || 90 < c < 97 || 122 < c) valid = false;
                }

                if (valid && at && at_len_ok) validation |= 16;
                else validation &= ~16;
            });

            var cancel_btn = (Button) builder.get_object("cancel_btn");
            cancel_btn.clicked.connect(() => { 
                run_command.begin("gh auth logout", (src, res) => {
                    run_command.end(res);
                    finish();
                });
            });

            create_btn = (Button) builder.get_object("create_btn");
            create_btn.clicked.connect(() => {
                var keyname = (string) app_settings["user"];
                var password = key_pass.text;
                var device_name = dev_name.text;

                var progress = (ProgressBar) builder.get_object("progress");
                var continue_pulsing = true;
                Timeout.add(100, () => {
                    progress.pulse();
                    if (!continue_pulsing) progress.fraction = 0;
                    return continue_pulsing;
                });

                user_settings["disp_name"] = disp_name.text;
                user_settings["email"] = email.text;

                if (!ssh_available) run_command.begin(@"ssh-keygen -t ed25519 -C $keyname -f ~/.ssh/$keyname -N \"$password\"", (src, res) => {
                    if (run_command.end(res) == 0) run_command.begin(@"gh ssh-key add ~/.ssh/$keyname.pub -t $device_name", (src, res) => {
                        if (run_command.end(res) == 0) get_application().activity_manager.start_activity(this, typeof(HomeActivity));
                        continue_pulsing = false;
                        finish();
                    }); 
                    else {
                        continue_pulsing = false;
                        finish();
                    }
                });
                else {
                    continue_pulsing = false;
                    get_application().activity_manager.start_activity(this, typeof(HomeActivity));
                    finish();
                } 
            });

            dev_name_valid = (Image) builder.get_object("dev_name_valid");
            key_pass_valid = (Image) builder.get_object("key_pass_valid");
            key_cpass_valid = (Image) builder.get_object("key_cpass_valid");
            disp_name_valid = (Image) builder.get_object("disp_name_valid");
            email_valid = (Image) builder.get_object("email_valid");

            Htg.list_dir.begin(Environment.get_home_dir()+"/.ssh", (src, res) => {
                try { ssh_available = @"$(app_settings["user"].get_string()).pub" in Htg.list_dir.end(res); }
                catch (Error e) { critical(e.message); }
                //  dev_name.sensitive = key_pass.sensitive = key_cpass.sensitive = !ssh_available;
                var ssh_configs = (Adw.PreferencesGroup) builder.get_object("ssh_configs");
                ssh_configs.visible = !ssh_available;
                validation |= 7;
            });
            disp_name.text = app_settings["user"].get_string();
            if ("disp_name" in user_settings) {
                print("Yes: %s\n", user_settings["disp_name"].get_string());
                disp_name.text = user_settings["disp_name"].get_string();
            } else print("No %s\n", app_settings["user"].get_string());
            if ("email" in user_settings) email.text = user_settings["email"].get_string();
        }
    }
}
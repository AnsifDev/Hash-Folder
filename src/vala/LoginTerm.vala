using Vte, Posix, Gee;

namespace HashFolder {
    public class LoginTerm: Htg.Activity {
        private int step = 0;
        private Terminal term;
        private string code;

        public override void on_create() {
            set_content("login_term.ui");

            var toast_overlay = (Adw.ToastOverlay) builder.get_object("toast_overlay");
            var code_view = (Gtk.Label) builder.get_object("code_view");
            var code_container = (Htg.Bin) builder.get_object("code_container");
            var copy_code = (Gtk.Button) builder.get_object("copy_code");
            copy_code.clicked.connect(() => {
                var clipboard = term.get_clipboard();
                clipboard.set_text(code);
                
                var toast = new Adw.Toast("Copied");
                toast_overlay.add_toast(toast);
            });

            var progress = (Gtk.ProgressBar) builder.get_object("progress");
            var continue_pulsing = true;
            var data_queue = new ArrayList<string>();

            Timeout.add(100, () => {
                progress.pulse();
                if (!continue_pulsing) progress.fraction = 0;
                return continue_pulsing;
            });

            term = (Terminal) builder.get_object("term");
            term.child_exited.connect((status) => {
                continue_pulsing = false;
                
                if (status == 0) {
                    var gh_config = new Htg.YAMLEngine().parse_file_to_hashmap(Environment.get_user_config_dir()+"/gh/hosts.yml");
                    var app = get_application().get_settings("app");
                    app["user"] = ((HashMap<string, Value?>) gh_config["github.com"])["user"].get_string();
                    
                    get_application().activity_manager.start_activity(this, typeof(SSHKeyActivity));
                    finish();
                } else {
                    var dg = new Adw.MessageDialog(get_application().active_window, "Something Went Wrong", @"Unexpected error occured on login. Sub command returned with error code: $(status)");
                    dg.add_response("_ok", "OK");
                    dg.present();
                }
                //  finish();
            });
            term.contents_changed.connect(() => {
                var data = term.get_text(null, null).strip();
                if (data.length <= 0) return;
                //  Htg.run_command.begin(@"echo \"$step: $data\" >> out.txt");
                if (data in data_queue) return;
                data_queue.add(data);
                if (data_queue.size == 1) {
                    Timeout.add(500, () => {
                        var current_data = data_queue.remove_at(0);
                        //  print("Running...\n");
                        //  print("Running...\n%s\n", current_data);
                        if ("Do you want to re-authenticate?" in current_data && step == 0) {
                            step++;
                            uint8[] inp = {89, 13};
                            term.feed_child(inp);
                        }
                        if ("Generate a new SSH key to add to your GitHub account?" in current_data && step < 2) {
                            step++;
                            if (step == 1) step++;
                            uint8[] inp = {78, 13};
                            term.feed_child(inp);
                        }
                        if ("Upload your SSH public key to your GitHub account?" in current_data && step < 2) {
                            step++;
                            if (step == 1) step++;
                            uint8[] inp = {27, 91, 65, 13};
                            term.feed_child(inp);
                        }
                        if ("Press Enter to open github.com in your browser" in current_data && step == 2) {
                            step++;
                            code = current_data.split(":")[1].split("\n")[0].strip();
                            
                            print("Code: %s\n", code);
                            code_view.label = @"Code: $code";
                            code_container.visible = true;
                            
                            var clipboard = term.get_clipboard();
                            clipboard.set_text(code);

                            var dg = new Adw.MessageDialog(get_application().window, "Login OTP Copied", @"$code is copied to your clipboard. A web browser will now pops up, just paste the code and then you are done.");
                            dg.add_response("cancel", "Cancel");
                            dg.add_response("ok", "OK");
                            dg.response.connect((res) => {
                                if (res == "cancel") return;
                                uint8[] inp = {13};
                                term.feed_child(inp);
                                print("Entering to web-browser\n");
                            });
                            dg.present();
                        }

                        //  Idle.add_once(() => {
                            
                        //  });
                        return data_queue.size != 0;
                    });
                }
                
            });
            step = 0;
            term.spawn_async(Vte.PtyFlags.DEFAULT, null, "/app/bin/gh gh auth login -h github.com -p ssh -s admin:public_key -s admin:ssh_signing_key -s delete_repo -w".split(" "), null, GLib.SpawnFlags.FILE_AND_ARGV_ZERO, null, 120, null, null);
            //  term.spawn_async(Vte.PtyFlags.DEFAULT, null, "/bin/bash".split(" "), null, GLib.SpawnFlags.FILE_AND_ARGV_ZERO, null, 120, null, null);
        }

        protected override void on_stopped() {
            uint8[] inp = {3};
            term.feed_child(inp);
        }
    }
}
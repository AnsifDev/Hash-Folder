using Vte, Posix, Gee;

namespace org.htg.hashfolder {
    public class LoginTerm: Htg.Activity {
        private int step = 0;
        private Terminal term;

        public override void on_create() {
            set_content("login_term.ui");

            var progress = (Gtk.ProgressBar) builder.get_object("progress");
            var continue_pulsing = true;

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
                } else {
                    var dg = new Adw.MessageDialog(get_application().active_window, "Something Went Wrong", @"Unexpected error occured on login. Sub command returned with error code: $(status/256)");
                    dg.add_response("_ok", "OK");
                    dg.present();
                }
                finish();
            });
            term.contents_changed.connect(() => {
                var data = term.get_text(null, null).strip();
                if (data.length <= 0) return;
                if ("Do you want to re-authenticate?" in data && step == 0) {
                    step++;
                    uint8[] inp = {89, 13};
                    term.feed_child(inp);
                }
                if ("Generate a new SSH key to add to your GitHub account?" in data && step < 2) {
                    step++;
                    if (step == 1) step++;
                    uint8[] inp = {78, 13};
                    term.feed_child(inp);
                }
                if ("Upload your SSH public key to your GitHub account?" in data && step < 2) {
                    step++;
                    if (step == 1) step++;
                    uint8[] inp = {27, 91, 65, 13};
                    term.feed_child(inp);
                }
                if ("Press Enter to open github.com in your browser" in data && step == 2) {
                    step++;
                    var code = data.split(":")[1].split("\n")[0].strip();
                    print("Code: %s\n", code);
                    var clipboard = term.get_clipboard();
                    clipboard.set_text(code);

                    print("Entering to web-browser\n");
                    var dg = new Adw.MessageDialog(get_application().window, "Login OTP Copied", @"$code is copied to your clipboard. A web browser will now pops up, just paste the code and then you are done.");
                    dg.add_response("ok", "OK");
                    dg.response.connect(() => {
                        uint8[] inp = {13};
                        term.feed_child(inp);
                    });
                    dg.present();
                }
            });
            step = 0;
            term.spawn_async(Vte.PtyFlags.DEFAULT, null, "/app/bin/gh gh auth login -h github.com -p ssh -s admin:public_key -s admin:ssh_signing_key -s delete_repo -w".split(" "), null, GLib.SpawnFlags.FILE_AND_ARGV_ZERO, null, 120, null, null);
        }

        protected override void on_stopped() {
            uint8[] inp = {3};
            term.feed_child(inp);
        }
    }
}
using Gtk, Gee;

namespace HashFolder {
    class NewRepoActivity: Htg.Activity {
        private Box base_box;
        private Box bottom_box;
        private Box content_box;
        private Adw.TimedAnimation animation;
        private Htg.Breakpoint breakpoint;
        private Button create_btn;
        private bool waiting_to_change = false;
        private ProgressBar progress;
        private CheckButton clone_check;

        private Htg.Settings app_settings;
        private Htg.Settings user_settings;

        public override void on_create() {
            set_content("new_repo_activity.ui");

            app_settings = get_application().get_settings ("app");
            var user = (string) app_settings["user"];
            user_settings = get_application().get_settings(user);

            progress = (ProgressBar) builder.get_object("progress");

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

            var folder_row = (Adw.ActionRow) builder.get_object("folder_row");
            var visibility = (Adw.ComboRow) builder.get_object("visibility");

            var cancel_btn = (Button) builder.get_object("cancel_btn");
            cancel_btn.clicked.connect(() => { finish(); });

            var clear_folder = (Button) builder.get_object("clear_folder");
            clear_folder.clicked.connect(() => { folder_row.subtitle = ""; clear_folder.visible = false; });

            var open_folder = (Button) builder.get_object("open_folder");
            open_folder.clicked.connect(() => {
                var file_dg = new FileDialog();
                file_dg.title = "Select Folder";
                file_dg.select_folder.begin(get_application().active_window, null, (source, result) => {
                    try {
                        var file = file_dg.select_folder.end(result);
                        clear_folder.visible = true;
                        folder_row.subtitle = file.get_path();
                    } catch (Error e) {}
                });
            });

            var repo_name_valid = (Image) builder.get_object("repo_name_valid");

            var repo_name = (Adw.EntryRow) builder.get_object("repo_name");
            repo_name.changed.connect(() => {
                var text = repo_name.text.strip();
                var valid = text.length > 4;

                for (var i = 0; i < text.length && valid; i++) {
                    var c = (int) text[i];
                    if (c < 48 && c != 45 || 57 < c < 65 || 90 < c < 97 && c != 95 || 122 < c) valid = false;
                    if (i == 0 && c < 65) valid = false;
                }

                repo_name_valid.visible = !(create_btn.sensitive = valid);
            });

            clone_check = (CheckButton) builder.get_object("clone_check");
            var description = (TextView) builder.get_object("description");

            create_btn = (Button) builder.get_object("create_btn");
            create_btn.clicked.connect(() => {
                var source_available = folder_row.subtitle.length > 0;
                if (source_available) {
                    var file = File.new_for_path(folder_row.subtitle+"/.git");
                    if (file.query_exists()) Posix.system(@"rm -rf $(folder_row.subtitle.replace(" ", "\\ "))/.git");
                    Htg.run_command.begin(@"git -C $(folder_row.subtitle.replace(" ", "\\ ")) init --initial-branch main");
                }

                var public_visible = visibility.selected != 0;
                var cmd = @"gh repo create $(repo_name.text.strip())";
                cmd += public_visible? " --public": " --private";
                if (source_available) cmd += @" --source $(folder_row.subtitle.replace(" ", "\\ "))";
                var description_text = description.get_buffer().text;
                if (description_text.length > 0) cmd += @" --description \"$description_text\"";
                
                var continue_pulsing = true;
                bottom_box.sensitive = false;
                Timeout.add(100, () => {
                    progress.pulse();
                    if (!continue_pulsing) {
                        progress.fraction = 0;
                        bottom_box.sensitive = true;
                    }
                    return continue_pulsing;
                });

                Htg.run_command.begin(cmd, (src, res) => {
                    var status = Htg.run_command.end(res);
                    if (status != 0) {
                        continue_pulsing = false;
                        var dg_create_failed = new Adw.MessageDialog(get_application().active_window, "Task Failed", @"Repository creation failed. Sub command returned with error code: $status");
                        dg_create_failed.add_response("_ok", "OK");
                        dg_create_failed.present();
                        return;
                    };

                    var repo_cache_path = @"$(Environment.get_user_cache_dir())/$(get_application().application_id)/repo_cache";
                    Htg.run_command.begin(@"gh repo view $(repo_name.text.strip()) --json=createdAt,description,diskUsage,forkCount,id,languages,name,owner,url,visibility > $repo_cache_path", (src, res) => {
                        status = Htg.run_command.end(res);
                        if (status != 0) {
                            var dg_clone_failed = new Adw.MessageDialog(get_application().active_window, "Repo Fetch Error", @"Repository creation suceeded but clone registeration failed. Sub command returned with error code: $status");
                            dg_clone_failed.add_response("_ok", "OK");
                            dg_clone_failed.present();
                            return;
                        };

                        continue_pulsing = false;
                        try {
                            var data = new Htg.JsonEngine().parse_file_to_hashmap(repo_cache_path);
                            var local_repos = (HashMap<string, Value?>) user_settings["local_repos"];
                            local_repos[data["id"].get_string()] = folder_row.subtitle;

                            var result = new HashMap<string, Value?>();
                            result["local_status"] = source_available ? 2: clone_check.active? 1: 0;
                            result["repo_data"] = data;
                            finish_with_result(result);
                        } catch (Error e) { critical(e.message); }
                    });
                    
                    //  if (source_available) {
                        
                    //      Htg.run_command.begin(@"gh repo view $(repo_name.text.strip()) --json=id > $repo_cache_path", (src, res) => {
                    //          status = Htg.run_command.end(res);
                    //          if (status != 0) {
                    //              var dg_clone_failed = new Adw.MessageDialog(get_application().active_window, "Repo Fetch Error", @"Repository creation suceeded but clone registeration failed. Sub command returned with error code: $status");
                    //              dg_clone_failed.add_response("_ok", "OK");
                    //              dg_clone_failed.present();
                    //              return;
                    //          };

                    //          continue_pulsing = false;
                    //          try {
                    //              var data = new Htg.JsonEngine().parse_file_to_hashmap(repo_cache_path);
                    //              var local_repos = (HashMap<string, Value?>) user_settings["local_repos"];
                    //              local_repos[data["id"].get_string()] = folder_row.subtitle;
                    //          } catch (Error e) { critical(e.message); }

                    //          var dg = new Adw.MessageDialog(get_application().active_window, "Do Commits and Pushing", "Repository is configured but changes in the local repository is not commited or pushed to the cloud repository. Please go to the local repository folder and do commits and pushing changes to upload all changes to the cloud");
                    //          dg.add_response("_ok", "OK");
                    //          dg.present();

                    //          finish_with_result(null);
                    //      });
                    //  } else {
                    //      continue_pulsing = false;
                    //      finish_with_result(null);
                    //  }
                });

            });
        }
    }
}
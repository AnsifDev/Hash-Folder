using Gee, Gtk;

namespace HashFolder {
    public class RepoContent: Htg.ActivityFragment {
        private Stack content_stack;
        private Adw.Clamp inner_clamp_head;
        private Box align_box_tiles;
        private Box align_box_head;
        private Box head_align;

        private Label repo_name;
        private Label repo_owner;
        private Label repo_visibility;
        private Label repo_description;
        private Box description_card;

        private BoxBinder langs_left_binder;
        private BoxBinder langs_right_binder;
        private BoxBinder props_left_binder;
        private BoxBinder props_right_binder;

        private Button btn_clone;
        private Button btn_open;
        private Button btn_open_with;
        private Button btn_remove;
        private Button btn_delete;

        private RepoContentTerminal terminal;
        private Adw.Banner banner;
        //  private CloneManager clone_mgr;
        private HashMap<string, Value?> local_repos;

        private Htg.Settings app_settings;
        private Htg.Settings user_settings;
        private HashMap<string, Value?> data;

        public RepoContent(Htg.Activity parent, Htg.Breakpoint breakpoint) {
            base(parent, "repo_content.ui");

            app_settings = parent.get_application().get_settings("app");
            var user = app_settings["user"].get_string();
            user_settings = parent.get_application().get_settings(user);
            if (!user_settings.contains("local_repos")) user_settings["local_repos"] = new HashMap<string, Value?>();
            local_repos = (HashMap<string, Value?>) user_settings["local_repos"];

            content_stack = (Stack) builder.get_object("content_stack");
            inner_clamp_head = (Adw.Clamp) builder.get_object("inner_clamp_head");
            align_box_head = (Box) builder.get_object("align_box_head");
            align_box_tiles = (Box) builder.get_object("align_box_tiles");
            head_align = (Box) builder.get_object("head_align");

            repo_name = (Label) builder.get_object("repo_name");
            repo_owner = (Label) builder.get_object("repo_owner");
            repo_visibility = (Label) builder.get_object("repo_visibility");
            repo_description = (Label) builder.get_object("repo_description");
            var repo_langs = (Box) builder.get_object("repo_langs");
            var repo_props = (Box) builder.get_object("repo_props");
            description_card = (Box) builder.get_object("description_card");
            btn_clone = (Button) builder.get_object("btn_clone");
            btn_open = (Button) builder.get_object("btn_open");
            btn_open_with = (Button) builder.get_object("btn_open_with");
            btn_remove = (Button) builder.get_object("btn_remove");
            btn_delete = (Button) builder.get_object("btn_delete");
            banner = (Adw.Banner) builder.get_object("banner");

            btn_clone.clicked.connect(on_button_clicked);
            btn_open.clicked.connect(on_button_clicked);
            btn_open_with.clicked.connect(on_button_clicked);
            btn_remove.clicked.connect(on_button_clicked);
            btn_delete.clicked.connect(on_button_clicked);

            banner.button_clicked.connect(() => {
                var repo_id = (string) data["id"];
                var repo_path = local_repos[repo_id].get_string();
                data["banner"] = banner.revealed = false;

                terminal.add_task(@"$repo_id-stage-sync", @"/app/bin/git git -C \"$repo_path\" add --all");
                terminal.add_task(@"$repo_id-commit-sync", @"/app/bin/git git -C \"$repo_path\" commit -a -m init");
                terminal.add_task(@"$repo_id-push-sync", @"/app/bin/git git -C \"$repo_path\" push");
            });

            repo_langs.width_request = 260;
            var repo_langs_left = new Box(Gtk.Orientation.VERTICAL, 2);
            repo_langs_left.width_request = 30;
            repo_langs_left.homogeneous = true;
            repo_langs.append(repo_langs_left);
            langs_left_binder = new BoxBinder(repo_langs_left, () => {
                var label = new Label(null);
                label.halign = Align.START;
                label.ellipsize = Pango.EllipsizeMode.END;
                return label;
            }, (widget, data) => {
                ((Label) widget).label = (string) ((HashMap<string, Value?>) ((HashMap<string, Value?>) data)["node"])["name"];
            });
            
            var repo_langs_right = new Box(Gtk.Orientation.VERTICAL, 2);
            repo_langs_right.homogeneous = true;
            repo_langs.append(repo_langs_right);
            langs_right_binder = new BoxBinder(repo_langs_right, () => {
                var progress = new ProgressView();
                progress.valign = Align.CENTER;
                progress.hexpand = true;
                return progress;
            }, (widget, data) => {
                var fraction = (float) ((HashMap<string, Value?>) data)["size"].get_long()/langs_right_binder.max;

                ((ProgressView) widget).progress.fraction = fraction;
                ((ProgressView) widget).textview.label = @"$(((float) (int) (fraction*10000))/100)%";
                //  ((ProgressView) widget).progress.fraction = 0.5;
            });

            var repo_props_left = new Box(Gtk.Orientation.VERTICAL, 2);
            repo_props_left.width_request = 30;
            repo_props_left.homogeneous = true;
            repo_props.append(repo_props_left);
            props_left_binder = new BoxBinder(repo_props_left, () => {
                var label = new Label(null);
                label.halign = Align.START;
                label.ellipsize = Pango.EllipsizeMode.END;
                label.add_css_class("dim-label");
                return label;
            }, (widget, data) => {
                ((Label) widget).label = (string) data;
            });
            
            var repo_props_right = new Box(Gtk.Orientation.VERTICAL, 2);
            repo_props_right.homogeneous = true;
            repo_props.append(repo_props_right);
            props_right_binder = new BoxBinder(repo_props_right, () => {
                var label = new Label(null);
                label.halign = Align.START;
                return label;
            }, (widget, data) => {
                ((Label) widget).label = ((string) data);
            });
            
            terminal = (RepoContentTerminal) builder.get_object("term");
            terminal.on_task_completed.connect((id, status) => {
                if (id.has_suffix("-clone")) {
                    var repo_store = (HashMap<string, Value?>) user_settings["repo_store"];
                    var clone_path = user_settings["clone_path"].get_string();

                    var repo_id = id.replace("-clone", "");
                    //  print("%s\n", repo_id);
                    var current_repo_id = data["id"].get_string();

                    var repo_data = (HashMap<string, Value?>) repo_store[repo_id];
                    var repo_name = repo_data["name"].get_string();
                    var email = user_settings["email"].get_string();
                    
                    if (status == 0) {
                        local_repos[repo_id] = @"$clone_path/$repo_name";
                        var repo_path = (string) local_repos[repo_id];
                        if (current_repo_id == repo_id) btn_clone.visible = false;
                        terminal.add_task(@"$repo_id-user-config", @"/app/bin/git git -C \"$repo_path\" config user.name $user");
                        terminal.add_task(@"$repo_id-email-config", @"/app/bin/git git -C \"$repo_path\" config user.email $email");
                    }
                    if (current_repo_id == repo_id) btn_clone.sensitive = true;
                }
            });
            terminal.notify["sleeping"].connect(() => {
                if (terminal.sleeping) ((HomeActivity) parent).stop_progress_indetermination();
                else ((HomeActivity) parent).start_progress_indetermination();
            });

            breakpoint.notify["narrow"].connect (() => {
                inner_clamp_head.tightening_threshold = breakpoint.narrow ? 600: 400;
                inner_clamp_head.maximum_size = breakpoint.narrow ? 400: 600;
                head_align.halign = breakpoint.narrow? Align.CENTER: Align.START;
                head_align.margin_start = breakpoint.narrow? 0: 12;
                align_box_head.orientation = breakpoint.narrow ? Orientation.VERTICAL: Orientation.HORIZONTAL;
                align_box_tiles.orientation = breakpoint.narrow ? Orientation.VERTICAL: Orientation.HORIZONTAL;
                terminal.term_bin.vnatural = breakpoint.narrow ? 200: 300;
                terminal.term_bin.queue_resize();
            });

            //  var term_revealer = (Gtk.Revealer) builder.get_object("term_revealer");
            //  term_revealer.transition_type = RevealerTransitionType.SLIDE_UP;
            //  var term_unreveal = (Button) builder.get_object("term_unreveal");
            //  term_bin = (Htg.Bin) builder.get_object("term_bin");

            //  clone_mgr = new CloneManager(this, term_revealer, term_unreveal, term, user_settings["clone_path"].get_string());
            //  clone_mgr.cloning_started.connect(((HomeActivity) parent).start_progress_indetermination);
            //  clone_mgr.cloning_ended.connect(((HomeActivity) parent).stop_progress_indetermination);
            //  clone_mgr.clone_finished.connect((status, data) => {
            //      if (status == 0) {
            //          var clone_path = user_settings["clone_path"].get_string();
            //          local_repos[data["id"].get_string()] = @"$clone_path/$(data["name"].get_string())";
            //          if (this.data == data) btn_clone.visible = false;
            //      }
            //      if (this.data == data) btn_clone.sensitive = true;
            //  });

            parent.on_result_available.connect((request_id, result) => {
                var result_map = (HashMap<string, Value?>) result;
                var repo_data = (HashMap<string, Value?>) result_map["repo_data"];
                var local_status = (int) result_map["local_status"];
                var repo_id = (string) repo_data["id"];

                var email = user_settings["email"].get_string();
                var repo_path = local_repos[repo_id].get_string();

                if (local_status == 2) { //If source attached
                    terminal.add_task(@"$repo_id-user-config", @"/app/bin/git git -C \"$repo_path\" config user.name $user");
                    terminal.add_task(@"$repo_id-email-config", @"/app/bin/git git -C \"$repo_path\" config user.email $email");
                    terminal.add_task(@"$repo_id-stage-sync", @"/app/bin/git git -C \"$repo_path\" add --all");
                    terminal.add_task(@"$repo_id-commit-sync", @"/app/bin/git git -C \"$repo_path\" commit -a -m init");
                    terminal.add_task(@"$repo_id-push-sync", @"/app/bin/git git -C \"$repo_path\" push --set-upstream origin main");
                } else if (local_status == 1) on_button_clicked(btn_clone);
            });
        }

        public void show_item(HashMap<string, Value?> data) {
            content_stack.set_visible_child_name("content");
            this.data = data;

            repo_name.label = (string) data["name"];
            repo_owner.label = (string) ((HashMap<string, Value?>) data["owner"])["login"];
            repo_visibility.label = (string) data["visibility"];
            repo_description.label = (string) data["description"];
            //  print(@"$(lang_left_binder == null)");

            var total_size = 0;
            foreach (var lang_map in ((ArrayList<Value?>) data["languages"])) 
                total_size += (int) ((HashMap<string, Value?>) lang_map)["size"].get_long();
            langs_right_binder.max = total_size;

            langs_left_binder.set_data_list((ArrayList<Value?>) data["languages"]);
            langs_right_binder.set_data_list((ArrayList<Value?>) data["languages"]);

            var prop_values = new ArrayList<Value?>();
            prop_values.add(((string) data["createdAt"]).split("T")[0]);
            prop_values.add(((long) data["diskUsage"]).to_string());
            prop_values.add(((long) data["forkCount"]).to_string());

            var prop_names = new ArrayList<Value?>();
            prop_names.add("Created At:");
            prop_names.add("Size:");
            prop_names.add("Fork Count:");

            props_left_binder.set_data_list((ArrayList<Value?>) prop_names);
            props_right_binder.set_data_list((ArrayList<Value?>) prop_values);

            var id = data["id"].get_string();
            if (local_repos.has_key(id) && !File.new_for_path(local_repos[id].get_string()).query_exists()) local_repos.unset(id); 

            description_card.visible = repo_description.label.length > 0;
            btn_clone.visible = !(user_settings.contains("local_repos") && local_repos.has_key(id));
            btn_clone.sensitive = !(@"$id-clone" in terminal);
            banner.revealed = data.has_key("banner") && data["banner"].get_boolean();
        }

        private void on_button_clicked(Button button) {
            var clone_path = user_settings["clone_path"].get_string();
            if (button == btn_clone) {
                button.sensitive = false;
                Htg.run_command.begin(@"rm -rf $clone_path/$(data["name"].get_string())");
                //  clone_mgr.start_clone(data);
                var repo_name = data["name"].get_string();
                var repo_id = data["id"].get_string();
                terminal.add_task(@"$repo_id-clone", @"/app/bin/gh gh repo clone $repo_name $clone_path/$repo_name");
                //  terminal.add_task("temp", "/bin/echo echo hello\\ world");
            } else if (button == btn_open) {
                var file = File.new_for_path(local_repos[data["id"].get_string()].get_string());
                var file_launcher = new FileLauncher(file);
                file_launcher.launch.begin(parent.get_application().active_window, null, (src, res) => {
                    try { 
                        if (file_launcher.launch.end(res)) {
                            if (!banner.revealed) {
                                var repo_id = (string) data["id"];
                                var repo_path = local_repos[repo_id].get_string();
                                terminal.add_task(@"$repo_id-pull-sync", @"/app/bin/git git -C \"$repo_path\" pull");
                            } data["banner"] = banner.revealed = true;
                        }
                    } catch (Error e) {}
                });
            } else if (button == btn_open_with) {
                var file = File.new_for_path(local_repos[data["id"].get_string()].get_string());
                var file_launcher = new FileLauncher(file);
                file_launcher.always_ask = true;
                file_launcher.launch.begin(parent.get_application().active_window, null, (src, res) => {
                    try { 
                        if (file_launcher.launch.end(res)) {
                            if (!banner.revealed) {
                                var repo_id = (string) data["id"];
                                var repo_path = local_repos[repo_id].get_string();
                                terminal.add_task(@"$repo_id-pull-sync", @"/app/bin/git git -C \"$repo_path\" pull");
                            } data["banner"] = banner.revealed = true;
                        }
                    } catch (Error e) {}
                });
            } else if (button == btn_remove) {
                var dg = new Adw.MessageDialog(parent.get_application().active_window, "Remove Repository?", "This will remove the repository only from this device");
                dg.add_response("_cancel", "Cancel");
                dg.add_response("_remove", "Remove");
                dg.set_response_appearance("_remove", Adw.ResponseAppearance.DESTRUCTIVE);
                dg.response.connect((res) => {
                    if (res == "_remove") {
                        var repo_path = local_repos[data["id"].get_string()].get_string().replace(" ", "\\ ");
                        Htg.run_command.begin(@"rm -rf $(repo_path)");
                        local_repos.unset(data["id"].get_string());
                        btn_clone.visible = true;
                    }
                });
                dg.present();
            } else if (button == btn_delete) {
                var dg = new Adw.MessageDialog(parent.get_application().active_window, "Delete Repository?", "This will remove the repository both from this device and the cloud");
                dg.add_response("_cancel", "Cancel");
                dg.add_response("_remove", "Remove");
                dg.set_response_appearance("_remove", Adw.ResponseAppearance.DESTRUCTIVE);
                dg.response.connect((res) => {
                    if (res == "_remove") {
                        ((HomeActivity) parent).start_progress_indetermination();

                        var repo_id = data["id"].get_string();
                        if (local_repos.has_key(repo_id)) {
                            var repo_path = local_repos[repo_id].get_string().replace(" ", "\\ ");
                            Htg.run_command.begin(@"rm -rf $(repo_path)/.git");
                            local_repos.unset(repo_id);
                        }

                        var repo_name = data["name"].get_string();
                        Htg.run_command.begin(@"gh repo delete $repo_name --yes", (src, res) => {
                            var status = Htg.run_command.end(res);
                            if (status != 0) {
                                dg = new Adw.MessageDialog(parent.get_application().active_window, "Task Failed", @"Repository is not removed. Subcommand returned with error code: $status");
                                dg.add_response("_ok", "OK");
                                dg.present();
                                return;
                            }

                            content_stack.set_visible_child_name("empty");
                            on_repo_deleted(data);
                            ((HomeActivity) parent).stop_progress_indetermination();
                        });
                    }
                });
                dg.present();
            }
        }

        public signal void on_repo_deleted(HashMap<string, Value?> repo_data);

        private class ProgressView: Box {
            
            public Label textview { get; private set; default = new Label(null); }
            public ProgressBar progress { get; private set; default = new ProgressBar(); }

            construct {
                progress.valign = Align.CENTER;
                progress.hexpand = true;
                spacing = 4;
                append(progress);
                append(textview);
            }
        }

        private class BoxBinder: Htg.ListBinder<Value?> {
            public delegate Widget setup_widget_func();
            public delegate void bind_widget_func(Widget widget, Value? data);

            private setup_widget_func setup_func;
            private bind_widget_func bind_func;

            public int max = 1;
            
            public BoxBinder(Box box, setup_widget_func setup_func, bind_widget_func bind_func) {
                base(box);
                this.setup_func = setup_func;
                this.bind_func = bind_func;
            }

            public override void insert_child(Gtk.Widget widget, int index) {
                critical("%s\n", "No insertion property supported");
            }

            public override void append_child(Gtk.Widget widget) {
                ((Box) container).append(widget);
            }

            public override void remove_child(Gtk.Widget widget) {
                ((Box) container).remove(widget);
            }

            public override Widget setup_widget() {
                return setup_func();
            }

            public override void bind_widget(Gtk.Widget widget, Value? data) {
                bind_func(widget, data);
            }
        }

        //  private class CloneManager: Object {
        //      //  private RepoContent outer_class;
        //      //  private Revealer term_revealer;
        //      //  private Button term_unreveal;
        //      //  private Vte.Terminal term;
        //      private RepoContentTerminal terminal;
        //      private string clone_path;
        //      private ArrayList<HashMap<string, Value?>> tasks = new ArrayList<HashMap<string, Value?>>();

        //      public CloneManager(RepoContentTerminal terminal, string clone_path) {
        //          this.terminal = terminal;
        //          //  this.term_revealer = term_revealer;
        //          //  this.term_unreveal = term_unreveal;
        //          //  this.term = term;
        //          this.clone_path = clone_path;

        //          //  term.child_exited.connect((status) => {
        //          //      var data = tasks.remove_at(0);
        //          //      clone_finished(status, data);
        //          //      if (tasks.size > 0 || false) start_task(); 
        //          //      else cloning_ended();
        //          //  });
        //      }

        //      public void start_clone(HashMap<string, Value?> data) {
        //          tasks.add(data);
        //          if (tasks.size == 1) {
        //              start_task();
        //              cloning_started();
        //          }
        //      }

        //      public void stop_clone(HashMap<string, Value?> data) {
        //          uint8[] inp = {3};
        //          if (tasks[0] == data) term.feed_child(inp);
        //          tasks.remove(data);
        //      }

        //      public bool contains(HashMap<string, Value?> data) { return data in tasks; }

        //      public bool is_cloning() { return tasks.size > 0; }

        //      private void start_task() {
        //          var repo_name = tasks[0]["name"].get_string();
        //          var args = new ArrayList<string>();
        //          args.add_all_array(@"/app/bin/gh gh repo clone $repo_name".split(" "));
        //          args.add(@"$clone_path/$repo_name");
        //          term.spawn_async(
        //              Vte.PtyFlags.DEFAULT, 
        //              null, 
        //              args.to_array(), 
        //              null, 
        //              GLib.SpawnFlags.FILE_AND_ARGV_ZERO, 
        //              null, 
        //              120, 
        //              null, 
        //              null
        //          );
        //      }

        //      public signal void cloning_started() { term_unreveal.visible = !(term_revealer.reveal_child = true); }

        //      //  private ArrayList<string> timer_params_queue = new ArrayList<string>();
        //      public signal void clone_finished(int status, HashMap<string, Value?> data) {
        //          //  timer_params_queue.add();
        //          var repo_name = data["name"].get_string();
        //          var user = outer_class.app_settings["user"].get_string();
        //          var email = outer_class.user_settings["email"].get_string();
        //          Htg.run_command.begin(@"git -C \"$clone_path/$repo_name\" config user.name $user", () => {
        //              Htg.run_command.begin(@"git -C \"$clone_path/$repo_name\" config user.email $email", () => {
        //                  print("Yes Completed\n");
        //              });
        //          });
        //      }

        //      public signal void cloning_ended() { term_unreveal.visible = true; }

        //      //  private void run_clone_post() {}
        //  }
    }
}
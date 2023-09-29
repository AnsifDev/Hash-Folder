using Gtk, Gee;

namespace HashFolder {
    class RepoActivity: Htg.ActivityFragment {
        private RepoSidebar sidebar_frag;
        private RepoContent content_frag;
        private Htg.BreakpointBin bin;
        private Adw.Leaflet leaflet;

        public RepoActivity (Htg.Activity parent, Adw.ViewStack viewstack, Button page_back) {
            base(parent, "repo_activity.ui");
            //  allow_default_header = false;

            var breakpoint = new Htg.Breakpoint(true);
            breakpoint.threshold_width = 980;

            bin = (Htg.BreakpointBin) builder.get_object("bin");
            bin.add_breakpoint(breakpoint);

            //  var nav_back = (Button) builder.get_object("nav_back");
            //  nav_back.clicked.connect(() => { get_application().activity_manager.navigate_back(); });
            //  get_application().activity_manager.bind_property("can-navigate-back", nav_back, "visible", GLib.BindingFlags.SYNC_CREATE);

            //  var page_back = (Button) builder.get_object("page_back");
            //  page_back.visible = leaflet.get_visible_child_name() == "content";
            viewstack.notify["visible-child-name"].connect(() => {
                page_back.visible = leaflet.get_visible_child_name() == "content" && leaflet.folded && viewstack.visible_child_name == "repos";
            });

            page_back.clicked.connect(() => {
                leaflet.navigate(Adw.NavigationDirection.BACK);
                page_back.visible = false;
            });

            leaflet = (Adw.Leaflet) builder.get_object("leaflet");
            leaflet.notify["folded"].connect(()=> {
                page_back.visible = leaflet.get_visible_child_name() == "content" && leaflet.folded && viewstack.visible_child_name == "repos";
            });

            sidebar_frag = new RepoSidebar(parent);
            ((Adw.Bin) builder.get_object("sidebar")).set_child(sidebar_frag.content);

            content_frag = new RepoContent(parent, breakpoint);
            content_frag.on_repo_deleted.connect((repo_data) => {
                sidebar_frag.remove_repo(repo_data);
                leaflet.navigate(Adw.NavigationDirection.BACK);
                page_back.visible = false;
            });
            ((Adw.Bin) builder.get_object("content")).set_child(content_frag.content);

            sidebar_frag.item_selected.connect(content_frag.show_item);
            sidebar_frag.item_selected.connect((data) => {
                leaflet.navigate(Adw.NavigationDirection.FORWARD);
                page_back.visible = leaflet.folded && viewstack.visible_child_name == "repos";
            });

            do_auto_download();
        }

        private void do_auto_download() {
            var app_settings = parent.get_application().get_settings("app");
            var user = app_settings["user"].get_string();
            var user_settings = parent.get_application().get_settings(user);
            var auto_download = user_settings["auto_download"].get_boolean();
            if (!auto_download) return;

            if (!user_settings.contains("local_repos")) user_settings["local_repos"] = new HashMap<string, Value?>();
            var local_repos = (HashMap<string, Value?>) user_settings["local_repos"];
            var repo_store = (HashMap<string, Value?>) user_settings["repo_store"];

            foreach (var repo_id in local_repos.keys) {
                if (!repo_store.has_key(repo_id)) continue;
                
                var repo_path = local_repos[repo_id].get_string();
                content_frag.terminal.add_task(@"$repo_id-pull-sync", @"/app/bin/git git -C \"$repo_path\" pull");
            }
        }

        protected override void on_destroy() {
            var app_settings = parent.get_application().get_settings("app");
            var user = app_settings["user"].get_string();
            var user_settings = parent.get_application().get_settings(user);
            var auto_upload = user_settings["auto_upload"].get_boolean();
            if (!auto_upload) return;

            if (!user_settings.contains("local_repos")) user_settings["local_repos"] = new HashMap<string, Value?>();
            var local_repos = (HashMap<string, Value?>) user_settings["local_repos"];
            var repo_store = (HashMap<string, Value?>) user_settings["repo_store"];
            var app = parent.get_application();

            foreach (var repo_id in local_repos.keys) {
                if (!repo_store.has_key(repo_id)) continue;
                var repo_data = (HashMap<string, Value?>) repo_store[repo_id];
                
                //  print(@"$repo_id, repo_data is null: $(repo_data == null), repo has banner: $(repo_data.has_key("banner"))\n");
                if (repo_data.has_key("banner") && repo_data["banner"].get_boolean()) {
                    app.hold();
                    
                    var repo_path = local_repos[repo_id].get_string();

                    Htg.run_command.begin(@"git -C \"$repo_path\" add --all", () => {
                        Htg.run_command.begin(@"git -C \"$repo_path\" commit -a -m update", () => {
                            Htg.run_command.begin(@"git -C \"$repo_path\" push", on_task_completed);
                        });
                    });
                }
                repo_data["banner"] = false;
            }
        }

        private void on_task_completed() {
            parent.get_application().release();
        }
    }
}
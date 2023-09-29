using Gee, Gtk;

namespace HashFolder {
    public class RepoSidebar: Htg.ActivityFragment {
        private ListBox listbox;
        private HashMap<string, Value?> repo_store;
        private ArrayList<Value?> original_list;
        private ArrayList<HashMap<string, Value?>> filtered_list = new ArrayList<HashMap<string, Value?>>();

        private RepoBinder data_model;
        private SearchEntry search_entry;
        private CheckButton local_only;
        private ToggleButton include_all;
        private ToggleButton private_only;
        private ToggleButton public_only;
        private MenuButton filter_btn;
        private Button refresh_repo;

        private Htg.Settings app_settings;
        private Htg.Settings user_settings;

        private Stack sidebar_stack;
        
        public RepoSidebar(Htg.Activity parent) {
            base(parent, "repo_sidebar.ui");

            app_settings = parent.get_application().get_settings ("app");
            var user = (string) app_settings["user"];
            user_settings = parent.get_application().get_settings(user);

            if (!user_settings.contains ("repos")) user_settings["repos"] = new ArrayList<Value?> ();
            original_list = (ArrayList<Value?>) user_settings["repos"];
            if (!user_settings.contains ("repo_store")) user_settings["repo_store"] = new HashMap<string, Value?>();
            repo_store = (HashMap<string, Value?>) user_settings["repo_store"];
            //  this.original_list = new ArrayList<Value?> ();

            sidebar_stack = (Stack) builder.get_object ("sidebar_stack");

            listbox = (ListBox) builder.get_object ("listbox");
            listbox.row_activated.connect ((row) => { item_selected ( ((MyListBoxRow) row).associated_data); });

            data_model = new RepoBinder (listbox);
            data_model.set_data_list (filtered_list);
            listbox.select_row ((ListBoxRow) listbox.get_first_child());

            var add_repo = (Button) builder.get_object("add_repo");
            add_repo.clicked.connect(() => {
                parent.get_application().activity_manager.start_activity_with_request(parent, typeof(NewRepoActivity), 1);
            });

            refresh_repo = (Button) builder.get_object("refresh_repo");
            refresh_repo.clicked.connect(() => {
                refresh();
            });

            search_entry = (SearchEntry) builder.get_object("search_entry");
            search_entry.set_key_capture_widget (parent.get_application ().active_window);
            search_entry.search_changed.connect(() => {
                if (search_entry.text.length == 1 && add_repo.visible) search_entry.grab_focus ();
                add_repo.visible = search_entry.text.length == 0;
                update_filter ();
            });
            search_entry.stop_search.connect (() => {
                search_entry.text = "";
                update_filter ();
            });

            filter_btn = (MenuButton) builder.get_object("filter_btn");

            local_only = (CheckButton) builder.get_object("local_only");
            local_only.toggled.connect (update_filter);

            include_all = (ToggleButton) builder.get_object("include_all");
            include_all.toggled.connect (update_filter);

            private_only = (ToggleButton) builder.get_object("private_only");
            private_only.toggled.connect (update_filter);

            public_only = (ToggleButton) builder.get_object("public_only");
            public_only.toggled.connect (update_filter);

            var repo_cache_path = @"$(Environment.get_user_cache_dir())/$(parent.get_application().application_id)/repo_cache";
            var file = File.new_for_path(repo_cache_path);
            if (!file.get_parent().query_exists()) try { file.get_parent().make_directory_with_parents(); }
            catch (Error e) { critical(e.message); }

            refresh();
            //  update_filter ();
            parent.on_result_available.connect((request_id, result) => {
                if (request_id == 1) {
                    var result_map = (HashMap<string, Value?>) result;
                    var repo_data = (HashMap<string, Value?>) result_map["repo_data"];
                    var repo_id = repo_data["id"].get_string();
                    original_list.insert (0, repo_id);
                    repo_store[repo_id] = repo_data;
                    update_filter ();
                    listbox.select_row ((ListBoxRow) listbox.get_first_child());
                    item_selected(repo_data);
                }
            });
        }

        internal void remove_repo(HashMap<string, Value?> repo_data) {
            var repo_id = repo_data["id"].get_string();
            for (int i = 0; i < original_list.size; i++) if (original_list[i].get_string() == repo_id) {
                original_list.remove_at (i);
                break;
            }

            repo_store.unset(repo_id);
            update_filter ();
            listbox.select_row ((ListBoxRow) listbox.get_first_child());
        }

        internal void refresh() {
            ((HomeActivity) parent).start_progress_indetermination ();
            refresh_repo.sensitive = false;

            var repo_cache_path = @"$(Environment.get_user_cache_dir())/$(parent.get_application().application_id)/repo_cache";
            Htg.run_command.begin(@"gh repo list --json=createdAt,description,diskUsage,forkCount,id,languages,name,owner,url,visibility > $repo_cache_path", (src, res) => {
                ((HomeActivity) parent).stop_progress_indetermination ();
                refresh_repo.sensitive = true;

                var status = Htg.run_command.end(res);
                if (status == 0) try {
                    var repos_list = new Htg.JsonEngine().parse_file_to_array(repo_cache_path);

                    //  if (!user_settings.contains("repo_store")) user_settings["repo_store"] = new HashMap<string, Value?>();
                    //  repo_store = (HashMap<string, Value?>) user_settings["repo_store"];
                    original_list.clear();
                    foreach (var repo_data in repos_list) {
                        var id = ((HashMap<string, Value?>) repo_data)["id"].get_string();
                        if (!repo_store.has_key (id)) repo_store[id] = new HashMap<string, Value?>();
                        var stored_repo_data = (HashMap<string, Value?>) repo_store[id];
                        foreach (var key in ((HashMap<string, Value?>) repo_data).keys) 
                            stored_repo_data[key] = ((HashMap<string, Value?>) repo_data)[key];
                        original_list.add (id);
                    }

                    //  user_settings["repo_store"] = repo_store;
                } catch (Error e) { critical (e.message); }
                else {
                    var dg = new Adw.MessageDialog (parent.get_application ().active_window, "Repository Fetch Failed", null);
                    dg.add_response("_ok", "OK");
                    dg.present();
                }
                update_filter();
            });
        }

        private void update_filter() {
            filtered_list.clear();
            if (!user_settings.contains ("local_repos")) user_settings["local_repos"] = new HashMap<string, Value?>();
            var local_repos = (HashMap<string, Value?>) user_settings["local_repos"];
            foreach (var id in original_list) {
                if (!repo_store.has_key (id.get_string())) { critical ("Unxpected id: %s in repos of user_settings", id.get_string()); continue; }
                var hashmap = (HashMap<string, Value?>) repo_store[id.get_string()];
                var name_ok = search_entry.text in (string) hashmap["name"];
                var visiblity_public = (string) hashmap["visibility"] == "PUBLIC";
                var visiblity_ok = visiblity_public == public_only.active || (!visiblity_public) == private_only.active || include_all.active;
                var local_only_ok = local_only.active? local_repos.has_key (hashmap["id"].get_string()): true;
                var includable = name_ok && visiblity_ok && local_only_ok;
                if (includable) filtered_list.add (hashmap);
            }
            data_model.notify_data_set_changed ();
            if (filtered_list.size > 0) sidebar_stack.set_visible_child_name ("content");
            else sidebar_stack.set_visible_child_name ("empty");
            if (include_all.active && !local_only.active) filter_btn.icon_name = "funnel-outline-symbolic";
            else filter_btn.icon_name = "funnel-symbolic";
        }

        public signal void item_selected(HashMap<string, Value?> hashmap);

        private class MyListBoxRow: ListBoxRow {
            public Label label { get; private set; }
            public HashMap<string, Value?> associated_data = null;

            public MyListBoxRow() {
                var box = new Box(Orientation.HORIZONTAL, 8);
                set_child(box);
                
                var img = new Image();
                img.icon_name = "folder-symbolic";
                img.margin_start = 8;
                img.margin_end = 4;
                box.append(img);

                label = new Label(null);
                label.halign = Align.START;
                //  label.margin_start = 32;
                label.margin_top = 12;
                label.margin_bottom = 12;
                label.ellipsize = Pango.EllipsizeMode.END;
                box.append(label);
            }
        }

        private class RepoBinder: Htg.ListBinder<HashMap<string, Value?>> {
            public RepoBinder(ListBox listbox) {
                base(listbox);
            }

            public override Widget setup_widget () {
                var row = new MyListBoxRow();
                //  row.activate.connect(() => {
                //      print("Hello\n");
                //  });
                return row;
            }

            public override void bind_widget (Gtk.Widget row, HashMap<string, Value?> data) {
                ((MyListBoxRow) row).label.label = (string) data["name"];
                ((MyListBoxRow) row).associated_data = data;
            }

            public override void insert_child(Widget widget, int index) {
                ((ListBox) container).insert (widget, index);
            }

            public override void append_child (Gtk.Widget widget) {
                ((ListBox) container).append (widget);
            }

            public override void remove_child (Gtk.Widget widget) {
                ((ListBox) container).remove (widget);
            }
        }
    }
}
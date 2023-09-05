using Gtk, Gee;

namespace org.htg.hashfolder {
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
            content_frag.on_update_request.connect(sidebar_frag.refresh);
            ((Adw.Bin) builder.get_object("content")).set_child(content_frag.content);

            sidebar_frag.item_selected.connect(content_frag.show_item);
            sidebar_frag.item_selected.connect((data) => {
                leaflet.navigate(Adw.NavigationDirection.FORWARD);
                page_back.visible = leaflet.folded && viewstack.visible_child_name == "repos";
            });

            //  leaflet.set_chi
        }
    }
}
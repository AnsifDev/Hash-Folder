using Gtk, Gee;

namespace Htg {
    public class ActivityPage: Box, Buildable {
        private Widget _title_bar = null;

        public Widget content { get; set; default = null; }
        public Widget title_bar { 
            get { return _title_bar; }
            set { 
                if (_title_bar != null) this.remove(_title_bar);
                if (value != null) this.prepend(value);
                _title_bar = value;
            }
        }

        construct {
            orientation = Orientation.VERTICAL;
            spacing = 0;
        }
    }

    public class Activity: Object {
        //Properties
        public ActivityPage activity_page { get; private set; default = null; }
        public Builder builder { get; private set; default = new Builder(); }
        public Value intent_data { get; private set; }
        public bool started { get; private set; default = false; }
        internal bool allow_default_header = true;

        private ArrayList<ActivityFragment> fragments = new ArrayList<ActivityFragment>();

        // General Methods
        protected void finish() {
            get_application().activity_manager.end_activity(this);
        }

        protected void finish_with_result(Value? result) {
            get_application().activity_manager.end_activity_with_result(this, result);
        }

        protected void set_content(string layout_name) {
            if (started) { critical("Setting ui file after construction not allowed"); return; }
            if (activity_page != null) { warning("Setting content is availed for only once!!!"); return; }
            try { builder.add_from_resource(@"/$(GLib.Application.get_default().get_application_id().replace(".", "/"))/gtk/$layout_name"); }
            catch (Error e) { error("%s\n", e.message); }
            foreach (var widget in builder.get_objects()) if (widget is ActivityPage) {
                activity_page = widget as ActivityPage;
                return;
            }
            warning("ActivityPage Widget not found");
        }

        public Application get_application() { return GLib.Application.get_default() as Application; }

        internal void add_fragment(ActivityFragment fragment) {
            if (fragment in fragments) warning("Fragment already registered to this activity\n");
            else fragments.add(fragment);
        }

        // Lifecycle Methods
        internal virtual void on_create() {}

        protected virtual void on_started() {
            foreach (var fragment in fragments) fragment.on_started();
        }

        protected virtual void on_stopped() {
            foreach (var fragment in fragments) fragment.on_stopped();
        }

        internal virtual void on_destroy() {
            foreach (var fragment in fragments) fragment.on_destroy();
        }

        internal virtual signal void on_result_available(int request_id, Value? result);

        // Lifecycle Handlers
        //  internal void perform_start_with_request(int request_id, Value? data = null) {
        //      this.request_id = request_id;
        //      perform_start(data);
        //  }

        internal void perform_start(Value? data = null) {
            if (started) { critical("Activity already started!!!"); return; }
            if (data != null) intent_data = data;
            else intent_data.unset();
            started = true;
            on_started();
        }

        internal void perform_stop() {
            if (!started) { critical("Activity already stopped!!!"); return; }
            on_stopped();
            started = false;
        }
    }
}
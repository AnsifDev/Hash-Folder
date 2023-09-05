using Gee, Gtk;

namespace Htg {
    public class ActivityFragment: Object {
        public Activity parent { get; private set; }
        public Builder builder { get; private set; }
        public ActivityPage content { get; private set; }

        public ActivityFragment(Activity parent, string? ui_file = null) {
            this.parent = parent;
            parent.add_fragment(this);

            if (ui_file != null) {
                builder = new Builder.from_resource (@"/$(parent.get_application().application_id.replace(".", "/"))/gtk/$ui_file");
                foreach (var widget in builder.get_objects()) if (widget is ActivityPage) {
                    content = widget as ActivityPage;
                    break;
                }
            }
        }

        internal virtual void on_started() {} 
        
        internal virtual void on_stopped() {}

        internal virtual void on_destroy() {}
    }
}
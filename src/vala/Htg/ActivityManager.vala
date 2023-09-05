using Gtk, Gee;

namespace Htg {
    public class ActivityManager: Box, Buildable {
        private Adw.Bin container;
        private Adw.HeaderBar header_bar;
        private Stack stack;
        private Button nav_back;
        private ArrayList<Activity> activity_stack = new ArrayList<Activity>();
    
        public bool can_navigate_back { get; private set; default = false;}

        construct {
            orientation = Orientation.VERTICAL;

            var builder = new Builder.from_resource(@"/$(GLib.Application.get_default().get_application_id().replace(".", "/"))/gtk/activity_mgr.ui");
            header_bar = builder.get_object("header_bar") as Adw.HeaderBar;
            container = builder.get_object("container") as Adw.Bin;
            stack = builder.get_object("stack") as Stack;
            nav_back = builder.get_object("nav_back") as Button;

            append(header_bar);
            append(container);

            bind_property("can-navigate-back", nav_back, "visible", GLib.BindingFlags.SYNC_CREATE);
            nav_back.clicked.connect(on_button_clicked);
            stack.transition_type = StackTransitionType.SLIDE_LEFT_RIGHT;
    
            base.constructed();
        }

        private void on_button_clicked(Button button) {
            if (button == nav_back) navigate_back();
        }

        private void launch_instance(Activity? current_activity, Activity new_activity, Value? data = null) {
            if (!(new_activity in activity_stack)) {
                activity_stack.insert(0, new_activity);
                new_activity.on_create();
                if (!(new_activity in activity_stack)) {
                    print("Finished on on_create\n");
                    return;
                }
                stack.add_child(new_activity.activity_page);
            }

            var new_activity_page = new_activity.activity_page;
            
            if (current_activity != null) current_activity.perform_stop();
            
            header_bar.visible = new_activity.allow_default_header && new_activity_page.title_bar == null;
            stack.set_visible_child(new_activity_page);
            new_activity.perform_start(null);

            can_navigate_back = activity_stack.size > 1;
        }

        public void start_activity(Activity? current_activity, Type activity_class, Value? data = null) {
            if (current_activity == null && activity_stack.size != 0 || current_activity != null && !current_activity.started) 
            { critical("Only started activities can invoke start_activity method"); return; }
            
            Activity new_activity = null;
            foreach (var instance in activity_stack) if (instance.get_type() == activity_class) {
                new_activity = instance;
                activity_stack.remove(instance);
                activity_stack.insert(0, instance);
                break;
            }
            
            if (new_activity == null) new_activity = (Activity) Object.new(activity_class);
            else if (new_activity == current_activity) {
                warning("Cannot start this activity again, since its already started and single instanced");
                return;
            }

            launch_instance(current_activity, new_activity, data);
        }

        internal void end_activity(Activity activity, Value? data = null) {
            activity_stack.remove(activity);
            if (activity.started) {
                if (activity_stack.size > 0) launch_instance(activity, activity_stack[0], data);
                else activity.perform_stop();
            }

            activity.on_destroy();
            var app = GLib.Application.get_default() as Application;
            if (activity_stack.size <= 0 && app != null) app.window.destroy();
        }

        public void navigate_back() {
            end_activity(activity_stack[0]);
        }

        public void clear_nav_stack() {
            while (activity_stack.size > 1) activity_stack.remove_at(1).on_destroy();
        }

        public void add_child(Builder builder, Object child, string? type) {
            critical("No childing is possible for this widget");
        }
    }
}
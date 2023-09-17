using Gtk, Gee;

namespace Htg {
    public class Application: Adw.Application {
        //  private bool flatpak;
        private Type launcher_activity_class;
        private HashMap<string, Settings> opened_settings = new HashMap<string, Settings>();
        private Settings settings;

        public Adw.Window window { get; private set; default = null; }
        public ActivityManager activity_manager { get; private set; default = null; }

        public Application(string? id, GLib.ApplicationFlags flags, Type launcher_activity_class) throws Error {
            Object (application_id: id, flags: flags);
            this.launcher_activity_class = launcher_activity_class;
            settings = get_settings("window");
        }

        public Settings get_settings(string filename) {
            if (!opened_settings.has_key(filename)) opened_settings[filename] = new Settings(filename);
            return opened_settings[filename];
        }

        public override void activate() {
            window = get_active_window() as Adw.Window;
            if (window == null) {
                window = new Adw.Window();
                window.set_default_size(600, 450);
                window.application = this;
                window.title = "Hash Folder";
                window.content = activity_manager = new ActivityManager();
                window.close_request.connect(on_window_closed);
                window.add_css_class("devel");
                settings.bind("width", window, "default-width", 1067);
                settings.bind("height", window, "default-height", 800);
                settings.bind("maximized", window, "maximized", false);
                settings.bind("fullscreened", window, "fullscreened", false);
                activity_manager.start_activity(null, launcher_activity_class);
            }

            window.present();
        }

        //  public override void shutdown() {
        //      activity_manager.clear_nav_stack();
        //      if (activity_manager.can_navigate_back) activity_manager.navigate_back();
        //      foreach (var filename in opened_settings.keys)
        //          try { opened_settings[filename].save(); }
        //          catch (Error e) { critical("%s: %s\n", filename, e.message); }
        //      base.shutdown();
        //  }

        private bool on_window_closed(Window window) {
            settings.unbind(window);
            activity_manager.clear_nav_stack();
            if (activity_manager.can_navigate_back) activity_manager.navigate_back();
            foreach (var filename in opened_settings.keys)
                try { opened_settings[filename].save(); }
                catch (Error e) { critical("%s: %s\n", filename, e.message); }
            return false;
        }
    }
}


using Gee, Gtk;

namespace Htg {
    public class Settings: Object {
        private string filename;
        private HashMap<string, Value?> settings;
        private HashMap<string, ObjectWrapper> key_to_property_map = new HashMap<string, ObjectWrapper>();
        private HashMap<Object, HashMap<string, string>> property_to_key_map = new HashMap<Object, HashMap<string, string>>();
        
        public Settings(string filename) {
            this.filename = @"$(Environment.get_user_config_dir())/$(GLib.Application.get_default().application_id)/$(filename)";
            var file = File.new_for_path (this.filename);
            if (file.query_exists()) 
                try { settings = new JsonEngine().parse_file_to_hashmap (this.filename); }
                catch (Error e) { error("%s\n", e.message); }
            else settings = new HashMap<string, Value?>();
        }

        public void save() throws Error{
            var file = File.new_for_path(filename);
            if (!file.query_exists()) {
                var dir = file.get_parent();
                if (!dir.query_exists()) dir.make_directory_with_parents();
                file.create(FileCreateFlags.NONE);
            }
            new JsonEngine().parse_hashmap_to_file(settings, filename);
        }

        public new void set(string key, Value? value) {
            if (key_to_property_map.has_key(key)) 
                key_to_property_map[key].set_value(value);
            else settings[key] = value;
            //  print(@"Settings set: $key, $(value.get_string())\n");
        }

        public new Value? get(string key) { return settings[key]; }

        public bool contains (string key) { return settings.has_key(key); }

        public void bind(string key, Object object, string property, Value? default_value) {
            if (!property_to_key_map.has_key(object)) 
                property_to_key_map[object] = new HashMap<string, string>();
            if (property_to_key_map[object].has_key(property)) {
                warning("Only one key per property is allowed and vise versa\n");
                unbind(object, property);
            }
            property_to_key_map[object][property] = key;
            if (key_to_property_map.has_key(key)) {
                warning("Only one key per property is allowed and vise versa\n");
                unbind(key_to_property_map[key].object, key_to_property_map[key].property);
            }
            key_to_property_map[key] = new ObjectWrapper(object, property);
            object.notify[property].connect(notify_handler); 
            if (!settings.has_key(key)) settings[key] = default_value;
            object.set_property(property, settings[key]);
        }

        public void unbind(Object object, string? property = null) {
            if (property == null) {
                foreach (var prop in property_to_key_map[object].keys) {
                    object.notify[prop].disconnect(notify_handler);
                    key_to_property_map.unset(property_to_key_map[object][prop]);
                }
                property_to_key_map.unset(object);
            } else {
                string key;
                object.notify[property].disconnect(notify_handler);
                property_to_key_map[object].unset(property, out key);
                key_to_property_map.unset(key);
            }
        }

        private void notify_handler(Object object, ParamSpec param_spec) {
            var key = property_to_key_map[object][param_spec.name];
            Value value = Value(param_spec.value_type);
            object.get_property(param_spec.name, ref value);
            settings[key] = value;
        }

        private class ObjectWrapper: Object {
            public Object object { get; private set; }
            public string property { get; private set; }

            public ObjectWrapper(Object object, string property) {
                this.object = object;
                this.property = property;
            }

            public void set_value(Value? value) {
                object.set_property(property, value);
            }
        }
    }
}
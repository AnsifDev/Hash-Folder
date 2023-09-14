using Gtk, Gee, Json;

namespace org.htg.hashfolder {
    public HashMap<string, Value?>? load_ssh_config() {
        if (!File.new_for_path(Environment.get_home_dir()+"/.ssh/config").query_exists()) 
            return new HashMap<string, Value?>();

        string c;
        try { FileUtils.get_contents(Environment.get_home_dir()+"/.ssh/config", out c); }
        catch (Error e) { critical(e.message); return null; }
        
        var lines = c.split("\n");
        var ssh_config = new HashMap<string, Value?>();
        var current_host = "";
        foreach (var line in lines) {
            if (line.strip().length <= 0) continue;
            var pairs = line.strip().split(" ", 2);
            var key = pairs[0];
            var value = pairs[1];
            
            if (line[0] != ' ' && line[0] != '\t') {
                current_host = value;
                ssh_config[value] = new HashMap<string, Value?>();
            } else ((HashMap<string, Value?>) ssh_config[current_host])[key] = value;
        }

        return ssh_config;
    }

    public void store_ssh_config(HashMap<string, Value?> config) {
        var str_builder = new StringBuilder();
        foreach (var host in config.keys) {
            var host_config = (HashMap<string, Value?>) config[host];
            if (host_config.size <= 0) continue;
            str_builder.append(@"Host $host\n");
            foreach (var key in host_config.keys) {
                var value = (string) host_config[key];
                str_builder.append(@"\t$key $value\n");
            }
            str_builder.append("\n");
        }
        
        try { FileUtils.set_contents(Environment.get_home_dir()+"/.ssh/config", str_builder.str); }
        catch (Error e) { critical(e.message); }
    }
    
    public static void main(string[] args) {
        try {
            var app = new Htg.Application("org.htg.hashfolder", 0, typeof(LauncherActivity));
            app.run();
        } catch (Error e) { critical("%s\n", e.message); }
    }
}
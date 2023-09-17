using Gtk, Gee, Json;

namespace HashFolder {
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
        
        var file = File.new_for_path(Environment.get_home_dir()+"/.ssh/config");
        try {
            if (!file.get_parent().query_exists()) file.make_directory_with_parents();
            FileUtils.set_contents(Environment.get_home_dir()+"/.ssh/config", str_builder.str);
        } catch (Error e) { critical(e.message); }
    }

    //  public string[] parse_to_args(string cmd) {
    //      var splited = cmd.split(" ");
    //      var args = new string[splited.length];
    //      var args_length = 0;
    //      var prevent_breaks = false;

    //      foreach (var arg in splited) {
    //          if (prevent_breaks) args[args_length-1] += " "+arg;
    //          else if (args_length > 0 && args[args_length-1].has_suffix("\\")) args[args_length-1] = args[args_length-1].replace("\\", " ") + arg;
    //          else args[args_length++] = arg;

    //          //  for (int i = 0; i < arg.length; i++) {
    //          //      if (arg[i] == '\"') prevent_breaks = !prevent_breaks;
    //          //  }
    //          if (arg[0] == '\"' || arg[arg.length-1] == '\"') prevent_breaks = !prevent_breaks;
    //      }

    //      var final_args = new string[args_length];
    //      var final_args_length = 0;
        
    //      for (int i = 0; i < args_length; i++) {
    //          var start = args[i][0] == '\"'? 1: 0;
    //          var end = args[i][args[i].length-1] == '\"'? args[i].length-1: args[i].length;
    //          final_args[final_args_length++] = args[i][start:end];
    //      }
    //      return final_args;
    //  }
    
    public static void main(string[] args) {
        try {
            var app = new Htg.Application("org.htg.hashfolder", 0, typeof(LauncherActivity));
            app.run();
        } catch (Error e) { critical("%s\n", e.message); }

        //  print("Hello\n"[2:]);
        //  var arguments = parse_to_args("gh repo create \"Hello World\" -s=Ansif/Lab\\ Programs/git");
        //  foreach (var arg in arguments) print("%s\n", arg);
    }
}
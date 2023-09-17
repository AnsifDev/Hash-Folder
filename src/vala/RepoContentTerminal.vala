using Gee, Gtk, Htg, Vte;

namespace HashFolder {
    class RepoContentTerminal: Adw.Bin {
        private ArrayList<string> cmd_queue = new ArrayList<string>();
        private HashMap<string, string> cmd_store = new HashMap<string, string>();

        private Terminal term;

        public bool sleeping { get; private set; default = true; }
        public bool safe_mode { get; set; default = false; }
        public Bin term_bin { get; private set; }

        construct {
            var builder = new Builder.from_resource ("/org/htg/hashfolder/gtk/repo_content_terminal.ui");
            var root = (Revealer) builder.get_object ("root");
            var term_unreveal = (Button) builder.get_object ("term_unreveal");
            term_bin = (Bin) builder.get_object ("term_bin");
            term = (Terminal) builder.get_object ("term");

            child = root;
            bind_property("sleeping", term_unreveal, "visible", GLib.BindingFlags.SYNC_CREATE);

            term_unreveal.clicked.connect (() => { root.reveal_child = false; });

            term.child_exited.connect ((status) => {
                on_task_completed(cmd_queue[0], status);

                if (status != 0 && safe_mode) clear_all_pending_tasks();
                cmd_store.unset(cmd_queue.remove_at(0));

                if (cmd_queue.size > 0) resume_task_execution();
                else sleeping = true;
            });
        }

        public void add_task(string id, string cmd) {
            //  print("Task added\n");
            if (id in cmd_queue) 
                { critical("Duplicate id for the task. Id provided is already holding a task in the queue."); return; }
            
            cmd_queue.add(id);
            cmd_store[id] = cmd;
            if (cmd_queue.size == 1) resume_task_execution();
        }

        public void remove_task(string id) {
            if (cmd_queue[0] == id) terminate_task();
            else { cmd_queue.remove(id); cmd_store.unset(id); }
        }

        public void terminate_all_tasks() {
            clear_all_pending_tasks();
            terminate_task();
        }

        public void clear_all_pending_tasks() { while (cmd_queue.size > 1) cmd_store.unset(cmd_queue.remove_at(1)); }

        public bool contains(string id) { return id in cmd_queue; }

        private void resume_task_execution() {
            //  print("Execution resumed\n");
            if (sleeping) {
                sleeping = false;
                ((Revealer) child).reveal_child = true;
            }
            term.spawn_async(
                Vte.PtyFlags.DEFAULT, 
                null, 
                //  parse_to_args("/bin/echo echo hello"),
                parse_to_args(cmd_store[cmd_queue[0]]), 
                //  cmd_store[cmd_queue[0]].split(" "),
                null, 
                GLib.SpawnFlags.FILE_AND_ARGV_ZERO, 
                null, 
                120, 
                null, 
                () => { on_task_started(cmd_queue[0]); }
            );
        }

        private void terminate_task() {
            uint8[] inp = {3};
            term.feed_child(inp);
        }

        //  private string[] parse_to_args(string cmd) {
        //      var args = new ArrayList<string>();
        //      var arg = "";
        //      var prevent_breaks = false;

        //      for (int i = 0; i < cmd.length; i++) {
        //          var character = cmd[i];

        //          if (character == '\\') arg = arg+(cmd[++i]).to_string();
        //          else if (character == '\"') prevent_breaks = !prevent_breaks;
        //          else if (character == ' ' && !prevent_breaks && arg.length > 0) { args.add((string) arg.strip()); arg = ""; }
        //          else arg = arg+(character).to_string();
        //      } if (arg.length > 0) args.add((string) arg.strip());

        //      foreach (var argument in args) print("%s\n", argument);
        //      return args.to_array();
        //  }

        private string[] parse_to_args(string cmd) {
            var splited = cmd.split(" ");
            var args = new string[splited.length];
            var args_length = 0;
            var prevent_breaks = false;

            foreach (var arg in splited) {
                if (prevent_breaks) args[args_length-1] += " "+arg;
                else if (args_length > 0 && args[args_length-1].has_suffix("\\")) args[args_length-1] = args[args_length-1].replace("\\", " ") + arg;
                else args[args_length++] = arg;

                //  print("%s\n", arg);
                if (arg[0] == '\"') prevent_breaks = !prevent_breaks;
                if (arg[arg.length-1] == '\"') prevent_breaks = !prevent_breaks;
            }

            var final_args = new string[args_length];
            var final_args_length = 0;
            
            for (int i = 0; i < args_length; i++) {
                var start = args[i][0] == '\"'? 1: 0;
                var end = args[i][args[i].length-1] == '\"'? args[i].length-1: args[i].length;
                final_args[final_args_length++] = args[i][start:end];
            }
            return final_args;
        }


        public signal void on_task_started(string id);

        public signal void on_task_completed(string id, int status);
    }
}
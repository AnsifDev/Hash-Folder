using Gee;

namespace Htg {
    public static void println(string str) { stdout.printf(str+"\n"); }
    public static string join_path(string str1, string str2) {
        if (str2.has_prefix("/")) return str2;
        if (str1.has_suffix("/")) return str1+str2;
        return str1+"/"+str2;
    }

    public async string[] list_dir(string path) throws Error {
        var folder = File.new_for_path(path);
        var files = new ArrayList<string>();
        var fileinfo_enum = yield folder.enumerate_children_async("", GLib.FileQueryInfoFlags.NOFOLLOW_SYMLINKS);
        FileInfo file_info;
        while ((file_info = fileinfo_enum.next_file ()) != null) 
            files.add(file_info.get_name());
        return files.to_array();
    }

    public async int run_command(string command) {
        var t = new Thread<int>("sub-command", () => {
            var status = Posix.system(command);
            Idle.add(run_command.callback);
            return status;
        });
        yield;
        return t.join();
    }
}
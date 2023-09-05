using Gee;

namespace Htg {
    public class YAMLEngine: GLib.Object {
        public HashMap<string, Value?>? parse_yaml_to_hashmap(string data) {
            var lines = data.strip().replace("\t", "    ").split("\n");
            var is_array = lines.length > 0? lines[0][0:2] == "- ": false;

            if (is_array) return null;
            else return handle_lines_to_hashmap(lines);
        }

        public ArrayList<Value?>? parse_yaml_to_array(string data) {
            var lines = data.strip().replace("\t", "    ").split("\n");
            var is_array = lines[0][0:2] == "- ";

            if (is_array) return handle_lines_to_array(lines);
            else return null;
        }

        public HashMap<string, Value?>? parse_file_to_hashmap(string filename) {
            string data;
            try { FileUtils.get_contents(filename, out data); }
            catch (Error e) { critical("%s\n", e.message); }
            return parse_yaml_to_hashmap(data);
        }

        public ArrayList<Value?>? parse_file_to_array(string filename) {
            string data;
            try { FileUtils.get_contents(filename, out data); }
            catch (Error e) { critical("%s\n", e.message); }
            return parse_yaml_to_array(data);
        }

        private int find_intendation(string line) {
            var intendation = 0;
            for (int i = 0; i < line.length; i++) 
                if (line[i] == ' ') intendation++;
                else break;
            return intendation;
        }

        private ArrayList<Value?> handle_lines_to_array(string[] lines) {
            var a = new ArrayList<Value?>();
            for (int i = 0; i < lines.length; i++) {
                Value value = lines[i].replace("- ", "").strip();
                if (value.get_string().strip().length == 0) {
                    var end = i+1;
                    var obj_intendation = find_intendation(lines[i]);
                    while (lines.length > end) 
                        if (find_intendation(lines[end]) < obj_intendation) break;
                        else end++;
                    i = end-1;

                    if (lines[++i][0:2] == "- ") value = handle_lines_to_array(lines[i: end]);
                    else value = handle_lines_to_hashmap(lines[i: end]);
                } else if (value.get_string().ascii_down() == "false") value = false;
                else if (value.get_string().ascii_down() == "true") value = true;
                else if (value.get_string()[0].isdigit()) value = double.parse(value.get_string());

                a.add(value);
            }
            return a;
        }
    
        private HashMap<string, Value?> handle_lines_to_hashmap(string[] lines) {
            var h = new HashMap<string, Value?>();
            for (int i = 0; i < lines.length; i++) {
                var line = lines[i].strip();
                var pairs = line.split(":", 2);
                var key = pairs[0];
                Value value = pairs[1].strip();
                
                if (value.get_string().strip().length == 0) {
                    var end = i+1;
                    var obj_intendation = find_intendation(lines[i]);
                    while (lines.length > end) 
                        if (find_intendation(lines[end]) < obj_intendation) break;
                        else end++;

                    if (lines[++i][0:2] == "- ") value = handle_lines_to_array(lines[i: end]);
                    else value = handle_lines_to_hashmap(lines[i: end]);
                    i = end-1;
                } else if (value.get_string().ascii_down() == "false") value = false;
                else if (value.get_string().ascii_down() == "true") value = true;
                else if (value.get_string()[0].isdigit()) value = double.parse(value.get_string());
    
                h[key] = value;
            }
            return h;
        }

        public string? parse_hashmap_to_string(HashMap<string, Value?> hashmap) {
            var lines = handle_hashmap_to_lines(hashmap, 0);
            StringBuilder strbuilder = new StringBuilder("");
            foreach (var line in lines) strbuilder.append(line+"\n");
            return strbuilder.str.strip();
        }

        public string? parse_array_to_string(ArrayList<Value?> array) {
            var lines = handle_array_to_lines(array, 0);
            StringBuilder strbuilder = new StringBuilder("");
            foreach (var line in lines) strbuilder.append(line+"\n");
            return strbuilder.str.strip();
        }

        private string build_intendation(int intendation) {
            StringBuilder strbuilder = new StringBuilder("");
            for(var i = 0; i < intendation*4; i++) strbuilder.append(" ");
            return strbuilder.str;
        }

        private string[] handle_hashmap_to_lines(HashMap<string, Value?> hashmap, int intendation) {
            string spaces = build_intendation(intendation);
            ArrayList<string> lines = new ArrayList<string>();
            foreach (var key in hashmap.keys) {
                var value = hashmap[key];
                if (value.type() == typeof(int)) lines.add(@"$spaces$key: $(value.get_int())");
                else if (value.type() == typeof(long)) lines.add(@"$spaces$key: $(value.get_long())");
                else if (value.type() == typeof(float)) lines.add(@"$spaces$key: $(value.get_float())");
                else if (value.type() == typeof(uint)) lines.add(@"$spaces$key: $(value.get_uint())");
                else if (value.type() == typeof(ulong)) lines.add(@"$spaces$key: $(value.get_ulong())");
                else if (value.type() == typeof(uint64)) lines.add(@"$spaces$key: $(value.get_uint64())");
                else if (value.type() == typeof(int64)) lines.add(@"$spaces$key: $(value.get_int64())");
                else if (value.type() == typeof(double)) lines.add(@"$spaces$key: $(value.get_double())");
                else if (value.type() == typeof(string)) lines.add(@"$spaces$key: $(value.get_string())");
                else if (value.type() == typeof(HashMap)) {
                    lines.add(@"$spaces$key: ");
                    lines.add_all_array(handle_hashmap_to_lines((HashMap<string, Value?>) value, intendation+1));
                } else if (value.type() == typeof(ArrayList)) {
                    lines.add(@"$spaces$key: ");
                    lines.add_all_array(handle_array_to_lines((ArrayList<Value?>) value, intendation+1));
                }
            }

            return lines.to_array();
        }

        private string[] handle_array_to_lines(ArrayList<Value?> array, int intendation) {
            string spaces = build_intendation(intendation);
            ArrayList<string> lines = new ArrayList<string>();
            foreach (var value in array) {
                if (value.type() == typeof(int)) lines.add(@"$spaces- $(value.get_int())");
                else if (value.type() == typeof(long)) lines.add(@"$spaces- $(value.get_long())");
                else if (value.type() == typeof(float)) lines.add(@"$spaces- $(value.get_float())");
                else if (value.type() == typeof(uint)) lines.add(@"$spaces- $(value.get_uint())");
                else if (value.type() == typeof(ulong)) lines.add(@"$spaces- $(value.get_ulong())");
                else if (value.type() == typeof(uint64)) lines.add(@"$spaces- $(value.get_uint64())");
                else if (value.type() == typeof(int64)) lines.add(@"$spaces- $(value.get_int64())");
                else if (value.type() == typeof(double)) lines.add(@"$spaces- $(value.get_double())");
                else if (value.type() == typeof(string)) lines.add(@"$spaces- $(value.get_string())");
                else if (value.type() == typeof(HashMap)) {
                    lines.add(@"$spaces- ");
                    lines.add_all_array(handle_hashmap_to_lines((HashMap<string, Value?>) value, intendation+1));
                } else if (value.type() == typeof(ArrayList)) {
                    lines.add(@"$spaces- ");
                    lines.add_all_array(handle_array_to_lines((ArrayList<Value?>) value, intendation+1));
                }
            }

            return lines.to_array();
        }
    }
}
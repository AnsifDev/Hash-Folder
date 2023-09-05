using Gee, Gtk;

namespace Htg {
    public abstract class ListBinder<T>: Object {
        public Widget container { get; private set; }

        private ArrayList<Widget> children = new ArrayList<ListBoxRow>();
        private ArrayList<Widget> trash = new ArrayList<ListBoxRow>();
        private ArrayList<T> data_list;

        protected ListBinder(Widget container) {
            this.container = container;
        }

        public void set_data_list(ArrayList<T> data_list) {
            this.data_list = data_list;

            //  print("Stage 0\n");
            //  var prev = container.get_first_child();
            //  for (var row = container.get_first_child(); row != null; row.get_next_sibling()) {
            //      print(@"$(prev == row)\n");
            //      children.add(row);
            //      prev = row;
            //  }

            //  print("Stage 1\n");
            while (children.size > 0) remove_child(children.remove_at(0));

            foreach (var data in data_list) {
                var widget = setup_widget();
                children.add(widget);
                append_child(widget);
                //  ((ListBox) container).append(widget);
                bind_widget(widget, data);
            }
        }

        public void notify_data_set_changed() {
            for (int i = 0; i < data_list.size; i++) {
                if (children.size <= i) {
                    var widget = trash.size > 0? trash.remove_at(0): setup_widget();
                    children.add(widget);
                    append_child(widget);
                }
                bind_widget(children[i], data_list[i]);
            }

            var prev_size = children.size;
            for (int i = data_list.size; i < prev_size; i++) {
                var widget = children.remove_at(data_list.size);
                remove_child(widget);
                trash.add(widget);
            }
        }

        public void notify_data_inserted_at(int position, int count = 1) {
            for (int i = position; i < position+count; i++) {
                var widget = trash.size > 0? trash.remove_at(0): setup_widget();
                insert_child(widget, i);
                children.insert(i, widget);
                bind_widget(children[i], data_list[i]);
            }
        }

        public void notify_data_deleted_at(int position, int count = 1) {
            for (int i = position; i < position+count; i++) {
                var widget = children.remove_at(i);
                remove_child(widget);

                trash.add(widget);
            }
        }

        public void notify_data_changed_at(int position) {
            bind_widget(children[position], data_list[position]);
        }

        public abstract void insert_child(Widget widget, int index);

        public abstract void append_child(Widget widget);

        public abstract void remove_child(Widget widget);

        public abstract Widget setup_widget();

        public abstract void bind_widget(Widget widget, T data);
    }
}
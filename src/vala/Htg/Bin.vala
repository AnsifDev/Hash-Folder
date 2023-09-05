using Gtk;

namespace Htg {
    public class Bin: Widget, Buildable {
        private Widget _child;

        //Properties
        public Widget child {
            get { return _child; }
            set { value.set_parent(this); _child = value; }
        }
        public int padding_start { get; set; default = 0; }
        public int padding_end { get; set; default = 0; }
        public int padding_top { get; set; default = 0; }
        public int padding_bottom { get; set; default = 0; }
        public int horizontal_padding {
            get { return padding_start == padding_end? padding_start: -1; }
            set { padding_start = padding_end = value; }
        }
        public int vertical_padding {
            get { return padding_top == padding_bottom? padding_top: -1; }
            set { padding_top = padding_bottom = value; }
        }
        public int padding {
            get { return horizontal_padding == vertical_padding? horizontal_padding: -1; }
            set { horizontal_padding = vertical_padding = value; }
        }
        public int horizontal_margin {
            get { return margin_start == margin_end? margin_start: -1; }
            set { margin_start = margin_end = value; }
        }
        public int vertical_margin {
            get { return margin_top == margin_bottom? margin_top: -1; }
            set { margin_top = margin_bottom = value; }
        }
        public int margin {
            get { return horizontal_margin == vertical_margin? horizontal_margin: -1; }
            set { horizontal_margin = vertical_margin = value; }
        }
        public int hnatural { get; set; default = -1; }
        public int vnatural { get; set; default = -1; }

        //Constructor
        public Bin() {}

        //Destructor
        ~Bin() { if (_child != null) _child.unparent(); }

        //Methods
        public virtual void add_child(Builder builder, Object child, string? type) {
            this.child=child as Widget;
        }

        public override void size_allocate(int width, int height, int baseline) {
            var allocation = Allocation();
            allocation.x = padding_start;
            allocation.y = padding_top;
            allocation.width = width - (padding_start + padding_end);
            allocation.height = height - (padding_top + padding_bottom);
            
            if (_child != null) _child.allocate_size(allocation, baseline);
        }

        public override void measure(Orientation orientation, int for_size, out int minimum, out int natural, out int minimum_baseline, out int natural_baseline) {
            if (_child != null) _child.measure(orientation, for_size, out minimum, out natural, out minimum_baseline, out natural_baseline);
            else {
                minimum_baseline = natural_baseline = -1;
                minimum = natural = 0;
            }

            if (orientation == Orientation.HORIZONTAL) { 
                if (hnatural > -1) natural = minimum > hnatural? minimum: hnatural;
                minimum += (padding_start + padding_end);
                natural += (padding_start + padding_end);
                //  if (-1 < hnatural < minimum) natural = minimum;
                //  else if (hnatural > minimum) natural = hnatural;
            } else { 
                if (vnatural > -1) natural = minimum > vnatural? minimum: vnatural;
                minimum += (padding_top + padding_bottom);
                natural += (padding_top + padding_bottom);
                //  if (-1 < vnatural <= minimum) natural = minimum;
                //  else if (vnatural > minimum) natural = vnatural;
            }
        }
    }
}
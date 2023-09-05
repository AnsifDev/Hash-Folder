using Gtk;
using Gee;

namespace Htg {
    public class BreakpointBin: Bin, Buildable {
        private ArrayList<Breakpoint> breakpoints = new ArrayList<Breakpoint>();
        private int min_width = -1;
        private int min_height = -1;
        private bool initialized = false;

        construct {
            hexpand = true;
            vexpand = true;
        }

        public void add_breakpoint(Breakpoint breakpoint) { breakpoints.add(breakpoint); }

        public void remove_breakpoint(Breakpoint breakpoint) { breakpoints.remove(breakpoint); }

        public override void size_allocate(int width, int height, int baseline) {
            //  println(@"Allocating width: $width, height: $height, baseline: $baseline");
            foreach (Breakpoint breakpoint in breakpoints) breakpoint.allocate(width);
            base.size_allocate(width, height, baseline);

            initialized = true;
        }

        public override void measure(Orientation orientation, int for_size, out int minimum, out int natural, out int minimum_baseline, out int natural_baseline) {
            base.measure(orientation, for_size, out minimum, out natural, out minimum_baseline, out natural_baseline);

            if (orientation == Orientation.HORIZONTAL && (min_width == -1 || min_width > minimum)) min_width = minimum;
            if (orientation == Orientation.VERTICAL && (min_height == -1 || min_height > minimum)) min_height = minimum;
            if (breakpoints.size > 0) 
                if (orientation == Orientation.HORIZONTAL) minimum = initialized? min_width: 0;
                else minimum = initialized? min_height: 0;
        }

        public override void add_child(Builder builder, Object object, string? type) {
            if (object is Breakpoint) add_breakpoint((Breakpoint) object);
            else base.add_child(builder, object, type);
        }
    }
}
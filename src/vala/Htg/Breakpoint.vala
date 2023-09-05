namespace Htg {
    public class Breakpoint: Object {
        public int threshold_width { get; set; default = -1; }
        public bool narrow { get; internal set; default = false; }

        public Breakpoint(bool narrow = false) { this.narrow = narrow; }

        public void allocate(int width) {
            bool new_narrow = width < threshold_width;
            if (narrow ^ new_narrow) narrow = new_narrow;
        }
    }
}
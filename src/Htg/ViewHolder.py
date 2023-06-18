class ViewHolder: 
    
    __signal_mapper = {}

    def connect_signal(self, widget, signal_name, callback):
        if widget not in self.__signal_mapper:
            signals = {}
            self.__signal_mapper[widget] = signals
        else: signals = self.__signal_mapper[widget]

        if signal_name not in signals:
            def signal_handler(widget, *args):
                self.__signal_mapper[widget][signal_name](widget, *args)

            widget.connect(signal_name, signal_handler)
        
        signals[signal_name] = callback

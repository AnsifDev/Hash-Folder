from . import EntryRow

class PasswordEntryRow(EntryRow):
    __gtype_name__ = "HtgPasswordEntryRow"

    def __init__(self) -> None:
        super().__init__()

        self._en_edit.set_visibility(False)
        self._en_edit.set_invisible_char("*")

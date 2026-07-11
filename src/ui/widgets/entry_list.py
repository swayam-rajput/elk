from textual.containers import VerticalScroll

from ui.messages import SelectionChanged
from ui.widgets.entry_item import EntryRow, EmailRow, SettingRow
from models.entry import Entry
from models.email import Email


class ScrollableList(VerticalScroll):
    can_focus = True
    BINDINGS = [
        ("up", "select_previous"),
        ("down", "select_next"),
        ("j", "select_next"),
        ("k", "select_previous"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._items = []
        self._row_widgets = []
        self.selected_index = 0

    def load_items(self, items, select_index: int = 0):
        self._items = items
        self.selected_index = 0
        self.remove_children()
        self._row_widgets = []
        for item in items:
            if isinstance(item, Entry):
                row = EntryRow(item, selected=False)
            elif isinstance(item, Email):
                row = EmailRow(item, selected=False)
            elif type(item).__name__ == "SettingItem":
                row = SettingRow(item, selected=False)
            else:
                continue
            self._row_widgets.append(row)
            self.mount(row)
        
        if self._row_widgets:
            idx = min(select_index, len(items) - 1)
            self.selected_index = idx
            self._row_widgets[idx].selected = True

    def action_select_next(self):
        if self.selected_index < len(self._items) - 1:
            self._row_widgets[self.selected_index].selected = False
            self.selected_index += 1
            self._row_widgets[self.selected_index].selected = True
            self.scroll_to_widget(self._row_widgets[self.selected_index])
            self.post_message(SelectionChanged(self.selected_index))

    def action_select_previous(self):
        if self.selected_index > 0:
            self._row_widgets[self.selected_index].selected = False
            self.selected_index -= 1
            self._row_widgets[self.selected_index].selected = True
            self.scroll_to_widget(self._row_widgets[self.selected_index])
            self.post_message(SelectionChanged(self.selected_index))

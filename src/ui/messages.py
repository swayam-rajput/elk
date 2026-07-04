from textual.message import Message


class SelectionChanged(Message):
    def __init__(self, index: int) -> None:
        self.index = index
        super().__init__()

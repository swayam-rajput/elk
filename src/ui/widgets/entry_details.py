from textual.widgets import Static

from models.entry import Entry


class EntryDetails(Static):

    def show_entry(
        self,
        entry: Entry,
    ):

        username = entry.username or "-"

        self.update(
f"""
Site

{entry.site.name}

URL

{entry.site.url}

Username

{username}

Password

**************

Notes

{entry.notes}
"""
        )
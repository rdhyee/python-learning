from rdhyee_utils.google_chrome import GoogleChrome
from pandas import DataFrame


from textual import on
from textual.app import App, ComposeResult
from textual.events import Mount
from textual.widgets import Footer, Header, SelectionList, Pretty
from textual.containers import ScrollableContainer
from textual.widgets.selection_list import Selection


class TabsList(SelectionList):
    def on_mount(self) -> None:
        self.border_title = "Tabs"

        self.gc = GoogleChrome()
        self.refresh_tabs()

    def load_tabs(self):
        self.df = DataFrame(
            [
                {
                    "title": tab.title,
                    "id": int(tab.id),
                    "window_id": int(tab.window_id),
                    "url": tab.url,
                    "tab": tab,
                }
                for tab in self.gc.tabs
            ]
        )

    def tabs_options(self):
        return self.df.apply(
            lambda row: (row["title"], (row["id"], row["window_id"])), axis=1
        ).to_list()

    def refresh_tabs(self, *args):
        self.load_tabs()

        self.clear_options()
        self.add_options(self.tabs_options())

    @property
    def current_tabs(self):
        tabs = []
        for c in self.selected:
            tab_id = c[0]
            # window_id = c[1]
            # rawtab = gco.gc.windows.ID(window_id).tabs.ID(tab_id)
            q = f"id == {tab_id}"
            try:
                rawtab = self.df.query(q).iloc[0]["tab"]
                tabs.append(rawtab)
            except Exception:
                pass
        return tabs


class BrowserApp(App):
    CSS_PATH = "browser.css"
    BINDINGS = [
        ("d", "toggle_dark_mode", "Toggle dark mode"),
        ("r", "refresh_tabs", "Refresh tabs"),
        ("f", "focus_tab", "Focus tab"),
        ("c", "close_tab", "Close tab"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer():
            yield TabsList(id="tabs-list")
        yield Pretty([], id="pretty")
        yield Footer()

    @on(Mount)
    @on(SelectionList.SelectedChanged)
    def update_selected_view(self) -> None:
        self.query_one("#pretty").update(self.query_one("#tabs-list").selected)

    def action_toggle_dark_mode(self):
        """
        Toggle the dark mode of the application.
        """
        self.dark = not self.dark

    def action_refresh_tabs(self):
        """
        Refresh the tabs list.
        """
        self.query_one("#tabs-list").refresh_tabs()

    def action_focus_tab(self):
        """
        Focus the selected tab.
        """
        # focus on the first selected tab
        tabs = self.query_one("#tabs-list").current_tabs
        if tabs:
            tabs[0].focus()

    def action_close_tab(self):
        """
        Close the selected tab.
        """
        # close all selected tabs
        tabs = self.query_one("#tabs-list").current_tabs
        for tab in tabs:
            tab.close()
        self.query_one("#tabs-list").refresh_tabs()


if __name__ == "__main__":
    BrowserApp().run()

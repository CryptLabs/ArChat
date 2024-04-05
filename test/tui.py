from typing import Coroutine
from textual.app import App, ComposeResult
from textual.widgets import Pretty
from textual.widgets import Header, Footer
from textual.widgets import Static
from textual import events
from textual.screen import Screen



# blue screen of death
ABOUT_TEXT = """
Arch Linux can be challenging for new users due to its minimalistic and do-it-yourself approach. The installation process requires manual configuration and a good understanding of Linux systems. Additionally, troubleshooting and finding relevant information from the official ArchWiki documentation can be time-consuming for both new users and experienced administrators.

ArchI aims to simplify the Arch Linux experience by providing a terminal-friendly AI assistant. It leverages data from the official ArchWiki documentation to provide fast and easy support for new users, administrators, and programmers. With ArchI, users can quickly access information, troubleshoot issues, and find solutions without the need for a desktop environment or a browser.
"""

class ABOUT(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        yield Static(" About", id="title")
        yield Static(ABOUT_TEXT)
        yield Static("Press Esc to continue [blink]_[/]", id="any-key")



class ArchIApp(App):
    CSS_PATH = "display.tcss"
    
    SCREENS = {"about": ABOUT()}
    
    BINDINGS = [("b", "push_screen('about')", "About"),("d", "toggle_dark", "Toggle dark mode"),("g", "toggle_green", "Toggle green mode")]
    
    COLORS = [
        "white",
        "maroon",
        "red",
        "purple",
        "fuchsia",
        "olive",
        "yellow",
        "navy",
        "teal",
        "aqua",
    ]
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        #yield Pretty(DATA)

        # yield Static("Widget 1")
        # yield Static("Widget 2", classes="remove")
        # yield Static("Widget 3")
        
    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_toggle_green(self) -> None:
        """An action to toggle dark mode."""
        self.screen.styles.background = "green"

    def on_mount(self) -> None:
        self.screen.styles.background = "darkblue"

    def on_key(self, event: events.Key) -> None:
        if event.key.isdecimal():
            self.screen.styles.background = self.COLORS[int(event.key)]


if __name__ == "__main__":
    app = ArchIApp()
    app.title = "ArchI"    
    app.run()
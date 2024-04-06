from typing import Coroutine
from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Pretty
from textual.widgets import Header, Footer
from textual.widgets import Static
from textual.widgets import Button
from textual.widgets import Input
from textual.widgets import Label
from textual import events
from textual.screen import Screen
from textual.widgets import Placeholder
import archi



# blue screen of death
ABOUT_TEXT = """
Arch Linux can be challenging for new users due to its minimalistic and do-it-yourself approach. The installation process requires manual configuration and a good understanding of Linux systems. Additionally, troubleshooting and finding relevant information from the official ArchWiki documentation can be time-consuming for both new users and experienced administrators.

ArchI aims to simplify the Arch Linux experience by providing a terminal-friendly AI assistant. It leverages data from the official ArchWiki documentation to provide fast and easy support for new users, administrators, and programmers. With ArchI, users can quickly access information, troubleshoot issues, and find solutions without the need for a desktop environment or a browser.
"""

class ABOUT(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen"),
                
                ]

    def compose(self) -> ComposeResult:
        yield Static(" About", id="title")
        yield Static(ABOUT_TEXT)
        yield Static("Press Esc to continue [blink]_[/]", id="any-key")


class ArchIApp(App):
    CSS_PATH = "display.tcss"
    SCREENS = {"about": ABOUT()}
    BINDINGS = [("b", "push_screen('about')", "About"),
                ("d", "toggle_dark", "Toggle dark mode"),
                ("g", "toggle_green", "Toggle green mode"),
                ("a", "ask_archi", "Ask ArchI"),
                ]
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
        #yield Button()
        #yield Input("Ask ArchI", id="ask")


        #yield Pretty(DATA)

        # yield Static("Widget 1")
        # yield Static("Widget 2", classes="remove")
        # yield Static("Widget 3")
        
    def action_ask_archi(self):
        #yield Label("Ask:")
        llm_type = "ChatOpenAI"
        llm = archi.load_llm(llm_type)

        query = "What is the the best editor for the terminal in Arch Linux?"
        chat_prompt = archi.create_chat_prompt(query)
        get_answer = archi.get_answer(llm, chat_prompt, query)
        
        self.mount(Static(get_answer,id="answer"))  

        
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
from typing import Coroutine
from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import (
    Pretty,
    Header,
    Footer,
    Static,
    Button,
    Input,
    Label,
    RichLog,
    Placeholder,
    LoadingIndicator,
)
from textual import events
from textual.screen import Screen
from textual.reactive import Reactive
from textual.containers import Horizontal, VerticalScroll
from textual import events
from pyfiglet import Figlet
import archi
import sys


# About screen
f = Figlet(font="slant")
BANNER = f.renderText("ArchI")
ABOUT_TEXT = (
    f.renderText("ArchI")
    + """
Arch Linux can be challenging for new users due to its minimalistic and do-it-yourself approach. The installation process requires manual configuration and a good understanding of Linux systems. Additionally, troubleshooting and finding relevant information from the official ArchWiki documentation can be time-consuming for both new users and experienced administrators.
ArchI aims to simplify the Arch Linux experience by providing a terminal-friendly AI assistant. It leverages data from the official ArchWiki documentation to provide fast and easy support for new users, administrators, and programmers. With ArchI, users can quickly access information, troubleshoot issues, and find solutions without the need for a desktop environment or a browser.
"""
)


class ABOUT(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        yield Static(" About", id="title")
        yield Static(ABOUT_TEXT, id="about")
        yield Static("Press Esc to continue", id="any-key")


class ArchIApp(App):

    CSS_PATH = "grid_layout_auto.tcss"

    #CSS_PATH = "display.tcss"
    SCREENS = {"about": ABOUT()}
    BINDINGS = [
        #("d", "toggle_dark", "Toggle dark mode"),
        # ("g", "toggle_green", "Toggle green mode"),
        ("b", "push_screen('about')", "About"),
        ("s", "search", "Search Packages"),
        ("g", "g", "Get Packages"),
        ("r", "r", "Remove Packages"),

        

        ("q", "quit", "Quit"),
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

    # def compose(self) -> ComposeResult:
    #     yield Header(show_clock=True)
    #     yield Static("Hello, I'm ArchI! How may I assist you today?", id="ask_window")
    #     yield Footer()
    #     yield Input("Ask me anything", id="ask_input")
    #     yield Horizontal(Button("Ask", id="ask_button"))
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(BANNER+"\n  Hello, I'm ArchI! How may I assist you today?", id="answer_window",classes="box")
        yield Input("Ask me anything ...", id="ask_input",classes="box")
        yield Button("Ask", id="ask_button", classes="box")
        yield Footer()

      


    def action_quit(self) -> None:
        sys.exit(0)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    # def action_toggle_green(self) -> None:
    #     """An action to toggle dark mode."""
    #     self.screen.styles.background = "green"

    # def on_mount(self) -> None:
    #     self.screen.styles.background = "darkblue"

    def on_key(self, event: events.Key) -> None:
        if event.key.isdecimal():
            self.screen.styles.background = self.COLORS[int(event.key)]

    def ask(self, query):
        # yield Label("Ask:")
        llm_type = "ChatOpenAI"
        llm = archi.load_llm(llm_type)

        # query = "What is the the best editor for the terminal in Arch Linux?"
        chat_prompt = archi.create_chat_prompt(query)
        get_answer = archi.get_answer(llm, chat_prompt, query)
        return get_answer

    def on_button_pressed(self) -> None:
        """Submit the asked question."""
        input = self.query_one(Input)
        query = input.value
        self.query_one(Input).value = ""
        self.query_one(Static).update(self.ask(query))


if __name__ == "__main__":
    app = ArchIApp()
    app.title = "ArchI"
    app.run()
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
from textual import log
from textual_terminal import Terminal
from textual.css.query import NoMatches
from pyfiglet import Figlet
import archat
import sys


# About screen
f = Figlet(font="slant")
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


class TerminalPlaceholder(Placeholder):
    pass


class ArchIApp(App):

    CSS_PATH = "display.tcss"
    SCREENS = {"about": ABOUT()}
    BINDINGS = [
        ("1", "start_1", "Start Terminal 1"),
        ("2", "start_2", "Start Terminal 2"),
        ("d", "toggle_dark", "Toggle dark mode"),
        # ("g", "toggle_green", "Toggle green mode"),
        ("b", "push_screen('about')", "About"),
        ("q", "quit", "Exit"),
    ]

    COMMANDS = {
        "terminal_1": "bash",
        "terminal_2": "bash",
        # "terminal_2": "htop -d15",s
    }

    COLORS = {
        "terminal_1": "system",
        "terminal_2": "textual",
    }

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Hello, I'm ArchI! How may I assist you today?", id="ask_window")
        yield Footer()
        yield Input("Ask me anything", id="ask_input")
        yield Horizontal(Button("Ask", id="ask_button"))

        yield VerticalScroll(
            Static("Terminal 1:", id="terminal_1_label"),
            TerminalPlaceholder("Terminal 1", id="terminal_1_ph"),
            # Terminal(self.COMMANDS["terminal_1"]),
            # Static("Terminal 2:", id="terminal_2_label"),
            # TerminalPlaceholder("Terminal 2", id="terminal_2_ph"),
            # Terminal(self.COMMANDS["terminal_2"]),
            classes="terminals",
        )

    def attach_terminal(self, name: str) -> None:
        try:
            self.query_one(f"#{name}_ph").remove()
        except NoMatches:
            log.warning(f"terminal {name} already attached")
            return

        log("attach terminal with id:", name)
        self.app.mount(
            Terminal(
                command=self.COMMANDS[name], id=name, default_colors=self.COLORS[name]
            ),
            after=f"#{name}_label",
        )

    def start_terminal(self, name: str) -> None:
        try:
            terminal: Terminal = self.app.query_one(f"Terminal#{name}")
        except NoMatches:
            log("no matches:", f"Terminal#{name}")
            return

        terminal.start()

    def stop_terminal(self, name: str) -> None:
        try:
            terminal: Terminal = self.app.query_one(f"Terminal#{name}")
        except NoMatches:
            log("no matches:", f"Terminal#{name}")
            return

        terminal.stop()

    def action_start_1(self) -> None:
        self.attach_terminal("terminal_1")
        self.start_terminal("terminal_1")

    def action_start_2(self) -> None:
        self.attach_terminal("terminal_2")
        self.start_terminal("terminal_2")

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

    # def on_key(self, event: events.Key) -> None:
    #     if event.key.isdecimal():
    #         self.screen.styles.background = self.COLORS[int(event.key)]

    def ask(self, query):
        # yield Label("Ask:")
        llm_type = "GPT4All"
        llm = archat.load_llm(llm_type)

        # query = "What is the the best editor for the terminal in Arch Linux?"
        chat_prompt = archat.create_chat_prompt(query)
        get_answer = archat.get_answer(llm, chat_prompt, query)
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

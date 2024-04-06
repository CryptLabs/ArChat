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
from textual.widgets import RichLog
from textual.widgets import Placeholder
from textual.widgets import LoadingIndicator
from textual.reactive import Reactive
from rich.align import Align
from rich.box import DOUBLE
from rich.console import RenderableType
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

from textual import events

from pyfiglet import Figlet
import archi
import sys



# About screen
f = Figlet(font='slant')
ABOUT_TEXT = f.renderText('ArchI') + """
Arch Linux can be challenging for new users due to its minimalistic and do-it-yourself approach. The installation process requires manual configuration and a good understanding of Linux systems. Additionally, troubleshooting and finding relevant information from the official ArchWiki documentation can be time-consuming for both new users and experienced administrators.

ArchI aims to simplify the Arch Linux experience by providing a terminal-friendly AI assistant. It leverages data from the official ArchWiki documentation to provide fast and easy support for new users, administrators, and programmers. With ArchI, users can quickly access information, troubleshoot issues, and find solutions without the need for a desktop environment or a browser.
"""

class ABOUT(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        yield Static(" About", id="title")
        yield Static(ABOUT_TEXT, id="about")
        yield Static("Press Esc to continue", id="any-key")
        
class InputText(Widget):
    title: Reactive[RenderableType] = Reactive("")
    content: Reactive[RenderableType] = Reactive("")

    def __init__(self, title: str):
        super().__init__(title)
        self.title = title

    def on_key(self, event: events.Key) -> None:
        self.content += event.key

    def validate_title(self, value) -> None:
        try:
          return value.lower()
        except (AttributeError, TypeError):
          raise AssertionError('title attribute should be a string.')

    def on_click(self) -> None:
        sys.exit(0)

    def render(self) -> RenderableType:
        renderable = Align.left(Text("", style="bold"))
        return Panel(
            renderable,
            title=self.title,
            title_align="center",
            height=3,
            style="bold white on rgb(50,57,50)",
            border_style=Style(color="green"),
            box=DOUBLE,
        )

class ArchIApp(App):
    
    CSS_PATH = "display.tcss"
    SCREENS = {"about": ABOUT()}
    BINDINGS = [("a", "ask_archi", "Ask ArchI"),
                ("d", "toggle_dark", "Toggle dark mode"),
                # ("g", "toggle_green", "Toggle green mode"),
                ("b", "push_screen('about')", "About"),
                ("q", "quit", "Quit")

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
   
    # async def on_mount(self) -> None:
    #     await InputText("input field")
        
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        yield InputText(title="ewqe")
        #yield Button()
        #yield Input("Ask ArchI", id="ask") 

        
    def action_ask_archi(self):
        #yield Label("Ask:")
        llm_type = "ChatOpenAI"
        llm = archi.load_llm(llm_type)

        query = "What is the the best editor for the terminal in Arch Linux?"
        chat_prompt = archi.create_chat_prompt(query)
        get_answer = archi.get_answer(llm, chat_prompt, query)
        
        self.mount(Static(get_answer,id="answer"))
        
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



if __name__ == "__main__":
    app = ArchIApp()
    app.title = "ArchI"    
    app.run()
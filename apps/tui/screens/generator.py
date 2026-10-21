from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Input, Label, Static


class GeneratorScreen(Screen):
    """AI Quiz Generator Screen for dynamic quiz synthesis."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("escape", "back_dashboard", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Container(classes="card"):
            yield Static("✨ [bold teal]AI Practice Quiz Generator[/bold teal]")
            yield Static("Generate custom adaptive quizzes tailored to your topic and difficulty.", classes="stat-label")
            yield Static("", id="gen-status", classes="stat-label")

            with Vertical(id="gen-form"):
                yield Label("Target Language:")
                yield Input(value="Spanish", id="gen-lang", placeholder="Spanish, Japanese, French, German, Italian")

                yield Label("CEFR Level:")
                yield Input(value="A1", id="gen-level", placeholder="A1, A2, B1, B2")

                yield Label("Practice Topic:")
                yield Input(value="Food & Dining", id="gen-topic", placeholder="e.g. Everyday Life, Travel, Coffee Shop")

                yield Label("Question Count (4, 6, or 10):")
                yield Input(value="4", id="gen-count", placeholder="4")

            with Horizontal(id="gen-buttons"):
                yield Button("Generate Quiz", variant="primary", id="btn-do-generate", classes="-primary")
                yield Button("Cancel", id="btn-gen-cancel", classes="-ghost")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-do-generate":
            self.run_worker(self.generate())
        elif event.button.id == "btn-gen-cancel":
            self.action_back_dashboard()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.run_worker(self.generate())

    async def generate(self) -> None:
        lang = self.query_one("#gen-lang", Input).value.strip() or "Spanish"
        level = self.query_one("#gen-level", Input).value.strip() or "A1"
        topic = self.query_one("#gen-topic", Input).value.strip() or "General Practice"
        count_str = self.query_one("#gen-count", Input).value.strip() or "4"
        try:
            count = int(count_str)
        except ValueError:
            count = 4

        status_lbl = self.query_one("#gen-status", Static)
        status_lbl.update("[bold cyan]Synthesizing exercises with natural grammar...[/bold cyan]")
        btn = self.query_one("#btn-do-generate", Button)
        btn.disabled = True

        try:
            quiz_id = await self.app.client.generate_quiz_job(
                language=lang,
                level=level,
                topic=topic,
                count=count,
            )
            if quiz_id:
                self.app.notify(f"Generated new {lang} quiz!", title="AI Generator", severity="information")
                self.app.start_quiz(quiz_id)
            else:
                status_lbl.update("[bold red]Failed to generate quiz. Please try again.[/bold red]")
                btn.disabled = False
        except Exception as e:
            status_lbl.update(f"[bold red]Error: {e}[/bold red]")
            btn.disabled = False

    def action_back_dashboard(self) -> None:
        self.app.switch_screen("dashboard")

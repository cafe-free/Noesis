from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Header, Label, Static


class ProgressScreen(Screen):
    """Learning Progress & Weak Areas Breakdown Screen."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("escape", "back_dashboard", "Back"),
        ("b", "back_dashboard", "Back to Dashboard"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(classes="card", id="progress-stats-row"):
            with Vertical(classes="stat-box"):
                yield Label("Consistency", classes="stat-label")
                yield Static("1 day streak", id="prog-streak", classes="stat-value")

            with Vertical(classes="stat-box"):
                yield Label("Total Mastery", classes="stat-label")
                yield Static("0 XP", id="prog-total-xp", classes="stat-value")

            with Vertical(classes="stat-box"):
                yield Label("Daily Target", classes="stat-label")
                yield Static("0 / 50 XP", id="prog-today-xp", classes="stat-value")

        with Container(classes="card"):
            yield Static("⚠️ Concepts Needing Reinforcement (Weak Areas)", classes="stat-label")
            yield DataTable(id="table-weaknesses", cursor_type="row")

        with Horizontal():
            yield Button("Back to Dashboard", variant="primary", id="btn-back", classes="-primary")

    async def on_mount(self) -> None:
        table = self.query_one("#table-weaknesses", DataTable)
        table.add_columns("#", "Concept / Topic", "Category", "Mistakes", "Accuracy", "Last Practiced")
        await self.load_data()

    async def load_data(self) -> None:
        client = self.app.client
        profile = await client.get_profile()

        self.query_one("#prog-streak", Static).update(f"🔥 {profile.get('streakDays', 1)} Days")
        self.query_one("#prog-total-xp", Static).update(f"✨ {profile.get('totalXp', 0)} XP")
        self.query_one("#prog-today-xp", Static).update(
            f"🎯 {profile.get('todayXp', 0)} / {profile.get('dailyGoalXp', 50)} XP"
        )

        weaknesses = await client.get_weaknesses()
        table = self.query_one("#table-weaknesses", DataTable)
        table.clear()

        if not weaknesses:
            table.add_row("-", "No weak areas detected! Great work.", "General", "0", "100%", "Today")
        else:
            for i, w in enumerate(weaknesses):
                table.add_row(
                    str(i + 1),
                    w.get("concept", "Grammar concept"),
                    w.get("topic", "Grammar"),
                    str(w.get("mistakeCount", 1)),
                    f"{w.get('accuracyRate', 50)}%",
                    str(w.get("lastPracticed", "Recently")),
                )

    def action_back_dashboard(self) -> None:
        self.app.switch_screen("dashboard")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.action_back_dashboard()

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Header, Label, ProgressBar, Static


class DashboardScreen(Screen):
    """Main Learn Dashboard showing user metrics and available quizzes."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("q", "start_quiz", "Start Quiz"),
        ("g", "open_generator", "Generate AI Quiz"),
        ("p", "open_progress", "Progress"),
        ("r", "open_references", "References (RAG)"),
        ("l", "logout", "Logout"),
    ]

    def __init__(self):
        super().__init__()
        self.quizzes: list[dict] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        # Top Stats Bar
        with Horizontal(classes="card", id="stats-bar"):
            with Vertical(classes="stat-box"):
                yield Label("User / Target", classes="stat-label")
                yield Static("Learner · Spanish A1", id="user-display", classes="stat-value")

            with Vertical(classes="stat-box"):
                yield Label("🔥 Streak", classes="stat-label")
                yield Static("1 day", id="streak-display", classes="stat-value")

            with Vertical(classes="stat-box"):
                yield Label("💖 Hearts", classes="stat-label")
                yield Static("5 / 5", id="hearts-display", classes="stat-value")

            with Vertical(classes="stat-box"):
                yield Label("✨ Total XP", classes="stat-label")
                yield Static("0 XP", id="xp-display", classes="stat-value")

            with Vertical(classes="stat-box"):
                yield Label("Daily Goal Progress", classes="stat-label")
                yield ProgressBar(total=50, id="daily-progress")

        # Action Toolbar
        with Horizontal(id="dashboard-toolbar"):
            yield Button("✨ Generate AI Quiz", id="btn-ai-gen", classes="-primary")
            yield Button("📊 Progress & Stats", id="btn-progress", classes="-ghost")
            yield Button("📚 Reference Library", id="btn-refs", classes="-ghost")
            yield Button("Start Selected Quiz", id="btn-start-quiz", classes="-success")
            yield Button("Logout", id="btn-logout", classes="-danger")

        # Quizzes Table
        with Container(classes="card"):
            yield Static("Available Lessons & Quizzes (Select row and press Enter or 'q' to start)", classes="stat-label")
            yield DataTable(id="quizzes-table", cursor_type="row")

    async def on_screen_resume(self) -> None:
        await self.load_data()

    async def on_mount(self) -> None:
        table = self.query_one("#quizzes-table", DataTable)
        table.add_columns("#", "Quiz Title", "Language", "Level", "Topic", "Questions")
        await self.load_data()

    async def load_data(self) -> None:
        client = self.app.client
        profile = await client.get_profile()

        # Update stats
        self.query_one("#user-display", Static).update(
            f"{profile.get('name', 'Learner')} · {profile.get('learningLanguage', 'Spanish')} {profile.get('currentLevel', 'A1')}"
        )
        self.query_one("#streak-display", Static).update(f"🔥 {profile.get('streakDays', 1)} days")
        self.query_one("#hearts-display", Static).update(
            f"💖 {profile.get('hearts', 5)} / {profile.get('maxHearts', 5)}"
        )
        self.query_one("#xp-display", Static).update(f"✨ {profile.get('totalXp', 0)} XP")

        prog = self.query_one("#daily-progress", ProgressBar)
        prog.update(total=profile.get("dailyGoalXp", 50), progress=profile.get("todayXp", 0))

        # Load quizzes
        self.quizzes = await client.list_quizzes()
        table = self.query_one("#quizzes-table", DataTable)
        table.clear()

        for idx, q in enumerate(self.quizzes):
            ex_count = q.get("exercise_count") or len(q.get("exercises", [])) or 4
            table.add_row(
                str(idx + 1),
                q.get("title", "Untitled Quiz"),
                q.get("language", "Spanish"),
                q.get("level", "A1"),
                q.get("topic", "General"),
                str(ex_count),
                key=str(q.get("id")),
            )

    def action_start_quiz(self) -> None:
        table = self.query_one("#quizzes-table", DataTable)
        if table.row_count == 0:
            self.app.notify("No quizzes available.", severity="warning")
            return

        cursor_row = table.cursor_row
        if 0 <= cursor_row < len(self.quizzes):
            selected_quiz = self.quizzes[cursor_row]
            quiz_id = str(selected_quiz["id"])
            self.app.start_quiz(quiz_id)

    def action_open_generator(self) -> None:
        self.app.switch_screen("generator")

    def action_open_progress(self) -> None:
        self.app.switch_screen("progress")

    def action_open_references(self) -> None:
        self.app.switch_screen("references")

    def action_logout(self) -> None:
        self.app.client.logout()
        self.app.switch_screen("auth")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        quiz_id = str(event.row_key.value)
        self.app.start_quiz(quiz_id)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-start-quiz":
            self.action_start_quiz()
        elif event.button.id == "btn-ai-gen":
            self.action_open_generator()
        elif event.button.id == "btn-progress":
            self.action_open_progress()
        elif event.button.id == "btn-refs":
            self.action_open_references()
        elif event.button.id == "btn-logout":
            self.action_logout()

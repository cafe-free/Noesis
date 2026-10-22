from typing import ClassVar

from textual.app import App
from textual.binding import Binding, BindingType
from textual.screen import Screen

from apps.tui.client import TUIClient
from apps.tui.screens.auth import AuthScreen
from apps.tui.screens.dashboard import DashboardScreen
from apps.tui.screens.generator import GeneratorScreen
from apps.tui.screens.progress import ProgressScreen
from apps.tui.screens.quiz import QuizScreen
from apps.tui.screens.references import ReferencesScreen
from apps.tui.styles import APP_CSS


class NoesisTUI(App):
    """
    Noesis Terminal User Interface (TUI).
    An adaptive, interactive language-learning experience in the terminal.
    """

    TITLE = "✨ Noesis"
    SUB_TITLE = "Adaptive Language Learning & RAG Knowledge Base"
    CSS = APP_CSS

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("ctrl+q", "quit", "Quit", show=True, priority=True),
        Binding("f1", "nav_dashboard", "Dashboard", show=True),
        Binding("f2", "nav_progress", "Progress", show=True),
        Binding("f3", "nav_references", "References", show=True),
        Binding("f4", "nav_generator", "AI Generator", show=True),
    ]

    SCREENS: ClassVar[dict[str, type[Screen]]] = {
        "auth": AuthScreen,
        "dashboard": DashboardScreen,
        "progress": ProgressScreen,
        "generator": GeneratorScreen,
        "references": ReferencesScreen,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = TUIClient()

    async def on_mount(self) -> None:
        if self.client.has_saved_session():
            try:
                profile = await self.client.get_profile()
                if profile:
                    self.push_screen("dashboard")
                    self.notify(
                        f"Logged in as {profile.get('name', 'Learner')} ({profile.get('email', '')})",
                        title="Session Restored",
                    )
                    return
            except Exception:
                pass

        # Start at auth screen
        self.push_screen("auth")

    def action_nav_dashboard(self) -> None:
        if self.client.current_user:
            self.switch_screen("dashboard")
        else:
            self.notify("Please sign in first.", severity="warning")

    def action_nav_progress(self) -> None:
        if self.client.current_user:
            self.switch_screen("progress")
        else:
            self.notify("Please sign in first.", severity="warning")

    def action_nav_references(self) -> None:
        if self.client.current_user:
            self.switch_screen("references")
        else:
            self.notify("Please sign in first.", severity="warning")

    def action_nav_generator(self) -> None:
        if self.client.current_user:
            self.switch_screen("generator")
        else:
            self.notify("Please sign in first.", severity="warning")

    def start_quiz(self, quiz_id: str) -> None:
        """Pushes an interactive quiz screen session."""
        self.push_screen(QuizScreen(quiz_id=quiz_id))


def run():
    """CLI launcher for Noesis TUI with subcommand routing."""
    import asyncio
    import sys
    from apps.tui.auth_cli import async_main

    # Handle auth CLI commands: `noesis-tui login ...`, `noesis-tui logout`, `noesis-tui status/whoami`
    if len(sys.argv) > 1 and sys.argv[1] in ("login", "auth", "logout", "status", "whoami"):
        cmd = sys.argv[1]
        remaining = sys.argv[2:]
        if cmd == "logout":
            remaining = ["--logout", *remaining]
        elif cmd in ("status", "whoami"):
            remaining = ["--status", *remaining]
        exit_code = asyncio.run(async_main(remaining))
        if exit_code != 0:
            sys.exit(exit_code)
        return

    # Handle flag `--demo` to authenticate before launching
    if "--demo" in sys.argv:
        client = TUIClient()
        asyncio.run(client.demo_login())
        sys.argv.remove("--demo")

    app = NoesisTUI()
    app.run()


if __name__ == "__main__":
    run()

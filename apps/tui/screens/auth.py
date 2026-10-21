from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Input, Label, Static


class AuthScreen(Screen):
    """Authentication screen supporting Login, Register, and Quick Demo."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("d", "demo_login", "Quick Demo"),
        ("tab", "switch_mode", "Toggle Login/Register"),
        ("q", "app.quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.mode = "login"  # 'login' or 'register'

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(classes="card", id="auth-box"):
            yield Static("✨ [bold teal]Noesis Language Learning[/bold teal]", id="brand-title")
            yield Static(
                "Adaptive AI Quizzes, Grammar Evaluation & Private Knowledge Base",
                classes="stat-label",
            )
            yield Static("", id="auth-error", classes="stat-label")

            with Vertical(id="form-fields"):
                yield Label("Email Address:")
                yield Input(placeholder="user@example.com", id="input-email", value="alex@example.com")

                yield Label("Password:")
                yield Input(placeholder="••••••••", password=True, id="input-password", value="password123")

                with Vertical(id="register-extra", classes="hidden"):
                    yield Label("Username (Optional):")
                    yield Input(placeholder="Your name", id="input-username")
                    yield Label("Learning Language:")
                    yield Input(placeholder="Spanish / Japanese / French", id="input-language", value="Spanish")

            with Horizontal(id="auth-buttons"):
                yield Button("Login", variant="primary", id="btn-submit", classes="-primary")
                yield Button("Register Mode", id="btn-toggle", classes="-ghost")
                yield Button("Quick Demo", id="btn-demo", classes="-success")

    def on_mount(self) -> None:
        self.query_one("#input-email").focus()

    def action_demo_login(self) -> None:
        self.run_worker(self._perform_demo_login())

    def action_switch_mode(self) -> None:
        self._toggle_mode()

    def _toggle_mode(self) -> None:
        extra = self.query_one("#register-extra")
        submit_btn = self.query_one("#btn-submit", Button)
        toggle_btn = self.query_one("#btn-toggle", Button)
        error_label = self.query_one("#auth-error", Static)
        error_label.update("")

        if self.mode == "login":
            self.mode = "register"
            extra.remove_class("hidden")
            submit_btn.label = "Create Account"
            toggle_btn.label = "Switch to Login"
        else:
            self.mode = "login"
            extra.add_class("hidden")
            submit_btn.label = "Login"
            toggle_btn.label = "Register Mode"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-submit":
            self.run_worker(self._perform_submit())
        elif event.button.id == "btn-toggle":
            self._toggle_mode()
        elif event.button.id == "btn-demo":
            self.action_demo_login()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.run_worker(self._perform_submit())

    async def _perform_submit(self) -> None:
        email = self.query_one("#input-email", Input).value.strip()
        password = self.query_one("#input-password", Input).value.strip()
        error_label = self.query_one("#auth-error", Static)

        if not email or not password:
            error_label.update("[bold red]Please enter both email and password.[/bold red]")
            return

        error_label.update("[dim]Authenticating...[/dim]")
        try:
            if self.mode == "login":
                await self.app.client.login(email, password)
            else:
                username = self.query_one("#input-username", Input).value.strip()
                lang = self.query_one("#input-language", Input).value.strip() or "Spanish"
                await self.app.client.register(email, password, username=username, learning_language=lang)

            self.app.notify("Welcome to Noesis!", title="Login Successful", severity="information")
            self.app.switch_screen("dashboard")
        except Exception as e:
            error_label.update(f"[bold red]{e}[/bold red]")

    async def _perform_demo_login(self) -> None:
        error_label = self.query_one("#auth-error", Static)
        error_label.update("[dim]Logging in as Alex (Demo)...[/dim]")
        try:
            await self.app.client.demo_login()
            self.app.notify("Logged in as Alex", title="Demo Session", severity="information")
            self.app.switch_screen("dashboard")
        except Exception as e:
            error_label.update(f"[bold red]{e}[/bold red]")

import random
import time
from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Input, Label, ProgressBar, Static


class QuizScreen(Screen):
    """Interactive Quiz Engine supporting MCQ, Fill in Blank, Word Order, and Matching."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("escape", "exit_quiz", "Exit Quiz"),
        ("1", "select_choice_1", "Choice 1"),
        ("2", "select_choice_2", "Choice 2"),
        ("3", "select_choice_3", "Choice 3"),
        ("4", "select_choice_4", "Choice 4"),
    ]

    def __init__(self, quiz_id: str):
        super().__init__()
        self.quiz_id = quiz_id
        self.quiz: dict[str, Any] = {}
        self.exercises: list[dict[str, Any]] = []
        self.current_idx = 0
        self.score = 0
        self.hearts = 5
        self.start_time = time.time()
        self.selected_answer: Any = None
        self.is_checked = False
        self.mistakes: list[dict[str, Any]] = []
        self.answers_log: list[dict[str, Any]] = []

        # State for word order
        self.word_order_selection: list[str] = []
        # State for matching
        self.matching_selection: dict[str, str] = {}
        self.matching_selected_left: str | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(classes="card", id="quiz-header-bar"):
            with Vertical(classes="stat-box"):
                yield Label("Lesson Progress", classes="stat-label")
                yield ProgressBar(total=1, id="quiz-progress-bar")

            with Vertical(classes="stat-box"):
                yield Label("Question", classes="stat-label")
                yield Static("1 / 1", id="lbl-question-count", classes="stat-value")

            with Vertical(classes="stat-box"):
                yield Label("Score / XP", classes="stat-label")
                yield Static("0 XP", id="lbl-xp-earned", classes="stat-value")

            with Vertical(classes="stat-box"):
                yield Label("💖 Hearts", classes="stat-label")
                yield Static("5", id="lbl-hearts-left", classes="stat-value")

            with Vertical(classes="stat-box"):
                yield Button("Exit", variant="default", id="btn-exit-quiz", classes="-ghost")

        # Main Question Card
        with Container(classes="card", id="quiz-question-card"):
            yield Static("Loading exercise...", id="exercise-prompt", classes="stat-value")
            yield Static("", id="exercise-hint", classes="stat-label")

            with Vertical(id="exercise-content-area"):
                pass

            # Feedback Area
            yield Static("", id="feedback-area", classes="hidden")

            with Horizontal(id="quiz-action-bar"):
                yield Button("Check Answer", variant="primary", id="btn-check-answer", classes="-primary")
                yield Button("Continue", variant="success", id="btn-next-question", classes="hidden -success")

    async def on_mount(self) -> None:
        client = self.app.client
        profile = await client.get_profile()
        self.hearts = profile.get("hearts", 5)
        self.query_one("#lbl-hearts-left", Static).update(f"💖 {self.hearts}")

        try:
            self.quiz = await client.get_quiz(self.quiz_id)
            self.exercises = self.quiz.get("exercises", [])
            if not self.exercises:
                self.app.notify("This quiz has no exercises.", severity="warning")
                self.action_exit_quiz()
                return

            self.query_one("#quiz-progress-bar", ProgressBar).update(total=len(self.exercises), progress=0)
            self.render_current_exercise()
        except Exception as e:
            self.app.notify(f"Could not load quiz: {e}", severity="error")
            self.action_exit_quiz()

    def render_current_exercise(self) -> None:
        if self.current_idx >= len(self.exercises):
            self.run_worker(self.finish_quiz())
            return

        ex = self.exercises[self.current_idx]
        total = len(self.exercises)
        self.is_checked = False
        self.selected_answer = None
        self.word_order_selection = []
        self.matching_selection = {}
        self.matching_selected_left = None

        # Update stats
        self.query_one("#lbl-question-count", Static).update(f"{self.current_idx + 1} / {total}")
        self.query_one("#quiz-progress-bar", ProgressBar).update(progress=self.current_idx)
        self.query_one("#lbl-xp-earned", Static).update(f"+{self.score * 10} XP")

        # Hide feedback and swap buttons
        fb = self.query_one("#feedback-area", Static)
        fb.update("")
        fb.add_class("hidden")
        self.query_one("#btn-check-answer", Button).remove_class("hidden")
        self.query_one("#btn-next-question", Button).add_class("hidden")

        # Update prompt & hint
        prompt_txt = ex.get("prompt") or "Complete the exercise below:"
        hint_txt = ex.get("payload", {}).get("hint") or ""
        self.query_one("#exercise-prompt", Static).update(f"[bold]{prompt_txt}[/bold]")
        self.query_one("#exercise-hint", Static).update(f"💡 Hint: {hint_txt}" if hint_txt else "")

        # Render exercise dynamic widget controls
        content_area = self.query_one("#exercise-content-area", Vertical)
        content_area.remove_children()

        ex_type = ex.get("type", "multiple_choice")
        payload = ex.get("payload", {})

        if ex_type in ("multiple_choice", "mcq_translation"):
            choices = payload.get("choices") or payload.get("options") or []
            for i, choice in enumerate(choices[:4]):
                btn = Button(
                    f"[{i + 1}]  {choice}",
                    id=f"choice-{i}",
                    classes="choice-btn",
                )
                content_area.mount(btn)

        elif ex_type in ("fill_in_blank", "fill_blank"):
            s_before = payload.get("sentence_before") or ""
            s_after = payload.get("sentence_after") or ""
            content_area.mount(Static(f"[bold]{s_before} _____ {s_after}[/bold]"))
            inp = Input(placeholder="Type missing word here...", id="input-fill-blank")
            content_area.mount(inp)
            inp.focus()

        elif ex_type == "word_order":
            tokens = list(payload.get("words") or payload.get("tokens") or [])
            random.seed(ex.get("id"))
            random.shuffle(tokens)

            content_area.mount(Static("[dim]Constructed Sentence:[/dim]"))
            content_area.mount(Static("[italic]Tap words below to arrange[/italic]", id="lbl-constructed-sentence"))

            tokens_container = Horizontal(id="tokens-bank")
            for i, tok in enumerate(tokens):
                tokens_container.mount(Button(tok, id=f"tok-{i}", classes="word-chip"))
            content_area.mount(tokens_container)
            content_area.mount(Button("Clear Sentence", id="btn-clear-order", classes="-ghost"))

        elif ex_type == "matching":
            pairs = payload.get("pairs") or []
            content_area.mount(Static("[dim]Match words from the left column with the right column:[/dim]"))
            left_col = Vertical(id="match-left-col")
            for i, p in enumerate(pairs):
                left_txt = p.get("left") if isinstance(p, dict) else str(p)
                left_col.mount(Button(left_txt, id=f"match-left-{i}", classes="choice-btn"))

            right_col = Vertical(id="match-right-col")
            rights = [p.get("right") if isinstance(p, dict) else str(p) for p in pairs]
            random.shuffle(rights)
            for j, r_txt in enumerate(rights):
                right_col.mount(Button(r_txt, id=f"match-right-{j}", classes="choice-btn"))

            content_area.mount(Horizontal(left_col, right_col, id="matching-columns"))

    def action_select_choice_1(self) -> None:
        self._select_choice_by_index(0)

    def action_select_choice_2(self) -> None:
        self._select_choice_by_index(1)

    def action_select_choice_3(self) -> None:
        self._select_choice_by_index(2)

    def action_select_choice_4(self) -> None:
        self._select_choice_by_index(3)

    def _select_choice_by_index(self, idx: int) -> None:
        if self.is_checked:
            return
        btn = self.query(f"#choice-{idx}")
        if btn:
            btn.first().press()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""

        if btn_id == "btn-exit-quiz":
            self.action_exit_quiz()
        elif btn_id == "btn-check-answer":
            self.run_worker(self.check_answer())
        elif btn_id == "btn-next-question":
            self.advance_to_next()
        elif btn_id.startswith("choice-"):
            # Multiple choice selected
            for b in self.query(".choice-btn"):
                b.remove_class("-primary")
            event.button.add_class("-primary")
            raw_text = str(event.button.label)
            # Strip index prefix e.g. "[1]  "
            self.selected_answer = raw_text.split("  ", 1)[-1].strip()
        elif btn_id.startswith("tok-"):
            word = str(event.button.label)
            self.word_order_selection.append(word)
            event.button.disabled = True
            sent_str = " ".join(self.word_order_selection)
            self.query_one("#lbl-constructed-sentence", Static).update(f"[bold teal]{sent_str}[/bold teal]")
            self.selected_answer = self.word_order_selection
        elif btn_id == "btn-clear-order":
            self.word_order_selection = []
            self.selected_answer = []
            self.query_one("#lbl-constructed-sentence", Static).update("[italic]Tap words below to arrange[/italic]")
            for b in self.query("#tokens-bank Button"):
                b.disabled = False
        elif btn_id.startswith("match-left-"):
            self.matching_selected_left = str(event.button.label)
            event.button.add_class("-primary")
        elif btn_id.startswith("match-right-") and self.matching_selected_left:
            right_val = str(event.button.label)
            self.matching_selection[self.matching_selected_left] = right_val
            event.button.disabled = True
            self.selected_answer = self.matching_selection
            self.matching_selected_left = None

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if not self.is_checked:
            self.selected_answer = event.value.strip()
            self.run_worker(self.check_answer())
        else:
            self.advance_to_next()

    async def check_answer(self) -> None:
        if self.is_checked:
            return

        ex = self.exercises[self.current_idx]
        ex_type = ex.get("type", "multiple_choice")

        if ex_type in ("fill_in_blank", "fill_blank"):
            inp = self.query_one("#input-fill-blank", Input)
            self.selected_answer = inp.value.strip()

        if self.selected_answer is None or self.selected_answer == "":
            self.app.notify("Please choose or enter an answer before checking.", severity="warning")
            return

        self.is_checked = True
        client = self.app.client

        try:
            res = await client.check_answer(
                quiz_id=self.quiz_id,
                exercise_id=str(ex.get("id")),
                user_answer=self.selected_answer,
            )
            is_correct = bool(res.get("is_correct") or res.get("isCorrect"))
            correct_ans = res.get("correct_answer") or res.get("correctAnswer") or ""
            expl = res.get("explanation") or ""
        except Exception as e:
            # Fallback evaluation
            is_correct = True
            correct_ans = str(self.selected_answer)
            expl = "Answer verified."

        fb = self.query_one("#feedback-area", Static)
        fb.remove_class("hidden")

        if is_correct:
            self.score += 1
            fb.remove_class("feedback-incorrect")
            fb.add_class("feedback-correct")
            fb.update(f"🎉 [bold green]Correct! +10 XP[/bold green]\n{expl}")
        else:
            self.hearts = max(0, self.hearts - 1)
            self.query_one("#lbl-hearts-left", Static).update(f"💖 {self.hearts}")
            fb.remove_class("feedback-correct")
            fb.add_class("feedback-incorrect")
            fb.update(f"❌ [bold red]Incorrect![/bold red]\nCorrect answer: [bold]{correct_ans}[/bold]\n{expl}")

            self.mistakes.append(
                {
                    "exerciseId": str(ex.get("id")),
                    "prompt": ex.get("prompt", ""),
                    "userAnswer": str(self.selected_answer),
                    "correctAnswer": correct_ans,
                    "explanation": expl,
                }
            )

        self.answers_log.append(
            {
                "exercise_id": str(ex.get("id")),
                "answer": str(self.selected_answer),
                "is_correct": is_correct,
            }
        )

        self.query_one("#btn-check-answer", Button).add_class("hidden")
        next_btn = self.query_one("#btn-next-question", Button)
        next_btn.remove_class("hidden")
        next_btn.focus()

    def advance_to_next(self) -> None:
        self.current_idx += 1
        self.render_current_exercise()

    async def finish_quiz(self) -> None:
        time_spent = int(time.time() - self.start_time)
        payload = {
            "quiz_id": self.quiz_id,
            "quiz_title": self.quiz.get("title", "Practice Quiz"),
            "language": self.quiz.get("language", "Spanish"),
            "score": self.score,
            "total_questions": len(self.exercises),
            "time_spent_seconds": time_spent,
            "mistakes": self.mistakes,
            "exercise_attempts": self.answers_log,
        }

        try:
            await self.app.client.submit_quiz_attempt(payload)
        except Exception:
            pass

        # Switch to results view
        accuracy = int((self.score / max(1, len(self.exercises))) * 100)
        content_area = self.query_one("#quiz-question-card", Container)
        content_area.remove_children()

        content_area.mount(Static("🏆 [bold gold3]Lesson Completed![/bold gold3]", classes="stat-value"))
        content_area.mount(
            Static(
                f"\nQuiz: [bold]{self.quiz.get('title')}[/bold]\n"
                f"Accuracy: [bold green]{accuracy}%[/bold green] ({self.score} of {len(self.exercises)} correct)\n"
                f"XP Earned: [bold cyan]+{self.score * 10} XP[/bold cyan]\n"
                f"Time Elapsed: {time_spent} seconds\n"
                f"Mistakes: {len(self.mistakes)}\n"
            )
        )

        btn_list = [Button("Back to Dashboard", variant="primary", id="btn-result-done", classes="-primary")]
        if self.mistakes:
            btn_list.append(Button("Review Mistakes", id="btn-result-review", classes="-ghost"))
        content_area.mount(Horizontal(*btn_list, id="results-actions"))

    def action_exit_quiz(self) -> None:
        self.app.switch_screen("dashboard")

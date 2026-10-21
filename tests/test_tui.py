import asyncio
from unittest.mock import AsyncMock, patch

from apps.tui.app import NoesisTUI
from apps.tui.screens.auth import AuthScreen
from apps.tui.screens.dashboard import DashboardScreen
from apps.tui.screens.generator import GeneratorScreen
from apps.tui.screens.progress import ProgressScreen
from apps.tui.screens.quiz import QuizScreen
from apps.tui.screens.references import ReferencesScreen


def test_tui_auth_screen_mount():
    async def _run():
        app = NoesisTUI()
        async with app.run_test():
            assert isinstance(app.screen, AuthScreen)
            # Toggle between login and register
            app.screen.action_switch_mode()
            assert app.screen.mode == "register"
            app.screen.action_switch_mode()
            assert app.screen.mode == "login"

    asyncio.run(_run())


def test_tui_demo_login_flow():
    async def _run():
        app = NoesisTUI()
        mock_user = {
            "id": "11111111-1111-1111-1111-111111111111",
            "name": "Alex",
            "email": "alex@example.com",
            "streakDays": 5,
            "totalXp": 250,
            "todayXp": 20,
            "dailyGoalXp": 50,
            "hearts": 5,
            "maxHearts": 5,
            "learningLanguage": "Spanish",
            "currentLevel": "A1",
        }

        with patch.object(app.client, "demo_login", new_callable=AsyncMock) as mock_demo, patch.object(
            app.client, "get_profile", new_callable=AsyncMock, return_value=mock_user
        ), patch.object(app.client, "list_quizzes", new_callable=AsyncMock, return_value=[]):
            mock_demo.return_value = {"token": "mock-token", "user": mock_user}

            async with app.run_test() as pilot:
                # Trigger quick demo
                await pilot.click("#btn-demo")
                await pilot.pause(0.2)

                assert isinstance(app.screen, DashboardScreen)
                user_label = app.screen.query_one("#user-display").content
                assert "Alex" in str(user_label)
                assert "Spanish" in str(user_label)

    asyncio.run(_run())


def test_tui_navigation_actions():
    async def _run():
        app = NoesisTUI()
        app.client.current_user = {
            "id": "user-123",
            "name": "Brian",
            "streakDays": 3,
            "totalXp": 120,
            "hearts": 5,
        }

        with patch.object(app.client, "get_profile", new_callable=AsyncMock, return_value=app.client.current_user), patch.object(
            app.client, "list_quizzes", new_callable=AsyncMock, return_value=[]
        ), patch.object(
            app.client, "get_weaknesses", new_callable=AsyncMock, return_value=[]
        ), patch.object(
            app.client, "list_references", new_callable=AsyncMock, return_value=[]
        ):
            async with app.run_test() as pilot:
                # Go to Dashboard
                app.action_nav_dashboard()
                await pilot.pause(0.1)
                assert isinstance(app.screen, DashboardScreen)

                # Navigate to Progress
                app.action_nav_progress()
                await pilot.pause(0.1)
                assert isinstance(app.screen, ProgressScreen)

                # Navigate to References
                app.action_nav_references()
                await pilot.pause(0.1)
                assert isinstance(app.screen, ReferencesScreen)

                # Navigate to Generator
                app.action_nav_generator()
                await pilot.pause(0.1)
                assert isinstance(app.screen, GeneratorScreen)

    asyncio.run(_run())


def test_tui_interactive_quiz_engine():
    async def _run():
        app = NoesisTUI()
        app.client.current_user = {"id": "user-1", "name": "Learner", "hearts": 5}

        mock_quiz_data = {
            "id": "quiz-test-1",
            "title": "Spanish Basics",
            "language": "Spanish",
            "level": "A1",
            "exercises": [
                {
                    "id": "ex-1",
                    "type": "multiple_choice",
                    "prompt": "How do you say Hello in Spanish?",
                    "payload": {
                        "options": ["Hola", "Adiós", "Gracias"],
                        "choices": ["Hola", "Adiós", "Gracias"],
                    },
                }
            ],
        }

        mock_check_response = {
            "is_correct": True,
            "correct_answer": "Hola",
            "explanation": "Hola means hello.",
            "xp_earned": 10,
        }

        with patch.object(app.client, "get_profile", new_callable=AsyncMock, return_value=app.client.current_user), patch.object(
            app.client, "get_quiz", new_callable=AsyncMock, return_value=mock_quiz_data
        ), patch.object(
            app.client, "check_answer", new_callable=AsyncMock, return_value=mock_check_response
        ), patch.object(
            app.client, "submit_quiz_attempt", new_callable=AsyncMock, return_value={"id": "att-1"}
        ):
            async with app.run_test() as pilot:
                app.start_quiz("quiz-test-1")
                await pilot.pause(0.2)
                assert isinstance(app.screen, QuizScreen)

                # Select choice 1
                app.screen.action_select_choice_1()
                await pilot.pause(0.2)
                assert app.screen.selected_answer == "Hola"

                # Check answer
                await app.screen.check_answer()
                await pilot.pause(0.2)
                assert app.screen.is_checked is True
                assert app.screen.score == 1

                # Continue to results
                app.screen.advance_to_next()
                await pilot.pause(0.2)
                assert app.screen.score == 1

    asyncio.run(_run())

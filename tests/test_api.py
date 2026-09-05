from uuid import uuid4
import pytest
from apps.api.schemas.quiz import QuizResponse
from apps.api.schemas.attempt import AnswerSubmissionResponse

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_generation_job(client, mock_db):
    mock_supabase, mock_redis = mock_db
    
    # Mock supabase insert
    mock_supabase.table().insert().execute.return_value = type('obj', (object,), {'data': [{'id': str(uuid4())}]})
    
    response = client.post("/generation/jobs", json={
        "language": "Spanish",
        "level": "A1",
        "topic": "Food",
        "count": 10
    })
    
    assert response.status_code == 200
    assert "job_id" in response.json()

def test_get_quiz_success(client, mock_db):
    mock_supabase, _ = mock_db
    quiz_id = str(uuid4())
    
    # Mock quiz data
    mock_supabase.table().select().eq().execute.return_value = type('obj', (object,), {
        'data': [{
            'id': quiz_id,
            'language': "Spanish",
            'level': "A1",
            'topic': "Food",
            'title': "Quiz on Food",
            'created_at': "2024-01-01T00:00:00Z"
        }]
    })
    
    # Needs side_effect to return exercises on second call
    def mock_select_execute():
        class MockEq:
            def eq(self, *args, **kwargs):
                class MockExecute:
                    def execute(self):
                        if args[0] == "id": # Quiz call
                            return type('obj', (object,), {
                                'data': [{
                                    'id': quiz_id,
                                    'language': "Spanish",
                                    'level': "A1",
                                    'topic': "Food",
                                    'title': "Quiz on Food",
                                    'created_at': "2024-01-01T00:00:00Z"
                                }]
                            })()
                        elif args[0] == "quiz_id": # Exercises call
                            class MockOrder:
                                def order(self, *oargs, **okwargs):
                                    class MockExecuteEx:
                                        def execute(self):
                                            return type('obj', (object,), {
                                                'data': [{
                                                    'id': str(uuid4()),
                                                    'quiz_id': quiz_id,
                                                    'type': "mcq_translation",
                                                    'position': 1,
                                                    'prompt': "I eat apples.",
                                                    'payload': {
                                                        'source_text': "I eat apples.",
                                                        'choices': ["A", "B", "C", "D"],
                                                        'correct_answer': "A"
                                                    },
                                                    'created_at': "2024-01-01T00:00:00Z"
                                                }]
                                            })()
                                    return MockExecuteEx()
                            return MockOrder()
                return MockExecute()
        return MockEq()

    mock_supabase.table().select = mock_select_execute

    response = client.get(f"/quizzes/{quiz_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == quiz_id
    assert len(data["exercises"]) == 1
    # Check that correct_answer is hidden
    assert "correct_answer" not in data["exercises"][0]["payload"]

def test_submit_attempt(client, mock_db):
    mock_supabase, _ = mock_db
    quiz_id = str(uuid4())
    user_id = str(uuid4())
    exercise_id = str(uuid4())
    attempt_id = str(uuid4())
    
    # Mocking for QuizService
    # 1. Select exercises
    # 2. Insert quiz attempt
    # 3. Insert exercise attempts
    # 4. Update quiz attempt
    
    def mock_table_actions(table_name):
        class MockTable:
            def select(self, *args, **kwargs):
                class MockEq:
                    def eq(self, *eargs, **ekwargs):
                        class MockExecute:
                            def execute(self):
                                return type('obj', (object,), {
                                    'data': [{
                                        'id': exercise_id,
                                        'quiz_id': quiz_id,
                                        'type': "mcq_translation",
                                        'position': 1,
                                        'prompt': "I eat apples.",
                                        'payload': {
                                            'correct_answer': "Yo como manzanas."
                                        }
                                    }]
                                })()
                        return MockExecute()
                return MockEq()
                
            def insert(self, data, **kwargs):
                class MockExecute:
                    def execute(self):
                        return type('obj', (object,), {'data': [{'id': attempt_id, 'started_at': '2024-01-01T00:00:00Z'}]})()
                return MockExecute()
                
            def update(self, data, **kwargs):
                class MockEq:
                    def eq(self, *eargs, **ekwargs):
                        class MockExecute:
                            def execute(self):
                                return type('obj', (object,), {'data': []})()
                        return MockExecute()
                return MockEq()
                
        return MockTable()
        
    mock_supabase.table = mock_table_actions
    
    response = client.post("/attempts", json={
        "user_id": user_id,
        "quiz_id": quiz_id,
        "answers": [
            {
                "exercise_id": exercise_id,
                "answer": "Yo como manzanas.",
                "response_time_ms": 2000
            }
        ]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 100.0
    assert data["correct_answers"] == 1
    assert data["results"][0]["is_correct"] is True


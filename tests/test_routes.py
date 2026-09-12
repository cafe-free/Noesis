import uuid


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from Noesis!"}


def test_users_endpoints(client):
    # 1. Create user
    user_payload = {"email": "user@example.com", "username": "testuser"}
    create_res = client.post("/users", json=user_payload)
    assert create_res.status_code == 201
    created_user = create_res.json()
    assert created_user["email"] == "user@example.com"
    assert created_user["username"] == "testuser"
    assert "id" in created_user
    user_id = created_user["id"]

    # 2. Get user by ID
    get_res = client.get(f"/users/{user_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == user_id

    # 3. List users
    list_res = client.get("/users")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 4. Update user
    update_res = client.put(f"/users/{user_id}", json={"username": "updateduser"})
    assert update_res.status_code == 200
    assert update_res.json()["username"] == "updateduser"

    # 5. Validation failure: Invalid email
    invalid_email_res = client.post("/users", json={"email": "notanemail"})
    assert invalid_email_res.status_code == 422

    # 6. Delete user
    del_res = client.delete(f"/users/{user_id}")
    assert del_res.status_code == 200

    # 7. Get deleted user -> 404
    not_found_res = client.get(f"/users/{user_id}")
    assert not_found_res.status_code == 404


def test_lessons_endpoints(client):
    # 1. Create lesson
    lesson_payload = {
        "language": "French",
        "level": "A1",
        "topic": "Greetings",
        "title": "Basic French Greetings",
        "description": "Learn to say Bonjour",
    }
    create_res = client.post("/lessons", json=lesson_payload)
    assert create_res.status_code == 201
    lesson = create_res.json()
    lesson_id = lesson["id"]
    assert lesson["title"] == "Basic French Greetings"

    # 2. Get lesson by ID
    get_res = client.get(f"/lessons/{lesson_id}")
    assert get_res.status_code == 200
    assert get_res.json()["language"] == "French"

    # 3. Filter lessons
    filter_res = client.get("/lessons?language=French&level=A1")
    assert filter_res.status_code == 200
    assert len(filter_res.json()) == 1

    # 4. Update lesson
    update_res = client.put(f"/lessons/{lesson_id}", json={"title": "Advanced French Greetings"})
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Advanced French Greetings"

    # 5. Delete lesson
    del_res = client.delete(f"/lessons/{lesson_id}")
    assert del_res.status_code == 200

    # 6. 404 on deleted
    assert client.get(f"/lessons/{lesson_id}").status_code == 404


def test_quizzes_and_exercises_endpoints(client):
    # 1. Create quiz
    quiz_payload = {
        "language": "Japanese",
        "level": "N5",
        "topic": "Hiragana",
        "title": "Hiragana Basics",
    }
    create_quiz_res = client.post("/quizzes", json=quiz_payload)
    assert create_quiz_res.status_code == 201
    quiz = create_quiz_res.json()
    quiz_id = quiz["id"]

    # 2. Add multiple choice exercise
    mc_payload = {
        "quiz_id": quiz_id,
        "type": "multiple_choice",
        "position": 1,
        "prompt": "What is 'あ'?",
        "payload": {
            "options": ["a", "i", "u", "e"],
            "correct_answer": "a",
        },
    }
    ex1_res = client.post("/exercises", json=mc_payload)
    assert ex1_res.status_code == 201
    ex1 = ex1_res.json()
    assert "correct_answer" not in ex1["payload"]

    # 3. Add fill in blank exercise
    fib_payload = {
        "quiz_id": quiz_id,
        "type": "fill_in_blank",
        "position": 2,
        "prompt": "Complete: Kon___wa",
        "payload": {
            "correct_answer": "nichi",
            "hint": "afternoon greeting",
        },
    }
    ex2_res = client.post("/exercises", json=fib_payload)
    assert ex2_res.status_code == 201

    # 4. Add word order exercise
    wo_payload = {
        "quiz_id": quiz_id,
        "type": "word_order",
        "position": 3,
        "prompt": "Arrange: Good morning",
        "payload": {
            "tokens": ["gozaimasu", "Ohayou"],
            "correct_order": ["Ohayou", "gozaimasu"],
        },
    }
    ex3_res = client.post("/exercises", json=wo_payload)
    assert ex3_res.status_code == 201

    # 5. Add matching exercise
    match_payload = {
        "quiz_id": quiz_id,
        "type": "matching",
        "position": 4,
        "prompt": "Match the pairs",
        "payload": {
            "pairs": [
                {"left": "Neko", "right": "Cat"},
                {"left": "Inu", "right": "Dog"},
            ]
        },
    }
    ex4_res = client.post("/exercises", json=match_payload)
    assert ex4_res.status_code == 201

    # 6. Fetch quiz by ID and verify sanitized exercises are returned inside quiz
    quiz_detail_res = client.get(f"/quizzes/{quiz_id}")
    assert quiz_detail_res.status_code == 200
    quiz_detail = quiz_detail_res.json()
    assert len(quiz_detail["exercises"]) == 4
    # Check that matching exercise payload in quiz detail has left_items and right_items
    matching_ex = next(e for e in quiz_detail["exercises"] if e["type"] == "matching")
    assert "left_items" in matching_ex["payload"]
    assert "right_items" in matching_ex["payload"]

    # 7. List exercises filtered by quiz_id
    ex_list_res = client.get(f"/exercises?quiz_id={quiz_id}")
    assert ex_list_res.status_code == 200
    assert len(ex_list_res.json()) == 4

    # 8. Update exercise
    update_ex_res = client.put(
        f"/exercises/{ex1['id']}",
        json={"prompt": "Select pronunciation for 'あ'"},
    )
    assert update_ex_res.status_code == 200
    assert update_ex_res.json()["prompt"] == "Select pronunciation for 'あ'"

    # 9. Exercise payload validation failure (invalid type payload)
    bad_ex_payload = {
        "quiz_id": quiz_id,
        "type": "multiple_choice",
        "position": 5,
        "prompt": "Invalid exercise",
        "payload": {"invalid_key": 123},
    }
    bad_res = client.post("/exercises", json=bad_ex_payload)
    assert bad_res.status_code == 422


def test_quiz_attempts_and_exercise_attempts_endpoints(client):
    # Create user and quiz
    user_res = client.post("/users", json={"email": "student@example.com", "username": "student"})
    user_id = user_res.json()["id"]

    quiz_res = client.post(
        "/quizzes",
        json={"language": "German", "level": "A1", "topic": "Numbers", "title": "German Numbers"},
    )
    quiz_id = quiz_res.json()["id"]

    ex_res = client.post(
        "/exercises",
        json={
            "quiz_id": quiz_id,
            "type": "multiple_choice",
            "position": 1,
            "prompt": "What is 'eins'?",
            "payload": {"options": ["1", "2", "3"], "correct_answer": "1"},
        },
    )
    ex_id = ex_res.json()["id"]

    # 1. Start quiz attempt
    attempt_res = client.post(
        "/quiz-attempts",
        json={"user_id": user_id, "quiz_id": quiz_id, "total_questions": 1},
    )
    assert attempt_res.status_code == 201
    attempt = attempt_res.json()
    attempt_id = attempt["id"]

    # 2. Record exercise attempt
    ea_res = client.post(
        "/exercise-attempts",
        json={
            "quiz_attempt_id": attempt_id,
            "exercise_id": ex_id,
            "answer": "1",
            "is_correct": True,
            "response_time_ms": 1500,
        },
    )
    assert ea_res.status_code == 201
    ea_id = ea_res.json()["id"]

    # 3. Get quiz attempt by ID - should include exercise attempts
    get_attempt_res = client.get(f"/quiz-attempts/{attempt_id}")
    assert get_attempt_res.status_code == 200
    attempt_data = get_attempt_res.json()
    assert len(attempt_data["exercise_attempts"]) == 1

    # 4. Update quiz attempt with score
    update_att_res = client.put(
        f"/quiz-attempts/{attempt_id}",
        json={"score": 100.0, "correct_answers": 1},
    )
    assert update_att_res.status_code == 200
    assert update_att_res.json()["score"] == 100.0

    # 5. List exercise attempts
    ea_list_res = client.get(f"/exercise-attempts?quiz_attempt_id={attempt_id}")
    assert ea_list_res.status_code == 200
    assert len(ea_list_res.json()) == 1


def test_generation_jobs_endpoints(client):
    # 1. Create generation job
    job_payload = {
        "language": "Italian",
        "level": "B1",
        "topic": "Past Tense",
        "count": 5,
    }
    create_res = client.post("/generation-jobs", json=job_payload)
    assert create_res.status_code == 201
    job = create_res.json()
    job_id = job["id"]
    assert job["status"] == "pending"
    assert job["count"] == 5

    # 2. Get generation job by ID
    get_res = client.get(f"/generation-jobs/{job_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == job_id

    # 3. Filter generation jobs
    list_res = client.get("/generation-jobs?status_filter=pending")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # 4. Update generation job
    update_res = client.put(f"/generation-jobs/{job_id}", json={"status": "completed"})
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "completed"

    # 5. Delete generation job
    del_res = client.delete(f"/generation-jobs/{job_id}")
    assert del_res.status_code == 200

    # 6. Check 404 after deletion
    assert client.get(f"/generation-jobs/{job_id}").status_code == 404

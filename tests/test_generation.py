from apps.api.schemas.generation import (
    GeneratedFillInBlank,
    GeneratedMatching,
    GeneratedMatchingPair,
    GeneratedMultipleChoice,
    GeneratedQuizContent,
    GeneratedWordOrder,
)
from apps.api.services.generation import QuizGenerationService


def test_generation_schemas():
    mcq = GeneratedMultipleChoice(
        prompt="How do you say 'Hello'?",
        options=["Hola", "Adiós", "Gracias"],
        correct_answer="Hola",
    )
    assert mcq.correct_answer in mcq.options

    fib = GeneratedFillInBlank(
        prompt="Complete: 'Buenos _____' (morning)",
        correct_answer="días",
        hint="Spanish word for days",
    )
    assert "_____" in fib.prompt

    wo = GeneratedWordOrder(
        prompt="Arrange the sentence:",
        correct_order=["Yo", "como", "manzanas"],
        distractors=["tú"],
    )
    assert len(wo.correct_order) == 3

    pair = GeneratedMatchingPair(left="Apple", right="La manzana")
    matching = GeneratedMatching(
        prompt="Match terms:",
        pairs=[pair],
    )
    assert len(matching.pairs) == 1

    quiz = GeneratedQuizContent(
        title="Test Spanish Quiz",
        description="A great test quiz",
        multiple_choice_exercises=[mcq],
        fill_in_blank_exercises=[fib],
        word_order_exercises=[wo],
        matching_exercises=[matching],
    )
    assert quiz.title == "Test Spanish Quiz"


def test_fallback_generation_service():
    service = QuizGenerationService()
    content = service.generate_fallback_content("Spanish", "A1", "Food & Dining", 4)
    assert "Spanish" in content.title or "Food & Dining" in content.title
    assert len(content.multiple_choice_exercises) >= 1
    assert len(content.fill_in_blank_exercises) >= 1
    assert len(content.word_order_exercises) >= 1
    assert len(content.matching_exercises) >= 1


def test_japanese_generation_service():
    service = QuizGenerationService()
    content = service.generate_fallback_content(
        "Japanese", "A1", "At the Coffee Shop", 4
    )
    assert "Japanese" in content.title
    mcq = content.multiple_choice_exercises[0]
    assert any("コーヒー" in opt for opt in mcq.options)
    assert not any("s'il vous plaît" in opt for opt in mcq.options)
    matching = content.matching_exercises[0]
    assert any("コーヒー" in p.right for p in matching.pairs)


def test_convert_to_exercise_records():
    service = QuizGenerationService()
    content = service.generate_fallback_content("Spanish", "A1", "Coffee Shop", 4)
    records = service._convert_to_exercise_records(content, "mock-quiz-uuid", count=4)
    assert len(records) == 4
    types = [r["type"] for r in records]
    assert "multiple_choice" in types
    assert "fill_in_blank" in types
    assert "word_order" in types
    assert "matching" in types

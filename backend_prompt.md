# Coding Agent Prompt — FastAPI AI Language Learning Backend

You are a senior Python backend engineer and AI application architect.

Build the backend for an **AI-powered language-learning platform: Noesis**.

The current goal is **not** to build the entire language-learning platform. Implement a clean, production-oriented MVP focused on:

1. Quiz generation
2. AI-generated exercises
3. Exercise validation
4. Quiz retrieval
5. User quiz attempts
6. Basic learning progress tracking

The backend must be implemented using **FastAPI + Supabase**.

Use an architecture that can later support adaptive learning, spaced repetition, speech recognition, and additional AI agents without requiring a major rewrite.

---

# 1. Technology Requirements

Use:

* Python 3.12+
* FastAPI
* Pydantic v2
* Supabase
* Redis
* pytest
* httpx
* Docker / Docker Compose

For the AI layer:

* Gemini API as the initial provider
* Design an LLM provider abstraction so additional providers such as Mistral can be added later

Use async APIs and async database access where appropriate.

Do not use an unnecessary framework such as LangChain for the initial implementation. Keep the agent architecture lightweight and explicit.

---

# 2. Project Structure

Keep business logic out of API route handlers.

Routes should call services.

Services should coordinate database operations and agents.

Agents should contain AI-specific logic.

---

# 3. Configuration

Implement configuration using Pydantic Settings.

Create:

```python
class Settings(BaseSettings):
    ...
```

Do not hardcode secrets.

Add `.env.example`.

---

# 4. Database

Use Supabase.

Create schemas for:

## User

```text
id
email
username
created_at
updated_at
```

## Lesson

```text
id
language
level
topic
title
description
created_at
updated_at
```

`level` should support CEFR levels:

```text
A1
A2
B1
B2
C1
C2
```

## Quiz

```text
id
lesson_id
language
level
topic
title
created_at
```

## Exercise

```text
id
quiz_id
type
position
prompt
payload
created_at
```

`payload` should use Supabase JSONB.

Do not create separate database tables for every exercise type.

The exercise type should determine the payload schema.

## QuizAttempt

```text
id
user_id
quiz_id
score
total_questions
correct_answers
started_at
completed_at
```

## ExerciseAttempt

```text
id
quiz_attempt_id
exercise_id
answer
is_correct
response_time_ms
created_at
```

## GenerationJob

```text
id
status
language
level
topic
count
quiz_id
error
created_at
started_at
completed_at
```

Statuses:

```text
pending
running
completed
failed
```

Add appropriate indexes and foreign keys.

Use UUIDs where appropriate if they make the API safer for public identifiers.

---

# 5. Exercise Types

Initially support:

### Multiple Choice Translation

```json
{
  "type": "mcq_translation",
  "prompt": "I eat apples.",
  "payload": {
    "source_text": "I eat apples.",
    "choices": [
      "Yo como manzanas.",
      "Yo come manzanas.",
      "Yo comen manzanas."
    ],
    "correct_answer": "Yo como manzanas."
  }
}
```

### Fill in the Blank

```json
{
  "type": "fill_blank",
  "prompt": "Yo ____ manzanas.",
  "payload": {
    "sentence": "Yo ____ manzanas.",
    "correct_answer": "como",
    "acceptable_answers": [
      "como"
    ]
  }
}
```

### Word Ordering

```json
{
  "type": "word_order",
  "prompt": "Put the words in the correct order.",
  "payload": {
    "tokens": [
      "manzanas",
      "como",
      "Yo"
    ],
    "correct_order": [
      "Yo",
      "como",
      "manzanas"
    ]
  }
}
```

### Matching

```json
{
  "type": "matching",
  "prompt": "Match the words.",
  "payload": {
    "pairs": [
      {
        "left": "apple",
        "right": "manzana"
      },
      {
        "left": "dog",
        "right": "perro"
      }
    ]
  }
}
```

Design the Pydantic schemas so that each exercise type has its own strongly typed payload schema.

---

# 6. AI Architecture

Implement four agents.

```text
CurriculumAgent
       ↓
ExerciseAgent
       ↓
DistractorAgent
       ↓
QAAgent
```

For the MVP, these can execute sequentially inside the generation service.

Do not over-engineer them into independent microservices.

---

# 7. Curriculum Agent

Create:

```python
class CurriculumAgent:
    async def generate_curriculum(...):
        ...
```

Input:

```text
language
level
topic
```

Output:

```json
{
  "language": "Spanish",
  "level": "A1",
  "topic": "Food",
  "learning_objectives": [
    "Learn basic food vocabulary",
    "Practice first-person present tense"
  ],
  "vocabulary": [
    "apple",
    "banana",
    "eat",
    "drink"
  ],
  "grammar": [
    "Present tense"
  ]
}
```

The output must be validated with Pydantic.

---

# 8. Exercise Agent

Create:

```python
class ExerciseAgent:
    async def generate_exercises(...):
        ...
```

Input:

```text
language
level
topic
curriculum
count
```

The agent should generate a mixture of exercise types.

For example:

```text
40% mcq_translation
30% fill_blank
20% word_order
10% matching
```

The exact distribution can be configurable.

---

# 9. Distractor Agent

For multiple-choice exercises, generate plausible incorrect answers.

Bad:

```text
apple
computer
mountain
```

Good:

```text
Yo como manzanas.
Yo come manzanas.
Yo comen manzanas.
Yo comí manzanas.
```

Distractors should reflect realistic learner mistakes.

The agent must not accidentally generate another valid answer.

---

# 10. QA Agent

Create:

```python
class QAAgent:
    async def validate_exercise(...):
        ...
```

Validate:

* Grammar
* Correct answer
* Difficulty
* Exercise structure
* Duplicate options
* Distractor quality
* Translation correctness
* CEFR appropriateness

Return:

```json
{
  "valid": true,
  "issues": []
}
```

or:

```json
{
  "valid": false,
  "issues": [
    "Distractor 2 is also grammatically valid."
  ]
}
```

Use deterministic validation wherever possible before calling the LLM.

For example:

```text
schema validation
duplicate detection
missing answer detection
```

Then use the LLM for linguistic validation.

---

# 11. LLM Provider Abstraction

Create:

```python
class LLMProvider(ABC):

    async def generate_structured(
        self,
        prompt: str,
        response_model: type[BaseModel]
    ) -> BaseModel:
        ...
```

The rest of the application must not directly depend on the Gemini SDK.

Use:

```text
agents → LLMProvider → Gemini
```

rather than:

```text
agents → Gemini SDK
```

This should allow a future implementation:

```text
GeminiProvider
MistralProvider
AnthropicProvider
LocalProvider
```

---

# 12. Structured AI Output

Do not rely on:

```python
json.loads(llm_response)
```

where possible.

Use structured output / Pydantic validation.

If the LLM returns invalid structured data:

1. Attempt validation
2. Retry generation
3. Return a meaningful error if retries fail

Implement a small retry mechanism.

Example:

```python
MAX_LLM_RETRIES = 2
```

---

# 13. Quiz Generation API

Implement:

```http
POST /generation/jobs
```

Request:

```json
{
  "language": "Spanish",
  "level": "A1",
  "topic": "Food",
  "count": 10
}
```

Response:

```json
{
  "job_id": "..."
}
```

Do not make the HTTP request wait for expensive AI generation.

---

# 14. Generation Job

Implement background processing.

For MVP, use Redis + a lightweight worker mechanism.

The API should:

1. Create GenerationJob
2. Set status to `pending`
3. Enqueue the job
4. Immediately return the job ID

Worker:

```text
pending
   ↓
running
   ↓
Curriculum Agent
   ↓
Exercise Agent
   ↓
Distractor Agent
   ↓
QA Agent
   ↓
save Quiz
   ↓
completed
```

If generation fails:

```text
running → failed
```

Store the error message.

Make the generation process idempotent where practical.

---

# 15. Generation Status API

Implement:

```http
GET /generation/jobs/{job_id}
```

Response:

```json
{
  "id": "...",
  "status": "completed",
  "quiz_id": "..."
}
```

For failed jobs:

```json
{
  "id": "...",
  "status": "failed",
  "error": "Quiz generation failed."
}
```

---

# 16. Quiz API

Implement:

```http
GET /quizzes/{quiz_id}
```

Return:

```json
{
  "id": "...",
  "language": "Spanish",
  "level": "A1",
  "topic": "Food",
  "title": "Spanish Food Basics",
  "exercises": [
    {
      "id": "...",
      "type": "mcq_translation",
      "position": 1,
      "prompt": "I eat apples.",
      "payload": {
        "source_text": "I eat apples.",
        "choices": [
          "Yo como manzanas.",
          "Yo come manzanas.",
          "Yo comen manzanas."
        ]
      }
    }
  ]
}
```

IMPORTANT:

Do not expose the correct answer in the normal quiz endpoint.

The frontend should receive enough information to display the exercise, but not the answer.

---

# 17. Answer Submission

Implement:

```http
POST /attempts
```

Request:

```json
{
  "user_id": "...",
  "quiz_id": "...",
  "answers": [
    {
      "exercise_id": "...",
      "answer": "Yo como manzanas.",
      "response_time_ms": 3200
    }
  ]
}
```

Response:

```json
{
  "attempt_id": "...",
  "score": 90,
  "correct_answers": 9,
  "total_questions": 10,
  "results": [
    {
      "exercise_id": "...",
      "is_correct": true
    }
  ]
}
```

Correct answers must be evaluated server-side.

Never trust the frontend's `is_correct` value.

---

# 18. Progress API

Implement:

```http
GET /progress/{user_id}
```

Return basic statistics:

```json
{
  "total_quizzes": 12,
  "completed_quizzes": 10,
  "total_exercises": 120,
  "correct_answers": 98,
  "accuracy": 0.8167
}
```

Also expose:

```http
GET /progress/{user_id}/weaknesses
```

Example:

```json
{
  "weaknesses": [
    {
      "topic": "present tense",
      "accuracy": 0.54
    },
    {
      "topic": "food vocabulary",
      "accuracy": 0.62
    }
  ]
}
```

Keep the weakness implementation simple for now.

Design it so it can later become an adaptive-learning system.

---

# 19. Authentication

For the initial MVP, do not spend excessive effort on authentication.

Create a basic `User` model and allow a development user ID to be supplied.

However, structure the API so authentication can later be added using:

```text
JWT
OAuth
```

Do not tightly couple business logic to authentication implementation.

---

# 20. Error Handling

Create consistent API errors.

Example:

```json
{
  "error": {
    "code": "QUIZ_NOT_FOUND",
    "message": "Quiz not found."
  }
}
```

Handle:

* Validation errors
* Database errors
* LLM errors
* Generation errors
* Missing resources
* Invalid exercise types

Do not expose API keys or internal stack traces.

---

# 21. Logging

Use Python logging.

Include useful context:

```text
generation_job_id
quiz_id
user_id
LLM provider
exercise count
generation duration
```

Do not log:

* API keys
* sensitive user data
* full prompts unnecessarily
* full model responses in production

---

# 22. Testing

Write tests for:

### Health

```http
GET /health
```

### Quiz retrieval

Test:

* Existing quiz
* Missing quiz
* Correct answer is NOT exposed

### Answer submission

Test:

* Correct answer
* Incorrect answer
* Multiple exercises
* Invalid exercise ID

### Generation

Mock the LLM provider.

Do NOT make real LLM API calls during tests.

Test:

```text
CurriculumAgent
ExerciseAgent
DistractorAgent
QAAgent
GenerationService
```

Use dependency injection so the LLM can easily be mocked.

---

# 23. Docker Compose

Use environment variables.

Add health checks where practical.

---

# 24. Database Migrations

support Supabase CLI

---

# 25. API Documentation

FastAPI's automatic Swagger documentation should work:

```text
/docs
```

Add useful summaries and descriptions to endpoints.

Use Pydantic examples where helpful.

---

# 26. README

Create a complete README containing:

* Project description
* Architecture
* Tech stack
* Project structure
* Installation
* Environment variables
* Docker instructions
* Database migration instructions
* Running API
* Running workers
* API examples
* Testing
* AI agent architecture
* Future roadmap

Include example curl commands.

---

# 27. Code Quality

Follow these principles:

* Type hints everywhere
* Small functions
* Dependency injection
* No business logic in route handlers
* No global database sessions
* No hardcoded secrets
* No unnecessary abstractions
* Clear naming
* Async I/O
* Pydantic validation
* Proper exception handling

Prefer straightforward code over excessive design patterns.

---

# 28. Important AI Design Principle

Do NOT make the AI responsible for everything.

Use deterministic code for:

```text
database operations
schema validation
duplicate detection
answer evaluation
score calculation
progress calculation
```

Use the LLM for:

```text
curriculum generation
exercise generation
natural-language reasoning
distractor generation
linguistic QA
```

The architecture should therefore look like:

```text
                    ┌──────────────────┐
                    │   FastAPI API    │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │    Services      │
                    └────────┬─────────┘
                             │
                ┌────────────▼────────────┐
                │    AI Generation        │
                │                          │
                │ Curriculum Agent         │
                │ Exercise Agent           │
                │ Distractor Agent         │
                │ QA Agent                 │
                └────────────┬────────────┘
                             │
                       LLM Provider
                             │
                    ┌────────▼────────┐
                    │     Gemini      │
                    └─────────────────┘

FastAPI ──────────────── Supabase
   │
   └──────────────────── Redis
                              │
                              ▼
                           Worker
```

---

# 29. Definition of Done

The implementation is complete when:

```text
✓ FastAPI starts successfully
✓ Supabase starts successfully
✓ Redis starts successfully
✓ /health works
✓ Quiz generation endpoint works
✓ Generation runs asynchronously
✓ AI provider is abstracted
✓ Generated exercises are Pydantic validated
✓ QA validation works
✓ Generated quiz is stored in Supabase
✓ Quiz endpoint returns exercises
✓ Correct answers are hidden from quiz retrieval
✓ Answer submission works
✓ Scores are calculated server-side
✓ Progress endpoint works
✓ Tests pass without requiring an actual LLM API call
✓ Docker Compose starts the complete system
✓ README explains how to run everything
```

---

# 30. Implementation Strategy

Implement incrementally.

### Step 1

Set up:

```text
FastAPI
Supabase
Docker
```

### Step 2

Implement:

```text
User
Lesson
Quiz
Exercise
```

### Step 3

Implement:

```text
LLMProvider
GeminiProvider
```

Use a mock provider for tests.

### Step 4

Implement:

```text
CurriculumAgent
ExerciseAgent
DistractorAgent
QAAgent
```

### Step 5

Implement:

```text
GenerationService
GenerationJob
Redis worker
```

### Step 6

Implement:

```text
GET /quizzes/{id}
POST /attempts
GET /progress/{user_id}
```

### Step 7

Write comprehensive tests.

### Step 8

Run:

```bash
pytest
```

Then:

```bash
docker compose up --build
```

Verify the complete generation flow manually.

---

# Final Requirement

Do not merely generate placeholder files.

Implement a **working MVP** with real FastAPI routes, Redis background processing, Pydantic schemas, mocked LLM tests, and an actual Gemini provider implementation.

If a design decision is ambiguous, choose the simplest implementation that preserves future extensibility for:

* adaptive learning
* spaced repetition
* personalized quizzes
* speech recognition
* pronunciation assessment
* additional LLM providers
* mobile clients
* large-scale quiz generation

After implementation, provide a concise summary of:

1. Files created
2. Architecture
3. API endpoints
4. Database schema
5. How to run locally
6. How to run tests
7. Any assumptions or TODOs

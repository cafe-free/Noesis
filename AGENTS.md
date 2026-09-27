# AGENTS.md — Agent & Developer Guidelines for Noesis

Welcome to the **Noesis** repository. This document serves as the canonical orientation, architecture guide, and operational instructions for AI coding agents and human contributors working on this codebase.

---

## 1. Project Overview & Philosophy

**Noesis** is an AI-powered, adaptive language-learning application featuring playful, bite-sized quizzes, instant grammatical correction, weak-spot tracking, and dynamic quiz generation.

### Core Tech Stack

| Domain | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS v4, Lucide React, Motion | Single-page client web app |
| **Frontend Tooling** | **pnpm** (strict requirement) | Package and build management |
| **Backend** | FastAPI, Python 3.11+, Pydantic v2, Python-Jose | RESTful API server & evaluation engine |
| **Backend Tooling**| **uv** | Python environment and dependency management |
| **Database** | Supabase (PostgreSQL) | Persistence layer for users, quizzes, and attempts |

---

## 2. Repository Layout

```text
Noesis/
├── apps/
│   ├── frontend/                 # React SPA
│   │   ├── src/
│   │   │   ├── components/       # Decomposed, modular React components
│   │   │   │   ├── auth/         # LoginForm, RegisterForm
│   │   │   │   ├── landing/      # HeroSection, InteractiveCard, HowItWorksSection, etc.
│   │   │   │   ├── layout/       # Navbar, MobileNav
│   │   │   │   ├── learning/     # LearnHeader, LessonGrid, FeaturedLessonBanner, DailyGoal
│   │   │   │   ├── progress/     # ProgressStatsGrid, WeakAreasBreakdown
│   │   │   │   ├── quiz/         # QuizEngine, ExerciseRenderer, QuizResult, exercises/
│   │   │   │   ├── review/       # MistakeCard, MistakeEmptyState, ReviewHeader
│   │   │   │   └── ui/           # Button, Card, ProgressBar
│   │   │   ├── context/          # AuthContext, ThemeContext
│   │   │   ├── lib/
│   │   │   │   ├── api/          # apiClient, auth, quizzes, attempts, progress
│   │   │   │   ├── mock/         # Fallback mock data fixtures
│   │   │   │   └── sound.ts      # Sound effect player (correct, incorrect, victory, tap)
│   │   │   ├── pages/            # Page-level view wrappers
│   │   │   └── types/            # Canonical TypeScript schemas and types
│   │   ├── index.html            # Vite entry HTML
│   │   ├── package.json          # Frontend dependencies & npm scripts
│   │   ├── tsconfig.json         # Strict TypeScript configuration
│   │   └── vite.config.ts        # Vite configuration
│   └── api/                      # FastAPI Python Backend
│       ├── core/                 # Config (Pydantic settings), auth (JWT), db (Supabase)
│       ├── routes/               # API route modules (auth, quizzes, progress, etc.)
│       ├── schemas/              # Pydantic request/response schemas
│       ├── static/               # Static web assets
│       └── main.py               # FastAPI entrypoint & router mounts
├── migrations/
│   └── init.sql                  # PostgreSQL schema definitions
├── tests/                        # Backend test suite (pytest)
├── scripts/                      # Utility scripts (test_auth.sh, etc.)
├── pyproject.toml                # Python package definitions & uv configuration
├── .env                          # Backend environment variables
└── AGENTS.md                     # Agent operating instructions (this document)
```

---

## 3. Tooling & Environment Standards

### Frontend (Must Use `pnpm`)
Always execute frontend actions inside `apps/frontend` using **pnpm**:
```bash
cd apps/frontend

# Install dependencies
pnpm install

# Start development server (port 3000)
pnpm run dev

# TypeScript type verification
pnpm run lint

# Production bundle build
pnpm run build
```
- **Do not** use `npm` or `yarn`. Always use `pnpm`.
- Ensure `pnpm run lint` (`tsc --noEmit`) and `pnpm run build` pass before completing any changes.

### Backend (Must Use `uv`)
Manage the Python environment and run backend commands using **uv**:
```bash
# Run FastAPI development server
uv run uvicorn apps.api.main:app --reload --port 8000

# Run backend test suite
PYTHONPATH=. uv run pytest

# Execute a one-off Python script
uv run python script.py
```

### Environment Variables
- Root `.env`:
  ```ini
  SUPABASE_URL=https://<your-project>.supabase.co
  SUPABASE_ANON_KEY=<anon-key>
  JWT_SECRET_KEY=<secret>
  ```
- Frontend `.env` (`apps/frontend/.env`):
  ```ini
  VITE_API_URL=http://localhost:8000
  VITE_USE_MOCK_API=false
  ```

---

## 4. Architectural Rules for Agents

### 1. UI & Design Preservation
- **Do not redesign UI** unless explicitly requested.
- Maintain existing component hierarchy, visual branding, color palettes (slate, teal, emerald, amber, rose), micro-interactions, sound triggers (`sound.playCorrect()`, etc.), and responsive behaviors.
- Decompose monolithic pages and components into focused functional components (e.g., `HeroSection`, `InteractiveCard`, `ProgressStatsGrid`, `MistakeCard`, etc.).

### 2. Frontend-Backend Communication
- All API interactions in the frontend must route through `apps/frontend/src/lib/api/` modules:
  - `client.ts`: Shared fetch wrapper handling JSON headers, base URLs, and Bearer token injection.
  - `auth.ts`: Authentication, registration, current user resolution, and token rotation.
  - `quizzes.ts`: Quiz retrieval, exercise payload normalization, and AI generation polling.
  - `attempts.ts`: Answer validation and quiz attempt submission.
  - `progress.ts`: User profile statistics and weak-area concept tracking.
- Store authentication tokens under `noesis_auth_token` and `noesis_refresh_token` in `localStorage`.

### 3. Exercise Schema & Grading Integrity
- **Answer Sanitization**: The backend (`apps/api/schemas/exercise.py`) sanitizes correct answers from `GET /quizzes/{id}` payloads so users cannot inspect client state to cheat.
- **Server Evaluation**: Answers are checked server-side via `POST /exercise-attempts/check`.
- Supported exercise formats:
  - `multiple_choice` (`mcq_translation` in frontend): Choice selection with optional audio phrase.
  - `fill_in_blank` (`fill_blank` in frontend): Missing key word with contextual sentence and hint.
  - `word_order`: Token reordering into correct syntactic sentences.
  - `matching`: Vocabulary pair matching across left and right columns.

### 4. Background AI Quiz Generation
- `POST /generation-jobs` receives `{ language, level, topic, count }`.
- Jobs return `status: "in_progress"` or `"completed"` with `quiz_id`.
- Frontend polls `GET /generation-jobs/{jobId}` until completed, then navigates to `/quiz/{quiz_id}`.

---

## 5. API Reference Summary

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/auth/register` | Register user & issue JWT tokens | No |
| `POST` | `/auth/login` | Login user & issue JWT tokens | No |
| `POST` | `/auth/refresh` | Rotate expired access token | No |
| `POST` | `/auth/logout` | Revoke refresh token | No |
| `GET` | `/auth/me` | Fetch authenticated user account info | Yes |
| `GET` | `/progress/me` | Aggregated user metrics, streak & total XP | Yes |
| `GET` | `/progress/me/weaknesses` | Concepts needing reinforcement | Yes |
| `GET` | `/quizzes` | List available quizzes | Yes |
| `GET` | `/quizzes/{quiz_id}` | Retrieve sanitized quiz with exercises | Yes |
| `POST` | `/exercise-attempts/check` | Validate exercise answer & calculate XP | Yes |
| `POST` | `/quiz-attempts` | Submit completed quiz session & mistakes | Yes |
| `GET` | `/quiz-attempts/{id}` | Retrieve review summary of a past attempt | Yes |
| `POST` | `/generation-jobs` | Trigger AI quiz synthesis for a topic | Yes |
| `GET` | `/generation-jobs/{id}` | Poll generation job progress and quiz ID | Yes |

---

## 6. Pre-Commit Checklist for Agents

Before completing any task or pull request:

- [ ] **Typecheck**: Run `pnpm run lint` in `apps/frontend/` — ensure zero TypeScript compilation errors.
- [ ] **Build**: Run `pnpm run build` in `apps/frontend/` — ensure the Vite production bundle builds successfully.
- [ ] **Backend Schema Validation**: Run `PYTHONPATH=. uv run pytest` — verify schemas and API routes pass tests.
- [ ] **No Dead Code**: Remove unused imports, dead placeholder files, or duplicate mock fallbacks.
- [ ] **Preserve Formatting**: Follow clean formatting, readable function decomposition, and consistent variable names across both TypeScript and Python.

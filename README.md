# EasyEcon

EasyEcon is an e-learning platform built for Modern Application Development (204212). Teachers can create courses, flashcards, and exams. Students can study content, take quizzes, and track their progress.

## Team Members

| Name | Student ID | Role |
|------|-----------|------|
| Natthanicha Rodaree | 670510653 | Fullstack |
| Noorfadilah Prayunto | 670510666 | Frontend and Documentation |
| Wannee Thanomworrakul | 670510679 | Fullstack |

## System Architecture

The application is composed of two primary services:

*   **Frontend**: A Single Page Application (SPA) built with Vue 3 and Vite. It serves the user interface and communicates with the backend.
*   **Backend**: A Python-based built with FastAPI. It handles data persistence, business logic, and authentication (JWT + Google OAuth + GitHub OAuth).
*   **Database**: PostgreSQL is used for relational data storage. The application is configured to switch between a local Dockerized instance and a remote Supabase instance based on environment configuration.

## Project Structure

```
├── fastapi/               # backend application source code
│   ├── app/               # core application logic (routers, models, schemas)
│   ├── main.py            # application entry point
│   └── requirements.txt
├── frontend/              # frontend application source code
│   └── src/
│       ├── views/         # page components
│       ├── components/    # shared ui components
│       ├── services/      # api call functions
│       └── store/         # pinia stores
├── docker-compose.yml     # container orchestration configuration
├── vercel.json            # deployment configuration for Vercel
├── run.sh                 # utility script for local environment initialization
└── .env.example           # environment variable template
```

## Local Development Setup

The project is designed to run in a containerized environment using Docker.

### 1. Environment Configuration

Copy the example configuration file and update the values with your credentials.
```bash
cp .env.example .env
```

### 2. Service Initialization

Execute the initialization script to start the services. This script automatically detects the database configuration.

```bash
./run.sh
```

**Database Modes:**
*   **Local**: Uses a local PostgreSQL container (default).
*   **Remote**: Set `USE_SUPABASE=true` in `.env` to connect to a managed Supabase instance.

### 3. Access Points

*   **Frontend**: `http://localhost:8080`
*   **API Documentation**: `http://localhost:56733/docs`

### 4. Create the First Admin

After startup, call this endpoint once to seed the admin account using `SEED_ADMIN_*` values from `.env`:

```bash
curl -X POST http://localhost:56733/admin/seed
```

## API Routes

Base URL: `http://localhost:56733` — Full interactive docs at `/docs`

| Router | Prefix | Roles |
|--------|--------|-------|
| Auth | `/auth` | Public |
| Users | `/users` | Authenticated |
| Admin | `/admin` | Admin |
| Courses | `/courses` | Teacher, Student |
| Learning | `/learning` | Teacher, Student |
| Flashcards | `/flashcards` | Teacher, Student |
| Exam | `/exam` | Teacher, Student |
| Search | `/search` | Teacher, Student |

## Deployment (Vercel)

The application is configured for deployment on the Vercel platform.

1.  **Installation**: Ensure the Vercel CLI is installed.
    ```bash
    npm i -g vercel
    ```

2.  **Deployment**:
    ```bash
    vercel --prod
    ```

### Configuration Requirements

Verify the following settings in the Vercel Project Dashboard:

*   **Environment Variables**:
    *   `DATABASE_URL`: Connection string for the production database (Supabase).
    *   `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`: Google OAuth credentials.
    *   `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET`: GitHub OAuth credentials.
    *   `SECRET_KEY`: Cryptographic signing key for JWT.
    *   `APP_ENV`: Set to `production`.
    *   `USE_SUPABASE`: Set to `true`.

*   **Build Settings**: Default settings are overridden by `vercel.json` and do not require manual configuration.

## Authentication

Authentication is implemented using JSON Web Tokens (JWT) and OAuth 2.0.

*   **JWT**: Stored as an HTTP-only cookie. A CSRF token is returned in the response body and must be sent as `X-CSRF-Token` on every state-changing request.
*   **Google OAuth**: Requires valid credentials from the Google Cloud Console.
    *   **Local Redirect URI**: `http://localhost:56733/auth/google/callback`
    *   **Production Redirect URI**: `https://<your-project>.vercel.app/api/auth/google/callback`
*   **GitHub OAuth**: Requires valid credentials from GitHub Developer Settings.
    *   **Local Redirect URI**: `http://localhost:56733/auth/github/callback`
    *   **Production Redirect URI**: `https://<your-project>.vercel.app/api/auth/github/callback`

## Dependency Management

Dependencies are managed separately for each service:

*   **Frontend**: `npm install` (within `frontend/` directory)
*   **Backend**: `pip install -r requirements.txt` (within `fastapi/` directory)
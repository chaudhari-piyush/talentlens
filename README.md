# TalentLens API

A FastAPI application for resume screening with respect to job descriptions.

## Features

- Firebase authentication
- Job posting management
- Candidate management with resume upload
- Resume screening with LLM-based scoring
- Q&A document generation for interviews

## Setup

1. Install uv (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install dependencies:
```bash
uv sync
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Set up Firebase:
- Create a Firebase project
- Option 1: Download the service account credentials JSON and set the path in FIREBASE_CREDENTIALS_PATH
- Option 2: Just set FIREBASE_PROJECT_ID in .env (for development with limited functionality)
- Note: For signup functionality, you need either the credentials file or project ID

5. Set up PostgreSQL database:
- Create a database
- Update DATABASE_URL in .env

6. Run database migrations:
```bash
uv run alembic upgrade head
```

7. Run the application:
```bash
uv run uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
All endpoints require Firebase authentication token in the Authorization header:
```
Authorization: Bearer <firebase-token>
```

### Users
- `GET /api/users/me` - Get current user info
- `POST /api/users/accept-terms` - Accept terms and conditions

### Jobs
- `POST /api/jobs/` - Create a new job
- `GET /api/jobs/` - List all jobs
- `GET /api/jobs/{job_id}` - Get specific job
- `PUT /api/jobs/{job_id}` - Update job
- `DELETE /api/jobs/{job_id}` - Delete job

### Candidates
- `POST /api/candidates/` - Create candidate with resume upload
- `GET /api/candidates/` - List candidates (filterable by job_id)
- `GET /api/candidates/{candidate_id}` - Get specific candidate
- `GET /api/candidates/{candidate_id}/resume` - Download resume
- `GET /api/candidates/{candidate_id}/qa-document` - Download Q&A document
- `POST /api/candidates/{candidate_id}/rescan` - Rescan resume
- `DELETE /api/candidates/{candidate_id}` - Delete candidate

## Resume Processing

The application now uses **Google Gemini Flash 2.5** for intelligent resume analysis and interview question generation.

### Gemini Integration Features:

1. **Resume Analysis & Scoring**:
   - Skills Match Score (0-10): How well candidate's skills match the expected skills
   - Resume Relevancy Score (0-10): Overall experience relevance to the role
   - Job Description Relevancy Score (0-10): Alignment with specific job requirements

2. **Interview Question Generation**:
   - **Round 1 - Technical Screening**: Fundamental technical questions
   - **Round 2 - Deep Technical Dive**: Complex scenarios and system design
   - **Round 3 - Behavioral & Cultural Fit**: Leadership, teamwork, and situational questions

3. **PDF Generation**:
   - Professional interview guide PDF with structured Q&A
   - Expected answers and follow-up questions
   - Red flags to watch for during interviews

### Configuration:
**Required**: Set `GEMINI_API_KEY` in your `.env` file for AI-powered resume processing.

To get a Gemini API key:
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

## Development

To run in development mode:
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

To install development dependencies:
```bash
uv sync --dev
```

To run linting and formatting:
```bash
uv run ruff check .
uv run black .
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

This application is configured for deployment on Render. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

### Quick Deploy to Render

1. Fork this repository
2. Connect to Render
3. Set environment variables:
   - `ENVIRONMENT=production`
   - `SECRET_KEY=<your-secret-key>`
   - `GEMINI_API_KEY=<your-gemini-api-key>`
   - `FIREBASE_PROJECT_ID=<your-firebase-project-id>`
4. Deploy!

The application will automatically:
- Create a PostgreSQL database
- Run migrations
- Start the API server
# Synzept Backend API

A FastAPI-based backend for the Synzept application, providing AI-powered productivity and goal management features.

## Features

- **User Authentication**: Google OAuth integration
- **Goal Management**: Create, track, and manage personal goals
- **Idea Management**: Capture and organize creative ideas
- **Memory System**: Store and retrieve user memories and insights
- **Chat Interface**: AI-powered conversations
- **Profile Management**: User profile and preferences

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (Azure Database for PostgreSQL)
- **ORM**: SQLAlchemy
- **Authentication**: Google OAuth 2.0
- **Deployment**: Azure App Service

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Google OAuth credentials

### Installation

1. Clone the repository:
```bash
git clone https://github.com/synzeptt/synzeptv1backend.git
cd synzeptv1backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- `GET /health` - Health check endpoint

### Authentication
- `GET /api/auth/google` - Google OAuth login
- `GET /api/auth/google/callback` - OAuth callback
- `POST /api/auth/logout` - Logout

### Profile
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update user profile

### Goals
- `GET /api/goals` - List user goals
- `POST /api/goals` - Create new goal
- `PUT /api/goals/{id}` - Update goal
- `DELETE /api/goals/{id}` - Delete goal

### Ideas
- `GET /api/ideas` - List user ideas
- `POST /api/ideas` - Create new idea
- `PUT /api/ideas/{id}` - Update idea
- `DELETE /api/ideas/{id}` - Delete idea

### Memories
- `GET /api/memories` - List user memories
- `POST /api/memories` - Create new memory
- `PUT /api/memories/{id}` - Update memory
- `DELETE /api/memories/{id}` - Delete memory

### Chat
- `POST /api/chat` - Send chat message
- `GET /api/chat/history` - Get chat history

## Database Schema

The application uses the following database tables:
- `users` - User accounts
- `user_profile` - User profile information
- `conversations` - Chat conversations
- `memories` - User memories and insights
- `ideas` - User ideas
- `goals` - User goals
- `projects` - User projects

## Deployment

### Azure App Service

1. Create an Azure App Service with Python runtime
2. Configure environment variables in Application Settings
3. Set startup command: `python run.py`
4. Deploy via GitHub Actions or Azure DevOps

### Environment Variables

Required environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - JWT signing secret
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- `GOOGLE_REDIRECT_URI` - OAuth redirect URI
- `CORS_ORIGINS` - Allowed CORS origins (comma-separated)

## Development

### Running with Reload

```bash
UVICORN_RELOAD=true python run.py
```

### Database Migrations

The application automatically creates database tables on startup using SQLAlchemy's `create_all()`.

## License

This project is part of the Synzept application.
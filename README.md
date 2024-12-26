# Dominion Todo API

An AI-powered todo API that helps you take over the world, or at least dominate your todo list. Built with FastAPI and PostgreSQL, this API powers intelligent task management with AI-driven features for better organization and productivity.

The React-based webapp is available here: [https://github.com/camman3d/dominion-todo-app](https://github.com/camman3d/dominion-todo-app)

Access the app here: [dominion.mischief-tech.com](https://dominion.mischief-tech.com)

## Features

- RESTful API endpoints for todo management
- AI-powered task organization and insights
- PostgreSQL for reliable data storage
- FastAPI for high-performance async operations
- Secure authentication and data protection

## Prerequisites

- Python 3.8+
- PostgreSQL
- pip (Python package manager)

## Quick Start

1. Clone the repository:
   ```bash
   git clone git@github.com:camman3d/dominion-todo-api.git
   cd dominion-todo-api
   ```

2. Create and activate virtual environment:

   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate on Unix/macOS
   source venv/bin/activate

   # Activate on Windows (cmd.exe)
   venv\Scripts\activate

   # Activate on Windows (PowerShell)
   .\venv\Scripts\activate.ps1
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set:
    - `SECRET_KEY`: Your secure random string
    - `SQLALCHEMY_DATABASE_URL`: Your PostgreSQL connection URL
      ```
      postgresql://user:password@localhost:5432/postgres
      ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

## API Documentation

Once running, view the interactive API docs at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Troubleshooting

Common issues:

1. **Database connection fails**
    - Verify PostgreSQL is running, and accessible with password auth
    - Check connection string in `.env`
    - Ensure database exists

2. **Dependencies installation fails**
    - Upgrade pip: `pip install --upgrade pip`
    - Install system dependencies for psycopg2

## Contributing

1. Fork the repository
2. Create your feature branch
3. Submit a pull request

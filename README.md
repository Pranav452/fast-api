# FastAPI Task Manager

A simple task management application built with FastAPI and a modern UI.

## Features

- Create, read, update, and delete tasks
- Mark tasks as complete/incomplete
- Modern UI with Tailwind CSS
- In-memory storage for simplicity

## Requirements

- Python 3.7+
- FastAPI
- Uvicorn
- Jinja2
- Python-multipart

## Setup

1. Clone the repository:
```bash
git clone <your-repository-url>
cd <repository-name>
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the server:
```bash
python main.py
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

## API Endpoints

- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create a new task
- `PUT /api/tasks/{task_id}` - Toggle task completion status
- `DELETE /api/tasks/{task_id}` - Delete a task

## Project Structure

```
.
├── main.py              # FastAPI application and API endpoints
├── templates/           # HTML templates
│   └── index.html      # Main UI template
├── requirements.txt     # Python dependencies
└── README.md           # This file
``` 
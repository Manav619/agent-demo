# Task Management API

A simple Task Management REST API built with FastAPI and SQLite.

## Features

- Create tasks
- List tasks
- Get a task by ID
- Update tasks
- Delete tasks

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the API

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Run tests

```bash
pytest
```

## API Endpoints

- `POST /tasks`
- `GET /tasks`
- `GET /tasks/{id}`
- `PUT /tasks/{id}`
- `DELETE /tasks/{id}`

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from app.database import get_connection, init_db


app = FastAPI(title="Task Management API")


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    completed: bool = False


class TaskUpdate(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    completed: bool = False


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    completed: bool
    created_at: str


@app.on_event("startup")
def startup() -> None:
    init_db()


def row_to_task(row) -> TaskResponse:
    return TaskResponse(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        completed=bool(row["completed"]),
        created_at=row["created_at"],
    )


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate) -> TaskResponse:
    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title, description, completed, created_at) VALUES (?, ?, ?, ?)",
            (task.title, task.description, int(task.completed), created_at),
        )
        task_id = cursor.lastrowid
        row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

    if row is None:
        raise HTTPException(status_code=500, detail="Failed to create task")

    return row_to_task(row)


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks() -> list[TaskResponse]:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM tasks ORDER BY id").fetchall()

    return [row_to_task(row) for row in rows]


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int) -> TaskResponse:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return row_to_task(row)


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate) -> TaskResponse:
    with get_connection() as connection:
        existing = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Task not found")

        connection.execute(
            "UPDATE tasks SET title = ?, description = ?, completed = ? WHERE id = ?",
            (task.title, task.description, int(task.completed), task_id),
        )
        row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

    if row is None:
        raise HTTPException(status_code=500, detail="Failed to update task")

    return row_to_task(row)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> None:
    with get_connection() as connection:
        existing = connection.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Task not found")

        connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

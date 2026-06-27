import os

from fastapi import Depends, FastAPI, HTTPException, Query, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import Base, engine, get_db

models.Base.metadata.create_all(bind=engine)

API_KEY_NAME = "X-API-Key"
# Read from environment variable; fall back to default for local dev only
API_KEY = os.getenv("API_KEY", "secret-task-key")
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_key(api_key: str | None = Security(api_key_header)) -> str:
    if api_key == API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
        headers={"WWW-Authenticate": "API Key"},
    )

app = FastAPI(
    title="Task Manager API",
    description="A simple task manager with CRUD operations built using FastAPI and SQLite.",
    version="1.0.0",
    dependencies=[Depends(get_api_key)],
)


@app.post("/tasks/", response_model=schemas.TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db=db, task=task)


@app.get("/tasks/", response_model=list[schemas.TaskOut])
def read_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    completed: bool | None = Query(None),
    db: Session = Depends(get_db),
):
    return crud.get_tasks(db=db, skip=skip, limit=limit, completed=completed)


@app.get("/tasks/{task_id}", response_model=schemas.TaskOut)
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db=db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return db_task


@app.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    db_task = crud.get_task(db=db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return crud.update_task(db=db, db_task=db_task, changes=task_update)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db=db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    crud.delete_task(db=db, db_task=db_task)
    return None

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, constr


class TaskBase(BaseModel):
    title: constr(strip_whitespace=True, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = False
    due_date: Optional[constr(strip_whitespace=True, max_length=50)] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[constr(strip_whitespace=True, min_length=1, max_length=200)] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[constr(strip_whitespace=True, max_length=50)] = None


class TaskOut(TaskBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

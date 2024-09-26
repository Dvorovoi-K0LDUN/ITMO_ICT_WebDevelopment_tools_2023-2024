from fastapi import APIRouter
from models import Task, TaskBase, TaskShow, User
from typing_extensions import TypedDict
import datetime
from fastapi import HTTPException, Depends
from database import get_session

task_router = APIRouter()

@task_router.post("/tasks/create")
def task_create(task: TaskBase, user_id: int, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "data": Task}):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    task = Task.model_validate(task)
    task.user_id = user_id
    session.add(task)
    session.commit()
    session.refresh(task)
    return {"status": 200, "data": task}

@task_router.get("/tasks/list")
def task_list(session=Depends(get_session)) -> list[Task]:
    return session.query(Task).all()

@task_router.get("/tasks/{task_id}", response_model=TaskShow)
def task_get(task_id: int, session=Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@task_router.patch("/tasks/update/{task_id}")
def task_update(task_id: int, task: TaskBase, session=Depends(get_session)) -> Task:
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = task.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        setattr(db_task, key, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@task_router.delete("/tasks/delete/{task_id}")
def task_delete(task_id: int, session=Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}

@task_router.patch("/tasks/time-spent/{task_id}")
def update_time_spent(task_id: int, time_spent: int, session=Depends(get_session)) -> Task:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.time_spent += time_spent

    if datetime.datetime.now() >= task.date_end and not task.status:
        task.status = True

    session.add(task)
    session.commit()
    session.refresh(task)
    return task
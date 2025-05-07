#game
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List

app = FastAPI()


class Task(BaseModel):
    id: int
    title: str
    due_date: datetime
    completed: bool = False
    created_at: datetime = datetime.now()

class TaskCreate(BaseModel):
    title: str
    due_date: datetime

class TaskHistory(BaseModel):
    task: str
    early: bool
    date: datetime

# memory storage
tasks_db: List[Task] = []
user_progress = {
    "stars": 0,
    "history": []  # List of TaskHistory
}

@app.post("/tasks/", response_model=Task)
def create_task(task: TaskCreate):
    new_task = Task(
        id=len(tasks_db) + 1,
        title=task.title,
        due_date=task.due_date,
        completed=False,
        created_at=datetime.now()
    )
    tasks_db.append(new_task)
    return new_task

@app.get("/tasks/", response_model=List[Task])
def get_tasks():
    return tasks_db

@app.post("/tasks/{task_id}/complete")
def complete_task(task_id: int):
    for task in tasks_db:
        if task.id == task_id:
            if not task.completed:
                task.completed = True
                early = datetime.now() < task.due_date
                user_progress["stars"] += 2 if early else 1
                user_progress["history"].append(TaskHistory(task=task.title, early=early, date=datetime.now()))
                return {"msg": "Task completed", "early": early}
            else:
                raise HTTPException(status_code=400, detail="Task already completed")
    raise HTTPException(status_code=404, detail="Task not found")

@app.get("/progress/")
def get_progress():
    today = datetime.now().date()
    today_tasks = [t for t in tasks_db if t.due_date.date() == today]
    completed = [t for t in today_tasks if t.completed]
    percent = int((len(completed) / len(today_tasks)) * 100) if today_tasks else 0
    return {
        "stars": user_progress["stars"],
        "progress_percent": percent,
        "completed_today": len(completed),
        "total_today": len(today_tasks)
    }

@app.get("/history/", response_model=List[TaskHistory])
def get_history():
    return user_progress["history"]

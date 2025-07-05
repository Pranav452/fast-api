from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Set up templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Task model
class Task(BaseModel):
    id: int
    title: str
    completed: bool = False

# In-memory storage
tasks = []
task_counter = 1

# API endpoints
@app.get("/api/tasks", response_model=List[Task])
async def get_tasks():
    return tasks

@app.post("/api/tasks", response_model=Task, status_code=201)
async def create_task(title: str = Form(...)):
    global task_counter
    task = Task(id=task_counter, title=title)
    tasks.append(task)
    task_counter += 1
    return task

@app.put("/api/tasks/{task_id}")
async def update_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            task.completed = not task.completed
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int):
    for i, task in enumerate(tasks):
        if task.id == task_id:
            return tasks.pop(i)
    raise HTTPException(status_code=404, detail="Task not found")

# Web UI routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "tasks": tasks}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
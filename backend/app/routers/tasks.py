import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Task
from app.schemas import TaskCreate, TaskListItem, TaskOut, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

EXPORT_VERSION = 1


def _get_task_or_404(task_id: int, db: Session) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> Task:
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=list[TaskListItem])
def list_tasks(db: Session = Depends(get_db)) -> list[Task]:
    return db.query(Task).order_by(Task.created_at.desc()).all()


# /{task_id} 보다 먼저 등록되어야 path 매칭이 정확함
@router.get("/export")
def export_tasks(db: Session = Depends(get_db)) -> Response:
    tasks = db.query(Task).order_by(Task.created_at.asc()).all()
    payload = {
        "version": EXPORT_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "count": len(tasks),
        "tasks": [TaskOut.model_validate(t).model_dump(mode="json") for t in tasks],
    }
    filename = (
        f"taskflow-export-{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"
    )
    return Response(
        content=json.dumps(payload, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)) -> Task:
    return _get_task_or_404(task_id, db)


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)
) -> Task:
    task = _get_task_or_404(task_id, db)
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    task = _get_task_or_404(task_id, db)
    db.delete(task)
    db.commit()

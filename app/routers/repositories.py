from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/repositories", tags=["repositories"])


@router.get("", response_model=list[schemas.RepositoryOut])
def list_repositories(db: Session = Depends(get_db)):
    return db.query(models.Repository).order_by(models.Repository.name).all()


@router.post("", response_model=schemas.RepositoryOut, status_code=201)
def add_repository(payload: schemas.RepositoryIn, db: Session = Depends(get_db)):
    if db.query(models.Repository).filter_by(name=payload.name).first():
        raise HTTPException(409, f"Repository '{payload.name}' already exists.")
    repo = models.Repository(**payload.model_dump())
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo


@router.get("/{repo_id}", response_model=schemas.RepositoryOut)
def get_repository(repo_id: int, db: Session = Depends(get_db)):
    repo = db.get(models.Repository, repo_id)
    if not repo:
        raise HTTPException(404, "Repository not found.")
    return repo


@router.delete("/{repo_id}", status_code=204)
def remove_repository(repo_id: int, db: Session = Depends(get_db)):
    repo = db.get(models.Repository, repo_id)
    if not repo:
        raise HTTPException(404, "Repository not found.")
    db.delete(repo)
    db.commit()

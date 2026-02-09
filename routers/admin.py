from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..Models import ToDo, User
from ..database import SessionLocal
from starlette import status
from .auth import get_current_user

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

# get user
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_users(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(User).all()

@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(ToDo).all()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail="Authentication Failed")
    todo_model = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="No Todo Found")
    
    db.query(ToDo).filter(ToDo.id == todo_id).delete()
    db.commit()
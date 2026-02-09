from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from Models import User
from database import SessionLocal
from starlette import status
from routers.auth import get_current_user, bcrypt_context

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

# user model class
class UserPasswordUpdateModel(BaseModel):
    password: str
    new_password: str

# # get all users
# @router.get("/", status_code=status.HTTP_200_OK)
# async def get_all_users(user: user_dependency, db: db_dependency):
#     if user is None or user.get('user_role') != 'admin':
#         raise HTTPException(status_code=401, detail="Authentication Failed")
#     return db.query(User).all()

# get user
@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(User).filter(User.id == user.get('id')).first()

# update password
@router.put("/password_change", status_code=status.HTTP_204_NO_CONTENT)
async def update_password(user: user_dependency, db: db_dependency, user_verifcation: UserPasswordUpdateModel ):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed") 
    user_model = db.query(User).filter(User.id == user.get("id")).first()

    if user_model is None:
        raise HTTPException(status_code=404, detail="No user found")
    
    if not bcrypt_context.verify(user_verifcation.password, user_model.password):
        raise HTTPException(status_code=401, detail="Error on password change") 
    
    user_model.password = bcrypt_context.hash(user_verifcation.new_password)
    db.add(user_model)
    db.commit()

# phone number change
@router.put("/phone_number", status_code=status.HTTP_204_NO_CONTENT)
async def update_password(user: user_dependency, db: db_dependency, new_phone_number: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed") 
    user_model = db.query(User).filter(User.id == user.get("id")).first()

    if user_model is None:
        raise HTTPException(status_code=404, detail="No user found")
    
    user_model.phone_number = new_phone_number
    db.add(user_model)
    db.commit()

# delete user
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: user_dependency, db: db_dependency, user_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    
    user_model = db.query(User).filter(User.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="No user found")
    
    db.query(User).filter(User.id == user_id).delete()
    db.commit()
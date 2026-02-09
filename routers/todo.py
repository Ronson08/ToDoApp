from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, Path, Request, status
from pydantic import BaseModel, Field
#from sqlalchemy.orm import Session
from Models import ToDo
from database import SessionLocal
from starlette import status
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from auth import get_current_user, get_user_from_token

templates = Jinja2Templates(directory="ToDoApp/templates")

router = APIRouter(
    prefix='/todo',
    tags=['todo']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

### Pages ###

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response

# pass all todos of user when login
@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try: 
        token = request.cookies.get('access_token')
        user = await get_user_from_token(token)

        if user is None:
            return redirect_to_login()
        
        todos = db.query(ToDo).filter(ToDo.owner_id == user.get("id")).all()

        return templates.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})
    
    except:
        return redirect_to_login()
    
@router.get("/add-todo-page")
async def render_todo_page(request: Request):
    try:
        token = request.cookies.get('access_token')
        user = await get_user_from_token(token)

        if user is None:
            return redirect_to_login()
        
        return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})
    except:
        return redirect_to_login()
    
@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db:db_dependency):
    try:
        token = request.cookies.get('access_token')
        
        if not token:
            return redirect_to_login()
        
        user = await get_user_from_token(token)

        if user is None:
            return redirect_to_login()
        
        # Get todo and verify ownership
        todo = db.query(ToDo).filter(ToDo.id == todo_id).filter(ToDo.owner_id == user.get("id")).first()
        
        if todo is None:
            return redirect_to_login()

        return templates.TemplateResponse("edit_todo.html", {"request": request, "todo": todo, "user": user})
    
    except Exception as e:
        # Log the error for debugging (you can remove this in production)
        print(f"Error in edit-todo-page: {e}")
        return redirect_to_login()

### EndPoints ###

# Request Model for TODO
class ToDoRequestModel(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=2, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

# get all todos
@router.get("/")
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    return db.query(ToDo).filter(ToDo.owner_id == user.get('id')).all()

# get todo by id
@router.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0), ):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    todo_model = db.query(ToDo).filter(ToDo.id == todo_id).filter(ToDo.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="ID Not Found")

# create new todo
@router.post("/create_todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_input: ToDoRequestModel):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    todo_model = ToDo(**todo_input.dict(), owner_id = user.get('id'))

    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model

# Update todo by id
@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_id: int, todo_update: ToDoRequestModel):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    todo_model = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Detail Not Found!")
    
    todo_model.title = todo_update.title
    todo_model.description = todo_update.description
    todo_model.priority = todo_update.priority
    todo_model.complete = todo_update.complete

    db.add(todo_model)
    db.commit()

# delete to by id
@router.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    todo_model = db.query(ToDo).filter(ToDo.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Details Not Found")
    
    db.query(ToDo).filter(ToDo.id == todo_id).delete()

    db.commit()

        
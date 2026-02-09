from datetime import datetime,timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, Request, status, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from Models import User
from database import SessionLocal
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# secret key and algorithm for jwt 
SECRET_KEY = "hsf9832u03rj09290u4rjfw09489f34hff094"
ALGORITHM = 'HS256'

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

# token model class
class TokenRequestModel(BaseModel):
    access_token: str
    token_type: str

templates = Jinja2Templates(directory="ToDoApp/templates")

### Pages ###
@router.get("/login-page")
def render_loginpage(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register-page")
def render_registerpage(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

### Endpoints ##

# authencation for token
def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user

#jwt for token
def access_token(username: str, user_id: int,role: str, expire_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expire = datetime.now(timezone.utc) + expire_delta
    encode.update({'exp': expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# Helper function to decode JWT from token string (for cookie-based auth)
async def get_user_from_token(token: str):
    """Decode JWT token and return user info. Returns None if token is invalid."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            return None
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except (JWTError, Exception) as e:
        # Catch all JWT errors (expired, invalid, etc.) and any other exceptions
        return None

# decode for current user (for dependency injection with Authorization header)
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldnot Validate the User")
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldnot Validate the User")

# token for authentication api
@router.post("/token", response_model=TokenRequestModel)
async def login_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):

    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldnot Validate the User")
    token = access_token(user.username, user.id, user.role, timedelta(minutes=20))

    return {"access_token": token, "token_type": "bearer"}

# user model class
class UserRequestModel(BaseModel):
    email: str
    username: str
    password: str
    first_name: str
    last_name: str
    role: str
    phone_number: str

# User Creation api
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user: UserRequestModel):
    create_user_model = User(
        email = create_user.email,
        username = create_user.username,
        password = bcrypt_context.hash(create_user.password),
        first_name = create_user.first_name,
        last_name = create_user.last_name,
        role = create_user.role,
        is_active = True,
        phone_number = create_user.phone_number
    )
    
    db.add(create_user_model)
    db.commit()



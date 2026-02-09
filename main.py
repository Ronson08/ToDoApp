from Models import Base
from database import engine
from routers import auth, todo, admin, users

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/")
def test(request: Request):
    return RedirectResponse(url="/todo/todo-page", status_code=status.HTTP_302_FOUND)
    
@app.get("/health")
async def health_check():
    return {"status": "Healthy"}

app.include_router(auth.router)
app.include_router(todo.router)
app.include_router(admin.router)
app.include_router(users.router)




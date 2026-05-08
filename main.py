from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import database, models, schemas, utils
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
import os

# DB tables create karne ki command
database.Base.metadata.create_all(bind=database.engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI(title="Ethara AI - Task Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, utils.SECRET_KEY, algorithms=[utils.ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# --- NAYA: FRONTEND FILES SERVE KARNE KA LOGIC ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    # Jab koi seedha URL kholega, index.html dikhao
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"message": "Ethara AI Task Manager is Live! (Frontend missing)"}

@app.get("/index.html", response_class=HTMLResponse)
def get_index():
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/dashboard.html", response_class=HTMLResponse)
def get_dashboard():
    file_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")
# ------------------------------------------------

# 1. SIGNUP API
@app.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed_pw = utils.get_password_hash(user.password)
    new_user = models.User(name=user.name, email=user.email, hashed_password=hashed_pw, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 2. LOGIN API
@app.post("/login", response_model=schemas.Token)
def login(creds: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == creds.email).first()
    if not user or not utils.verify_password(creds.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = utils.create_access_token(data={"user_id": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

# 3. GET ALL USERS (Admin Only - Operator Directory ke liye)
@app.get("/users", response_model=list[schemas.UserResponse])
def get_all_users(db: Session = Depends(database.get_db), user: models.User = Depends(get_current_user)):
    if user.role != models.RoleEnum.Admin:
        raise HTTPException(status_code=403, detail="Admins only")
    return db.query(models.User).all()

# 4. CREATE PROJECT (Admin Only)
@app.post("/projects", response_model=schemas.ProjectResponse)
def create_project(proj: schemas.ProjectCreate, db: Session = Depends(database.get_db), user: models.User = Depends(get_current_user)):
    if user.role != models.RoleEnum.Admin:
        raise HTTPException(status_code=403, detail="Admins only")
    new_proj = models.Project(**proj.dict(), admin_id=user.id)
    db.add(new_proj)
    db.commit()
    db.refresh(new_proj)
    return new_proj

# 5. CREATE TASK (Admin Only)
@app.post("/tasks", response_model=schemas.TaskResponse)
def create_task(task: schemas.TaskCreate, db: Session = Depends(database.get_db), user: models.User = Depends(get_current_user)):
    if user.role != models.RoleEnum.Admin:
        raise HTTPException(status_code=403, detail="Admins only")
    new_task = models.Task(**task.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# 6. GET TASKS (Admin sees all, Member sees own)
@app.get("/tasks/me", response_model=list[schemas.TaskResponse])
def my_tasks(db: Session = Depends(database.get_db), user: models.User = Depends(get_current_user)):
    if user.role == models.RoleEnum.Admin:
        return db.query(models.Task).all()
    return db.query(models.Task).filter(models.Task.assigned_to == user.id).all()

# 7. UPDATE TASK STATUS
@app.patch("/tasks/{task_id}/status")
def update_status(task_id: int, status_update: schemas.TaskStatusUpdate, db: Session = Depends(database.get_db), user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task: 
        raise HTTPException(status_code=404, detail="Task not found")
    
    if user.role != models.RoleEnum.Admin and task.assigned_to != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
    
    task.status = status_update.status
    db.commit()
    return {"message": "Status updated"}
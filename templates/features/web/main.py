"""Modern web API template with FastAPI, database integration, and authentication."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import uvicorn

__version__ = "0.1.0"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Simple in-memory database (replace with real database in production)
users_db: Dict[str, Dict[str, Any]] = {}
todos_db: Dict[str, Dict[str, Any]] = {}

# Pydantic models
class UserCreate(BaseModel):
    """User creation schema."""
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema."""
    id: str
    username: str
    email: str
    created_at: datetime


class TodoCreate(BaseModel):
    """Todo creation schema."""
    title: str
    description: Optional[str] = None
    completed: bool = False


class TodoUpdate(BaseModel):
    """Todo update schema."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TodoResponse(BaseModel):
    """Todo response schema."""
    id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
    user_id: str


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    version: str
    timestamp: datetime


# Authentication functions
def create_user(user_data: UserCreate) -> str:
    """Create a new user and return user ID."""
    if any(u["username"] == user_data.username for u in users_db.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    if any(u["email"] == user_data.email for u in users_db.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    user_id = f"user_{len(users_db) + 1}"
    users_db[user_id] = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "password": user_data.password,  # In production, hash this!
        "created_at": datetime.utcnow()
    }
    
    logger.info(f"Created user: {user_data.username}")
    return user_id


def authenticate_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Authenticate user and return user ID."""
    # Simple token-based auth (in production, use proper JWT)
    token = credentials.credentials
    
    # For demo purposes, token format is "user_<id>"
    if not token.startswith("user_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    
    user_id = token
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user_id


# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting web application...")
    
    # Create sample data
    sample_user = UserCreate(
        username="demo",
        email="demo@example.com",
        password="password123"
    )
    user_id = create_user(sample_user)
    
    # Create sample todo
    todo_id = f"todo_{len(todos_db) + 1}"
    todos_db[todo_id] = {
        "id": todo_id,
        "title": "Sample Todo",
        "description": "This is a sample todo item",
        "completed": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "user_id": user_id
    }
    
    logger.info("Application startup complete")
    yield
    
    # Shutdown
    logger.info("Shutting down web application...")


# Create FastAPI app
app = FastAPI(
    title="uvstart Web API",
    description="A modern web API template built with FastAPI",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Configure for your frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.utcnow()
    )


# User endpoints
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
async def create_user_endpoint(user_data: UserCreate):
    """Create a new user."""
    user_id = create_user(user_data)
    user = users_db[user_id]
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        created_at=user["created_at"]
    )


@app.get("/users/me", response_model=UserResponse, tags=["Users"])
async def get_current_user(user_id: str = Depends(authenticate_user)):
    """Get current user information."""
    user = users_db[user_id]
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        created_at=user["created_at"]
    )


@app.get("/users", response_model=List[UserResponse], tags=["Users"])
async def list_users():
    """List all users (admin endpoint)."""
    return [
        UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            created_at=user["created_at"]
        )
        for user in users_db.values()
    ]


# Todo endpoints
@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED, tags=["Todos"])
async def create_todo(
    todo_data: TodoCreate,
    user_id: str = Depends(authenticate_user)
):
    """Create a new todo item."""
    todo_id = f"todo_{len(todos_db) + 1}"
    now = datetime.utcnow()
    
    todos_db[todo_id] = {
        "id": todo_id,
        "title": todo_data.title,
        "description": todo_data.description,
        "completed": todo_data.completed,
        "created_at": now,
        "updated_at": now,
        "user_id": user_id
    }
    
    todo = todos_db[todo_id]
    logger.info(f"Created todo: {todo_data.title} for user: {user_id}")
    
    return TodoResponse(**todo)


@app.get("/todos", response_model=List[TodoResponse], tags=["Todos"])
async def list_todos(
    completed: Optional[bool] = None,
    user_id: str = Depends(authenticate_user)
):
    """List todos for the current user."""
    user_todos = [
        todo for todo in todos_db.values()
        if todo["user_id"] == user_id
    ]
    
    if completed is not None:
        user_todos = [todo for todo in user_todos if todo["completed"] == completed]
    
    return [TodoResponse(**todo) for todo in user_todos]


@app.get("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
async def get_todo(
    todo_id: str,
    user_id: str = Depends(authenticate_user)
):
    """Get a specific todo item."""
    if todo_id not in todos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    todo = todos_db[todo_id]
    if todo["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return TodoResponse(**todo)


@app.put("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
async def update_todo(
    todo_id: str,
    todo_update: TodoUpdate,
    user_id: str = Depends(authenticate_user)
):
    """Update a todo item."""
    if todo_id not in todos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    todo = todos_db[todo_id]
    if todo["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update fields
    update_data = todo_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        todo[field] = value
    
    todo["updated_at"] = datetime.utcnow()
    
    logger.info(f"Updated todo: {todo_id}")
    return TodoResponse(**todo)


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Todos"])
async def delete_todo(
    todo_id: str,
    user_id: str = Depends(authenticate_user)
):
    """Delete a todo item."""
    if todo_id not in todos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    todo = todos_db[todo_id]
    if todo["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    del todos_db[todo_id]
    logger.info(f"Deleted todo: {todo_id}")


# Statistics endpoint
@app.get("/stats", tags=["Statistics"])
async def get_stats(user_id: str = Depends(authenticate_user)):
    """Get user statistics."""
    user_todos = [
        todo for todo in todos_db.values()
        if todo["user_id"] == user_id
    ]
    
    total_todos = len(user_todos)
    completed_todos = len([todo for todo in user_todos if todo["completed"]])
    pending_todos = total_todos - completed_todos
    
    return {
        "total_todos": total_todos,
        "completed_todos": completed_todos,
        "pending_todos": pending_todos,
        "completion_rate": (completed_todos / total_todos * 100) if total_todos > 0 else 0
    }


def main() -> None:
    """Main function to run the web server."""
    print(f"uvstart Web API Template (version {__version__})")
    print("Starting FastAPI development server...")
    print()
    print("API Documentation:")
    print("  - http://localhost:8000/docs - Interactive API docs (Swagger)")
    print("  - http://localhost:8000/redoc - Alternative API docs")
    print()
    print("Sample API calls:")
    print("  curl http://localhost:8000/")
    print("  curl http://localhost:8000/health")
    print("  curl http://localhost:8000/users/1")
    print()
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise


if __name__ == "__main__":
    main()

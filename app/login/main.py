from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

import sqlite3


DATABASE_URL = "user.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn


def create_user_table():
    with get_db_connection() as conn:
        conn.execute("""
                         CREATE TABLE IF NOT EXISTS users (
                             username TEXT NOT NULL PRIMARY KEY,
                             password TEXT NOT NULL,
                             is_admin BOOLEAN NOT NULL DEFAULT 0
                         );
                     """)
        conn.commit()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
        if cursor.fetchone() is None:
            password = "111111"
            cursor.execute(
                "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                ("admin", password, True),
            )
            conn.commit()
            print(f"Default admin user 'admin' with password '{password}' created.")


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_user_table()
    yield


router = APIRouter(tags=["login"])


@router.get("/hi")
async def hi(name: str = "login") -> str:
    return f"hi, {name}"


class AuthUser(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class UserCreate(AuthUser):
    is_admin: bool = False


class UserInDB(BaseModel):
    username: str
    password: str
    is_admin: bool

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    code: int
    message: str


class RegisterResponde(BaseModel):
    code: int
    message: str


def get_user(username: str) -> UserInDB | None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_row = cursor.fetchone()
        if user_row:
            return UserInDB(**dict(user_row))
        return None


def authenticate_user(user_creds: AuthUser) -> UserInDB:
    user = get_user(username=user_creds.username)
    if (
        not user
        or user.is_admin != user_creds.is_admin
        or user.password != user_creds.password
    ):
        raise HTTPException(status_code=401, detail="Incorrect username or password.")
    return user


@router.post("/register", response_model=RegisterResponde)
def regiter_user(user: UserCreate):
    db_user = get_user(username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered.")
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
            (user.username, user.password, user.is_admin),
        )
        conn.commit()
    return RegisterResponde(code=200, message="User register successfully.")


@router.post("/login", response_model=AuthResponse)
async def login(user_creds: AuthUser):
    user = authenticate_user(user_creds)
    return AuthResponse(code=200, message=f"Login successful for user {user.username}.")

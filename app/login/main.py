from fastapi import APIRouter
from pydantic import BaseModel

from app.config import ADMINS, USERS

router = APIRouter(tags=["login"])


@router.get("/hi")
async def hi(name: str = "login") -> str:
    return f"hi, {name}"


class AuthUser(BaseModel):
    username: str
    password: str


@router.post("/auth/user")
async def auth_user(user: AuthUser):
    entry = USERS.get(user.username)
    if entry is not None and entry["password"] == user.password:
        return {"code": 200, "message": "Login successful."}
    else:
        return {"code": 400, "message": "Can not find the user."}


@router.post("/auth/admin")
async def auth_admin(user: AuthUser):
    entry = ADMINS.get(user.username)
    if entry is not None and entry["password"] == user.password:
        return {"code": 200, "message": "Login successful."}
    else:
        return {"code": 400, "message": "Can not find the user."}

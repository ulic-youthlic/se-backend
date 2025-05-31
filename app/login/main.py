from typing import Annotated

from fastapi import APIRouter, Path
from pydantic import BaseModel

from app.config import ADMINS, USERS

router = APIRouter(tags=["login"])


@router.get("/hi")
async def hi(name: str = "login") -> str:
    return f"hi, {name}"


class AuthUser(BaseModel):
    username: str
    password: str


@router.post("/auth/{type}")
async def auth(user: AuthUser, type: Annotated[str, Path(pattern="^user|admin$")]):
    if type == "user":
        entry = USERS.get(user.username)
        if entry is not None and entry["password"] == user.password:
            return {"code": 200, "message": "Login successful."}
        else:
            return {"code": 400, "message": "Can not find the user."}
    else:
        entry = ADMINS.get(user.username)
        if entry is not None and entry["password"] == user.password:
            return {"code": 200, "message": "Login successful."}
        else:
            return {"code": 400, "message": "Can not find the user."}

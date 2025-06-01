from fastapi import APIRouter
from pydantic import BaseModel

from app.config import ADMINS, USERS
from app.state import UserContext, admin_contexts, user_contexts

router = APIRouter(tags=["login"])


@router.get("/hi")
async def hi(name: str = "login") -> str:
    return f"hi, {name}"


class AuthUser(BaseModel):
    username: str
    password: str


class Response(BaseModel):
    code: int
    message: str


@router.post("/user")
async def auth_user(user: AuthUser) -> Response:
    entry = USERS.get(user.username)
    if entry is not None and entry["password"] == user.password:
        user_contexts.update({user.username: UserContext(user.username)})
        return Response(code=200, message="Login successful.")
    else:
        return Response(code=400, message="Can not find the user.")


@router.post("/admin")
async def auth_admin(user: AuthUser) -> Response:
    entry = ADMINS.get(user.username)
    if entry is not None and entry["password"] == user.password:
        admin_contexts.update({user.username: UserContext(user.username)})
        return Response(code=200, message="Login successful.")
    else:
        return Response(code=400, message="Can not find the user.")

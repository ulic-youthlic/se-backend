from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from app.boundary.api.schemas.login import (
    LoginLoginRequest,
    LoginLoginResponse,
    LoginRegisterRequest,
    LoginRegisterResponse,
)
from app.boundary.deps import get_user_controller
from app.control.user import User

router = APIRouter(prefix="/login", tags=["login"])


@router.get("/hi")
async def hi(name: str = "login") -> str:
    return f"hi, {name}"


@router.post("/register", response_model=LoginRegisterResponse)
async def register(
    request: LoginRegisterRequest,
    controller: Annotated[User, Depends(get_user_controller)],
):
    if not controller.register_user(
        request.username, request.password, request.is_admin
    ):
        raise HTTPException(status_code=400, detail="Username already registered.")
    return LoginRegisterResponse(code=200, message="User register successfully.")


@router.post("/login", response_model=LoginLoginResponse)
async def login(
    request: LoginLoginRequest,
    controller: Annotated[User, Depends(get_user_controller)],
):
    if not controller.authenticate_user(
        request.username, request.password, request.is_admin
    ):
        raise HTTPException(status_code=401, detail="Incorrect username or password.")
    return LoginLoginResponse(
        code=200, message=f"Login successful for user {request.username}."
    )

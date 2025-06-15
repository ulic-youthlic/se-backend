from fastapi import APIRouter
from pydantic import BaseModel

from app import core

router = APIRouter(tags=["gamesupport"])


@router.get("/hi")
async def hi(name: str = "gamesupport") -> str:
    return f"hi, {name}"


class ToggleRequest(BaseModel):
    username: str
    enable: bool


class ToggleResponse(BaseModel):
    success: bool


class GameSupportStatus(BaseModel):
    enable: bool


enable = False
process = None


@router.post("/toggle", response_model=ToggleResponse)
async def toggle(request: ToggleRequest):
    global enable
    global process
    if request.enable:
        if enable:
            return ToggleResponse(success=False)
        else:
            process = core.launch()
            enable = True
            return ToggleResponse(success=True)
    else:
        if enable:
            if process is not None:
                core.teminate(process)
                process = None
            enable = False
            return ToggleResponse(success=True)
        else:
            return ToggleResponse(success=False)


@router.get("/status")
async def status():
    return GameSupportStatus(enable=enable)

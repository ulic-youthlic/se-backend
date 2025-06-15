from fastapi import APIRouter
from pydantic import BaseModel

from app import core

router = APIRouter(tags=["autoaim"])


@router.get("/hi")
async def hi(name: str = "autoaim") -> str:
    return f"hi, {name}"


class ToggleRequest(BaseModel):
    username: str
    enable: bool


class ToggleResponse(BaseModel):
    success: bool


class AutoaimStatus(BaseModel):
    enable: bool


enable = False
process = None


@router.post("/toggle", response_model=ToggleResponse)
async def toggle(request: ToggleRequest):
    global enable
    global process
    if request.enable != enable:
        if not enable:
            process = core.launch()
            enable = True
        elif process is not None:
            core.teminate(process=process)
        else:
            return ToggleResponse(success=False)
        return ToggleResponse(success=True)
    else:
        return ToggleResponse(success=True)


@router.get("/status")
async def status():
    return AutoaimStatus(enable=enable)

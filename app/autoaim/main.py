from fastapi import APIRouter
from pydantic import BaseModel
from app import core

router = APIRouter(tags=["autoaim"])


@router.get("/hi")
async def hi(name: str = "autoaim") -> str:
    return f"hi, {name}"


class Status(BaseModel):
    username: str
    enabled: bool
    sensitiveity: int | None = None
    lockStrength: int | None = None
    headshotPriority: bool | None = None
    autoFile: bool | None = None
    targetTraking: bool | None = None


class Response(BaseModel):
    success: bool


process = None


@router.post("/set")
async def set(status: Status) -> Response:
    global process
    if status.enabled:
        if process is None:
            process = core.launch()
    else:
        if process is not None:
            core.teminate(process=process)
            process = None
    return Response(success=True)


@router.get("/status")
# [TODO]: impl get_status func
async def status(username: str) -> Status:
    return Status(
        username=username,
        enabled=True,
        sensitiveity=0,
        lockStrength=0,
        headshotPriority=True,
        autoFile=True,
        targetTraking=True,
    )

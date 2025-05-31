from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["autoaim"])


@router.get("/hi")
async def hi(name: str = "autoaim") -> str:
    return f"hi, {name}"


class Status(BaseModel):
    username: str
    enabled: bool
    sensitiveity: int
    lockStrength: int
    headshotPriority: bool
    autoFile: bool
    targetTraking: bool


class Response(BaseModel):
    success: bool


@router.post("/set")
# [TODO]: impl func for setting autoaim status
async def set(status: Status) -> Response:
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

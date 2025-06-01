from fastapi import APIRouter
from pydantic import BaseModel
from app import core
from app.state import user_contexts, admin_contexts

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


@router.post("/set")
async def set(status: Status) -> Response:
    context = user_contexts.get(status.username)
    if context is None:
        return Response(success=False)
    if status.enabled:
        if context.process is None:
            context.process = core.launch()
    else:
        if context.process is not None:
            core.teminate(process=context.process)
            context.process = None
    return Response(success=True)


@router.get("/status")
async def status(username: str) -> Status:
    context = user_contexts.get(username)
    if context is None:
        return Status(username=username, enabled=False)
    if context.process is not None and context.process.is_alive():
        return Status(username=username, enabled=True)
    else:
        return Status(username=username, enabled=False)

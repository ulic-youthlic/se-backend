import platform
import subprocess
import sys

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["game"])


@router.get("/hi")
async def hi(name: str = "game") -> str:
    return f"hi, {name}"


class ToggleRequest(BaseModel):
    enable: bool


class ToggleResponse(BaseModel):
    success: bool


class GameStatus(BaseModel):
    running: bool


class GameContext(object):
    def __init__(self, process=None) -> None:
        self.process = process

    @property
    def running(self) -> bool:
        return self.process is not None and self.process.poll() is None


context = GameContext()

if platform.system() != "Windows":
    raise RuntimeError("This server is configured to run on Windows only.")


@router.post("/toggle", response_model=ToggleResponse)
async def toggle(request: ToggleRequest):
    global context
    if request.enable:
        if context.running:
            raise HTTPException(status_code=400, detail="Process is already running.")
        command = [sys.executable, "game/CG/panda3D3/main.py"]

        try:
            context.process = subprocess.Popen(command)
            return ToggleResponse(success=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to start process: {e}")
    else:
        if not context.running:
            raise HTTPException(status_code=400, detail="Process is not running.")
        pid = context.process.pid
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                check=True,
                capture_output=True,
            )
            context.process = None
            return ToggleResponse(success=True)
        except subprocess.CalledProcessError as e:
            if "not found" in e.stderr.decode(errors="ignore"):
                context.process = None
                return ToggleResponse(success=True)
            return ToggleResponse(success=False)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to stop process: {e}")


@router.get("/status")
async def process_status():
    if context.running:
        return GameStatus(running=True)
    return GameStatus(running=False)

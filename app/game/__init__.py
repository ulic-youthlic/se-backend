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


process = None

if platform.system() != "Windows":
    raise RuntimeError("This server is configured to run on Windows only.")


@router.post("/toggle", response_model=ToggleResponse)
async def toggle(request: ToggleRequest):
    global process
    if request.enable:
        if process is not None and process.poll() is None:
            raise HTTPException(status_code=400, detail="Process is already running.")
        command = [sys.executable, "game/CG/panda3D3/main.py"]

        try:
            process = subprocess.Popen(command)
            return ToggleResponse(success=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to start process: {e}")
    else:
        if process is None or process.poll() is not None:
            raise HTTPException(status_code=400, detail="Process is not running.")
        pid = process.pid
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                check=True,
                capture_output=True,
            )
            process = None
            return ToggleResponse(success=True)
        except subprocess.CalledProcessError as e:
            if "not found" in e.stderr.decode(errors="ignore"):
                process = None
                return ToggleResponse(success=True)
            return ToggleResponse(success=False)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to stop process: {e}")


@router.get("/status")
async def process_status():
    if process is not None and process.poll() is None:
        return GameStatus(running=True)
    return GameStatus(running=False)

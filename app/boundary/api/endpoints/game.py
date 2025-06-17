from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.boundary.api.schemas.game import (
    GameStatusResponse,
    GameToggleRequest,
    GameToggleResponse,
)
from app.boundary.deps import get_game_manager_controller
from app.control.game import GameManager

router = APIRouter(prefix="/game", tags=["game"])


@router.get("/hi")
async def hi(name: str = "game") -> str:
    return f"hi, {name}"


@router.post("/toggle", response_model=GameToggleResponse)
async def toggle(
    request: GameToggleRequest,
    controller: Annotated[GameManager, Depends(get_game_manager_controller)],
):
    if not controller.set_game_status(request.enable):
        raise HTTPException(status_code=400, detail="Set game status failed.")
    else:
        return GameToggleResponse(success=True)


@router.get("/status", response_model=GameStatusResponse)
async def status(
    controller: Annotated[GameManager, Depends(get_game_manager_controller)],
):
    return GameStatusResponse(running=controller.game_running)

from typing import Annotated
from fastapi import APIRouter, Depends

from app.boundary.api.schemas.gamesupport import (
    GameSupportStatusResponse,
    GameSupportToggleRequest,
    GameSupportToggleResponse,
)
from app.boundary.deps import get_game_manager_controller
from app.control.game import GameManager

router = APIRouter(prefix="/gamesupport", tags=["gamesupport"])


@router.get("/hi")
async def hi(name: str = "gamesupport") -> str:
    return f"hi, {name}"


@router.post("/toggle", response_model=GameSupportToggleResponse)
async def toggle(
    request: GameSupportToggleRequest,
    controller: Annotated[GameManager, Depends(get_game_manager_controller)],
):
    return GameSupportToggleResponse(
        success=controller.set_support_status(request.enable)
    )


@router.get("/status", response_model=GameSupportStatusResponse)
async def status(
    controller: Annotated[GameManager, Depends(get_game_manager_controller)],
):
    return GameSupportStatusResponse(enable=controller.support_enabled)

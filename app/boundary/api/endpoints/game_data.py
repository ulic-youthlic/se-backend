from typing import Annotated
from fastapi import APIRouter, Depends

from app.boundary.api.schemas.game_data import GameDataInfoResponse, GameRecord
from app.boundary.deps import get_game_log_controller
from app.control.game_log import GameLog

router = APIRouter(prefix="/game-data", tags=["game-data"])


@router.get("/hi")
async def hi(name: str = "game-data") -> str:
    return f"hi, {name}"


@router.get("/{username}", response_model=GameDataInfoResponse)
async def info(controller: Annotated[GameLog, Depends(get_game_log_controller)]):
    records = controller.get_all_info()
    records = [GameRecord(**dict(x)) for x in records]
    return GameDataInfoResponse(success=True, message="", records=records)

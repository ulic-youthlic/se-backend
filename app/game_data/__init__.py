from fastapi import APIRouter
from app.core import meta

router = APIRouter(tags=["game-data"])


@router.get("/hi")
async def hi(name: str = "game-data") -> str:
    return f"hi, {name}"


@router.get("/{username}")
async def metainfo(username: str):
    info = meta()
    return {
        "success": True,
        "message": "",
        "records": [
            {
                "gameId": "G20231018002",
                "date": info["timestamp"],
                "map": "炼狱小镇",
                "result": "胜利",
                "accuracy": 72,
                "kills": info["kills"],
                "deaths": 0,
                "kdRatio": 1.58,
                "autoAim": True,
            }
        ],
    }

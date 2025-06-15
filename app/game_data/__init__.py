from fastapi import APIRouter
from app.core import meta

router = APIRouter(tags=["game-data"])


@router.get("/hi")
async def hi(name: str = "game-data") -> str:
    return f"hi, {name}"


@router.get("/{username}")
async def metainfo(username: str):
    infos = meta()
    return {
        "success": True,
        "message": "",
        "records": infos,
    }

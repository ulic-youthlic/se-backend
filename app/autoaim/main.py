from fastapi import APIRouter

router = APIRouter(tags=["autoaim"])


@router.get("/hi")
async def hi(name: str = "autoaim") -> str:
    return f"hi, {name}"

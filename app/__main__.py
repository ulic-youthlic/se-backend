import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import login, game_data, history, gamesupport, game
from .config import HOST, PORT

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login")
api_router.include_router(gamesupport.router, prefix="/gamesupport")
api_router.include_router(game_data.router, prefix="/game-data")
api_router.include_router(history.router, prefix="/history")
api_router.include_router(game.router, prefix="/game")

origins = ["*"]

app = FastAPI(lifespan=login.lifespan)
app.include_router(api_router, prefix="/api")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def main():
    uvicorn.run("__main__:app", port=PORT, host=HOST, log_level="info")


if __name__ == "__main__":
    main()

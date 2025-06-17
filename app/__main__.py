from contextlib import asynccontextmanager

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .boundary.api.endpoints import game, game_data, gamesupport, history, login
from .entity.repositories.user import init_db

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(gamesupport.router)
api_router.include_router(game_data.router)
api_router.include_router(history.router)
api_router.include_router(game.router)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(api_router, prefix="/api")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def main():
    uvicorn.run("__main__:app", port=5000, host="127.0.0.1", log_level="info")


if __name__ == "__main__":
    main()

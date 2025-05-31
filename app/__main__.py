import uvicorn
from fastapi import APIRouter, FastAPI

from . import autoaim, login
from .config import HOST, PORT

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login")
api_router.include_router(autoaim.router, prefix="/autoaim")

app = FastAPI()
app.include_router(api_router, prefix="/api")


def main():
    uvicorn.run("__main__:app", port=PORT, host=HOST, log_level="info")


if __name__ == "__main__":
    main()

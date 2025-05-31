import uvicorn
from fastapi import APIRouter, FastAPI

from . import autoaim, login

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login")
api_router.include_router(autoaim.router, prefix="/autoaim")

app = FastAPI()
app.include_router(api_router)


def main():
    uvicorn.run("__main__:app", port=5000, log_level="info")


if __name__ == "__main__":
    main()

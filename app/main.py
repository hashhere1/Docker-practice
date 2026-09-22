from fastapi import FastAPI
from app.router import users, auth, profiles
from app.router.files import router as files_router

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(files_router)
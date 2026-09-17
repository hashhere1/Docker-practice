from fastapi import FastAPI
from app.router import users, auth, profiles

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(profiles.router)
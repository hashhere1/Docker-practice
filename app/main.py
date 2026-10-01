from fastapi import FastAPI
from app.router import users, auth, profiles
from app.router.files import router as files_router
from app.router.google_drive_auth import router as google_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FastApi Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(files_router)
app.include_router(google_router)
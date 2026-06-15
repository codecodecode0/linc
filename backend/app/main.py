"""linc backend — FastAPI application entrypoint."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .deps import get_registry
from .routers import auth, brands, creators, login, platform

settings = get_settings()

app = FastAPI(
    title="linc API",
    version="0.1.0",
    description="Creator–brand platform API. Instagram connect flow + insights.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers (registered before the static mount so /api/* wins).
# login.router is added BEFORE auth.router so literal /api/auth/otp|google/*
# paths win over the social /api/auth/{platform}/* pattern.
app.include_router(platform.router)
app.include_router(creators.router)
app.include_router(brands.router)
app.include_router(login.router)
app.include_router(auth.router)


@app.get("/health", tags=["health"])
def health():
    return {
        "status": "ok",
        "service": "linc",
        "providers": get_registry().modes(),
    }


# Serve the existing static UI from the repo's public/ folder, if present.
_public_dir = Path(__file__).resolve().parents[2] / "public"
if _public_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(_public_dir), html=True), name="ui")

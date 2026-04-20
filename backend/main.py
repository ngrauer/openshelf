"""
OpenShelf MVP v2 — Main Application Entry Point

Start the server:
    cd backend && python main.py

Then open Swagger UI:
    http://localhost:8000/docs
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import APP_TITLE, APP_DESCRIPTION, APP_VERSION
from app.database import engine, Base
from app.routers import auth, courses, textbooks, listings, matching, messages, conversations, reviews, notifications, websocket, chat, uploads

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Add image_urls column to listings if it doesn't exist (SQLite migration)
from sqlalchemy import text
with engine.connect() as _conn:
    try:
        _conn.execute(text("ALTER TABLE listings ADD COLUMN image_urls TEXT"))
        _conn.commit()
    except Exception:
        pass  # column already exists

# Initialize FastAPI app
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow all origins for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(textbooks.router)
app.include_router(listings.router)
app.include_router(matching.router)
app.include_router(conversations.router)
app.include_router(messages.router)
app.include_router(reviews.router)
app.include_router(notifications.router)
app.include_router(chat.router)
app.include_router(uploads.router)
app.include_router(websocket.router)

# Serve uploaded images as static files
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/", tags=["Health"])
def root():
    """Health check and API info."""
    return {
        "app": "OpenShelf",
        "version": APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "description": "AI-Powered Campus Textbook Marketplace — Backend Proof of Concept",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    print("\nStarting OpenShelf MVP v1...")
    print("   Swagger UI: http://localhost:8000/docs")
    print("   ReDoc:       http://localhost:8000/redoc\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

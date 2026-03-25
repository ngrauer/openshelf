from fastapi import FastAPI

from app.api import auth, chat, conversations, listings, matches
from app.db.seed import seed_if_empty
from app.db.session import Base, SessionLocal, engine

app = FastAPI(title="OpenShelf MVP v1")

app.include_router(auth.router)
app.include_router(listings.router)
app.include_router(matches.router)
app.include_router(conversations.router)
app.include_router(chat.router)


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "OpenShelf MVP v1 running"}

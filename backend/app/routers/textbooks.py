"""
OpenShelf MVP v1 — Textbooks Router
List, search, and retrieve textbooks from the canonical catalog.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.models import Textbook
from app.schemas.schemas import TextbookOut

router = APIRouter(prefix="/textbooks", tags=["Textbooks"])


@router.get("/", response_model=List[TextbookOut])
def list_textbooks(
    isbn: Optional[str] = Query(None),
    title: Optional[str] = Query(None, description="Partial title search"),
    author: Optional[str] = Query(None, description="Partial author search"),
    db: Session = Depends(get_db),
):
    """List textbooks with optional search filters."""
    q = db.query(Textbook)
    if isbn:
        q = q.filter(Textbook.isbn == isbn)
    if title:
        q = q.filter(Textbook.title.ilike(f"%{title}%"))
    if author:
        q = q.filter(Textbook.author.ilike(f"%{author}%"))
    return q.all()


@router.get("/{textbook_id}", response_model=TextbookOut)
def get_textbook(textbook_id: int, db: Session = Depends(get_db)):
    """Get a single textbook by ID."""
    textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")
    return textbook


@router.get("/isbn/{isbn}", response_model=TextbookOut)
def get_textbook_by_isbn(isbn: str, db: Session = Depends(get_db)):
    """Look up a textbook by ISBN."""
    textbook = db.query(Textbook).filter(Textbook.isbn == isbn).first()
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")
    return textbook

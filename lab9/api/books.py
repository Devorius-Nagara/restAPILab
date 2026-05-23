from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.book import BookCreate, BookResponse, BookStatus, BookListResponse
from services import book_service
from database import get_db

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=BookListResponse, status_code=200)
async def fetch_books(
    status: Optional[BookStatus] = Query(None, description="Filter by book status"),
    author: Optional[str] = Query(None, description="Filter by author (partial, case-insensitive)"),
    sort_by: Optional[str] = Query(None, pattern="^(title|year)$", description="Sort by: title or year"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Items to skip"),
    db: AsyncSession = Depends(get_db),
):
    items, total = await book_service.get_books(
        db, status=status, author=author, sort_by=sort_by, limit=limit, offset=offset
    )
    return BookListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{book_id}", response_model=BookResponse, status_code=200)
async def fetch_book(book_id: str, db: AsyncSession = Depends(get_db)):
    record = await book_service.get_book(db, book_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return record


@router.post("/", response_model=BookResponse, status_code=201)
async def create_book(payload: BookCreate, db: AsyncSession = Depends(get_db)):
    return await book_service.add_book(db, payload)


@router.delete("/{book_id}", status_code=204)
async def remove_book(book_id: str, db: AsyncSession = Depends(get_db)):
    deleted = await book_service.remove_book(db, book_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Book not found")

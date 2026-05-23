from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from schemas.book import BookCreate, BookResponse, BookStatus, BookListResponse
from services import book_service
from database import get_database

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=BookListResponse, status_code=200)
async def list_books(
    status: Optional[BookStatus] = Query(None, description="Filter by status"),
    author: Optional[str] = Query(None, description="Partial author, case-insensitive"),
    sort_by: Optional[str] = Query(None, pattern="^(title|year)$", description="Sort field"),
    limit: int = Query(10, ge=1, le=100, description="Page size"),
    offset: int = Query(0, ge=0, description="Skip count"),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    books, total = await book_service.fetch_books(
        db, status=status, author=author, sort_by=sort_by, limit=limit, offset=offset
    )
    return BookListResponse(items=books, total=total, limit=limit, offset=offset)


@router.get("/{book_id}", response_model=BookResponse, status_code=200)
async def get_book(book_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    book = await book_service.fetch_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=BookResponse, status_code=201)
async def create_book(payload: BookCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    return await book_service.add_book(db, payload)


@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    removed = await book_service.remove_book(db, book_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Book not found")

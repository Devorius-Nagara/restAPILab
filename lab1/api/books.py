from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from schemas.book import BookCreate, BookResponse, BookStatus
from services import book_service

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=List[BookResponse], status_code=200)
async def list_books(
    status: Optional[BookStatus] = Query(None, description="Filter by status"),
    author: Optional[str] = Query(None, description="Partial author name, case-insensitive"),
    sort_by: Optional[str] = Query(None, pattern="^(title|year)$", description="Sort field: title or year"),
):
    return await book_service.fetch_books(status=status, author=author, sort_by=sort_by)


@router.get("/{book_id}", response_model=BookResponse, status_code=200)
async def get_book(book_id: str):
    book = await book_service.fetch_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=BookResponse, status_code=201)
async def create_book(payload: BookCreate):
    return await book_service.add_book(payload)


@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: str):
    removed = await book_service.remove_book(book_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Book not found")

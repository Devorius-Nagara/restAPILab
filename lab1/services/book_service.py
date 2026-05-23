import uuid
from typing import List, Dict, Optional
from schemas.book import BookCreate, BookStatus
from repository import book_repository


async def fetch_books(
    status: Optional[BookStatus] = None,
    author: Optional[str] = None,
    sort_by: Optional[str] = None,
) -> List[Dict]:
    result = await book_repository.get_all()

    if status is not None:
        result = [b for b in result if b["status"] == status.value]

    if author is not None:
        result = [b for b in result if author.lower() in b["author"].lower()]

    if sort_by == "title":
        result = sorted(result, key=lambda b: b["title"].lower())
    elif sort_by == "year":
        result = sorted(result, key=lambda b: b["year"])

    return result


async def fetch_book(book_id: str) -> Optional[Dict]:
    return await book_repository.get_by_id(book_id)


async def add_book(book_data: BookCreate) -> Dict:
    record = {
        "id": str(uuid.uuid4()),
        **book_data.model_dump(),
    }
    return await book_repository.create(record)


async def remove_book(book_id: str) -> bool:
    return await book_repository.delete(book_id)

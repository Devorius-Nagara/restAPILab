from typing import List, Dict, Optional
from models.book import books_db


async def get_all() -> List[Dict]:
    return list(books_db)


async def get_by_id(book_id: str) -> Optional[Dict]:
    for item in books_db:
        if item["id"] == book_id:
            return item
    return None


async def create(record: Dict) -> Dict:
    books_db.append(record)
    return record


async def delete(book_id: str) -> bool:
    for idx, item in enumerate(books_db):
        if item["id"] == book_id:
            books_db.pop(idx)
            return True
    return False

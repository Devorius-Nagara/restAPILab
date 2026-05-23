from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI

import database
from api.books import router as books_router
from models.book import BOOKS_COLLECTION


async def _seed() -> None:
    sample_books = [
        {"title": "Kobzar", "author": "Taras Shevchenko", "description": "Ukrainian poetry collection", "status": "available", "year": 1840},
        {"title": "Eneyida", "author": "Ivan Kotlyarevsky", "description": "Comic epic poem", "status": "available", "year": 1798},
        {"title": "Lisova pisnia", "author": "Lesia Ukrainka", "description": "Drama in verse", "status": "issued", "year": 1911},
        {"title": "Tini zabutykh predkiv", "author": "Mykhailo Kotsiubynsky", "description": "Short story", "status": "available", "year": 1911},
        {"title": "Kaidasheva simia", "author": "Ivan Nechui-Levytsky", "description": "Ukrainian family novel", "status": "available", "year": 1879},
    ]
    db = await database.get_database()
    col = db[BOOKS_COLLECTION]
    if await col.count_documents({}) > 0:
        return
    await col.insert_many([{"_id": str(uuid4()), **b} for b in sample_books])


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect_db()
    await _seed()
    yield
    await database.close_db()


app = FastAPI(
    title="Library API",
    description="REST API for library book management (MongoDB)",
    version="4.0.0",
    lifespan=lifespan,
)

app.include_router(books_router)


@app.get("/")
async def root():
    return {"message": "Library API is running"}

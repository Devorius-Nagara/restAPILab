from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI
from sqlalchemy import select, func

import database
from api.books import router as books_router
from models.book import Book


async def _seed() -> None:
    sample_books = [
        {"title": "Kobzar", "author": "Taras Shevchenko", "description": "Ukrainian poetry collection", "status": "available", "year": 1840},
        {"title": "Eneyida", "author": "Ivan Kotlyarevsky", "description": "Comic epic poem", "status": "available", "year": 1798},
        {"title": "Lisova pisnia", "author": "Lesia Ukrainka", "description": "Drama in verse", "status": "issued", "year": 1911},
        {"title": "Tini zabutykh predkiv", "author": "Mykhailo Kotsiubynsky", "description": "Short story", "status": "available", "year": 1911},
        {"title": "Kaidasheva simia", "author": "Ivan Nechui-Levytsky", "description": "Ukrainian family novel", "status": "available", "year": 1879},
    ]
    async with database.AsyncSessionLocal() as session:
        count = (await session.execute(select(func.count()).select_from(Book))).scalar()
        if count > 0:
            return
        for data in sample_books:
            session.add(Book(id=str(uuid4()), **data))
        await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database.engine.begin() as conn:
        await conn.run_sync(database.Base.metadata.create_all)
    await _seed()
    yield


app = FastAPI(
    title="Library API",
    description="REST API for library book management with PostgreSQL",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(books_router)


@app.get("/")
async def root():
    return {"message": "Library API is running"}

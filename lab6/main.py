from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI
from sqlalchemy import select, func

import database
from api.books import router as books_router
from api.auth import router as auth_router
from models.book import Book
from models.user import User
from core.security import hash_password


async def _seed() -> None:
    async with database.AsyncSessionLocal() as session:
        user_count = (await session.execute(select(func.count()).select_from(User))).scalar()
        if user_count == 0:
            session.add(User(
                id=str(uuid4()),
                username="librarian",
                hashed_password=hash_password("librarian123"),
                role="user",
                is_active=True,
            ))

        book_count = (await session.execute(select(func.count()).select_from(Book))).scalar()
        if book_count == 0:
            sample_books = [
                Book(id=str(uuid4()), title="Kobzar", author="Taras Shevchenko", description="Ukrainian poetry collection", status="available", year=1840),
                Book(id=str(uuid4()), title="Eneyida", author="Ivan Kotlyarevsky", description="Comic epic poem", status="available", year=1798),
                Book(id=str(uuid4()), title="Lisova pisnia", author="Lesia Ukrainka", description="Drama in verse", status="issued", year=1911),
                Book(id=str(uuid4()), title="Tini zabutykh predkiv", author="Mykhailo Kotsiubynsky", description="Short story", status="available", year=1911),
            ]
            session.add_all(sample_books)

        await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database.engine.begin() as conn:
        await conn.run_sync(database.Base.metadata.create_all)
    await _seed()
    yield


app = FastAPI(
    title="Library API",
    description="REST API with JWT authentication",
    version="6.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(books_router)


@app.get("/")
async def root():
    return {"message": "Library API is running"}

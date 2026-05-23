from fastapi import FastAPI
from api.books import router as books_router

app = FastAPI(
    title="Library API",
    description="Simple REST API for managing library books",
    version="1.0.0",
)

app.include_router(books_router)


@app.get("/")
async def root():
    return {"message": "Library API is running"}

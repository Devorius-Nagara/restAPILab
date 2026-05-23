from fastapi.testclient import TestClient

TEST_BOOK = {
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "description": "A novel about the American Dream",
    "status": "available",
    "year": 1925,
}


# ── POST /books/ ──────────────────────────────────────────────────────────────

def test_create_book_returns_201(client: TestClient):
    assert client.post("/books/", json=TEST_BOOK).status_code == 201


def test_create_book_returns_correct_data(client: TestClient):
    data = client.post("/books/", json=TEST_BOOK).json()
    assert data["title"] == TEST_BOOK["title"]
    assert data["author"] == TEST_BOOK["author"]
    assert data["year"] == TEST_BOOK["year"]
    assert data["status"] == "available"


def test_create_book_generates_unique_uuid(client: TestClient):
    r1 = client.post("/books/", json=TEST_BOOK).json()
    r2 = client.post("/books/", json=TEST_BOOK).json()
    assert len(r1["id"]) == 36
    assert r1["id"] != r2["id"]


def test_create_book_default_status(client: TestClient):
    book = {k: v for k, v in TEST_BOOK.items() if k != "status"}
    assert client.post("/books/", json=book).json()["status"] == "available"


def test_create_book_issued_status(client: TestClient):
    assert client.post("/books/", json={**TEST_BOOK, "status": "issued"}).json()["status"] == "issued"


def test_create_book_without_description(client: TestClient):
    book = {k: v for k, v in TEST_BOOK.items() if k != "description"}
    assert client.post("/books/", json=book).json()["description"] is None


def test_create_book_missing_title_returns_422(client: TestClient):
    assert client.post("/books/", json={k: v for k, v in TEST_BOOK.items() if k != "title"}).status_code == 422


def test_create_book_missing_author_returns_422(client: TestClient):
    assert client.post("/books/", json={k: v for k, v in TEST_BOOK.items() if k != "author"}).status_code == 422


def test_create_book_missing_year_returns_422(client: TestClient):
    assert client.post("/books/", json={k: v for k, v in TEST_BOOK.items() if k != "year"}).status_code == 422


def test_create_book_empty_title_returns_422(client: TestClient):
    assert client.post("/books/", json={**TEST_BOOK, "title": ""}).status_code == 422


def test_create_book_empty_author_returns_422(client: TestClient):
    assert client.post("/books/", json={**TEST_BOOK, "author": ""}).status_code == 422


def test_create_book_year_too_low_returns_422(client: TestClient):
    assert client.post("/books/", json={**TEST_BOOK, "year": 999}).status_code == 422


def test_create_book_year_too_high_returns_422(client: TestClient):
    assert client.post("/books/", json={**TEST_BOOK, "year": 2101}).status_code == 422


def test_create_book_invalid_status_returns_422(client: TestClient):
    assert client.post("/books/", json={**TEST_BOOK, "status": "lost"}).status_code == 422


# ── GET /books/ ───────────────────────────────────────────────────────────────

def test_get_all_books_returns_200(client: TestClient):
    assert client.get("/books/").status_code == 200


def test_get_all_books_empty(client: TestClient):
    data = client.get("/books/").json()
    assert data["items"] == []
    assert data["next_cursor"] is None


def test_get_all_books_response_structure(client: TestClient):
    client.post("/books/", json=TEST_BOOK)
    data = client.get("/books/").json()
    assert "items" in data
    assert "next_cursor" in data
    assert "limit" in data
    assert "total" not in data


def test_get_all_books_returns_items(client: TestClient):
    client.post("/books/", json=TEST_BOOK)
    client.post("/books/", json={**TEST_BOOK, "title": "Book 2"})
    data = client.get("/books/").json()
    assert len(data["items"]) == 2


# ── Filtering ─────────────────────────────────────────────────────────────────

def test_filter_by_status_available(client: TestClient):
    client.post("/books/", json={**TEST_BOOK, "status": "available"})
    client.post("/books/", json={**TEST_BOOK, "title": "Issued", "status": "issued"})
    data = client.get("/books/?status=available").json()
    assert len(data["items"]) == 1
    assert data["items"][0]["status"] == "available"


def test_filter_by_status_issued(client: TestClient):
    client.post("/books/", json={**TEST_BOOK, "status": "issued"})
    client.post("/books/", json={**TEST_BOOK, "title": "Available", "status": "available"})
    data = client.get("/books/?status=issued").json()
    assert len(data["items"]) == 1
    assert data["items"][0]["status"] == "issued"


def test_filter_by_author_exact(client: TestClient):
    client.post("/books/", json={**TEST_BOOK, "author": "Tolkien"})
    client.post("/books/", json={**TEST_BOOK, "title": "HP", "author": "Rowling"})
    data = client.get("/books/?author=Tolkien").json()
    assert len(data["items"]) == 1
    assert data["items"][0]["author"] == "Tolkien"


def test_filter_by_author_case_insensitive(client: TestClient):
    client.post("/books/", json={**TEST_BOOK, "author": "Tolkien"})
    assert len(client.get("/books/?author=tolkien").json()["items"]) == 1


def test_filter_by_author_partial_match(client: TestClient):
    client.post("/books/", json={**TEST_BOOK, "author": "John Ronald Reuel Tolkien"})
    assert len(client.get("/books/?author=tolkien").json()["items"]) == 1


def test_filter_no_match_returns_empty(client: TestClient):
    client.post("/books/", json=TEST_BOOK)
    data = client.get("/books/?author=NoSuchAuthorXYZ").json()
    assert data["items"] == []
    assert data["next_cursor"] is None


# ── Sorting ───────────────────────────────────────────────────────────────────

def test_sort_by_title(client: TestClient):
    for title in ["Zebra", "Apple", "Mango"]:
        client.post("/books/", json={**TEST_BOOK, "title": title})
    items = client.get("/books/?sort_by=title").json()["items"]
    titles = [b["title"] for b in items]
    assert titles == sorted(titles, key=str.lower)


def test_sort_by_year(client: TestClient):
    for year in [2005, 1990, 2020]:
        client.post("/books/", json={**TEST_BOOK, "title": f"Book {year}", "year": year})
    items = client.get("/books/?sort_by=year").json()["items"]
    years = [b["year"] for b in items]
    assert years == sorted(years)


def test_sort_by_invalid_field_returns_422(client: TestClient):
    assert client.get("/books/?sort_by=invalid").status_code == 422


# ── Cursor pagination ─────────────────────────────────────────────────────────

def test_cursor_first_page_has_next_cursor(client: TestClient):
    for i in range(5):
        client.post("/books/", json={**TEST_BOOK, "title": f"Book {i:02d}"})
    data = client.get("/books/?limit=3&sort_by=title").json()
    assert len(data["items"]) == 3
    assert data["next_cursor"] is not None
    assert data["limit"] == 3


def test_cursor_last_page_next_cursor_is_none(client: TestClient):
    for i in range(3):
        client.post("/books/", json={**TEST_BOOK, "title": f"Book {i:02d}"})
    data = client.get("/books/?limit=5&sort_by=title").json()
    assert len(data["items"]) == 3
    assert data["next_cursor"] is None


def test_cursor_next_page_has_correct_items(client: TestClient):
    for i in range(5):
        client.post("/books/", json={**TEST_BOOK, "title": f"Book {i:02d}"})
    p1 = client.get("/books/?limit=2&sort_by=title").json()
    p2 = client.get(f"/books/?limit=2&sort_by=title&cursor={p1['next_cursor']}").json()
    p1_titles = {b["title"] for b in p1["items"]}
    p2_titles = {b["title"] for b in p2["items"]}
    assert p1_titles.isdisjoint(p2_titles)


def test_cursor_pages_cover_all_items_no_duplicates(client: TestClient):
    for i in range(7):
        client.post("/books/", json={**TEST_BOOK, "title": f"Book {i:02d}"})
    all_ids, cursor = [], None
    while True:
        url = "/books/?limit=3&sort_by=title"
        if cursor:
            url += f"&cursor={cursor}"
        data = client.get(url).json()
        all_ids.extend(b["id"] for b in data["items"])
        cursor = data["next_cursor"]
        if not cursor:
            break
    assert len(all_ids) == 7
    assert len(set(all_ids)) == 7


def test_cursor_sort_by_year_traversal(client: TestClient):
    for year in [2001, 2002, 2003, 2004, 2005]:
        client.post("/books/", json={**TEST_BOOK, "title": f"Book {year}", "year": year})
    p1 = client.get("/books/?limit=2&sort_by=year").json()
    assert [b["year"] for b in p1["items"]] == [2001, 2002]
    p2 = client.get(f"/books/?limit=2&sort_by=year&cursor={p1['next_cursor']}").json()
    assert [b["year"] for b in p2["items"]] == [2003, 2004]
    p3 = client.get(f"/books/?limit=2&sort_by=year&cursor={p2['next_cursor']}").json()
    assert [b["year"] for b in p3["items"]] == [2005]
    assert p3["next_cursor"] is None


def test_cursor_invalid_format_returns_422(client: TestClient):
    assert client.get("/books/?cursor=!!!INVALID!!!").status_code == 422


def test_cursor_random_string_returns_422(client: TestClient):
    assert client.get("/books/?cursor=notavalidcursor123").status_code == 422


def test_cursor_limit_zero_returns_422(client: TestClient):
    assert client.get("/books/?limit=0").status_code == 422


def test_cursor_limit_over_100_returns_422(client: TestClient):
    assert client.get("/books/?limit=101").status_code == 422


def test_cursor_empty_db_no_next_cursor(client: TestClient):
    data = client.get("/books/?limit=10").json()
    assert data["items"] == []
    assert data["next_cursor"] is None


# ── GET /books/{id} ───────────────────────────────────────────────────────────

def test_get_book_by_id_returns_200(client: TestClient):
    created = client.post("/books/", json=TEST_BOOK).json()
    assert client.get(f"/books/{created['id']}").status_code == 200


def test_get_book_by_id_returns_correct_data(client: TestClient):
    created = client.post("/books/", json=TEST_BOOK).json()
    data = client.get(f"/books/{created['id']}").json()
    assert data["id"] == created["id"]
    assert data["title"] == TEST_BOOK["title"]


def test_get_book_by_id_not_found_returns_404(client: TestClient):
    assert client.get("/books/00000000-0000-0000-0000-000000000000").status_code == 404


def test_get_book_by_id_404_has_detail(client: TestClient):
    resp = client.get("/books/00000000-0000-0000-0000-000000000000")
    assert "detail" in resp.json()


# ── DELETE /books/{id} ────────────────────────────────────────────────────────

def test_delete_existing_book_returns_204(client: TestClient):
    created = client.post("/books/", json=TEST_BOOK).json()
    assert client.delete(f"/books/{created['id']}").status_code == 204


def test_delete_removes_book(client: TestClient):
    created = client.post("/books/", json=TEST_BOOK).json()
    client.delete(f"/books/{created['id']}")
    assert client.get(f"/books/{created['id']}").status_code == 404


def test_delete_nonexistent_returns_404(client: TestClient):
    assert client.delete("/books/00000000-0000-0000-0000-000000000000").status_code == 404


def test_delete_twice_second_returns_404(client: TestClient):
    created = client.post("/books/", json=TEST_BOOK).json()
    client.delete(f"/books/{created['id']}")
    assert client.delete(f"/books/{created['id']}").status_code == 404


def test_delete_does_not_affect_other_books(client: TestClient):
    b1 = client.post("/books/", json=TEST_BOOK).json()
    b2 = client.post("/books/", json={**TEST_BOOK, "title": "Book 2"}).json()
    client.delete(f"/books/{b1['id']}")
    assert client.get(f"/books/{b2['id']}").status_code == 200

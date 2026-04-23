"""
Integration тесты CRUD-операций.
Используют отдельную in-memory SQLite БД, не затрагивая продовую.
"""
import os
import pytest

# Подменяем DATABASE_URL ДО импорта моделей
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Book, get_engine
import app.crud as crud


# ── фикстуры ─────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def fresh_db(monkeypatch):
    """Каждый тест получает чистую in-memory БД."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    def mock_get_session():
        return Session()

    monkeypatch.setattr(crud, "get_session", mock_get_session)
    yield
    Base.metadata.drop_all(engine)


# ── тесты ────────────────────────────────────────────────────────────────────

def test_add_book():
    book = crud.add_book("Мастер и Маргарита", "Булгаков", 1967, "Роман")
    assert book.id is not None
    assert book.title == "Мастер и Маргарита"
    assert book.author == "Булгаков"


def test_get_all_books_empty():
    books = crud.get_all_books()
    assert books == []


def test_get_all_books_after_add():
    crud.add_book("Идиот", "Достоевский", 1869, "Роман")
    crud.add_book("1984", "Оруэлл", 1949, "Антиутопия")
    books = crud.get_all_books()
    assert len(books) == 2


def test_update_book():
    book = crud.add_book("Старое название", "Автор", 2000, "Жанр")
    updated = crud.update_book(book.id, "Новое название", "Автор", 2001, "Жанр")
    assert updated is not None
    assert updated.title == "Новое название"
    assert updated.year == 2001


def test_update_nonexistent_book():
    result = crud.update_book(9999, "X", "X", 2000, "X")
    assert result is None


def test_delete_book():
    book = crud.add_book("Война и мир", "Толстой", 1869, "Роман")
    result = crud.delete_book(book.id)
    assert result is True
    assert crud.get_all_books() == []


def test_delete_nonexistent_book():
    result = crud.delete_book(9999)
    assert result is False


def test_get_book_by_id():
    book = crud.add_book("Преступление и наказание", "Достоевский", 1866, "Роман")
    found = crud.get_book_by_id(book.id)
    assert found is not None
    assert found.title == "Преступление и наказание"


def test_get_book_by_id_not_found():
    result = crud.get_book_by_id(9999)
    assert result is None

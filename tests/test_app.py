"""
Тесты для приложения "Библиотека книг".
Используют SQLite в памяти — никакой реальной БД не нужно!
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Импортируем модели и CRUD из нашего приложения
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import Base, Book

# ─────────────────────────────────────────────
# Фикстуры — создают временную БД для каждого теста
# ─────────────────────────────────────────────
@pytest.fixture
def engine():
    """Создаёт БД SQLite в памяти для тестов."""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(test_engine)
    yield test_engine
    Base.metadata.drop_all(test_engine)

@pytest.fixture
def session(engine):
    """Открывает сессию к тестовой БД."""
    with Session(engine) as s:
        yield s

# ─────────────────────────────────────────────
# Тесты
# ─────────────────────────────────────────────
def test_create_book(session):
    """Тест создания книги (Create)."""
    book = Book(title="Мастер и Маргарита", author="Булгаков", year=1967, rating=9.5)
    session.add(book)
    session.commit()

    result = session.query(Book).first()
    assert result is not None
    assert result.title == "Мастер и Маргарита"
    assert result.author == "Булгаков"
    assert result.year == 1967
    assert result.rating == 9.5


def test_read_books(session):
    """Тест чтения списка книг (Read)."""
    session.add_all([
        Book(title="Книга 1", author="Автор 1", year=2000, rating=7.0),
        Book(title="Книга 2", author="Автор 2", year=2010, rating=8.0),
    ])
    session.commit()

    books = session.query(Book).all()
    assert len(books) == 2


def test_update_book(session):
    """Тест обновления книги (Update)."""
    book = Book(title="Старое название", author="Автор", year=2000, rating=5.0)
    session.add(book)
    session.commit()

    # Обновляем
    book.title = "Новое название"
    book.rating = 9.0
    session.commit()

    updated = session.get(Book, book.id)
    assert updated.title == "Новое название"
    assert updated.rating == 9.0


def test_delete_book(session):
    """Тест удаления книги (Delete)."""
    book = Book(title="Удалить меня", author="Автор", year=2020, rating=3.0)
    session.add(book)
    session.commit()
    book_id = book.id

    session.delete(book)
    session.commit()

    result = session.get(Book, book_id)
    assert result is None


def test_book_fields_are_saved_correctly(session):
    """Тест что все поля сохраняются корректно."""
    book = Book(title="1984", author="Оруэлл", year=1949, rating=9.8)
    session.add(book)
    session.commit()

    found = session.query(Book).filter_by(author="Оруэлл").first()
    assert found.title == "1984"
    assert found.year == 1949

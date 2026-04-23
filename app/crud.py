from app.models import Book, get_session


def get_all_books():
    session = get_session()
    try:
        return session.query(Book).all()
    finally:
        session.close()


def add_book(title: str, author: str, year: int, genre: str) -> Book:
    session = get_session()
    try:
        book = Book(title=title, author=author, year=year, genre=genre)
        session.add(book)
        session.commit()
        session.refresh(book)
        return book
    finally:
        session.close()


def update_book(book_id: int, title: str, author: str, year: int, genre: str) -> Book | None:
    session = get_session()
    try:
        book = session.query(Book).filter(Book.id == book_id).first()
        if not book:
            return None
        book.title = title
        book.author = author
        book.year = year
        book.genre = genre
        session.commit()
        session.refresh(book)
        return book
    finally:
        session.close()


def delete_book(book_id: int) -> bool:
    session = get_session()
    try:
        book = session.query(Book).filter(Book.id == book_id).first()
        if not book:
            return False
        session.delete(book)
        session.commit()
        return True
    finally:
        session.close()


def get_book_by_id(book_id: int) -> Book | None:
    session = get_session()
    try:
        return session.query(Book).filter(Book.id == book_id).first()
    finally:
        session.close()

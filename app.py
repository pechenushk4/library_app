import os
from flask import Flask, render_template_string, request, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, Session

app = Flask(__name__)

class Base(DeclarativeBase):
    pass

class Book(Base):
    __tablename__ = "books"
    id     = Column(Integer, primary_key=True, autoincrement=True)
    title  = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    year   = Column(Integer)
    rating = Column(Float)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///library.db")
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>📚 Библиотека книг</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, sans-serif; background: #f5f5f5; padding: 30px; }
    h1 { text-align: center; margin-bottom: 24px; color: #333; }
    .form-box { background: white; padding: 20px; border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 24px; }
    .form-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; }
    .form-group { display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 150px; }
    label { font-size: 13px; color: #666; }
    input { padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
    .btn { padding: 9px 18px; border: none; border-radius: 6px; cursor: pointer;
           font-size: 14px; font-weight: bold; white-space: nowrap; }
    .btn-green  { background: #4CAF50; color: white; }
    .btn-blue   { background: #2196F3; color: white; }
    .btn-red    { background: #f44336; color: white; }
    .btn:hover  { opacity: 0.85; }
    table { width: 100%; border-collapse: collapse; background: white;
            border-radius: 10px; overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    th { background: #2196F3; color: white; padding: 12px 16px; text-align: left; }
    td { padding: 11px 16px; border-bottom: 1px solid #eee; }
    tr:last-child td { border-bottom: none; }
    tr:hover td { background: #f0f7ff; }
    .actions { display: flex; gap: 8px; }
    .msg { background: #e8f5e9; color: #2e7d32; padding: 10px 16px;
           border-radius: 6px; margin-bottom: 16px; }
  </style>
</head>
<body>
  <h1>📚 Библиотека книг</h1>

  {% if message %}<div class="msg">{{ message }}</div>{% endif %}

  <!-- Форма добавления -->
  <div class="form-box">
    <form method="POST" action="/add">
      <div class="form-row">
        <div class="form-group">
          <label>Название</label>
          <input name="title" placeholder="Название книги" required>
        </div>
        <div class="form-group">
          <label>Автор</label>
          <input name="author" placeholder="Автор" required>
        </div>
        <div class="form-group" style="max-width:100px">
          <label>Год</label>
          <input name="year" type="number" placeholder="2024" required>
        </div>
        <div class="form-group" style="max-width:120px">
          <label>Рейтинг (0-10)</label>
          <input name="rating" type="number" step="0.1" placeholder="8.5" required>
        </div>
        <button class="btn btn-green" type="submit">➕ Добавить</button>
      </div>
    </form>
  </div>

  <!-- Таблица книг -->
  <table>
    <thead>
      <tr>
        <th>ID</th><th>Название</th><th>Автор</th><th>Год</th><th>Рейтинг</th><th>Действия</th>
      </tr>
    </thead>
    <tbody>
      {% for book in books %}
      <tr>
        <td>{{ book.id }}</td>
        <td>{{ book.title }}</td>
        <td>{{ book.author }}</td>
        <td>{{ book.year }}</td>
        <td>{{ book.rating }}</td>
        <td class="actions">
          <form method="POST" action="/delete/{{ book.id }}">
            <button class="btn btn-red" type="submit">🗑 Удалить</button>
          </form>
          <a href="/edit/{{ book.id }}"><button class="btn btn-blue" type="button">✏️ Изменить</button></a>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""

EDIT_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Редактировать книгу</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, sans-serif; background: #f5f5f5;
           display: flex; justify-content: center; align-items: center; height: 100vh; }
    .box { background: white; padding: 30px; border-radius: 10px;
           box-shadow: 0 2px 8px rgba(0,0,0,0.1); width: 400px; }
    h2 { margin-bottom: 20px; color: #333; }
    .form-group { display: flex; flex-direction: column; gap: 4px; margin-bottom: 14px; }
    label { font-size: 13px; color: #666; }
    input { padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
    .btns { display: flex; gap: 10px; margin-top: 6px; }
    .btn { padding: 9px 18px; border: none; border-radius: 6px; cursor: pointer;
           font-size: 14px; font-weight: bold; flex: 1; }
    .btn-blue { background: #2196F3; color: white; }
    .btn-gray { background: #9E9E9E; color: white; text-decoration: none;
                text-align: center; line-height: 38px; }
  </style>
</head>
<body>
  <div class="box">
    <h2>✏️ Редактировать книгу</h2>
    <form method="POST" action="/edit/{{ book.id }}">
      <div class="form-group">
        <label>Название</label>
        <input name="title" value="{{ book.title }}" required>
      </div>
      <div class="form-group">
        <label>Автор</label>
        <input name="author" value="{{ book.author }}" required>
      </div>
      <div class="form-group">
        <label>Год</label>
        <input name="year" type="number" value="{{ book.year }}" required>
      </div>
      <div class="form-group">
        <label>Рейтинг (0-10)</label>
        <input name="rating" type="number" step="0.1" value="{{ book.rating }}" required>
      </div>
      <div class="btns">
        <button class="btn btn-blue" type="submit">💾 Сохранить</button>
        <a class="btn btn-gray" href="/">Отмена</a>
      </div>
    </form>
  </div>
</body>
</html>
"""

# ── Маршруты (routes) ──────────────────────────
@app.route("/")
def index():
    with Session(engine) as session:
        books = session.query(Book).all()
        return render_template_string(HTML, books=books, message=request.args.get("msg"))

@app.route("/add", methods=["POST"])
def add():
    with Session(engine) as session:
        book = Book(
            title=request.form["title"],
            author=request.form["author"],
            year=int(request.form["year"]),
            rating=float(request.form["rating"])
        )
        session.add(book)
        session.commit()
    return redirect(url_for("index", msg="Книга добавлена!"))

@app.route("/delete/<int:book_id>", methods=["POST"])
def delete(book_id):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if book:
            session.delete(book)
            session.commit()
    return redirect(url_for("index", msg="Книга удалена!"))

@app.route("/edit/<int:book_id>")
def edit(book_id):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        return render_template_string(EDIT_HTML, book=book)

@app.route("/edit/<int:book_id>", methods=["POST"])
def update(book_id):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if book:
            book.title  = request.form["title"]
            book.author = request.form["author"]
            book.year   = int(request.form["year"])
            book.rating = float(request.form["rating"])
            session.commit()
    return redirect(url_for("index", msg="Книга обновлена!"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
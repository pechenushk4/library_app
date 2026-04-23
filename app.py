import os
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, Session

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

def get_all_books():
    with Session(engine) as session:
        return session.query(Book).all()

def add_book(title, author, year, rating):
    with Session(engine) as session:
        book = Book(title=title, author=author, year=int(year), rating=float(rating))
        session.add(book)
        session.commit()

def update_book(book_id, title, author, year, rating):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if book:
            book.title  = title
            book.author = author
            book.year   = int(year)
            book.rating = float(rating)
            session.commit()

def delete_book(book_id):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if book:
            session.delete(book)
            session.commit()

if HAS_GUI:
    class LibraryApp(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("📚 Библиотека книг")
            self.geometry("800x500")
            self.resizable(True, True)
            self.configure(bg="#f0f0f0")
            self._selected_id = None
            self._build_ui()
            self._refresh_table()

        def _build_ui(self):
            form_frame = tk.LabelFrame(self, text="Данные книги", bg="#f0f0f0", padx=10, pady=8)
            form_frame.pack(fill="x", padx=10, pady=(10, 0))
            labels = ["Название", "Автор", "Год", "Рейтинг (0-10)"]
            self._entries = {}
            for col, label in enumerate(labels):
                tk.Label(form_frame, text=label, bg="#f0f0f0").grid(row=0, column=col*2, sticky="w", padx=(5,2))
                entry = tk.Entry(form_frame, width=20)
                entry.grid(row=0, column=col*2+1, padx=(0,10))
                self._entries[label] = entry
            btn_frame = tk.Frame(self, bg="#f0f0f0")
            btn_frame.pack(fill="x", padx=10, pady=6)
            btn_cfg = [
                ("➕ Добавить",        "#4CAF50", self._add),
                ("✏️ Обновить",        "#2196F3", self._update),
                ("🗑️ Удалить",         "#f44336", self._delete),
                ("🔄 Обновить список", "#9E9E9E", self._refresh_table),
            ]
            for text, color, cmd in btn_cfg:
                tk.Button(btn_frame, text=text, bg=color, fg="white",
                          relief="flat", padx=10, pady=4,
                          command=cmd).pack(side="left", padx=4)
            table_frame = tk.Frame(self)
            table_frame.pack(fill="both", expand=True, padx=10, pady=(0,10))
            cols = ("id", "title", "author", "year", "rating")
            self._tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=16)
            headers = {"id":"ID","title":"Название","author":"Автор","year":"Год","rating":"Рейтинг"}
            widths  = {"id":40,"title":280,"author":180,"year":60,"rating":80}
            for c in cols:
                self._tree.heading(c, text=headers[c])
                self._tree.column(c, width=widths[c], anchor="center" if c in ("id","year","rating") else "w")
            scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self._tree.yview)
            self._tree.configure(yscroll=scroll.set)
            self._tree.pack(side="left", fill="both", expand=True)
            scroll.pack(side="right", fill="y")
            self._tree.bind("<<TreeviewSelect>>", self._on_select)

        def _refresh_table(self):
            for row in self._tree.get_children():
                self._tree.delete(row)
            for book in get_all_books():
                self._tree.insert("", "end", values=(book.id, book.title, book.author, book.year, book.rating))

        def _clear_entries(self):
            for e in self._entries.values():
                e.delete(0, "end")
            self._selected_id = None

        def _get_fields(self):
            title  = self._entries["Название"].get().strip()
            author = self._entries["Автор"].get().strip()
            year   = self._entries["Год"].get().strip()
            rating = self._entries["Рейтинг (0-10)"].get().strip()
            if not all([title, author, year, rating]):
                messagebox.showwarning("Ошибка", "Заполните все поля!")
                return None
            try:
                int(year); float(rating)
            except ValueError:
                messagebox.showwarning("Ошибка", "Год — целое число, рейтинг — число (например 8.5)")
                return None
            return title, author, year, rating

        def _on_select(self, _event):
            selected = self._tree.focus()
            if not selected:
                return
            values = self._tree.item(selected)["values"]
            self._selected_id = values[0]
            fields_order = ["Название", "Автор", "Год", "Рейтинг (0-10)"]
            for i, key in enumerate(fields_order):
                self._entries[key].delete(0, "end")
                self._entries[key].insert(0, values[i+1])

        def _add(self):
            fields = self._get_fields()
            if not fields:
                return
            add_book(*fields)
            self._clear_entries()
            self._refresh_table()

        def _update(self):
            if not self._selected_id:
                messagebox.showwarning("Ошибка", "Выберите книгу в таблице!")
                return
            fields = self._get_fields()
            if not fields:
                return
            update_book(self._selected_id, *fields)
            self._clear_entries()
            self._refresh_table()

        def _delete(self):
            if not self._selected_id:
                messagebox.showwarning("Ошибка", "Выберите книгу в таблице!")
                return
            if messagebox.askyesno("Подтверждение", "Удалить выбранную книгу?"):
                delete_book(self._selected_id)
                self._clear_entries()
                self._refresh_table()

if __name__ == "__main__":
    if HAS_GUI:
        app = LibraryApp()
        app.mainloop()
    else:
        print("GUI недоступен. Проверка подключения к БД...")
        print("Таблицы созданы успешно!")
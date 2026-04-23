import tkinter as tk
from tkinter import ttk, messagebox
from app.crud import get_all_books, add_book, update_book, delete_book


class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Библиотека книг")
        self.geometry("820x520")
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")

        self._build_table()
        self._build_form()
        self._build_buttons()
        self._load_books()

    # ── таблица ──────────────────────────────────────────────────────────────

    def _build_table(self):
        frame = tk.Frame(self, bg="#f0f0f0")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        cols = ("ID", "Название", "Автор", "Год", "Жанр")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=14)

        widths = (40, 260, 200, 60, 120)
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor=tk.CENTER if w < 100 else tk.W)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    # ── форма ─────────────────────────────────────────────────────────────────

    def _build_form(self):
        form = tk.LabelFrame(self, text="Данные книги", bg="#f0f0f0", padx=8, pady=6)
        form.pack(fill=tk.X, padx=10, pady=(0, 4))

        labels = ["Название", "Автор", "Год", "Жанр"]
        self.entries: dict[str, tk.Entry] = {}

        for i, label in enumerate(labels):
            tk.Label(form, text=label + ":", bg="#f0f0f0", width=9,
                     anchor=tk.E).grid(row=0, column=i * 2, sticky=tk.E, padx=(6, 2))
            entry = tk.Entry(form, width=20 if label in ("Название", "Автор") else 8)
            entry.grid(row=0, column=i * 2 + 1, padx=(0, 10))
            self.entries[label] = entry

        self.selected_id: int | None = None

    # ── кнопки ────────────────────────────────────────────────────────────────

    def _build_buttons(self):
        btn_frame = tk.Frame(self, bg="#f0f0f0")
        btn_frame.pack(pady=(0, 8))

        actions = [
            ("Добавить",   "#4CAF50", self._add),
            ("Обновить",   "#2196F3", self._update),
            ("Удалить",    "#f44336", self._delete),
            ("Сбросить",   "#9E9E9E", self._clear_form),
        ]
        for text, color, cmd in actions:
            tk.Button(
                btn_frame, text=text, bg=color, fg="white",
                width=12, relief=tk.FLAT, command=cmd
            ).pack(side=tk.LEFT, padx=5)

    # ── загрузка данных ───────────────────────────────────────────────────────

    def _load_books(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for book in get_all_books():
            self.tree.insert("", tk.END, values=(
                book.id, book.title, book.author, book.year, book.genre
            ))

    # ── события ───────────────────────────────────────────────────────────────

    def _on_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])["values"]
        self.selected_id = values[0]
        keys = ["Название", "Автор", "Год", "Жанр"]
        for key, val in zip(keys, values[1:]):
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, val)

    def _get_form_data(self):
        title  = self.entries["Название"].get().strip()
        author = self.entries["Автор"].get().strip()
        year   = self.entries["Год"].get().strip()
        genre  = self.entries["Жанр"].get().strip()
        if not all([title, author, year, genre]):
            messagebox.showwarning("Ошибка", "Заполните все поля")
            return None
        try:
            year = int(year)
        except ValueError:
            messagebox.showwarning("Ошибка", "Год должен быть числом")
            return None
        return title, author, year, genre

    def _add(self):
        data = self._get_form_data()
        if not data:
            return
        add_book(*data)
        self._load_books()
        self._clear_form()

    def _update(self):
        if not self.selected_id:
            messagebox.showwarning("Ошибка", "Выберите книгу в таблице")
            return
        data = self._get_form_data()
        if not data:
            return
        update_book(self.selected_id, *data)
        self._load_books()
        self._clear_form()

    def _delete(self):
        if not self.selected_id:
            messagebox.showwarning("Ошибка", "Выберите книгу в таблице")
            return
        if messagebox.askyesno("Подтверждение", "Удалить выбранную книгу?"):
            delete_book(self.selected_id)
            self._load_books()
            self._clear_form()

    def _clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())


def main():
    app = LibraryApp()
    app.mainloop()


if __name__ == "__main__":
    main()

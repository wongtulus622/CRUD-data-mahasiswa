import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

class Database:
    def __init__(self, db_name="mahasiswa.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS mahasiswa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nim TEXT NOT NULL UNIQUE,
                nama TEXT NOT NULL,
                jurusan TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def fetch_all(self):
        return self.conn.execute("SELECT * FROM mahasiswa").fetchall()

    def insert(self, nim, nama, jurusan):
        try:
            self.conn.execute("INSERT INTO mahasiswa (nim, nama, jurusan) VALUES (?, ?, ?)", (nim, nama, jurusan))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def update(self, id_mhs, nim, nama, jurusan):
        self.conn.execute("UPDATE mahasiswa SET nim=?, nama=?, jurusan=? WHERE id=?", (nim, nama, jurusan, id_mhs))
        self.conn.commit()

    def delete(self, id_mhs):
        self.conn.execute("DELETE FROM mahasiswa WHERE id=?", (id_mhs,))
        self.conn.commit()


class MahasiswaApp:
    def __init__(self, root):
        self.db = Database()
        self.root = root
        self.root.title("Data Mahasiswa")
        self.root.geometry("360x600")  # Ukuran layar kecil
        self.selected_id = None

        self.setup_ui()
        self.populate_treeview()

    def setup_ui(self):
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=False)

        def add_label_entry(text):
            tk.Label(frame, text=text).pack(anchor="w", pady=(5, 0))
            entry = tk.Entry(frame, width=30)
            entry.pack(fill=tk.X, pady=2)
            return entry

        self.entry_nim = add_label_entry("NIM")
        self.entry_nama = add_label_entry("Nama")
        self.entry_jurusan = add_label_entry("Jurusan")

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Tambah", width=8, command=self.add_data).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Update", width=8, command=self.update_data).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Hapus", width=8, command=self.delete_data).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Reset", width=8, command=self.reset_form).pack(side=tk.LEFT, padx=2)

        # Treeview frame with scrollbar
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(tree_frame, columns=("id", "nim", "nama", "jurusan"), show="headings", height=10)
        for col in ("id", "nim", "nama", "jurusan"):
            self.tree.heading(col, text=col.title())
            self.tree.column(col, anchor="center", width=80)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.db.fetch_all():
            self.tree.insert("", "end", values=row)

    def get_entry_values(self):
        return self.entry_nim.get(), self.entry_nama.get(), self.entry_jurusan.get()

    def add_data(self):
        nim, nama, jurusan = self.get_entry_values()
        if not all([nim, nama, jurusan]):
            messagebox.showwarning("Validasi", "Semua field wajib diisi.")
            return
        if self.db.insert(nim, nama, jurusan):
            self.populate_treeview()
            self.reset_form()
        else:
            messagebox.showerror("Error", "NIM sudah terdaftar.")

    def update_data(self):
        if self.selected_id is None:
            messagebox.showwarning("Pilih Data", "Silakan pilih data yang ingin diupdate.")
            return
        nim, nama, jurusan = self.get_entry_values()
        if not all([nim, nama, jurusan]):
            messagebox.showwarning("Validasi", "Semua field wajib diisi.")
            return
        self.db.update(self.selected_id, nim, nama, jurusan)
        self.populate_treeview()
        self.reset_form()

    def delete_data(self):
        if self.selected_id is None:
            messagebox.showwarning("Pilih Data", "Silakan pilih data yang ingin dihapus.")
            return
        confirm = messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus data ini?")
        if confirm:
            self.db.delete(self.selected_id)
            self.populate_treeview()
            self.reset_form()

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])["values"]
            self.selected_id = values[0]
            self.entry_nim.delete(0, tk.END)
            self.entry_nim.insert(0, values[1])
            self.entry_nama.delete(0, tk.END)
            self.entry_nama.insert(0, values[2])
            self.entry_jurusan.delete(0, tk.END)
            self.entry_jurusan.insert(0, values[3])

    def reset_form(self):
        self.entry_nim.delete(0, tk.END)
        self.entry_nama.delete(0, tk.END)
        self.entry_jurusan.delete(0, tk.END)
        self.selected_id = None


if __name__ == "__main__":
    root = tk.Tk()
    app = MahasiswaApp(root)
    root.mainloop()

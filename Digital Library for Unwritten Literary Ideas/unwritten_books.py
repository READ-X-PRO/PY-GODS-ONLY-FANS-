import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os

class DigitalLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Library of Unwritten Books")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Setup database
        self.db_path = "unwritten_books.db"
        self.init_db()
        
        # Create GUI
        self.create_widgets()
        self.load_books()
        
    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS books (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        author TEXT,
                        summary TEXT NOT NULL,
                        conceived_date DATE,
                        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'Idea'
                     )''')
            conn.commit()

    def create_widgets(self):
        # Main frames
        self.search_frame = ttk.Frame(self.root, padding=10)
        self.search_frame.pack(fill=tk.X)
        
        self.list_frame = ttk.Frame(self.root, padding=10)
        self.list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.detail_frame = ttk.LabelFrame(self.root, text="Book Details", padding=10)
        self.detail_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Search area
        ttk.Label(self.search_frame, text="Search:").grid(row=0, column=0, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=0, column=1, padx=5)
        self.search_entry.bind("<KeyRelease>", self.load_books)
        
        # Status filter
        ttk.Label(self.search_frame, text="Status:").grid(row=0, column=2, padx=5)
        self.status_var = tk.StringVar(value="All")
        statuses = ["All", "Idea", "Outline", "Partial Draft", "Abandoned"]
        self.status_combo = ttk.Combobox(self.search_frame, textvariable=self.status_var, 
                                        values=statuses, state="readonly", width=15)
        self.status_combo.grid(row=0, column=3, padx=5)
        self.status_combo.bind("<<ComboboxSelected>>", self.load_books)
        
        # Add new button
        self.add_btn = ttk.Button(self.search_frame, text="Add New Unwritten Book", 
                                command=self.add_book)
        self.add_btn.grid(row=0, column=4, padx=20)
        
        # Book list
        self.tree = ttk.Treeview(self.list_frame, columns=("author", "status", "conceived"), 
                                show="headings", selectmode="browse")
        self.tree.heading("title", text="Title")
        self.tree.heading("author", text="Author")
        self.tree.heading("status", text="Status")
        self.tree.heading("conceived", text="Conceived Date")
        self.tree.column("title", width=300)
        self.tree.column("author", width=150)
        self.tree.column("status", width=100)
        self.tree.column("conceived", width=120)
        
        vsb = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.list_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        self.tree.bind("<<TreeviewSelect>>", self.show_book_details)
        
        # Detail frame
        ttk.Label(self.detail_frame, text="Title:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.title_var = tk.StringVar()
        ttk.Entry(self.detail_frame, textvariable=self.title_var, width=60).grid(row=0, column=1, columnspan=3, sticky="ew", padx=5, pady=2)
        
        ttk.Label(self.detail_frame, text="Author:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.author_var = tk.StringVar()
        ttk.Entry(self.detail_frame, textvariable=self.author_var).grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(self.detail_frame, text="Conceived:").grid(row=1, column=2, sticky="e", padx=5, pady=2)
        self.date_var = tk.StringVar()
        ttk.Entry(self.detail_frame, textvariable=self.date_var, width=12).grid(row=1, column=3, sticky="w", padx=5, pady=2)
        
        ttk.Label(self.detail_frame, text="Status:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.status_detail_var = tk.StringVar()
        status_combo = ttk.Combobox(self.detail_frame, textvariable=self.status_detail_var, 
                                   values=["Idea", "Outline", "Partial Draft", "Abandoned"], 
                                   state="readonly", width=15)
        status_combo.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        self.status_detail_var.set("Idea")
        
        ttk.Label(self.detail_frame, text="Summary:").grid(row=3, column=0, sticky="ne", padx=5, pady=2)
        self.summary_text = tk.Text(self.detail_frame, width=60, height=8)
        self.summary_text.grid(row=3, column=1, columnspan=3, sticky="nsew", padx=5, pady=2)
        
        # Action buttons
        button_frame = ttk.Frame(self.root, padding=10)
        button_frame.pack(fill=tk.X)
        
        self.save_btn = ttk.Button(button_frame, text="Save", command=self.save_book)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(button_frame, text="Delete", command=self.delete_book)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_form)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        self.list_frame.grid_rowconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)
        
        # Set current book ID
        self.current_book_id = None
        
    def load_books(self, event=None):
        search_term = f"%{self.search_var.get()}%"
        status_filter = self.status_var.get()
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            if status_filter == "All":
                c.execute("""SELECT id, title, author, status, conceived_date 
                          FROM books 
                          WHERE title LIKE ? OR author LIKE ? OR summary LIKE ?
                          ORDER BY added_date DESC""", 
                          (search_term, search_term, search_term))
            else:
                c.execute("""SELECT id, title, author, status, conceived_date 
                          FROM books 
                          WHERE (title LIKE ? OR author LIKE ? OR summary LIKE ?) 
                          AND status = ?
                          ORDER BY added_date DESC""", 
                          (search_term, search_term, search_term, status_filter))
            
            books = c.fetchall()
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Populate tree
        for book in books:
            conceived_date = book[4] if book[4] else "Unknown"
            self.tree.insert("", "end", iid=book[0], values=(
                book[1], 
                book[2] if book[2] else "Anonymous", 
                book[3],
                conceived_date
            ))
    
    def show_book_details(self, event):
        selected = self.tree.selection()
        if not selected:
            return
            
        book_id = selected[0]
        self.current_book_id = book_id
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT title, author, summary, conceived_date, status FROM books WHERE id=?", (book_id,))
            book = c.fetchone()
        
        if book:
            self.title_var.set(book[0])
            self.author_var.set(book[1] if book[1] else "")
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(tk.END, book[2])
            self.date_var.set(book[3] if book[3] else "")
            self.status_detail_var.set(book[4] if book[4] else "Idea")
    
    def add_book(self):
        self.clear_form()
        self.title_var.set("New Unwritten Book")
        self.status_detail_var.set("Idea")
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.summary_text.insert(tk.END, "Detailed summary of this unwritten book...")
        self.current_book_id = None
    
    def save_book(self):
        title = self.title_var.get().strip()
        author = self.author_var.get().strip()
        summary = self.summary_text.get(1.0, tk.END).strip()
        conceived_date = self.date_var.get().strip()
        status = self.status_detail_var.get()
        
        if not title:
            messagebox.showerror("Error", "Title is required!")
            return
            
        if not summary:
            messagebox.showerror("Error", "Summary is required!")
            return
            
        if conceived_date:
            try:
                datetime.strptime(conceived_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Date must be in YYYY-MM-DD format")
                return
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            if self.current_book_id:
                # Update existing book
                c.execute("""UPDATE books 
                          SET title=?, author=?, summary=?, conceived_date=?, status=?
                          WHERE id=?""", 
                          (title, author or None, summary, conceived_date or None, status, self.current_book_id))
            else:
                # Add new book
                c.execute("""INSERT INTO books 
                          (title, author, summary, conceived_date, status) 
                          VALUES (?, ?, ?, ?, ?)""", 
                          (title, author or None, summary, conceived_date or None, status))
            
            conn.commit()
        
        self.load_books()
        self.clear_form()
        messagebox.showinfo("Success", "Book saved successfully!")
    
    def delete_book(self):
        if not self.current_book_id:
            return
            
        if messagebox.askyesno("Confirm", "Delete this unwritten book?"):
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("DELETE FROM books WHERE id=?", (self.current_book_id,))
                conn.commit()
            
            self.load_books()
            self.clear_form()
    
    def clear_form(self):
        self.current_book_id = None
        self.title_var.set("")
        self.author_var.set("")
        self.summary_text.delete(1.0, tk.END)
        self.date_var.set("")
        self.status_detail_var.set("Idea")

if __name__ == "__main__":
    root = tk.Tk()
    app = DigitalLibraryApp(root)
    root.mainloop()
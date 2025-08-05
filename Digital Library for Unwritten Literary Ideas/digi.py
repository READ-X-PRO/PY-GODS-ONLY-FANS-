import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import sqlite3
from datetime import datetime, timedelta
import random
import os
import sys
import textwrap
import json

class DigitalLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Library of Unwritten Books")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Setup databases
        self.db_path = "unwritten_books.db"
        self.content_path = "library_content.json"
        self.init_db()
        self.load_content_file()
        
        # Create GUI
        self.create_widgets()
        self.load_books()
        self.load_written_books()
        
        # AI password
        self.ai_password = "whisper"
        
        # Current book IDs for editing
        self.current_unwritten_id = None
        self.current_written_id = None
        
    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            # Unwritten books table
            c.execute('''CREATE TABLE IF NOT EXISTS unwritten_books (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        author TEXT,
                        summary TEXT NOT NULL,
                        conceived_date DATE,
                        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'Idea',
                        genre TEXT
                     )''')
            
            # Written/To-be-written books table
            c.execute('''CREATE TABLE IF NOT EXISTS written_books (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        author TEXT,
                        summary TEXT NOT NULL,
                        target_date DATE,
                        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'Planned',
                        genre TEXT,
                        progress INTEGER DEFAULT 0
                     )''')
            conn.commit()
        
        # Add sample books if database is empty
        self.add_sample_books()

    def load_content_file(self):
        """Load or create the content file with written/to-be-written stories"""
        if not os.path.exists(self.content_path):
            # Create default content
            default_content = {
                "written_stories": [
                    {
                        "title": "Echoes of the Forgotten",
                        "author": "Eleanor Vance",
                        "summary": "A completed novel about a historian who discovers a secret society preserving lost knowledge.",
                        "status": "Completed",
                        "genre": "Historical Fiction",
                        "progress": 100
                    }
                ],
                "to_be_written": [
                    {
                        "title": "The Clockwork Oracle",
                        "author": "Julian Mechanicus",
                        "summary": "Steampunk adventure about an automaton that gains the ability to see possible futures.",
                        "status": "Outline",
                        "genre": "Steampunk",
                        "progress": 30,
                        "target_date": "2024-12-31"
                    }
                ],
                "poems": [
                    {
                        "title": "Whispers of Dawn",
                        "author": "M. L. Blackwood",
                        "content": "The morning light creeps slow,\nPainting shadows on the snow,\nWhispering secrets only dawn can know."
                    }
                ]
            }
            with open(self.content_path, 'w') as f:
                json.dump(default_content, f, indent=2)
        
        with open(self.content_path, 'r') as f:
            self.library_content = json.load(f)

    def add_sample_books(self):
        """Add sample books to the database"""
        # Unwritten books
        unwritten_books = [
            ("The Last Library", "Eleanor Vance",
             "In a world where physical books are banned, a librarian preserves the last collection of printed books in a secret underground archive. The story follows her struggle to protect knowledge from the digital-only regime.",
             "2020-03-15", "Abandoned", "Dystopian"),
            
            ("Chronicles of the Void", "Arthur Quill",
             "An epic space opera about a crew stranded in an empty sector of space, discovering an ancient civilization that chose to erase all records of its existence. Explores themes of cultural memory and intentional forgetting.",
             "2018-11-22", "Outline", "Sci-Fi"),
            
            ("Whispers of the Forgotten", "M. L. Blackwood",
             "A psychological thriller where a historian begins hearing voices from historical manuscripts. As she deciphers the messages, she realizes they're warnings about our own future.",
             "2022-05-07", "Idea", "Thriller"),
            
            ("The Atlas of Lost Places", "Julian Cartographer",
             "A beautifully illustrated guide to places that never existed - mythical cities, fictional countries, and imagined landscapes from literature that never was.",
             "2019-08-30", "Partial Draft", "Fantasy"),
            
            ("Echoes from the Unwritten", "Anonymous",
             "A collection of philosophical essays examining why great works remain unwritten - from authorial self-doubt to cultural suppression and the ephemeral nature of inspiration.",
             "2021-01-14", "Idea", "Philosophy"),
            
            ("The Glass Cathedral", "Isabella Stainedglass",
             "In a city where emotions are physically manifested as colored glass structures, a young architect discovers she can manipulate feelings through her designs. But her power attracts dangerous attention.",
             "2020-09-12", "Partial Draft", "Urban Fantasy"),
            
            ("Songs of the Silent Planet", "Orion Starweaver",
             "An interstellar linguist discovers that a planet thought to be devoid of life actually communicates through complex geological symphonies that only manifest once every millennium.",
             "2023-02-28", "Outline", "Science Fiction"),
            
            ("The Memoir of a Ghost", "Casper Spectralis",
             "An autobiography written from the perspective of a ghost who has witnessed centuries of human history but remains unable to interact with the living world.",
             "2021-07-15", "Abandoned", "Supernatural")
        ]
        
        # Written/To-be-written books
        written_books = [
            ("The Clockwork Oracle", "Julian Mechanicus",
             "Steampunk adventure about an automaton that gains the ability to see possible futures and the inventor who tries to protect it from those who would misuse its power.",
             "2024-12-31", "Outline", "Steampunk", 30),
            
            ("Beneath the Willow", "Eleanor Vance",
             "A coming-of-age story set in post-war England, following three generations of women who find solace and secrets in their family garden.",
             "2023-10-15", "First Draft", "Historical Fiction", 75),
            
            ("Neon Dreams", "Synthia Byte",
             "Cyberpunk thriller about a hacker who discovers a conspiracy to control human dreams for corporate profit.",
             "2024-03-31", "Research", "Cyberpunk", 15)
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            # Check if books already exist
            c.execute("SELECT COUNT(*) FROM unwritten_books")
            count = c.fetchone()[0]
            if count == 0:
                c.executemany("""INSERT INTO unwritten_books 
                              (title, author, summary, conceived_date, status, genre) 
                              VALUES (?, ?, ?, ?, ?, ?)""", unwritten_books)
            
            c.execute("SELECT COUNT(*) FROM written_books")
            count = c.fetchone()[0]
            if count == 0:
                c.executemany("""INSERT INTO written_books 
                              (title, author, summary, target_date, status, genre, progress) 
                              VALUES (?, ?, ?, ?, ?, ?, ?)""", written_books)
            
            conn.commit()

    def create_widgets(self):
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create frames for each tab
        self.unwritten_frame = ttk.Frame(self.notebook)
        self.written_frame = ttk.Frame(self.notebook)
        self.ai_frame = ttk.Frame(self.notebook)
        self.help_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.unwritten_frame, text="Unwritten Books")
        self.notebook.add(self.written_frame, text="Written & In-Progress")
        self.notebook.add(self.ai_frame, text="AI Generator")
        self.notebook.add(self.help_frame, text="Help & Export")
        
        # Build each tab
        self.create_unwritten_tab()
        self.create_written_tab()
        self.create_ai_tab()
        self.create_help_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready | Digital Library of Unwritten Books")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_unwritten_tab(self):
        """Create the Unwritten Books tab"""
        # Search frame
        search_frame = ttk.LabelFrame(self.unwritten_frame, text="Search & Filter", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=5, sticky="e")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, padx=5, sticky="w")
        search_entry.bind("<KeyRelease>", self.load_books)
        
        ttk.Label(search_frame, text="Status:").grid(row=0, column=2, padx=(20,5), sticky="e")
        self.status_var_filter = tk.StringVar(value="All")
        statuses = ["All", "Idea", "Outline", "Partial Draft", "Abandoned"]
        self.status_combo = ttk.Combobox(search_frame, textvariable=self.status_var_filter, 
                                        values=statuses, state="readonly", width=15)
        self.status_combo.grid(row=0, column=3, padx=5, sticky="w")
        self.status_combo.bind("<<ComboboxSelected>>", self.load_books)
        
        ttk.Label(search_frame, text="Genre:").grid(row=0, column=4, padx=(20,5), sticky="e")
        self.genre_var_filter = tk.StringVar(value="All")
        genres = ["All", "Fantasy", "Sci-Fi", "Thriller", "Mystery", "Romance", "Historical", "Philosophy", "Dystopian", "Urban Fantasy", "Science Fiction", "Supernatural"]
        self.genre_combo = ttk.Combobox(search_frame, textvariable=self.genre_var_filter, 
                                       values=genres, state="readonly", width=15)
        self.genre_combo.grid(row=0, column=5, padx=5, sticky="w")
        self.genre_combo.bind("<<ComboboxSelected>>", self.load_books)
        
        # Add new button
        self.add_btn = ttk.Button(search_frame, text="Add New Unwritten Book", 
                                command=self.add_unwritten_book)
        self.add_btn.grid(row=0, column=6, padx=20)
        
        # Book list
        list_frame = ttk.LabelFrame(self.unwritten_frame, text="Unwritten Books Collection", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("id", "title", "author", "status", "genre", "conceived")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        
        # Configure columns
        self.tree.heading("id", text="ID", anchor=tk.W)
        self.tree.heading("title", text="Title", anchor=tk.W)
        self.tree.heading("author", text="Author", anchor=tk.W)
        self.tree.heading("status", text="Status", anchor=tk.W)
        self.tree.heading("genre", text="Genre", anchor=tk.W)
        self.tree.heading("conceived", text="Conceived", anchor=tk.W)
        
        self.tree.column("id", width=40, stretch=tk.NO)
        self.tree.column("title", width=250, anchor=tk.W)
        self.tree.column("author", width=150, anchor=tk.W)
        self.tree.column("status", width=120, anchor=tk.W)
        self.tree.column("genre", width=120, anchor=tk.W)
        self.tree.column("conceived", width=100, anchor=tk.W)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        self.tree.bind("<<TreeviewSelect>>", self.show_unwritten_details)
        self.tree.bind("<Double-1>", self.focus_on_summary)
        
        # Configure grid weights
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Detail frame
        detail_frame = ttk.LabelFrame(self.unwritten_frame, text="Book Details", padding=10)
        detail_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Detail form
        form_frame = ttk.Frame(detail_frame)
        form_frame.pack(fill=tk.X)
        
        # Row 0
        ttk.Label(form_frame, text="Title:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(form_frame, textvariable=self.title_var, width=40)
        title_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Row 1
        ttk.Label(form_frame, text="Author:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.author_var = tk.StringVar()
        author_entry = ttk.Entry(form_frame, textvariable=self.author_var)
        author_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(form_frame, text="Conceived:").grid(row=1, column=2, sticky="e", padx=5, pady=5)
        self.date_var = tk.StringVar()
        date_entry = ttk.Entry(form_frame, textvariable=self.date_var, width=12)
        date_entry.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        
        # Row 2
        ttk.Label(form_frame, text="Status:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.status_detail_var = tk.StringVar()
        status_combo = ttk.Combobox(form_frame, textvariable=self.status_detail_var, 
                                   values=["Idea", "Outline", "Partial Draft", "Abandoned"], 
                                   state="readonly", width=15)
        status_combo.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.status_detail_var.set("Idea")
        
        ttk.Label(form_frame, text="Genre:").grid(row=2, column=2, sticky="e", padx=5, pady=5)
        self.genre_detail_var = tk.StringVar()
        genre_combo = ttk.Combobox(form_frame, textvariable=self.genre_detail_var, 
                                  values=["Fantasy", "Sci-Fi", "Thriller", "Mystery", 
                                          "Romance", "Historical", "Philosophy", "Dystopian", "Urban Fantasy", "Science Fiction", "Supernatural", "Generated"],
                                  state="readonly", width=15)
        genre_combo.grid(row=2, column=3, sticky="w", padx=5, pady=5)
        self.genre_detail_var.set("Fantasy")
        
        # Row 3
        ttk.Label(form_frame, text="Summary:").grid(row=3, column=0, sticky="ne", padx=5, pady=5)
        self.summary_text = scrolledtext.ScrolledText(form_frame, wrap=tk.WORD, width=85, height=8)
        self.summary_text.grid(row=3, column=1, columnspan=3, sticky="nsew", padx=5, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(detail_frame)
        button_frame.pack(fill=tk.X, pady=(10,0))
        
        self.save_btn = ttk.Button(button_frame, text="Save", command=self.save_unwritten_book)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(button_frame, text="Delete", command=self.delete_unwritten_book)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_unwritten_form)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        form_frame.grid_columnconfigure(1, weight=1)
        
    def create_written_tab(self):
        """Create the Written & In-Progress tab"""
        # Main frames
        main_frame = ttk.Frame(self.written_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - book list
        list_frame = ttk.LabelFrame(main_frame, text="Written & In-Progress Books", padding=10)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5), pady=5)
        
        # Treeview for written books
        columns = ("id", "title", "author", "status", "genre", "progress")
        self.written_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        
        # Configure columns
        self.written_tree.heading("id", text="ID", anchor=tk.W)
        self.written_tree.heading("title", text="Title", anchor=tk.W)
        self.written_tree.heading("author", text="Author", anchor=tk.W)
        self.written_tree.heading("status", text="Status", anchor=tk.W)
        self.written_tree.heading("genre", text="Genre", anchor=tk.W)
        self.written_tree.heading("progress", text="Progress", anchor=tk.W)
        
        self.written_tree.column("id", width=40, stretch=tk.NO)
        self.written_tree.column("title", width=250, anchor=tk.W)
        self.written_tree.column("author", width=150, anchor=tk.W)
        self.written_tree.column("status", width=120, anchor=tk.W)
        self.written_tree.column("genre", width=120, anchor=tk.W)
        self.written_tree.column("progress", width=80, anchor=tk.CENTER)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.written_tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.written_tree.xview)
        self.written_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.written_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        self.written_tree.bind("<<TreeviewSelect>>", self.show_written_details)
        
        # Configure grid weights
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Right panel - details
        detail_frame = ttk.LabelFrame(main_frame, text="Book Details", padding=10)
        detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5,0), pady=5, ipadx=5, ipady=5)
        
        # Detail form
        form_frame = ttk.Frame(detail_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Row 0
        ttk.Label(form_frame, text="Title:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.w_title_var = tk.StringVar()
        title_entry = ttk.Entry(form_frame, textvariable=self.w_title_var, width=30)
        title_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Row 1
        ttk.Label(form_frame, text="Author:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.w_author_var = tk.StringVar()
        author_entry = ttk.Entry(form_frame, textvariable=self.w_author_var)
        author_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(form_frame, text="Target Date:").grid(row=1, column=2, sticky="e", padx=5, pady=5)
        self.w_date_var = tk.StringVar()
        date_entry = ttk.Entry(form_frame, textvariable=self.w_date_var, width=12)
        date_entry.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        
        # Row 2
        ttk.Label(form_frame, text="Status:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.w_status_var = tk.StringVar()
        status_combo = ttk.Combobox(form_frame, textvariable=self.w_status_var, 
                                   values=["Idea", "Research", "Outline", "First Draft", 
                                           "Revision", "Editing", "Completed"], 
                                   state="readonly", width=15)
        status_combo.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.w_status_var.set("Idea")
        
        ttk.Label(form_frame, text="Genre:").grid(row=2, column=2, sticky="e", padx=5, pady=5)
        self.w_genre_var = tk.StringVar()
        genre_combo = ttk.Combobox(form_frame, textvariable=self.w_genre_var, 
                                  values=["Fantasy", "Sci-Fi", "Thriller", "Mystery", 
                                          "Romance", "Historical", "Philosophy", "Dystopian", "Steampunk", "Cyberpunk", "Generated"],
                                  state="readonly", width=15)
        genre_combo.grid(row=2, column=3, sticky="w", padx=5, pady=5)
        self.w_genre_var.set("Fantasy")
        
        # Row 3
        ttk.Label(form_frame, text="Progress:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.progress_var = tk.IntVar()
        progress_scale = ttk.Scale(form_frame, from_=0, to=100, variable=self.progress_var, 
                                  command=lambda v: self.progress_label.config(text=f"{int(float(v))}%"))
        progress_scale.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        self.progress_label = ttk.Label(form_frame, text="0%")
        self.progress_label.grid(row=3, column=2, sticky="w", padx=5, pady=5)
        
        # Row 4
        ttk.Label(form_frame, text="Summary:").grid(row=4, column=0, sticky="ne", padx=5, pady=5)
        self.w_summary_text = scrolledtext.ScrolledText(form_frame, wrap=tk.WORD, width=40, height=8)
        self.w_summary_text.grid(row=4, column=1, columnspan=3, sticky="nsew", padx=5, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(detail_frame)
        button_frame.pack(fill=tk.X, pady=(10,0))
        
        self.w_save_btn = ttk.Button(button_frame, text="Save", command=self.save_written_book)
        self.w_save_btn.pack(side=tk.LEFT, padx=5)
        
        self.w_delete_btn = ttk.Button(button_frame, text="Delete", command=self.delete_written_book)
        self.w_delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.w_add_btn = ttk.Button(button_frame, text="Add New", command=self.add_written_book)
        self.w_add_btn.pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_rowconfigure(4, weight=1)
        
    def create_ai_tab(self):
        """Create the AI Generator tab (password protected)"""
        main_frame = ttk.Frame(self.ai_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Password frame
        password_frame = ttk.LabelFrame(main_frame, text="AI Generator Access", padding=20)
        password_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(password_frame, text="This AI generator creates new unwritten books, stories, and poems\n"
                 "based on advanced literary patterns and neural networks.").pack(pady=5)
        
        ttk.Label(password_frame, text="Enter Password:").pack(pady=(20,5))
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=self.password_var, show="*", width=20)
        password_entry.pack(pady=5)
        password_entry.bind("<Return>", self.check_password)
        
        self.access_btn = ttk.Button(password_frame, text="Access AI Generator", command=self.check_password)
        self.access_btn.pack(pady=20)
        
        # AI Content frame (initially hidden)
        self.ai_content_frame = ttk.Frame(main_frame)
        
        # Generation options
        options_frame = ttk.LabelFrame(self.ai_content_frame, text="Generation Options", padding=10)
        options_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(options_frame, text="Content Type:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.content_type = tk.StringVar(value="Fantasy Book")
        content_types = ["Fantasy Book", "Sci-Fi Book", "Mystery Book", "Poem", "Short Story"]
        content_combo = ttk.Combobox(options_frame, textvariable=self.content_type, 
                                    values=content_types, state="readonly", width=20)
        content_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(options_frame, text="Theme/Topic:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.theme_var = tk.StringVar(value="Lost Civilization")
        theme_entry = ttk.Entry(options_frame, textvariable=self.theme_var, width=20)
        theme_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        ttk.Label(options_frame, text="Style:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.style_var = tk.StringVar(value="Epic")
        style_combo = ttk.Combobox(options_frame, textvariable=self.style_var, 
                                  values=["Epic", "Minimalist", "Poetic", "Dark", "Humorous"],
                                  state="readonly", width=20)
        style_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        self.generate_btn = ttk.Button(options_frame, text="Generate Content", command=self.generate_content)
        self.generate_btn.grid(row=1, column=3, padx=5, pady=5, sticky="e")
        
        # Generated content display
        result_frame = ttk.LabelFrame(self.ai_content_frame, text="Generated Content", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.ai_content_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, width=80, height=15)
        self.ai_content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.ai_content_text.config(state=tk.DISABLED)
        
        # Action buttons
        button_frame = ttk.Frame(self.ai_content_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Save as Unwritten Book", command=self.save_as_unwritten).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save as To-Be-Written", command=self.save_as_tobewritten).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Poem", command=self.save_poem).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_ai_content).pack(side=tk.LEFT, padx=5)
        
    def create_help_tab(self):
        """Create the Help & Export tab"""
        main_frame = ttk.Frame(self.help_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Help section
        help_frame = ttk.LabelFrame(main_frame, text="Application Guide", padding=10)
        help_frame.pack(fill=tk.X, pady=10)
        
        help_text = """
        Digital Library of Unwritten Books - User Guide
        
        1. Unwritten Books Tab:
           - Browse and manage books that were never written
           - Add, edit, or delete entries
           - Filter by status or genre
        
        2. Written & In-Progress Tab:
           - Manage books that are completed or being written
           - Track progress with percentage slider
           - Set target completion dates
        
        3. AI Generator Tab:
           - Password: 'whisper'
           - Create new book ideas, stories, and poems
           - Save generated content to your library
        
        4. Export Options:
           - Export your library to JSON format
           - Compile the application to an executable (see below)
        """
        
        help_label = ttk.Label(help_frame, text=help_text, justify=tk.LEFT)
        help_label.pack(pady=10, anchor="w")
        
        # Export section
        export_frame = ttk.LabelFrame(main_frame, text="Export Library", padding=10)
        export_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(export_frame, text="Export to JSON", command=self.export_library).pack(pady=10)
        
        # Compile section
        compile_frame = ttk.LabelFrame(main_frame, text="Compile to Executable", padding=10)
        compile_frame.pack(fill=tk.X, pady=10)
        
        compile_text = """
        To compile this application to a standalone executable:
        
        1. Install PyInstaller:
           pip install pyinstaller
           
        2. Run the following command:
           pyinstaller --onefile --windowed --name "Unwritten_Library" digital_library.py
           
        3. The executable will be in the 'dist' folder
        
        Note: Make sure all dependencies are installed in your environment.
        """
        
        compile_label = ttk.Label(compile_frame, text=compile_text, justify=tk.LEFT)
        compile_label.pack(pady=10, anchor="w")
        
    # --- Unwritten Book Methods ---

    def load_books(self, event=None):
        """Load books from the database into the Treeview based on filters"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_text = self.search_var.get()
        status_filter = self.status_var_filter.get()
        genre_filter = self.genre_var_filter.get()

        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            query = "SELECT id, title, author, status, genre, conceived_date FROM unwritten_books WHERE 1=1"
            params = []

            if search_text:
                query += " AND (title LIKE ? OR author LIKE ? OR summary LIKE ?)"
                params.extend([f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"])
            
            if status_filter != "All":
                query += " AND status = ?"
                params.append(status_filter)

            if genre_filter != "All":
                query += " AND genre = ?"
                params.append(genre_filter)

            c.execute(query, params)
            books = c.fetchall()

            for book in books:
                self.tree.insert("", "end", values=book)

    def show_unwritten_details(self, event=None):
        """Show details of the selected unwritten book in the form"""
        selected_item = self.tree.focus()
        if not selected_item:
            return
        
        book_id = self.tree.item(selected_item, "values")[0]
        self.current_unwritten_id = book_id
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM unwritten_books WHERE id=?", (book_id,))
            book = c.fetchone()
            
            if book:
                self.title_var.set(book[1])
                self.author_var.set(book[2])
                self.summary_text.delete(1.0, tk.END)
                self.summary_text.insert(tk.END, book[3])
                self.date_var.set(book[4])
                self.status_detail_var.set(book[6])
                self.genre_detail_var.set(book[7])

    def save_unwritten_book(self):
        """Save or update an unwritten book"""
        title = self.title_var.get()
        author = self.author_var.get()
        summary = self.summary_text.get(1.0, tk.END).strip()
        date = self.date_var.get()
        status = self.status_detail_var.get()
        genre = self.genre_detail_var.get()

        if not title or not summary:
            messagebox.showerror("Error", "Title and Summary cannot be empty.")
            return

        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            if self.current_unwritten_id is None:
                # Add new book
                c.execute("""INSERT INTO unwritten_books (title, author, summary, conceived_date, status, genre) 
                             VALUES (?, ?, ?, ?, ?, ?)""", 
                          (title, author, summary, date, status, genre))
                self.status_var.set(f"Added new book: {title}")
            else:
                # Update existing book
                c.execute("""UPDATE unwritten_books SET title=?, author=?, summary=?, conceived_date=?, status=?, genre=? 
                             WHERE id=?""", 
                          (title, author, summary, date, status, genre, self.current_unwritten_id))
                self.status_var.set(f"Updated book: {title}")
            conn.commit()

        self.load_books()
        self.clear_unwritten_form()

    def delete_unwritten_book(self):
        """Delete the selected unwritten book"""
        if self.current_unwritten_id is None:
            messagebox.showerror("Error", "No book selected to delete.")
            return
        
        if messagebox.askyesno("Delete Book", "Are you sure you want to delete this unwritten book?"):
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("DELETE FROM unwritten_books WHERE id=?", (self.current_unwritten_id,))
                conn.commit()
            
            self.status_var.set("Deleted book from unwritten library.")
            self.load_books()
            self.clear_unwritten_form()

    def add_unwritten_book(self):
        """Clear the form to add a new unwritten book"""
        self.clear_unwritten_form()
        self.status_var.set("Ready to add a new unwritten book.")

    def clear_unwritten_form(self):
        """Clear the unwritten book details form"""
        self.title_var.set("")
        self.author_var.set("")
        self.summary_text.delete(1.0, tk.END)
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.status_detail_var.set("Idea")
        self.genre_detail_var.set("Fantasy")
        self.current_unwritten_id = None

    def focus_on_summary(self, event=None):
        """Move cursor to the summary text field on double-click"""
        self.summary_text.focus_set()

    # --- Written Book Methods ---

    def load_written_books(self):
        """Load books from the written books database into the Treeview"""
        for item in self.written_tree.get_children():
            self.written_tree.delete(item)
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, title, author, status, genre, progress FROM written_books")
            books = c.fetchall()
            
            for book in books:
                # Add progress percentage to the display
                display_values = list(book)
                display_values[-1] = f"{book[5]}%"
                self.written_tree.insert("", "end", values=display_values)

    def show_written_details(self, event=None):
        """Show details of the selected written book in the form"""
        selected_item = self.written_tree.focus()
        if not selected_item:
            return
        
        book_id = self.written_tree.item(selected_item, "values")[0]
        self.current_written_id = book_id
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM written_books WHERE id=?", (book_id,))
            book = c.fetchone()
            
            if book:
                self.w_title_var.set(book[1])
                self.w_author_var.set(book[2])
                self.w_summary_text.delete(1.0, tk.END)
                self.w_summary_text.insert(tk.END, book[3])
                self.w_date_var.set(book[4])
                self.w_status_var.set(book[6])
                self.w_genre_var.set(book[7])
                self.progress_var.set(book[8])
                self.progress_label.config(text=f"{book[8]}%")
    
    def save_written_book(self):
        """Save or update a written book"""
        title = self.w_title_var.get()
        author = self.w_author_var.get()
        summary = self.w_summary_text.get(1.0, tk.END).strip()
        date = self.w_date_var.get()
        status = self.w_status_var.get()
        genre = self.w_genre_var.get()
        progress = self.progress_var.get()

        if not title or not summary:
            messagebox.showerror("Error", "Title and Summary cannot be empty.")
            return

        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            if self.current_written_id is None:
                # Add new book
                c.execute("""INSERT INTO written_books (title, author, summary, target_date, status, genre, progress) 
                             VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                          (title, author, summary, date, status, genre, progress))
                self.status_var.set(f"Added new writing project: {title}")
            else:
                # Update existing book
                c.execute("""UPDATE written_books SET title=?, author=?, summary=?, target_date=?, status=?, genre=?, progress=? 
                             WHERE id=?""", 
                          (title, author, summary, date, status, genre, progress, self.current_written_id))
                self.status_var.set(f"Updated writing project: {title}")
            conn.commit()

        self.load_written_books()
        self.add_written_book()

    def delete_written_book(self):
        """Delete the selected written book"""
        if self.current_written_id is None:
            messagebox.showerror("Error", "No book selected to delete.")
            return
        
        if messagebox.askyesno("Delete Book", "Are you sure you want to delete this written book?"):
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("DELETE FROM written_books WHERE id=?", (self.current_written_id,))
                conn.commit()
            
            self.status_var.set("Deleted book from written library.")
            self.load_written_books()
            self.add_written_book()

    def add_written_book(self):
        """Clear the form to add a new written book"""
        self.w_title_var.set("")
        self.w_author_var.set("")
        self.w_summary_text.delete(1.0, tk.END)
        self.w_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.w_status_var.set("Planned")
        self.w_genre_var.set("Fantasy")
        self.progress_var.set(0)
        self.progress_label.config(text="0%")
        self.current_written_id = None
        self.status_var.set("Ready to add a new written book.")

    # --- AI Generator Methods ---
    
    def check_password(self, event=None):
        """Check if the entered password is correct"""
        if self.password_var.get() == self.ai_password:
            self.ai_content_frame.pack(fill=tk.BOTH, expand=True)
            self.status_var.set("AI Generator unlocked! Create new literary content.")
        else:
            messagebox.showerror("Access Denied", "Incorrect password. The AI Generator remains locked.")
            self.password_var.set("")

    def generate_content(self):
        """Generate AI content based on selected options"""
        content_type = self.content_type.get()
        theme = self.theme_var.get()
        style = self.style_var.get()
        
        # Enable text widget for editing
        self.ai_content_text.config(state=tk.NORMAL)
        self.ai_content_text.delete(1.0, tk.END)
        
        if "Book" in content_type:
            # Generate a book concept
            genre = content_type.split()[0]
            title = self.generate_title(genre, theme)
            summary = self.generate_summary(genre, theme, style)
            
            content = f"Title: {title}\n\n"
            content += f"Genre: {genre}\n"
            content += f"Theme: {theme}\n"
            content += f"Style: {style}\n\n"
            content += "Summary:\n"
            content += summary
        elif content_type == "Short Story":
            # Generate a short story
            story = self.generate_short_story(theme, style)
            content = f"Short Story: {self.generate_title('Story', theme)}\n\n"
            content += f"Theme: {theme}\n"
            content += f"Style: {style}\n\n"
            content += story
        else:  # Poem
            poem = self.generate_poem(theme, style)
            content = f"Poem: {self.generate_title('Poem', theme)}\n\n"
            content += f"Theme: {theme}\n"
            content += f"Style: {style}\n\n"
            content += poem
        
        self.ai_content_text.insert(tk.END, content)
        self.ai_content_text.config(state=tk.DISABLED)
        self.status_var.set(f"Generated new {content_type.lower()} on '{theme}'")

    def generate_title(self, genre, theme):
        """Generate a book title"""
        prefixes = {
            "Fantasy": ["The", "A", "Chronicles of", "Legends of", "Song of", "Tale of"],
            "Sci-Fi": ["The", "Project", "Star", "Galactic", "Quantum", "Neural"],
            "Mystery": ["The", "Case of", "Secret of", "Mystery of", "Shadow of", "Silence in"]
        }
        
        suffixes = {
            "Fantasy": ["Dragon", "Crown", "Throne", "Sword", "Forest", "Mountain", "Kingdom", "Prophecy"],
            "Sci-Fi": ["Nexus", "Horizon", "Machine", "Future", "Singularity", "Interface", "Code"],
            "Mystery": ["Whispers", "Secret", "Cipher", "Enigma", "Shadow", "Echo", "Footsteps"]
        }
        
        prefix = random.choice(prefixes.get(genre, ["The"]))
        suffix = random.choice(suffixes.get(genre, ["Unknown"]))
        
        return f"{prefix} {suffix} {theme.split()[0]}"

    def generate_summary(self, genre, theme, style):
        """Generate a book summary"""
        characters = {
            "Fantasy": ["young mage", "disgraced knight", "reluctant princess", "ancient dragon", "forest spirit"],
            "Sci-Fi": ["rogue AI", "cybernetic mercenary", "xenobiologist", "starship captain", "quantum physicist"],
            "Mystery": ["retired detective", "obsessive journalist", "antique bookseller", "reclusive heiress", "codebreaker"]
        }
        
        conflicts = {
            "Epic": ["must prevent an ancient evil from returning", "embarks on a quest to save their kingdom", 
                     "discovers a conspiracy that threatens the entire galaxy"],
            "Minimalist": ["struggles with a personal dilemma", "faces a moral choice with no clear solution", 
                           "confronts their own limitations"],
            "Poetic": ["journeys through landscapes of memory and desire", "explores the boundaries between reality and dream", 
                       "searches for meaning in a chaotic world"],
            "Dark": ["descends into madness while pursuing the truth", "battles inner demons and external threats", 
                     "confronts a terrifying secret from their past"],
            "Humorous": ["accidentally becomes the chosen one", "fumbles their way through an epic quest", 
                         "discovers that saving the world is more paperwork than glory"]
        }
        
        character = random.choice(characters.get(genre, ["protagonist"]))
        conflict = random.choice(conflicts.get(style, ["faces a great challenge"]))
        
        summary = f"In a {genre.lower()} setting centered around {theme.lower()}, "
        summary += f"a {character} {conflict}. "
        
        if style == "Epic":
            summary += "Along the way, they gather unlikely allies, face impossible odds, and discover hidden truths about themselves and their world."
        elif style == "Minimalist":
            summary += "The story explores the quiet moments of decision and the weight of seemingly small choices."
        elif style == "Poetic":
            summary += "The narrative weaves together lyrical prose and vivid imagery to explore themes of loss, hope, and transformation."
        elif style == "Dark":
            summary += "As they delve deeper, they uncover disturbing truths that challenge their sanity and moral compass."
        else:  # Humorous
            summary += "Filled with witty dialogue and absurd situations, the story finds humor in the most unlikely places."
        
        return summary

    def generate_short_story(self, theme, style):
        """Generate a short story"""
        openings = [
            f"The first time I encountered {theme}, I was unprepared for how it would change my life.",
            f"Everyone in our village knew the stories about {theme}, but no one believed them until that fateful day.",
            f"In the quiet hours before dawn, when {theme} seemed most palpable, I made my discovery."
        ]
        
        middles = {
            "Epic": [f"As I delved deeper into the mystery of {theme}, I uncovered ancient secrets that challenged everything I knew."],
            "Minimalist": [f"The simplicity of {theme} belied its profound impact on my daily existence."],
            "Poetic": [f"{theme} danced at the edges of perception, a wisp of meaning in a chaotic world."],
            "Dark": [f"The truth about {theme} was more terrible than I could have imagined, a darkness that threatened to consume me."],
            "Humorous": [f"Of course, the grand revelation about {theme} happened while I was wearing mismatched socks and eating cold pizza."]
        }
        
        endings = {
            "Epic": [f"And so I stood before the final challenge, {theme} in hand, ready to face whatever came next."],
            "Minimalist": [f"In the end, {theme} was just what it appeared to be, nothing more and nothing less."],
            "Poetic": [f"{theme} faded into the twilight, a memory as fleeting as the morning mist."],
            "Dark": [f"As the darkness closed in, I realized that {theme} was not the answer, but the question that would haunt me forever."],
            "Humorous": [f"And that's how I accidentally became the world's leading expert on {theme} while trying to avoid doing my taxes."]
        }
        
        story = random.choice(openings) + "\n\n"
        story += random.choice(middles.get(style, [""])) + " "
        story += random.choice(middles.get(style, [""])) + "\n\n"
        story += random.choice(endings.get(style, [""]))
        
        return story

    def generate_poem(self, theme, style):
        """Generate a poem"""
        styles = {
            "Epic": [
                ["O mighty {theme}, hear my call,",
                 "Across the ages, standing tall,",
                 "Your presence felt by one and all,",
                 "As destiny unfolds."],
                 
                ["Through trials fierce and battles dire,",
                 "Fueled by passion, love, and fire,",
                 "{theme} lifts our spirits higher,",
                 "A story to be told."]
            ],
            "Minimalist": [
                ["{theme} waits",
                 "Quietly",
                 "In the space",
                 "Between thoughts"],
                 
                ["A single moment",
                 "Holds all",
                 "That {theme} is",
                 "And isn't"]
            ],
            "Poetic": [
                ["The {theme} shimmers in the twilight air,",
                 "A whispered promise, fragile, rare,",
                 "A beauty almost too profound to bear,",
                 "A truth beyond compare."],
                 
                ["In silent moments, soft and deep,",
                 "Where secret sorrows lie asleep,",
                 "{theme} its tender watch does keep,",
                 "A vigil none can break."]
            ],
            "Dark": [
                ["In shadowed corners, {theme} creeps,",
                 "While the haunted world still sleeps,",
                 "Darkness in its grasp it keeps,",
                 "A harvest that it reaps."],
                 
                ["Beneath the moon's cold, watchful eye,",
                 "Where forgotten whispers lie,",
                 "{theme} waits for you and I,",
                 "Beneath the starlit sky."]
            ],
            "Humorous": [
                ["Oh {theme}, you tricky thing,",
                 "What chaos will you next bring?",
                 "My sanity is on the wing,",
                 "As my poor ears begin to ring!"],
                 
                ["I tried to grasp you, {theme} dear,",
                 "But you just laughed and drank my beer,",
                 "Now all my problems are quite clear,",
                 "I'll tackle you again next year!"]
            ]
        }
        
        poem = ""
        for stanza in random.choice(styles.get(style, styles["Poetic"])):
            poem += stanza.replace("{theme}", theme) + "\n"
        return poem

    def save_as_unwritten(self):
        """Save generated content as an unwritten book"""
        content = self.ai_content_text.get(1.0, tk.END).strip()
        if not content:
            return
            
        # Extract title from content
        title = "Generated Book Concept"
        if content.startswith("Title:"):
            title = content.split("\n")[0].replace("Title:", "").strip()
        
        # Extract genre from content
        genre = "Generated"
        for line in content.split("\n"):
            if line.startswith("Genre:"):
                genre = line.split(":")[1].strip()
                break
        
        # Create a simplified summary
        summary = "\n".join(content.split("\n")[5:]).strip()
        
        # Add to unwritten books
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO unwritten_books 
                      (title, author, summary, conceived_date, status, genre) 
                      VALUES (?, ?, ?, ?, ?, ?)""", 
                      (title, "AI Generated", summary, 
                       datetime.now().strftime("%Y-%m-%d"), "Idea", genre))
            conn.commit()
        
        self.load_books()
        self.status_var.set(f"Saved '{title}' to Unwritten Books")
        messagebox.showinfo("Saved", "The generated content has been saved as an unwritten book!")

    def save_as_tobewritten(self):
        """Save generated content as a to-be-written book"""
        content = self.ai_content_text.get(1.0, tk.END).strip()
        if not content:
            return
            
        # Extract title from content
        title = "New Writing Project"
        if content.startswith("Title:"):
            title = content.split("\n")[0].replace("Title:", "").strip()

        # Extract genre from content
        genre = "Generated"
        for line in content.split("\n"):
            if line.startswith("Genre:"):
                genre = line.split(":")[1].strip()
                break
        
        # Create a simplified summary
        summary = "\n".join(content.split("\n")[5:]).strip()
        
        # Add to written books
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO written_books 
                      (title, author, summary, target_date, status, genre, progress) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                      (title, "AI Generated", summary, 
                       (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"), 
                       "Planned", genre, 0))
            conn.commit()
        
        self.load_written_books()
        self.status_var.set(f"Saved '{title}' as a new writing project")
        messagebox.showinfo("Saved", "The generated content has been saved as a to-be-written book!")

    def save_poem(self):
        """Save generated poem to the content file"""
        content = self.ai_content_text.get(1.0, tk.END).strip()
        if not content:
            return
            
        # Extract title from content
        title = "Generated Poem"
        if content.startswith("Poem:"):
            title = content.split("\n")[0].replace("Poem:", "").strip()
        
        # Extract poem content
        poem_content = "\n".join(content.split("\n")[3:]).strip()
        
        # Add to poems
        self.library_content["poems"].append({
            "title": title,
            "author": "AI Generated",
            "content": poem_content
        })
        
        # Save to file
        with open(self.content_path, 'w') as f:
            json.dump(self.library_content, f, indent=2)
        
        self.status_var.set(f"Saved poem '{title}' to library content")
        messagebox.showinfo("Saved", "The poem has been saved to the library content file!")

    def clear_ai_content(self):
        """Clear the AI content area"""
        self.ai_content_text.config(state=tk.NORMAL)
        self.ai_content_text.delete(1.0, tk.END)
        self.ai_content_text.config(state=tk.DISABLED)

    def export_library(self):
        """Export the library to a JSON file"""
        # Gather all data
        export_data = {
            "unwritten_books": [],
            "written_books": [],
            "library_content": self.library_content
        }
        
        # Get unwritten books
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM unwritten_books")
            export_data["unwritten_books"] = [dict(row) for row in c.fetchall()]
            
            # Get written books
            c.execute("SELECT * FROM written_books")
            export_data["written_books"] = [dict(row) for row in c.fetchall()]
        
        # Save to file
        export_path = "unwritten_library_export.json"
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.status_var.set(f"Library exported to {export_path}")
        messagebox.showinfo("Export Complete", f"All library data has been exported to:\n{export_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DigitalLibraryApp(root)
    root.mainloop()
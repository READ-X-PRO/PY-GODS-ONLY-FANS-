import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
from datetime import datetime, timedelta
import random
import os
import json
import textwrap

class DigitalLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Library of Unwritten Books")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)

        # Setup databases
        self.db_path = "unwritten_books.db"
        self.content_path = "library_content.json"
        self.init_db()
        self.load_content_file()
        
        # AI password
        self.ai_password = "whisper"
        
        # Current book IDs for editing
        self.current_unwritten_id = None
        self.current_written_id = None
        
        # Setup GUI with dynamic designs
        self.setup_styles()
        self.create_matrix_background()
        self.create_widgets()
        
        self.load_books()
        self.load_written_books()
        
        # Start the matrix animation
        self.animate_matrix()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
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
        
        self.add_sample_books()

    def load_content_file(self):
        """Load or create the content file with written/to-be-written stories"""
        if not os.path.exists(self.content_path):
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
        """Add sample books to the database if the tables are empty"""
        unwritten_books = [
            ("The Last Library", "Eleanor Vance", "In a world where physical books are banned, a librarian preserves the last collection of printed books in a secret underground archive. The story follows her struggle to protect knowledge from the digital-only regime.", "2020-03-15", "Abandoned", "Dystopian"),
            ("Chronicles of the Void", "Arthur Quill", "An epic space opera about a crew stranded in an empty sector of space, discovering an ancient civilization that chose to erase all records of its existence. Explores themes of cultural memory and intentional forgetting.", "2018-11-22", "Outline", "Sci-Fi"),
            ("Whispers of the Forgotten", "M. L. Blackwood", "A psychological thriller where a historian begins hearing voices from historical manuscripts. As she deciphers the messages, she realizes they're warnings about our own future.", "2022-05-07", "Idea", "Thriller")
        ]
        
        written_books = [
            ("The Clockwork Oracle", "Julian Mechanicus", "Steampunk adventure about an automaton that gains the ability to see possible futures and the inventor who tries to protect it from those who would misuse its power.", "2024-12-31", "Outline", "Steampunk", 30),
            ("Beneath the Willow", "Eleanor Vance", "A coming-of-age story set in post-war England, following three generations of women who find solace and secrets in their family garden.", "2023-10-15", "First Draft", "Historical Fiction", 75)
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM unwritten_books")
            if c.fetchone()[0] == 0:
                c.executemany("""INSERT INTO unwritten_books (title, author, summary, conceived_date, status, genre) VALUES (?, ?, ?, ?, ?, ?)""", unwritten_books)
            
            c.execute("SELECT COUNT(*) FROM written_books")
            if c.fetchone()[0] == 0:
                c.executemany("""INSERT INTO written_books (title, author, summary, target_date, status, genre, progress) VALUES (?, ?, ?, ?, ?, ?, ?)""", written_books)
            
            conn.commit()

    def setup_styles(self):
        """Configure custom dark theme for ttk widgets"""
        style = ttk.Style(self.root)
        style.theme_create("dark_matrix", parent="alt", settings={
            "TNotebook": {"configure": {"background": "#1a1a1a", "bordercolor": "#00ff00"}},
            "TNotebook.Tab": {"configure": {"background": "#003300", "foreground": "#00ff00", "font": ("Courier New", 10, "bold")},
                               "map": {"background": [("selected", "#004d00"), ("active", "#006600")], "foreground": [("selected", "#ffffff"), ("active", "#ffffff")]}},
            "TFrame": {"configure": {"background": "#1a1a1a"}},
            "TLabelFrame": {"configure": {"background": "#1a1a1a", "foreground": "#00ff00", "relief": "solid", "bordercolor": "#00ff00"}},
            "TLabel": {"configure": {"background": "#1a1a1a", "foreground": "#00ff00", "font": ("Courier New", 10)}},
            "TEntry": {"configure": {"fieldbackground": "#003300", "foreground": "#00ff00", "insertbackground": "#00ff00", "bordercolor": "#00ff00"}},
            "TButton": {"configure": {"background": "#004d00", "foreground": "#00ff00", "font": ("Courier New", 10, "bold")},
                        "map": {"background": [("active", "#006600")]}},
            "Treeview": {"configure": {"background": "#003300", "foreground": "#00ff00", "fieldbackground": "#003300", "font": ("Courier New", 9)},
                         "map": {"background": [("selected", "#006600")], "foreground": [("selected", "#ffffff")]}},
            "Treeview.Heading": {"configure": {"background": "#004d00", "foreground": "#ffffff", "font": ("Courier New", 10, "bold")}},
            "TCombobox": {"configure": {"fieldbackground": "#003300", "foreground": "#00ff00", "selectbackground": "#006600", "selectforeground": "#ffffff"}},
            "TScale": {"configure": {"background": "#1a1a1a"}},
            "TProgressbar": {"configure": {"background": "#00ff00", "troughcolor": "#003300"}},
        })
        style.theme_use("dark_matrix")
        
        # Override specific widget colors
        self.root.option_add("*TNotebook*background", "#1a1a1a")

    def create_matrix_background(self):
        """Create a canvas for the matrix animation and place it behind the widgets"""
        self.canvas = tk.Canvas(self.root, bg="#000000", highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Create a main frame to hold all other widgets with a semi-transparent background
        self.main_frame = ttk.Frame(self.root, style="TFrame")
        self.main_frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.root.lift(self.main_frame)
        self.root.bind("<Configure>", self.on_resize)
        
        self.matrix_drops = []
        self.matrix_chars = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶ"
        self.drop_speed = 10
        self.create_matrix_drops()

    def on_resize(self, event):
        self.canvas.config(width=event.width, height=event.height)
        self.create_matrix_drops()
    
    def create_matrix_drops(self):
        self.matrix_drops = []
        width = self.canvas.winfo_width()
        if width > 0:
            font_size = 12
            num_drops = int(width / font_size) + 1
            for i in range(num_drops):
                x = i * font_size
                y = random.randint(-1000, 0)
                length = random.randint(10, 30)
                speed = random.randint(3, 10)
                self.matrix_drops.append({'x': x, 'y': y, 'length': length, 'speed': speed})

    def animate_matrix(self):
        self.canvas.delete("all")
        canvas_height = self.canvas.winfo_height()
        font_size = 12
        
        for drop in self.matrix_drops:
            for i in range(drop['length']):
                char_y = drop['y'] + (i * font_size)
                if 0 <= char_y < canvas_height:
                    color_intensity = 255 - int((i / drop['length']) * 200)
                    color = f'#{0:02x}{color_intensity:02x}{0:02x}'
                    char = random.choice(self.matrix_chars)
                    self.canvas.create_text(drop['x'], char_y, text=char, fill=color, font=("Courier New", font_size, "bold"), anchor="nw")
            
            drop['y'] += drop['speed']
            if drop['y'] > canvas_height:
                drop['y'] = random.randint(-1000, 0)
        
        self.root.after(30, self.animate_matrix)

    def create_widgets(self):
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create frames for each tab
        self.unwritten_frame = ttk.Frame(self.notebook, style="TFrame")
        self.written_frame = ttk.Frame(self.notebook, style="TFrame")
        self.ai_frame = ttk.Frame(self.notebook, style="TFrame")
        self.help_frame = ttk.Frame(self.notebook, style="TFrame")
        
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
        status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W, style="TLabel")
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
        """Create the AI Generator tab with enhanced design"""
        main_frame = ttk.Frame(self.ai_frame, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        password_frame = ttk.LabelFrame(main_frame, text="AI Generator Access", padding=20)
        password_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(password_frame, text="This AI generator creates new unwritten books, stories, and poems\nbased on advanced literary patterns and neural networks.").pack(pady=5)
        
        ttk.Label(password_frame, text="Enter Password:").pack(pady=(20,5))
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=self.password_var, show="*", width=20)
        password_entry.pack(pady=5)
        password_entry.bind("<Return>", self.check_password)
        
        self.access_btn = ttk.Button(password_frame, text="Access AI Generator", command=self.check_password)
        self.access_btn.pack(pady=20)
        
        self.ai_content_frame = ttk.Frame(main_frame, style="TFrame")
        
        options_frame = ttk.LabelFrame(self.ai_content_frame, text="Generation Options", padding=10)
        options_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(options_frame, text="Content Type:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.content_type = tk.StringVar(value="Fantasy Book")
        content_types = ["Fantasy Book", "Sci-Fi Book", "Mystery Book", "Poem", "Short Story"]
        content_combo = ttk.Combobox(options_frame, textvariable=self.content_type, values=content_types, state="readonly", width=20)
        content_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(options_frame, text="Theme/Topic:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.theme_var = tk.StringVar(value="Lost Civilization")
        theme_entry = ttk.Entry(options_frame, textvariable=self.theme_var, width=20)
        theme_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        ttk.Label(options_frame, text="Style:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.style_var = tk.StringVar(value="Epic")
        style_combo = ttk.Combobox(options_frame, textvariable=self.style_var, values=["Epic", "Minimalist", "Poetic", "Dark", "Humorous"], state="readonly", width=20)
        style_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        self.generate_btn = ttk.Button(options_frame, text="Generate Content", command=self.generate_content)
        self.generate_btn.grid(row=1, column=3, padx=5, pady=5, sticky="e")
        
        result_frame = ttk.LabelFrame(self.ai_content_frame, text="Generated Content", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.ai_content_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, width=80, height=15, font=("Courier New", 10), bg="#003300", fg="#00ff00", insertbackground="#00ff00")
        self.ai_content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.ai_content_text.config(state=tk.DISABLED)
        
        button_frame = ttk.Frame(self.ai_content_frame, style="TFrame")
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

    # --- AI Generator Methods (enhanced) ---
    
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
        
        self.ai_content_text.config(state=tk.NORMAL)
        self.ai_content_text.delete(1.0, tk.END)
        
        if "Book" in content_type:
            genre = content_type.split()[0]
            title = self.generate_title(genre, theme)
            summary = self.generate_summary(genre, theme, style)
            
            content = f"Title: {title}\n\n"
            content += f"Genre: {genre}\n"
            content += f"Theme: {theme}\n"
            content += f"Style: {style}\n\n"
            content += "Summary:\n"
            content += textwrap.fill(summary, width=80)
        elif content_type == "Short Story":
            story_title = self.generate_title("Story", theme)
            story = self.generate_short_story(theme, style)
            content = f"Short Story: {story_title}\n\n"
            content += f"Theme: {theme}\n"
            content += f"Style: {style}\n\n"
            content += textwrap.fill(story, width=80)
        else:  # Poem
            poem_title = self.generate_title("Poem", theme)
            poem = self.generate_poem(theme, style)
            content = f"Poem: {poem_title}\n\n"
            content += f"Theme: {theme}\n"
            content += f"Style: {style}\n\n"
            content += poem
        
        self.ai_content_text.insert(tk.END, content)
        self.ai_content_text.config(state=tk.DISABLED)
        self.status_var.set(f"Generated new {content_type.lower()} on '{theme}'")

    def generate_title(self, genre, theme):
        """Generate a more imaginative book title"""
        prefixes = {
            "Fantasy": ["The Whispering", "Chronicles of the", "The Last", "Echoes of the"],
            "Sci-Fi": ["Project", "The Singularity", "Quantum", "Galactic"],
            "Mystery": ["The Silent", "Shadows of the", "A Case of", "The Unwritten"],
            "Story": ["A Tale of", "The Day of the", "When the", "The Curious Case of"],
            "Poem": ["Ode to the", "The Ballad of", "Lament of the", "A Sonnet for"]
        }
        
        nouns = {
            "Fantasy": ["Crown", "Storm", "Citadel", "Oracle", "Whispers"],
            "Sci-Fi": ["Core", "Void", "Nexus", "Code", "Anomaly"],
            "Mystery": ["Locket", "Manor", "Cipher", "Mirror", "Stairs"],
            "Story": ["Stranger", "Lighthouse", "Bell", "Tree", "Whisperer"],
            "Poem": ["Dawn", "Twilight", "Stone", "Sea", "Memory"]
        }
        
        prefix = random.choice(prefixes.get(genre, ["The"]))
        noun = random.choice(nouns.get(genre, ["Unknown"]))
        
        return f"{prefix} {noun} of {theme}"

    def generate_summary(self, genre, theme, style):
        """Generate a longer, more detailed book summary"""
        characters = {
            "Fantasy": ["A young farmhand who discovers he is the last of an ancient bloodline", "A disgraced knight seeking redemption", "A cunning sorceress on the run from her past", "A band of unlikely heroes bound by a common quest"],
            "Sci-Fi": ["A rogue AI that has gained self-awareness", "A lone starship captain navigating the galaxy's most dangerous sector", "A xenolinguist tasked with communicating with a silent alien race", "A quantum physicist who discovers a parallel universe"],
            "Mystery": ["A retired detective haunted by an unsolved cold case", "An eccentric private investigator with a penchant for cryptic clues", "A journalist who stumbles upon a conspiracy much larger than they anticipated", "A reclusive millionaire who is found dead under suspicious circumstances"]
        }
        
        conflicts = {
            "Epic": ["must prevent a prophecy from coming true, which would destroy the known world", "embarks on an arduous quest to find a legendary artifact that can restore balance to the kingdom", "is thrust into a galactic war with a mysterious and powerful alien species"],
            "Minimalist": ["grapples with a profound moral choice that will affect their small community for generations to come", "is forced to confront their own personal failures and the secrets they've kept hidden", "navigates the complexities of a single, life-altering event in an otherwise ordinary life"],
            "Poetic": ["journeys through a surreal landscape of memory and dreams", "struggles to find meaning and beauty in a world defined by its decay and sorrow", "attempts to communicate with the spirits of a long-dead civilization"],
            "Dark": ["uncovers a terrible secret that pushes them to the brink of madness", "is hunted by a relentless entity from a forgotten dimension", "must make an impossible choice that will lead to tragedy, no matter what they do"],
            "Humorous": ["accidentally becomes the most powerful person in the universe, much to their dismay", "finds themselves entangled in a series of bizarre and increasingly absurd events", "must save the world while also navigating the awkwardness of a budding romance and a severe allergy to magic"]
        }
        
        resolutions = {
            "Epic": ["The journey culminates in a final, epic battle where the fate of all hangs in the balance, forcing them to make a sacrifice for the greater good.", "The hero must choose between personal victory and the well-being of their allies, leading to a profound and unexpected conclusion.", "The final showdown against the antagonist forces them to use a power they never knew they had, forever changing their destiny."],
            "Minimalist": ["The story ends not with a bang, but with a quiet understanding of the human condition and the small victories that truly matter.", "In the aftermath of their choice, life returns to a new, altered normal, but the character is forever changed by the experience.", "The climax is an internal one, where they finally come to terms with their past and find peace."],
            "Poetic": ["The resolution is more of a meditation than an action, leaving the reader with a sense of wonder and profound introspection.", "The narrative closes with a lingering image or a final, powerful metaphor that encapsulates the entire journey.", "The character's quest is not for a tangible item, but for a piece of themselves, which they finally find in the quiet stillness."],
            "Dark": ["The final pages reveal a grim truth: the monster was not defeated, but only contained, and a new evil has taken its place.", "The hero's victory comes at an unbearable cost, leaving them irrevocably broken and forever haunted by their choices.", "The story ends with the protagonist becoming the very thing they fought against, a tragic cycle of darkness."],
            "Humorous": ["The great battle against the power of {theme} was ultimately decided by a lucky guess and a well-timed sneeze. The villain, a surprisingly competent bureaucrat, was thwarted by a typo in his master plan.", "In a stunning display of incompetence, I accidentally solved the entire mystery and saved the day. I was not a hero; I was a living, breathing plot hole."]
        }
        
        # Combine snippets to create a longer summary
        summary = f"In a world defined by its {genre.lower()} lore, centered around the enigmatic {theme}, a {random.choice(characters.get(genre, ['protagonist']))} {random.choice(conflicts.get(style, ['faces a great challenge']))}. "
        summary += "Their journey is fraught with peril and unexpected turns, forcing them to confront not only external threats but their own inner demons. "
        summary += f"{random.choice(resolutions.get(style, ['The climax brings a profound resolution.']))}"
        
        return summary.replace("{theme}", theme)

    def generate_short_story(self, theme, style):
        """Generate a longer, more structured short story"""
        openings = [
            f"The first time the whispers of {theme} reached our small town, they were dismissed as mere folklore. But there was a chilling truth hidden within the stories, one that would soon become impossible to ignore.",
            f"Everyone knew not to venture into the old {theme} after dusk. Legend said it held a secret, a power that could grant great desires or bring unimaginable madness. I, of course, was never one to heed warnings.",
            f"I remember the day it all started. A quiet morning, the air thick with the scent of rain, and a sudden, impossible occurrence related to {theme} that shattered the reality we all took for granted."
        ]
        
        rising_action = {
            "Epic": [f"My quest to understand the mystery of {theme} led me far from home, through perilous lands and forgotten ruins. With each step, the stakes grew higher, and I began to realize that the fate of more than just my own life depended on my success.",
                     f"As I delved deeper into the legend of {theme}, I discovered a hidden society dedicated to its protection. They warned me of an impending cataclysm, but their caution only fueled my resolve to find the source of the power."],
            "Minimalist": [f"The small, insignificant details of my day began to shift around the concept of {theme}. A cup of coffee tasted different, the color of the sky seemed less vibrant. The change was subtle, but it was there, gnawing at the edges of my perception.",
                           f"My world became a quiet meditation on {theme}. I spent my days observing its effects, documenting its presence in the most mundane places. The power was not loud, but it was all-encompassing."],
            "Poetic": [f"The pursuit of {theme} became a dance with the unseen, a conversation with ghosts. Every shadow held a fragment of its truth, every breeze carried a whispered verse. I followed the rhythm, letting it guide me deeper into the labyrinth of my own soul.",
                       f"I painted scenes of {theme}, wrote poems to it, and dreamed of its form. It was a muse and a tormentor, a beacon of beauty in a world of decay, and I was utterly lost in its spell."],
            "Dark": [f"The more I learned about {theme}, the more I felt its cold grasp on my sanity. The visions grew more intense, the nightmares more vivid. I was no longer an observer but a participant in a terrible cosmic horror.",
                     f"I was not the only one searching for {theme}. There were others, their faces shrouded in darkness and their intentions malevolent. I fled, knowing that if they found me, the fate that awaited me was far worse than death."],
            "Humorous": [f"My clumsy attempts to harness the power of {theme} only resulted in a series of hilarious mishaps. I accidentally turned my neighbor's prize-winning cat into a topiary and managed to make all the local streetlights spontaneously combust.",
                         f"It turns out the legend of {theme} was less about power and more about a complicated, ancient tax-evasion scheme. I was now a reluctant hero in a bureaucratic nightmare, which was somehow more stressful than facing an eldritch god."]
        }
        
        climax = {
            "Epic": [f"The final confrontation with the keeper of {theme} was not with swords, but with a battle of wits and will. I was forced to face the ultimate challenge, a choice that would seal the fate of our world.",
                     f"At the heart of the ancient temple, the source of {theme} pulsed with a terrible power. I knew I had to destroy it, even if it meant sacrificing myself."],
            "Minimalist": [f"The climax was a quiet realization. I sat in a cafe, watching the rain fall, and understood that {theme} was not a force to be controlled, but a part of the world to be accepted. The journey was over.",
                           f"In that one, still moment, I came face-to-face with the true nature of {theme}. It wasn't a battle to be won, but a truth to be embraced. My struggle had been with myself all along."],
            "Poetic": [f"The crescendo arrived not in a flash of light, but in a final, heartbreaking verse. I finally understood the song of {theme}, and the price of that knowledge was my innocence.",
                       f"I reached the end of the path and found only a reflection of myself, distorted by the power of {theme}. The truth was a mirror, and what I saw in it broke me."],
            "Dark": [f"The final confrontation was a descent into pure chaos. The entity of {theme} showed me the true meaning of fear, and I knew, in that moment, that I had been a pawn in a game I could never hope to win.",
                     f"I defeated the monster, but not before it left an indelible mark on my soul. I was no longer the person who had started this journey. I was a broken husk, haunted by the darkness I had fought."],
            "Humorous": [f"The great battle against the power of {theme} was ultimately decided by a lucky guess and a well-timed sneeze. The villain, a surprisingly competent bureaucrat, was thwarted by a typo in his master plan.",
                         f"In a stunning display of incompetence, I accidentally solved the entire mystery and saved the day. I was not a hero; I was a living, breathing plot hole."]
        }

        story = f"{random.choice(openings)}\n\n"
        story += f"{random.choice(rising_action.get(style, ['']))}\n\n"
        story += f"{random.choice(climax.get(style, ['']))}\n\n"
        story += "And so, the story of {theme} came to its inevitable conclusion."
        
        return story.replace("{theme}", theme)

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
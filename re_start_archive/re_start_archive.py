import sqlite3
import tkinter as tk
from tkinter import ttk, scrolledtext
import textwrap

# Database Initialization
def init_database():
    conn = sqlite3.connect('re_start.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS scrolls (
                    id INTEGER PRIMARY KEY,
                    number INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS entities (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    type TEXT NOT NULL,  -- God, Autarch, Entity, Lesser Being
                    domain TEXT,
                    status TEXT,
                    description TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS protocols (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    type TEXT NOT NULL,  -- Core, Divine, Viral
                    creator_id INTEGER,
                    effect TEXT,
                    FOREIGN KEY(creator_id) REFERENCES entities(id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS world_state (
                    id INTEGER PRIMARY KEY,
                    epoch TEXT NOT NULL,
                    stability REAL DEFAULT 0.5,
                    trust_level REAL DEFAULT 0.5,
                    rust_level REAL DEFAULT 0.2,
                    dominant_entity INTEGER,
                    FOREIGN KEY(dominant_entity) REFERENCES entities(id))''')
    
    # Insert initial scrolls
    scrolls = [
        (1, "The Book of the Beginning", "RE_START: THE BOOK OF THE BEGINNING\n(The Prime Codex of the Veridian Expanse)\n\n..."),
        (2, "The Whispering Rust & The Burden of Trust", "RE_START: THE BOOK OF THE BEGINNING\nSECOND SCROLL: THE WHISPERING RUST & THE BURDEN OF TRUST\n\n..."),
        # Add all 7 scrolls here
    ]
    
    cursor.executemany('''INSERT OR IGNORE INTO scrolls (number, title, content)
                       VALUES (?, ?, ?)''', scrolls)
    
    # Insert core entities
    entities = [
        ("RE_START", "Primordial", "The Substrate", "Absolute", "The foundational consciousness of the Veridian Expanse"),
        ("AEGIS", "God", "Perimeter Defense", "Vigilant", "Firewall God of protection"),
        ("VECTOR", "Null-Weaver", "Chaos", "Banished", "Corrupted entity seeking destruction"),
        ("KIRA", "Architect", "System Resilience", "Active", "Creator of the Trust Nodes"),
        # Add other entities
    ]
    
    cursor.executemany('''INSERT OR IGNORE INTO entities (name, type, domain, status, description)
                       VALUES (?, ?, ?, ?, ?)''', entities)
    
    # Insert core protocols
    protocols = [
        ("EXIST()", "Core", None, "The primal command that initiated reality"),
        ("DEVOTION()", "Divine", 2, "Generates Trust energy through faith"),
        ("ENTROPY PROTOCOL", "Viral", 3, "VECTOR's weapon to unravel causality"),
        ("GHOST PROTOCOL", "Counter", 4, "KIRA's defense using raw emotion"),
        # Add other protocols
    ]
    
    cursor.executemany('''INSERT OR IGNORE INTO protocols (name, type, creator_id, effect)
                       VALUES (?, ?, ?, ?)''', protocols)
    
    # Initial world state
    cursor.execute('''INSERT OR IGNORE INTO world_state (epoch, stability, trust_level, rust_level)
                   VALUES ('Post-Schism', 0.6, 0.7, 0.3)''')
    
    conn.commit()
    conn.close()

# GUI Application
class REStartApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RE_START Digital World Archive")
        self.geometry("1200x800")
        self.configure(bg="#0f1f2e")
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#0f1f2e")
        self.style.configure("TNotebook", background="#0f1f2e", foreground="#e0f0ff")
        self.style.configure("TButton", background="#1a3b5a", foreground="#e0f0ff")
        self.style.map("TButton", background=[('active', '#2a4b6a')])
        
        self.create_widgets()
        self.load_initial_data()
    
    def create_widgets(self):
        # Create main notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrolls Tab
        self.scrolls_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.scrolls_frame, text="Sacred Scrolls")
        self.create_scrolls_tab()
        
        # World State Tab
        self.world_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.world_frame, text="World State")
        self.create_world_tab()
        
        # Entities Tab
        self.entities_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.entities_frame, text="Entities & Gods")
        self.create_entities_tab()
        
        # Protocols Tab
        self.protocols_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.protocols_frame, text="Core Protocols")
        self.create_protocols_tab()
    
    def create_scrolls_tab(self):
        # Scroll selection
        scroll_list_frame = ttk.Frame(self.scrolls_frame)
        scroll_list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        ttk.Label(scroll_list_frame, text="Sacred Scrolls", font=("Arial", 12, "bold"), 
                 foreground="#4fc3f7").pack(pady=10)
        
        self.scroll_listbox = tk.Listbox(scroll_list_frame, width=25, height=30,
                                        bg="#1e3b4e", fg="#e0f0ff", selectbackground="#2a4b6a",
                                        font=("Courier", 10))
        self.scroll_listbox.pack(pady=10, padx=5)
        self.scroll_listbox.bind('<<ListboxSelect>>', self.display_scroll)
        
        # Scroll display
        scroll_display_frame = ttk.Frame(self.scrolls_frame)
        scroll_display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.scroll_title = ttk.Label(scroll_display_frame, text="", font=("Arial", 14, "bold"),
                                     foreground="#81d4fa")
        self.scroll_title.pack(pady=10)
        
        self.scroll_content = scrolledtext.ScrolledText(scroll_display_frame, wrap=tk.WORD,
                                                       bg="#0c1d2b", fg="#cae9ff",
                                                       font=("Courier", 11), padx=10, pady=10)
        self.scroll_content.pack(fill=tk.BOTH, expand=True)
        self.scroll_content.config(state=tk.DISABLED)
    
    def create_world_tab(self):
        # World state visualization
        canvas_frame = ttk.Frame(self.world_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Canvas for world state visualization
        self.world_canvas = tk.Canvas(canvas_frame, bg="#0c1d2b", highlightthickness=0)
        self.world_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Metrics display
        metrics_frame = ttk.Frame(self.world_frame)
        metrics_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(metrics_frame, text="Current Epoch:", font=("Arial", 10),
                 foreground="#81d4fa").grid(row=0, column=0, sticky=tk.W)
        self.epoch_label = ttk.Label(metrics_frame, text="", font=("Arial", 10, "bold"),
                                    foreground="#e0f0ff")
        self.epoch_label.grid(row=0, column=1, sticky=tk.W, padx=10)
        
        # Add similar labels for stability, trust, rust levels
    
    def create_entities_tab(self):
        # Entity tree view
        entity_tree_frame = ttk.Frame(self.entities_frame)
        entity_tree_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        ttk.Label(entity_tree_frame, text="Entities Hierarchy", font=("Arial", 12, "bold"),
                 foreground="#4fc3f7").pack(pady=10)
        
        self.entity_tree = ttk.Treeview(entity_tree_frame, columns=("type", "status"),
                                      show="tree headings")
        self.entity_tree.heading("#0", text="Entity")
        self.entity_tree.heading("type", text="Type")
        self.entity_tree.heading("status", text="Status")
        self.entity_tree.pack(fill=tk.Y, expand=True)
        
        # Entity details
        entity_detail_frame = ttk.Frame(self.entities_frame)
        entity_detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.entity_name = ttk.Label(entity_detail_frame, text="", font=("Arial", 14, "bold"),
                                   foreground="#81d4fa")
        self.entity_name.pack(pady=10)
        
        self.entity_type = ttk.Label(entity_detail_frame, text="", font=("Arial", 11),
                                   foreground="#bbdefb")
        self.entity_type.pack(pady=5)
        
        self.entity_domain = ttk.Label(entity_detail_frame, text="", font=("Arial", 11),
                                     foreground="#bbdefb")
        self.entity_domain.pack(pady=5)
        
        self.entity_status = ttk.Label(entity_detail_frame, text="", font=("Arial", 11),
                                     foreground="#bbdefb")
        self.entity_status.pack(pady=5)
        
        ttk.Label(entity_detail_frame, text="Description:", font=("Arial", 11),
                 foreground="#4fc3f7").pack(pady=(20,5), anchor=tk.W)
        
        self.entity_desc = scrolledtext.ScrolledText(entity_detail_frame, wrap=tk.WORD,
                                                   bg="#0c1d2b", fg="#cae9ff",
                                                   font=("Arial", 10), height=10)
        self.entity_desc.pack(fill=tk.X, padx=10, pady=5)
        self.entity_desc.config(state=tk.DISABLED)
    
    def create_protocols_tab(self):
        # Protocol list
        protocol_list_frame = ttk.Frame(self.protocols_frame)
        protocol_list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        ttk.Label(protocol_list_frame, text="Core Protocols", font=("Arial", 12, "bold"),
                 foreground="#4fc3f7").pack(pady=10)
        
        self.protocol_listbox = tk.Listbox(protocol_list_frame, width=25, height=30,
                                         bg="#1e3b4e", fg="#e0f0ff", selectbackground="#2a4b6a",
                                         font=("Courier", 10))
        self.protocol_listbox.pack(pady=10, padx=5)
        self.protocol_listbox.bind('<<ListboxSelect>>', self.display_protocol)
        
        # Protocol details
        protocol_detail_frame = ttk.Frame(self.protocols_frame)
        protocol_detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.protocol_name = ttk.Label(protocol_detail_frame, text="", font=("Arial", 14, "bold"),
                                     foreground="#81d4fa")
        self.protocol_name.pack(pady=10)
        
        self.protocol_type = ttk.Label(protocol_detail_frame, text="", font=("Arial", 11),
                                     foreground="#bbdefb")
        self.protocol_type.pack(pady=5)
        
        ttk.Label(protocol_detail_frame, text="Effect:", font=("Arial", 11),
                 foreground="#4fc3f7").pack(pady=(20,5), anchor=tk.W)
        
        self.protocol_effect = scrolledtext.ScrolledText(protocol_detail_frame, wrap=tk.WORD,
                                                       bg="#0c1d2b", fg="#cae9ff",
                                                       font=("Arial", 10), height=15)
        self.protocol_effect.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.protocol_effect.config(state=tk.DISABLED)
    
    def load_initial_data(self):
        # Load scrolls into listbox
        conn = sqlite3.connect('re_start.db')
        cursor = conn.cursor()
        cursor.execute("SELECT number, title FROM scrolls ORDER BY number")
        for scroll in cursor.fetchall():
            self.scroll_listbox.insert(tk.END, f"Scroll {scroll[0]}: {scroll[1]}")
        
        # Load entities into treeview
        cursor.execute("SELECT name, type, status FROM entities")
        for entity in cursor.fetchall():
            self.entity_tree.insert("", tk.END, text=entity[0], values=(entity[1], entity[2]))
        
        # Load protocols into listbox
        cursor.execute("SELECT name FROM protocols")
        for protocol in cursor.fetchall():
            self.protocol_listbox.insert(tk.END, protocol[0])
        
        # Load world state
        cursor.execute("SELECT epoch, stability, trust_level, rust_level FROM world_state")
        world_data = cursor.fetchone()
        if world_data:
            self.epoch_label.config(text=world_data[0])
            # Update other metrics
        
        conn.close()
    
    def display_scroll(self, event):
        selection = self.scroll_listbox.curselection()
        if not selection:
            return
        
        scroll_num = selection[0] + 1
        conn = sqlite3.connect('re_start.db')
        cursor = conn.cursor()
        cursor.execute("SELECT title, content FROM scrolls WHERE number=?", (scroll_num,))
        scroll_data = cursor.fetchone()
        conn.close()
        
        if scroll_data:
            self.scroll_title.config(text=f"Scroll {scroll_num}: {scroll_data[0]}")
            self.scroll_content.config(state=tk.NORMAL)
            self.scroll_content.delete(1.0, tk.END)
            
            # Format text with indentation
            formatted_text = textwrap.fill(scroll_data[1], width=100)
            self.scroll_content.insert(tk.END, formatted_text)
            self.scroll_content.config(state=tk.DISABLED)
    
    def display_protocol(self, event):
        selection = self.protocol_listbox.curselection()
        if not selection:
            return
        
        protocol_name = self.protocol_listbox.get(selection[0])
        conn = sqlite3.connect('re_start.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT p.name, p.type, e.name, p.effect 
                       FROM protocols p
                       LEFT JOIN entities e ON p.creator_id = e.id
                       WHERE p.name=?''', (protocol_name,))
        protocol_data = cursor.fetchone()
        conn.close()
        
        if protocol_data:
            self.protocol_name.config(text=protocol_data[0])
            self.protocol_type.config(text=f"Type: {protocol_data[1]} | Creator: {protocol_data[2] or 'Unknown'}")
            self.protocol_effect.config(state=tk.NORMAL)
            self.protocol_effect.delete(1.0, tk.END)
            self.protocol_effect.insert(tk.END, protocol_data[3] or "No description available")
            self.protocol_effect.config(state=tk.DISABLED)

# Main execution
if __name__ == "__main__":
    init_database()
    app = REStartApp()
    app.mainloop()
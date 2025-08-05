import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Database setup
def create_database():
    conn = sqlite3.connect('players.db')
    c = conn.cursor()
    
    # Players table
    c.execute('''CREATE TABLE IF NOT EXISTS players (
                player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT)''')
    
    # Stats table
    c.execute('''CREATE TABLE IF NOT EXISTS stats (
                stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                kills INTEGER DEFAULT 0,
                deaths INTEGER DEFAULT 0,
                score INTEGER DEFAULT 0,
                playtime REAL DEFAULT 0.0,
                FOREIGN KEY (player_id) REFERENCES players (player_id))''')
    
    # Progression table
    c.execute('''CREATE TABLE IF NOT EXISTS progression (
                progression_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                achievements TEXT,
                last_updated TEXT,
                FOREIGN KEY (player_id) REFERENCES players (player_id))''')
    
    conn.commit()
    conn.close()

class PlayerDBApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Player Database Manager")
        self.root.geometry("900x600")
        
        create_database()
        self.create_widgets()
        self.load_players()
        
    def create_widgets(self):
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Players Tab
        self.players_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.players_frame, text="Players")
        
        # Stats Tab
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        
        # Progression Tab
        self.progression_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.progression_frame, text="Progression")
        
        # Create tab contents
        self.create_players_tab()
        self.create_stats_tab()
        self.create_progression_tab()
    
    def create_players_tab(self):
        # Player List
        columns = ("ID", "Username", "Email", "Created", "Last Login")
        self.player_tree = ttk.Treeview(self.players_frame, columns=columns, show='headings')
        for col in columns:
            self.player_tree.heading(col, text=col)
            self.player_tree.column(col, width=120)
        self.player_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Player Form
        form_frame = ttk.Frame(self.players_frame)
        form_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky='w')
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Email:").grid(row=0, column=2, sticky='w')
        self.email_entry = ttk.Entry(form_frame, width=30)
        self.email_entry.grid(row=0, column=3, padx=5)
        
        ttk.Button(form_frame, text="Add Player", command=self.add_player).grid(row=0, column=4, padx=5)
        ttk.Button(form_frame, text="Update Player", command=self.update_player).grid(row=0, column=5, padx=5)
        ttk.Button(form_frame, text="Delete Player", command=self.delete_player).grid(row=0, column=6, padx=5)
    
    def create_stats_tab(self):
        # Stats List
        columns = ("Player ID", "Username", "Kills", "Deaths", "Score", "Playtime")
        self.stats_tree = ttk.Treeview(self.stats_frame, columns=columns, show='headings')
        for col in columns:
            self.stats_tree.heading(col, text=col)
            self.stats_tree.column(col, width=120)
        self.stats_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Stats Form
        form_frame = ttk.Frame(self.stats_frame)
        form_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(form_frame, text="Player:").grid(row=0, column=0, sticky='w')
        self.player_combo = ttk.Combobox(form_frame, state="readonly")
        self.player_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Kills:").grid(row=0, column=2, sticky='w')
        self.kills_entry = ttk.Entry(form_frame, width=10)
        self.kills_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(form_frame, text="Deaths:").grid(row=0, column=4, sticky='w')
        self.deaths_entry = ttk.Entry(form_frame, width=10)
        self.deaths_entry.grid(row=0, column=5, padx=5)
        
        ttk.Label(form_frame, text="Score:").grid(row=0, column=6, sticky='w')
        self.score_entry = ttk.Entry(form_frame, width=10)
        self.score_entry.grid(row=0, column=7, padx=5)
        
        ttk.Label(form_frame, text="Playtime:").grid(row=0, column=8, sticky='w')
        self.playtime_entry = ttk.Entry(form_frame, width=10)
        self.playtime_entry.grid(row=0, column=9, padx=5)
        
        ttk.Button(form_frame, text="Update Stats", command=self.update_stats).grid(row=0, column=10, padx=5)
    
    def create_progression_tab(self):
        # Progression List
        columns = ("Player ID", "Username", "Level", "Experience", "Achievements", "Last Updated")
        self.progression_tree = ttk.Treeview(self.progression_frame, columns=columns, show='headings')
        for col in columns:
            self.progression_tree.heading(col, text=col)
            self.progression_tree.column(col, width=120)
        self.progression_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Progression Form
        form_frame = ttk.Frame(self.progression_frame)
        form_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(form_frame, text="Player:").grid(row=0, column=0, sticky='w')
        self.prog_player_combo = ttk.Combobox(form_frame, state="readonly")
        self.prog_player_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Level:").grid(row=0, column=2, sticky='w')
        self.level_entry = ttk.Entry(form_frame, width=10)
        self.level_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(form_frame, text="Experience:").grid(row=0, column=4, sticky='w')
        self.exp_entry = ttk.Entry(form_frame, width=10)
        self.exp_entry.grid(row=0, column=5, padx=5)
        
        ttk.Label(form_frame, text="Achievements (comma separated):").grid(row=0, column=6, sticky='w')
        self.achievements_entry = ttk.Entry(form_frame, width=30)
        self.achievements_entry.grid(row=0, column=7, padx=5)
        
        ttk.Button(form_frame, text="Update Progression", command=self.update_progression).grid(row=0, column=8, padx=5)
    
    def load_players(self):
        # Clear existing data
        for item in self.player_tree.get_children():
            self.player_tree.delete(item)
        
        conn = sqlite3.connect('players.db')
        c = conn.cursor()
        c.execute("SELECT player_id, username, email, created_at, last_login FROM players")
        players = c.fetchall()
        conn.close()
        
        player_names = []
        for player in players:
            self.player_tree.insert('', 'end', values=player)
            player_names.append(player[1])
        
        # Update comboboxes
        self.player_combo['values'] = player_names
        self.prog_player_combo['values'] = player_names
        
        self.load_stats()
        self.load_progression()
    
    def load_stats(self):
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)
        
        conn = sqlite3.connect('players.db')
        c = conn.cursor()
        c.execute('''SELECT s.player_id, p.username, s.kills, s.deaths, s.score, s.playtime 
                     FROM stats s JOIN players p ON s.player_id = p.player_id''')
        stats = c.fetchall()
        conn.close()
        
        for stat in stats:
            self.stats_tree.insert('', 'end', values=stat)
    
    def load_progression(self):
        for item in self.progression_tree.get_children():
            self.progression_tree.delete(item)
        
        conn = sqlite3.connect('players.db')
        c = conn.cursor()
        c.execute('''SELECT pr.player_id, p.username, pr.level, pr.experience, 
                     pr.achievements, pr.last_updated 
                     FROM progression pr JOIN players p ON pr.player_id = p.player_id''')
        progression = c.fetchall()
        conn.close()
        
        for prog in progression:
            self.progression_tree.insert('', 'end', values=prog)
    
    def add_player(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        
        if not username:
            messagebox.showerror("Error", "Username is required")
            return
        
        try:
            conn = sqlite3.connect('players.db')
            c = conn.cursor()
            c.execute("INSERT INTO players (username, email) VALUES (?, ?)", (username, email))
            
            # Create associated stats and progression records
            player_id = c.lastrowid
            c.execute("INSERT INTO stats (player_id) VALUES (?)", (player_id,))
            c.execute("INSERT INTO progression (player_id) VALUES (?)", (player_id,))
            
            conn.commit()
            conn.close()
            
            self.username_entry.delete(0, 'end')
            self.email_entry.delete(0, 'end')
            self.load_players()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
    
    def update_player(self):
        selected = self.player_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a player to update")
            return
        
        player_id = self.player_tree.item(selected[0])['values'][0]
        username = self.username_entry.get()
        email = self.email_entry.get()
        
        if not username:
            messagebox.showerror("Error", "Username is required")
            return
        
        try:
            conn = sqlite3.connect('players.db')
            c = conn.cursor()
            c.execute("UPDATE players SET username=?, email=? WHERE player_id=?", 
                      (username, email, player_id))
            conn.commit()
            conn.close()
            
            self.load_players()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
    
    def delete_player(self):
        selected = self.player_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a player to delete")
            return
        
        player_id = self.player_tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Confirm", "Delete this player and all associated data?"):
            conn = sqlite3.connect('players.db')
            c = conn.cursor()
            c.execute("DELETE FROM players WHERE player_id=?", (player_id,))
            c.execute("DELETE FROM stats WHERE player_id=?", (player_id,))
            c.execute("DELETE FROM progression WHERE player_id=?", (player_id,))
            conn.commit()
            conn.close()
            
            self.load_players()
    
    def update_stats(self):
        username = self.player_combo.get()
        if not username:
            messagebox.showerror("Error", "Select a player")
            return
        
        try:
            kills = int(self.kills_entry.get() or 0)
            deaths = int(self.deaths_entry.get() or 0)
            score = int(self.score_entry.get() or 0)
            playtime = float(self.playtime_entry.get() or 0.0)
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric input")
            return
        
        conn = sqlite3.connect('players.db')
        c = conn.cursor()
        c.execute("SELECT player_id FROM players WHERE username=?", (username,))
        player_id = c.fetchone()[0]
        
        c.execute('''UPDATE stats SET kills=?, deaths=?, score=?, playtime=?
                     WHERE player_id=?''',
                 (kills, deaths, score, playtime, player_id))
        conn.commit()
        conn.close()
        
        self.load_stats()
        self.kills_entry.delete(0, 'end')
        self.deaths_entry.delete(0, 'end')
        self.score_entry.delete(0, 'end')
        self.playtime_entry.delete(0, 'end')
    
    def update_progression(self):
        username = self.prog_player_combo.get()
        if not username:
            messagebox.showerror("Error", "Select a player")
            return
        
        try:
            level = int(self.level_entry.get() or 1)
            experience = int(self.exp_entry.get() or 0)
            achievements = self.achievements_entry.get()
        except ValueError:
            messagebox.showerror("Error", "Level and Experience must be numbers")
            return
        
        conn = sqlite3.connect('players.db')
        c = conn.cursor()
        c.execute("SELECT player_id FROM players WHERE username=?", (username,))
        player_id = c.fetchone()[0]
        
        c.execute('''UPDATE progression 
                     SET level=?, experience=?, achievements=?, last_updated=datetime('now')
                     WHERE player_id=?''',
                 (level, experience, achievements, player_id))
        conn.commit()
        conn.close()
        
        self.load_progression()
        self.level_entry.delete(0, 'end')
        self.exp_entry.delete(0, 'end')
        self.achievements_entry.delete(0, 'end')

if __name__ == "__main__":
    root = tk.Tk()
    app = PlayerDBApp(root)
    root.mainloop()
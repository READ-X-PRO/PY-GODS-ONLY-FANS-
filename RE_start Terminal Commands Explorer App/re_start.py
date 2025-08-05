import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import webbrowser
import random
import time
import sys
from PIL import Image, ImageTk
import threading
import pyperclip
import os
import json

class RE_start(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RE_start - Terminal Commands Explorer")
        self.geometry("1200x800")
        self.configure(bg="#0a0a0a")
        self.style = ttk.Style()
        
        # Configure styles for cyberpunk theme
        self.style.configure("TFrame", background="#0a0a0a")
        self.style.configure("TNotebook", background="#0a0a0a", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#121212", foreground="#00ff00", 
                            font=("Terminal", 10, "bold"), padding=[10, 5], borderwidth=1)
        self.style.map("TNotebook.Tab", background=[("selected", "#003300")])
        self.style.configure("Cyber.TButton", background="#003300", foreground="#00ff00", 
                            font=("Terminal", 10, "bold"), borderwidth=1, relief="flat")
        self.style.map("Cyber.TButton", background=[("active", "#005500")])
        self.style.configure("Cyber.TRadiobutton", background="#0a0a0a", foreground="#00ff00")
        self.style.configure("Cyber.TCombobox", fieldbackground="#121212", background="#121212", foreground="#00ff00")
        
        # Create cyberpunk color scheme
        self.cyber_colors = {
            "bg": "#0a0a0a",
            "fg": "#00ff00",
            "accent1": "#ff00ff",
            "accent2": "#00ffff",
            "panel": "#121212",
            "highlight": "#005500"
        }
        
        # Animation speed
        self.animation_speed = 80  # ms
        
        # Load command data from JSON file
        self.commands_data = self.load_command_data()
        
        # Create main frames
        self.create_header()
        self.create_main_content()
        self.create_footer()
        
        # Start terminal simulation
        self.terminal_sim_active = True
        threading.Thread(target=self.simulate_terminal_output, daemon=True).start()
        
        # Initialize favorites
        self.favorites = []
        self.load_favorites()
    
    def load_command_data(self):
        """Load command data from JSON file or use default if not found"""
        try:
            with open("commands.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Default data if file not found
            return {
                "Linux": [
                    {"command": "ls", "description": "List directory contents", "category": "File System", 
                     "examples": ["ls -l  # Long format", "ls -a  # Show hidden files", "ls -lh  # Human readable sizes"], 
                     "dependencies": "Core utility"},
                    {"command": "grep", "description": "Search text using patterns", "category": "Text Processing", 
                     "examples": ["grep 'error' log.txt", "ps aux | grep 'nginx'", "grep -r 'function' src/"], 
                     "dependencies": "Core utility"},
                    {"command": "chmod", "description": "Change file permissions", "category": "Permissions", 
                     "examples": ["chmod 755 script.sh", "chmod u+x file", "chmod -R 644 directory/"], 
                     "dependencies": "Core utility"},
                    {"command": "ssh", "description": "Secure shell remote login", "category": "Networking", 
                     "examples": ["ssh user@192.168.1.100", "ssh -i key.pem user@server.com", "ssh -p 2222 user@host"], 
                     "dependencies": "openssh-client"},
                    {"command": "find", "description": "Search for files in directory hierarchy", "category": "File System", 
                     "examples": ["find . -name '*.py'", "find /var/log -size +10M", "find . -mtime -7 -exec rm {} \\;"], 
                     "dependencies": "Core utility"},
                    {"command": "apt-get", "description": "Package management utility (Debian)", "category": "Package Management", 
                     "examples": ["sudo apt-get update", "sudo apt-get install nginx", "sudo apt-get remove package"], 
                     "dependencies": "apt"},
                    {"command": "systemctl", "description": "Control systemd system and service manager", "category": "System Management", 
                     "examples": ["systemctl start nginx", "systemctl enable docker", "systemctl status ssh"], 
                     "dependencies": "systemd"},
                    {"command": "cron", "description": "Time-based job scheduler", "category": "System Management", 
                     "examples": ["crontab -e  # Edit cron jobs", "crontab -l  # List cron jobs", "*/5 * * * * /path/to/script.sh"], 
                     "dependencies": "cron"},
                    {"command": "iptables", "description": "Administration tool for IPv4 packet filtering", "category": "Networking", 
                     "examples": ["iptables -L", "iptables -A INPUT -p tcp --dport 22 -j ACCEPT", "iptables -P OUTPUT DROP"], 
                     "dependencies": "iptables"},
                    {"command": "dd", "description": "Convert and copy a file", "category": "System Management", 
                     "examples": ["dd if=/dev/sda of=backup.img", "dd if=/dev/zero of=file.bin bs=1M count=100", 
                                 "dd if=image.iso of=/dev/sdb status=progress"], 
                     "dependencies": "Core utility"}
                ],
                "Windows": [
                    {"command": "dir", "description": "List directory contents", "category": "File System", 
                     "examples": ["dir", "dir /w", "dir /s *.txt"], 
                     "dependencies": "Built-in"},
                    {"command": "ipconfig", "description": "Display network configuration", "category": "Networking", 
                     "examples": ["ipconfig", "ipconfig /all", "ipconfig /release"], 
                     "dependencies": "Built-in"},
                    {"command": "tasklist", "description": "Display running processes", "category": "Process Management", 
                     "examples": ["tasklist", "tasklist /svc", "tasklist /fi \"IMAGENAME eq chrome*\""], 
                     "dependencies": "Built-in"},
                    {"command": "netsh", "description": "Network shell configuration tool", "category": "Networking", 
                     "examples": ["netsh wlan show profiles", "netsh advfirewall set allprofiles state off", 
                                 "netsh interface ip set address \"Local Area Connection\" static 192.168.1.100 255.255.255.0 192.168.1.1"], 
                     "dependencies": "Built-in"},
                    {"command": "reg", "description": "Windows registry editor", "category": "System Management", 
                     "examples": ["reg query HKLM\\Software\\Microsoft\\Windows", "reg add \"HKLM\\Software\\MyApp\" /v Version /t REG_SZ /d 1.0", 
                                 "reg delete \"HKLM\\Software\\ObsoleteApp\" /f"], 
                     "dependencies": "Built-in"},
                    {"command": "choco", "description": "Chocolatey package manager", "category": "Package Management", 
                     "examples": ["choco install git", "choco upgrade all", "choco list -l"], 
                     "dependencies": "Chocolatey (https://chocolatey.org/install)"},
                    {"command": "powershell", "description": "Task automation framework", "category": "Scripting", 
                     "examples": ["powershell Get-Process", "powershell -Command \"Get-Service | Where Status -eq 'Running'\""], 
                     "dependencies": "Built-in"},
                    {"command": "wmic", "description": "Windows Management Instrumentation", "category": "System Management", 
                     "examples": ["wmic os get caption", "wmic process get name,processid", "wmic startup list full"], 
                     "dependencies": "Built-in"},
                    {"command": "netstat", "description": "Display network connections", "category": "Networking", 
                     "examples": ["netstat -ano", "netstat -ab", "netstat -r"], 
                     "dependencies": "Built-in"},
                    {"command": "sfc", "description": "System File Checker", "category": "System Management", 
                     "examples": ["sfc /scannow"], 
                     "dependencies": "Built-in"}
                ],
                "macOS": [
                    {"command": "ls", "description": "List directory contents", "category": "File System", 
                     "examples": ["ls -l", "ls -a", "ls -lh"], 
                     "dependencies": "Core utility"},
                    {"command": "brew", "description": "Homebrew package manager", "category": "Package Management", 
                     "examples": ["brew install wget", "brew update", "brew upgrade"], 
                     "dependencies": "Homebrew (https://brew.sh/)"},
                    {"command": "say", "description": "Convert text to speech", "category": "Utilities", 
                     "examples": ["say \"Hello World\"", "say -v Daniel \"How are you?\""], 
                     "dependencies": "Built-in"},
                    {"command": "pmset", "description": "Power management settings", "category": "System Management", 
                     "examples": ["pmset -g", "pmset sleepnow", "pmset displaysleep 10"], 
                     "dependencies": "Built-in"},
                    {"command": "diskutil", "description": "Disk management utility", "category": "Storage", 
                     "examples": ["diskutil list", "diskutil info disk0", "diskutil eject /dev/disk2"], 
                     "dependencies": "Built-in"},
                    {"command": "networksetup", "description": "Network configuration tool", "category": "Networking", 
                     "examples": ["networksetup -listallnetworkservices", "networksetup -setairportpower en0 off", 
                                 "networksetup -setdnsservers Wi-Fi 8.8.8.8"], 
                     "dependencies": "Built-in"},
                    {"command": "launchctl", "description": "Service management framework", "category": "System Management", 
                     "examples": ["launchctl list", "launchctl load ~/Library/LaunchAgents/my.script.plist", 
                                 "launchctl unload /Library/LaunchDaemons/com.example.daemon.plist"], 
                     "dependencies": "Built-in"},
                    {"command": "screencapture", "description": "Screen capture utility", "category": "Utilities", 
                     "examples": ["screencapture screen.png", "screencapture -iW ~/Desktop/screen.jpg", 
                                 "screencapture -T 5 ~/Desktop/delayed.png"], 
                     "dependencies": "Built-in"},
                    {"command": "airport", "description": "Wi-Fi diagnostic tool", "category": "Networking", 
                     "examples": ["airport -s", "airport -z", "airport -I"], 
                     "dependencies": "Built-in (located at /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport)"},
                    {"command": "defaults", "description": "Modify user defaults system", "category": "System Management", 
                     "examples": ["defaults read com.apple.finder", "defaults write com.apple.dock autohide -bool true", 
                                 "defaults delete com.apple.safari HomePage"], 
                     "dependencies": "Built-in"}
                ]
            }
    
    def load_favorites(self):
        """Load favorites from file if exists"""
        try:
            with open("favorites.json", "r") as f:
                self.favorites = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.favorites = []
    
    def save_favorites(self):
        """Save favorites to file"""
        try:
            with open("favorites.json", "w") as f:
                json.dump(self.favorites, f)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save favorites: {str(e)}")
    
    def create_header(self):
        """Create the header with app title and matrix effect"""
        header_frame = ttk.Frame(self, style="TFrame")
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Title with cyberpunk style
        title_label = tk.Label(
            header_frame, 
            text="RE_start", 
            font=("Courier New", 28, "bold"), 
            fg="#00ff00", 
            bg="#0a0a0a",
            padx=10
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(
            header_frame, 
            text="Terminal Commands Explorer", 
            font=("Courier New", 12), 
            fg="#00cc00", 
            bg="#0a0a0a"
        )
        subtitle_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Matrix effect canvas
        matrix_canvas = tk.Canvas(header_frame, width=200, height=40, bg="#0a0a0a", highlightthickness=0)
        matrix_canvas.pack(side=tk.RIGHT, padx=10)
        self.matrix_chars = []
        for _ in range(30):
            x = random.randint(0, 190)
            y = random.randint(0, 35)
            char = random.choice("01")
            char_id = matrix_canvas.create_text(
                x, y, 
                text=char, 
                fill="#00aa00", 
                font=("Courier New", 8)
            )
            self.matrix_chars.append((char_id, x, y))
        
        # Animate matrix effect
        self.animate_matrix(matrix_canvas)
    
    def animate_matrix(self, canvas):
        """Animate the matrix effect in the header"""
        for char_id, x, y in self.matrix_chars:
            # Move character down
            y += random.randint(2, 6)
            if y > 40:
                y = 0
                x = random.randint(0, 190)
            
            # Update character position
            canvas.coords(char_id, x, y)
            
            # Occasionally change character
            if random.random() < 0.3:
                new_char = random.choice("01")
                canvas.itemconfig(char_id, text=new_char)
        self.after(self.animation_speed, lambda: self.animate_matrix(canvas))
    
    def create_main_content(self):
        """Create the main content area with OS tabs and command display"""
        main_frame = ttk.Frame(self, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Per-tab search/category variables
        self.search_vars = {}
        self.category_vars = {}
        
        self.linux_frame = self.create_os_tab("Linux", "#003300")
        self.windows_frame = self.create_os_tab("Windows", "#000033")
        self.macos_frame = self.create_os_tab("macOS", "#330033")
        self.favorites_frame = self.create_favorites_tab()
        
        self.notebook.add(self.linux_frame, text=" Linux ")
        self.notebook.add(self.windows_frame, text=" Windows ")
        self.notebook.add(self.macos_frame, text=" macOS ")
        self.notebook.add(self.favorites_frame, text=" ★ Favorites ")
        
        # Create command details panel
        details_frame = ttk.LabelFrame(main_frame, text="Command Details", style="TFrame")
        details_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10, ipady=5)
        
        self.details_text = scrolledtext.ScrolledText(
            details_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=10,
            bg="#121212", 
            fg="#00ff00", 
            insertbackground="#00ff00",
            font=("Consolas", 10),
            relief=tk.FLAT
        )
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.details_text.insert(tk.END, "Select a command to view details...")
        self.details_text.config(state=tk.DISABLED)
    
    def create_favorites_tab(self):
        """Create the favorites tab"""
        frame = ttk.Frame(self.notebook, style="TFrame")
        filter_frame = ttk.Frame(frame, style="TFrame")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(filter_frame, text="Filter:", bg="#0a0a0a", fg="#00ff00", font=("Consolas", 10)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.fav_search_var = tk.StringVar()
        search_entry = tk.Entry(
            filter_frame, 
            textvariable=self.fav_search_var, 
            bg="#121212", 
            fg="#00ff00", 
            insertbackground="#00ff00",
            font=("Consolas", 10),
            relief=tk.FLAT
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        search_entry.bind("<KeyRelease>", lambda e: self.filter_favorites())
        
        # Create command list
        list_frame = ttk.Frame(frame, style="TFrame")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create Treeview with style
        style = ttk.Style()
        style.configure("Fav.Treeview", background="#121212", fieldbackground="#121212", 
                       foreground="#00ff00", font=("Consolas", 10))
        style.configure("Fav.Treeview.Heading", background="#555500", foreground="#00ff00", 
                       font=("Consolas", 10, "bold"))
        style.map("Fav.Treeview", background=[("selected", "#005500")])
        
        columns = ("os", "command", "description", "category")
        self.fav_tree = ttk.Treeview(
            list_frame, 
            columns=columns, 
            show="headings",
            style="Fav.Treeview",
            selectmode="browse"
        )
        
        # Configure columns
        self.fav_tree.column("os", width=70, anchor=tk.W)
        self.fav_tree.column("command", width=150, anchor=tk.W)
        self.fav_tree.column("description", width=400, anchor=tk.W)
        self.fav_tree.column("category", width=150, anchor=tk.W)
        
        # Create headings
        self.fav_tree.heading("os", text="OS", anchor=tk.W)
        self.fav_tree.heading("command", text="Command", anchor=tk.W)
        self.fav_tree.heading("description", text="Description", anchor=tk.W)
        self.fav_tree.heading("category", text="Category", anchor=tk.W)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.fav_tree.yview)
        self.fav_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.fav_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.fav_tree.bind("<<TreeviewSelect>>", self.show_favorite_details)
        
        # Populate favorites
        self.populate_favorites()
        
        return frame
    
    def populate_favorites(self):
        """Populate the favorites treeview"""
        for item in self.fav_tree.get_children():
            self.fav_tree.delete(item)
        
        for fav in self.favorites:
            os_name, command = fav.split(":", 1)
            for cmd in self.commands_data[os_name]:
                if cmd["command"] == command:
                    self.fav_tree.insert("", tk.END, values=(
                        os_name, 
                        cmd["command"], 
                        cmd["description"], 
                        cmd["category"]
                    ))
                    break
    
    def filter_favorites(self):
        """Filter favorites based on search text"""
        search_text = self.fav_search_var.get().lower()
        
        for item in self.fav_tree.get_children():
            self.fav_tree.delete(item)
        
        for fav in self.favorites:
            os_name, command = fav.split(":", 1)
            for cmd in self.commands_data[os_name]:
                if cmd["command"] == command:
                    if (search_text in os_name.lower() or 
                        search_text in cmd["command"].lower() or 
                        search_text in cmd["description"].lower() or 
                        search_text in cmd["category"].lower()):
                        self.fav_tree.insert("", tk.END, values=(
                            os_name, 
                            cmd["command"], 
                            cmd["description"], 
                            cmd["category"]
                        ))
                    break
    
    def show_favorite_details(self, event):
        """Show details for the selected favorite command"""
        tree = self.fav_tree
        selected = tree.selection()
        
        if not selected:
            return
        
        item = tree.item(selected[0])
        os_name, command, description, category = item["values"]
        
        # Find the command in our data
        for cmd in self.commands_data[os_name]:
            if cmd["command"] == command:
                self.show_command_details(os_name, cmd)
                return
    
    def create_os_tab(self, os_name, color):
        """Create a tab for a specific OS"""
        frame = ttk.Frame(self.notebook, style="TFrame")
        filter_frame = ttk.Frame(frame, style="TFrame")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(filter_frame, text="Filter:", bg="#0a0a0a", fg="#00ff00", 
                font=("Consolas", 10)).pack(side=tk.LEFT, padx=(0, 5))
        
        # Per-tab search/category variables
        self.search_vars[os_name] = tk.StringVar()
        self.category_vars[os_name] = tk.StringVar(value="All")
        
        search_entry = tk.Entry(
            filter_frame, 
            textvariable=self.search_vars[os_name], 
            bg="#121212", 
            fg="#00ff00", 
            insertbackground="#00ff00",
            font=("Consolas", 10),
            relief=tk.FLAT
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        search_entry.bind("<KeyRelease>", lambda e, os=os_name: self.filter_commands(os))
        
        categories = ["All", "File System", "Networking", "System Management", 
                     "Package Management", "Permissions", "Text Processing", "Utilities", "Storage", "Process Management", "Scripting"]
        category_menu = ttk.Combobox(
            filter_frame, 
            textvariable=self.category_vars[os_name], 
            values=categories,
            state="readonly",
            width=15
        )
        category_menu.config(style="Cyber.TCombobox")
        category_menu.pack(side=tk.RIGHT)
        category_menu.bind("<<ComboboxSelected>>", lambda e, os=os_name: self.filter_commands(os))
        
        # Create command list
        list_frame = ttk.Frame(frame, style="TFrame")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create Treeview with style
        style = ttk.Style()
        style.configure(f"{os_name}.Treeview", background="#121212", fieldbackground="#121212", 
                       foreground="#00ff00", font=("Consolas", 10))
        style.configure(f"{os_name}.Treeview.Heading", background=color, foreground="#00ff00", 
                       font=("Consolas", 10, "bold"))
        style.map(f"{os_name}.Treeview", background=[("selected", "#005500")])
        
        columns = ("command", "description", "category")
        tree = ttk.Treeview(
            list_frame, 
            columns=columns, 
            show="headings",
            style=f"{os_name}.Treeview",
            selectmode="browse"
        )
        
        # Configure columns
        tree.column("command", width=150, anchor=tk.W)
        tree.column("description", width=400, anchor=tk.W)
        tree.column("category", width=150, anchor=tk.W)
        
        # Create headings
        tree.heading("command", text="Command", anchor=tk.W)
        tree.heading("description", text="Description", anchor=tk.W)
        tree.heading("category", text="Category", anchor=tk.W)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection event
        tree.bind("<<TreeviewSelect>>", lambda e, os=os_name: self.show_command_details(os))
        
        # Store tree reference
        setattr(self, f"{os_name.lower()}_tree", tree)
        
        # Populate command list
        for cmd in self.commands_data[os_name]:
            tree.insert("", tk.END, values=(cmd["command"], cmd["description"], cmd["category"]))
        
        return frame
    
    def filter_commands(self, os_name):
        """Filter commands based on search text and category"""
        search_text = self.search_vars[os_name].get().lower()
        category = self.category_vars[os_name].get()
        tree = getattr(self, f"{os_name.lower()}_tree")
        for item in tree.get_children():
            tree.delete(item)
        for cmd in self.commands_data[os_name]:
            if (search_text in cmd["command"].lower() or 
                search_text in cmd["description"].lower()) and \
               (category == "All" or cmd["category"] == category):
                tree.insert("", tk.END, values=(cmd["command"], cmd["description"], cmd["category"]))
    
    def copy_to_clipboard(self):
        """Copy the current command to clipboard"""
        if hasattr(self, "current_cmd"):
            try:
                pyperclip.copy(self.current_cmd["command"])
                self.status_var.set(f"Command '{self.current_cmd['command']}' copied to clipboard")
            except pyperclip.PyperclipException:
                messagebox.showerror("Clipboard Error", "Failed to copy to clipboard.")
    
    def simulate_terminal_output(self):
        """Simulate terminal output in the status bar"""
        messages = [
            "Initializing system...",
            "Loading command database...",
            "Establishing secure connection...",
            "System ready for exploration",
            "Monitoring network activity...",
            "Scanning for vulnerabilities...",
            "Firewall active and monitoring",
            "Connection established with terminal servers",
            "Security protocols engaged",
            "RE_start operational at 100%",
            "Encrypting session data...",
            "Updating command cache...",
            "Verifying system integrity...",
            "Ready for user input"
        ]
        while self.terminal_sim_active:
            for msg in messages:
                if not self.terminal_sim_active:
                    break
                self.after(0, self.status_var.set, f">>> {msg}")
                time.sleep(2)
    
    def open_settings(self):
        """Open settings dialog"""
        settings = tk.Toplevel(self)
        settings.title("RE_start Settings")
        settings.geometry("400x300")
        settings.configure(bg="#0a0a0a")
        
        theme_frame = ttk.LabelFrame(settings, text="Theme Settings", style="TFrame")
        theme_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(theme_frame, text="Color Scheme:", bg="#0a0a0a", fg="#00ff00").pack(anchor=tk.W, padx=5, pady=5)
        
        theme_var = tk.StringVar(value="Cyberpunk")
        ttk.Radiobutton(theme_frame, text="Cyberpunk (Green)", variable=theme_var, value="Cyberpunk", style="Cyber.TRadiobutton").pack(anchor=tk.W, padx=10)
        ttk.Radiobutton(theme_frame, text="Matrix (Green/Black)", variable=theme_var, value="Matrix", style="Cyber.TRadiobutton").pack(anchor=tk.W, padx=10)
        ttk.Radiobutton(theme_frame, text="Neon (Blue/Purple)", variable=theme_var, value="Neon", style="Cyber.TRadiobutton").pack(anchor=tk.W, padx=10)
        
        other_frame = ttk.LabelFrame(settings, text="Other Settings", style="TFrame")
        other_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(other_frame, text="Animation Speed:", bg="#0a0a0a", fg="#00ff00").pack(anchor=tk.W, padx=5, pady=5)
        
        speed_var = tk.StringVar(value="Medium")
        speed_box = ttk.Combobox(other_frame, textvariable=speed_var, values=["Slow", "Medium", "Fast"], state="readonly", width=10)
        speed_box.pack(anchor=tk.W, padx=10, pady=5)
        
        def apply_settings():
            # Theme switching stub
            theme = theme_var.get()
            # Animation speed stub
            speed = speed_var.get()
            if speed == "Slow":
                self.animation_speed = 150
            elif speed == "Medium":
                self.animation_speed = 80
            elif speed == "Fast":
                self.animation_speed = 30
            self.status_var.set(f"Applied theme: {theme}, animation speed: {speed}")
            settings.destroy()
        
        ttk.Button(settings, text="Apply Settings", style="Cyber.TButton", command=apply_settings).pack(pady=10)
    
    def confirm_exit(self):
        """Confirm before exiting the application"""
        if messagebox.askyesno(
            "Exit RE_start", 
            "Are you sure you want to terminate the session?",
            icon="warning",
            parent=self
        ):
            self.terminal_sim_active = False
            self.status_var.set("System shutting down...")
            self.after(1000, self.destroy)

if __name__ == "__main__":
    app = RE_start()
    app.mainloop()
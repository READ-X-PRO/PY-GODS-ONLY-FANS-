import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import webbrowser
import random
import time
import sys
from PIL import Image, ImageTk
import threading

class RE_start(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RE_start - Terminal Commands Explorer")
        self.geometry("1000x700")
        self.configure(bg="#0a0a0a")
        self.style = ttk.Style()
        
        # Configure styles for hacking theme
        self.style.configure("TFrame", background="#0a0a0a")
        self.style.configure("TNotebook", background="#0a0a0a", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#121212", foreground="#00ff00", 
                            font=("Consolas", 10, "bold"), padding=[10, 5], borderwidth=1)
        self.style.map("TNotebook.Tab", background=[("selected", "#003300")])
        self.style.configure("Hacker.TButton", background="#003300", foreground="#00ff00", 
                            font=("Consolas", 10, "bold"), borderwidth=1)
        self.style.map("Hacker.TButton", background=[("active", "#005500")])
        
        # Create main frames
        self.create_header()
        self.create_main_content()
        self.create_footer()
        
        # Start terminal simulation
        self.start_terminal_simulation()
        
        # Terminal commands data
        self.commands_data = {
            "Linux": [
                {"command": "ls", "description": "List directory contents", "category": "File System"},
                {"command": "grep", "description": "Search text using patterns", "category": "Text Processing"},
                {"command": "chmod", "description": "Change file permissions", "category": "Permissions"},
                {"command": "ssh", "description": "Secure shell remote login", "category": "Networking"},
                {"command": "find", "description": "Search for files in directory hierarchy", "category": "File System"},
                {"command": "apt-get", "description": "Package management utility (Debian)", "category": "Package Management"},
                {"command": "systemctl", "description": "Control systemd system and service manager", "category": "System Management"},
                {"command": "cron", "description": "Time-based job scheduler", "category": "System Management"},
                {"command": "iptables", "description": "Administration tool for IPv4 packet filtering", "category": "Networking"},
                {"command": "dd", "description": "Convert and copy a file", "category": "System Management"}
            ],
            "Windows": [
                {"command": "dir", "description": "List directory contents", "category": "File System"},
                {"command": "ipconfig", "description": "Display network configuration", "category": "Networking"},
                {"command": "tasklist", "description": "Display running processes", "category": "Process Management"},
                {"command": "netsh", "description": "Network shell configuration tool", "category": "Networking"},
                {"command": "reg", "description": "Windows registry editor", "category": "System Management"},
                {"command": "choco", "description": "Chocolatey package manager", "category": "Package Management"},
                {"command": "powershell", "description": "Task automation framework", "category": "Scripting"},
                {"command": "wmic", "description": "Windows Management Instrumentation", "category": "System Management"},
                {"command": "netstat", "description": "Display network connections", "category": "Networking"},
                {"command": "sfc", "description": "System File Checker", "category": "System Management"}
            ],
            "macOS": [
                {"command": "ls", "description": "List directory contents", "category": "File System"},
                {"command": "brew", "description": "Homebrew package manager", "category": "Package Management"},
                {"command": "say", "description": "Convert text to speech", "category": "Utilities"},
                {"command": "pmset", "description": "Power management settings", "category": "System Management"},
                {"command": "diskutil", "description": "Disk management utility", "category": "Storage"},
                {"command": "networksetup", "description": "Network configuration tool", "category": "Networking"},
                {"command": "launchctl", "description": "Service management framework", "category": "System Management"},
                {"command": "screencapture", "description": "Screen capture utility", "category": "Utilities"},
                {"command": "airport", "description": "Wi-Fi diagnostic tool", "category": "Networking"},
                {"command": "defaults", "description": "Modify user defaults system", "category": "System Management"}
            ]
        }
        
        # Populate command lists
        self.populate_command_lists()
        
    def create_header(self):
        """Create the header with app title and matrix effect"""
        header_frame = ttk.Frame(self, style="TFrame")
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Title with hacking style
        title_label = tk.Label(
            header_frame, 
            text="RE_start", 
            font=("Courier", 28, "bold"), 
            fg="#00ff00", 
            bg="#0a0a0a",
            padx=10
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(
            header_frame, 
            text="Terminal Commands Explorer", 
            font=("Courier", 12), 
            fg="#00cc00", 
            bg="#0a0a0a"
        )
        subtitle_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Matrix effect canvas
        matrix_canvas = tk.Canvas(header_frame, width=200, height=40, bg="#0a0a0a", highlightthickness=0)
        matrix_canvas.pack(side=tk.RIGHT, padx=10)
        self.matrix_chars = []
        for _ in range(20):
            x = random.randint(0, 190)
            y = random.randint(0, 35)
            char = random.choice("01")
            char_id = matrix_canvas.create_text(
                x, y, 
                text=char, 
                fill="#00aa00", 
                font=("Courier", 8)
            )
            self.matrix_chars.append((char_id, x, y))
        
        # Animate matrix effect
        self.animate_matrix(matrix_canvas)
    
    def animate_matrix(self, canvas):
        """Animate the matrix effect in the header"""
        for char_id, x, y in self.matrix_chars:
            # Move character down
            y += 5
            if y > 40:
                y = 0
                x = random.randint(0, 190)
            
            # Update character position
            canvas.coords(char_id, x, y)
            
            # Occasionally change character
            if random.random() < 0.2:
                new_char = random.choice("01")
                canvas.itemconfig(char_id, text=new_char)
        
        self.after(100, lambda: self.animate_matrix(canvas))
    
    def create_main_content(self):
        """Create the main content area with OS tabs and command display"""
        main_frame = ttk.Frame(self, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create notebook for OS tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create OS tabs
        self.linux_frame = self.create_os_tab("Linux", "#003300")
        self.windows_frame = self.create_os_tab("Windows", "#000033")
        self.macos_frame = self.create_os_tab("macOS", "#330033")
        
        self.notebook.add(self.linux_frame, text=" Linux ")
        self.notebook.add(self.windows_frame, text=" Windows ")
        self.notebook.add(self.macos_frame, text=" macOS ")
        
        # Create command details panel
        details_frame = ttk.LabelFrame(main_frame, text="Command Details", style="TFrame")
        details_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10, ipady=5)
        
        self.details_text = scrolledtext.ScrolledText(
            details_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=8,
            bg="#121212", 
            fg="#00ff00", 
            insertbackground="#00ff00",
            font=("Consolas", 10),
            relief=tk.FLAT
        )
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.details_text.insert(tk.END, "Select a command to view details...")
        self.details_text.config(state=tk.DISABLED)
        
    def create_os_tab(self, os_name, color):
        """Create a tab for a specific OS"""
        frame = ttk.Frame(self.notebook, style="TFrame")
        
        # Create filter controls
        filter_frame = ttk.Frame(frame, style="TFrame")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(filter_frame, text="Filter:", bg="#0a0a0a", fg="#00ff00", 
                font=("Consolas", 10)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            filter_frame, 
            textvariable=self.search_var, 
            bg="#121212", 
            fg="#00ff00", 
            insertbackground="#00ff00",
            font=("Consolas", 10),
            relief=tk.FLAT
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        search_entry.bind("<KeyRelease>", lambda e, os=os_name: self.filter_commands(os))
        
        # Category filter
        categories = ["All", "File System", "Networking", "System Management", 
                     "Package Management", "Permissions", "Text Processing", "Utilities"]
        self.category_var = tk.StringVar(value="All")
        category_menu = ttk.Combobox(
            filter_frame, 
            textvariable=self.category_var, 
            values=categories,
            state="readonly",
            width=15
        )
        category_menu.config(style="Hacker.TCombobox")
        category_menu.pack(side=tk.RIGHT)
        category_menu.bind("<<ComboboxSelected>>", lambda e, os=os_name: self.filter_commands(os))
        
        # Create command list
        list_frame = ttk.Frame(frame, style="TFrame")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create Treeview with style
        style = ttk.Style()
        style.configure("Hacker.Treeview", background="#121212", fieldbackground="#121212", 
                       foreground="#00ff00", font=("Consolas", 10))
        style.configure("Hacker.Treeview.Heading", background="#003300", foreground="#00ff00", 
                       font=("Consolas", 10, "bold"))
        style.map("Hacker.Treeview", background=[("selected", "#005500")])
        
        columns = ("command", "description", "category")
        tree = ttk.Treeview(
            list_frame, 
            columns=columns, 
            show="headings",
            style="Hacker.Treeview",
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
        
        return frame
    
    def populate_command_lists(self):
        """Populate the command lists for each OS"""
        for os_name, commands in self.commands_data.items():
            tree = getattr(self, f"{os_name.lower()}_tree")
            for cmd in commands:
                tree.insert("", tk.END, values=(cmd["command"], cmd["description"], cmd["category"]))
    
    def filter_commands(self, os_name):
        """Filter commands based on search text and category"""
        search_text = self.search_var.get().lower()
        category = self.category_var.get()
        
        tree = getattr(self, f"{os_name.lower()}_tree")
        
        # Clear current items
        for item in tree.get_children():
            tree.delete(item)
        
        # Filter and insert matching commands
        for cmd in self.commands_data[os_name]:
            if (search_text in cmd["command"].lower() or 
                search_text in cmd["description"].lower()) and \
               (category == "All" or cmd["category"] == category):
                tree.insert("", tk.END, values=(cmd["command"], cmd["description"], cmd["category"]))
    
    def show_command_details(self, os_name):
        """Show details for the selected command"""
        tree = getattr(self, f"{os_name.lower()}_tree")
        selected = tree.selection()
        
        if not selected:
            return
        
        item = tree.item(selected[0])
        command, description, category = item["values"]
        
        # Generate command details
        details = f"Command: {command}\n"
        details += f"OS: {os_name}\n"
        details += f"Category: {category}\n\n"
        details += f"Description:\n{description}\n\n"
        
        # Add usage examples
        details += "Usage Examples:\n"
        if os_name == "Linux":
            if command == "ls":
                details += "  $ ls -l      # List in long format\n"
                details += "  $ ls -a      # List all files including hidden\n"
            elif command == "grep":
                details += "  $ grep 'pattern' file.txt\n"
                details += "  $ ps aux | grep 'process'\n"
        elif os_name == "Windows":
            if command == "dir":
                details += "  > dir /w     # Wide list format\n"
                details += "  > dir /a     # List all files including hidden\n"
            elif command == "ipconfig":
                details += "  > ipconfig /all\n"
                details += "  > ipconfig /release\n"
        elif os_name == "macOS":
            if command == "ls":
                details += "  $ ls -l      # List in long format\n"
                details += "  $ ls -a      # List all files including hidden\n"
            elif command == "brew":
                details += "  $ brew install package\n"
                details += "  $ brew update\n"
        
        # Add installation instructions for package managers
        if "package" in command.lower() or command in ["apt-get", "choco", "brew"]:
            details += "\nInstallation:\n"
            if command == "apt-get":
                details += "  Built-in on Debian-based Linux distributions\n"
            elif command == "choco":
                details += "  Install Chocolatey from https://chocolatey.org/install\n"
            elif command == "brew":
                details += "  Install Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"\n"
        
        # Display details
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, details)
        self.details_text.config(state=tk.DISABLED)
    
    def create_footer(self):
        """Create the footer with status bar and buttons"""
        footer_frame = ttk.Frame(self, style="TFrame")
        footer_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="System ready...")
        status_bar = tk.Label(
            footer_frame, 
            textvariable=self.status_var, 
            bg="#0a0a0a", 
            fg="#00cc00", 
            font=("Consolas", 9),
            anchor=tk.W
        )
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(footer_frame, style="TFrame")
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(
            button_frame, 
            text="Run Simulation", 
            style="Hacker.TButton",
            command=self.run_terminal_simulation
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Documentation", 
            style="Hacker.TButton",
            command=self.open_documentation
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Exit", 
            style="Hacker.TButton",
            command=self.confirm_exit
        ).pack(side=tk.LEFT, padx=5)
    
    def start_terminal_simulation(self):
        """Start a simulated terminal output in the background"""
        self.terminal_sim_active = True
        threading.Thread(target=self.simulate_terminal_output, daemon=True).start()
    
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
            "RE_start operational at 100%"
        ]
        
        while self.terminal_sim_active:
            for msg in messages:
                if not self.terminal_sim_active:
                    break
                self.status_var.set(f">>> {msg}")
                time.sleep(3)
    
    def run_terminal_simulation(self):
        """Run a terminal simulation in the details panel"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, "Starting terminal simulation...\n\n")
        
        # Simulate terminal output
        commands = [
            "$ whoami",
            "root",
            "",
            "$ uname -a",
            "Linux kali 5.10.0-kali9-amd64 #1 SMP Debian 5.10.46-4kali1 (2021-08-09) x86_64 GNU/Linux",
            "",
            "$ ip addr",
            "1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000",
            "    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00",
            "    inet 127.0.0.1/8 scope host lo",
            "       valid_lft forever preferred_lft forever",
            "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000",
            "    link/ether 08:00:27:4a:2d:48 brd ff:ff:ff:ff:ff:ff",
            "    inet 192.168.1.105/24 brd 192.168.1.255 scope global dynamic eth0",
            "       valid_lft 85678sec preferred_lft 85678sec",
            "",
            "$ ping -c 4 google.com",
            "PING google.com (142.250.185.206) 56(84) bytes of data.",
            "64 bytes from fra24s25-in-f14.1e100.net (142.250.185.206): icmp_seq=1 ttl=117 time=12.3 ms",
            "64 bytes from fra24s25-in-f14.1e100.net (142.250.185.206): icmp_seq=2 ttl=117 time=11.8 ms",
            "64 bytes from fra24s25-in-f14.1e100.net (142.250.185.206): icmp_seq=3 ttl=117 time=12.1 ms",
            "64 bytes from fra24s25-in-f14.1e100.net (142.250.185.206): icmp_seq=4 ttl=117 time=12.5 ms",
            "",
            "--- google.com ping statistics ---",
            "4 packets transmitted, 4 received, 0% packet loss, time 3005ms",
            "rtt min/avg/max/mdev = 11.879/12.208/12.543/0.269 ms",
            "",
            "$ exit",
            "Connection closed by remote host."
        ]
        
        # Insert each line with a delay to simulate typing
        for line in commands:
            self.details_text.insert(tk.END, line + "\n")
            self.details_text.see(tk.END)
            self.update()
            time.sleep(0.1)
        
        self.details_text.insert(tk.END, "\nSimulation complete. Select a command to view details.")
        self.details_text.config(state=tk.DISABLED)
    
    def open_documentation(self):
        """Open documentation in browser"""
        self.status_var.set("Opening online documentation...")
        webbrowser.open("https://en.wikipedia.org/wiki/List_of_command-line_commands")
    
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
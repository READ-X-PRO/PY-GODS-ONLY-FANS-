import os
import time
import random
import hashlib
import binascii
import sqlite3
import textwrap
import threading
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, Canvas, Frame

# Database setup
def init_database():
    conn = sqlite3.connect('restart_os.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS processes (
                 pid INTEGER PRIMARY KEY,
                 name TEXT,
                 priority INTEGER,
                 state TEXT,
                 security TEXT,
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS network_logs (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 event_type TEXT,
                 details TEXT,
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS encryption_logs (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 algorithm TEXT,
                 plaintext TEXT,
                 ciphertext TEXT,
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS pentest_results (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 tool TEXT,
                 target TEXT,
                 result TEXT,
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS system_status (
                 id INTEGER PRIMARY KEY,
                 security_level TEXT,
                 memory_protection INTEGER,
                 user_mode INTEGER,
                 network_monitor INTEGER,
                 promiscuous_mode INTEGER)''')
    
    # Initialize system status
    c.execute('''INSERT OR IGNORE INTO system_status 
                 (id, security_level, memory_protection, user_mode, network_monitor, promiscuous_mode)
                 VALUES (1, 'PARANOID', 1, 1, 0, 0)''')
    
    conn.commit()
    conn.close()

# Initialize database
init_database()

class REstartOS:
    def __init__(self):
        self.name = "RE_start"
        self.boot_time = datetime.now()
        self.load_system_status()
        self.add_boot_processes()
        
    def load_system_status(self):
        conn = sqlite3.connect('restart_os.db')
        c = conn.cursor()
        c.execute("SELECT security_level, memory_protection, user_mode, network_monitor, promiscuous_mode FROM system_status WHERE id=1")
        status = c.fetchone()
        conn.close()
        
        if status:
            self.security_level = status[0]
            self.memory_protection = bool(status[1])
            self.user_mode = bool(status[2])
            self.network_stack = {
                "monitor_mode": bool(status[3]),
                "promiscuous_mode": bool(status[4]),
                "connections": []
            }
        else:
            # Default values if no status found
            self.security_level = "PARANOID"
            self.memory_protection = True
            self.user_mode = True
            self.network_stack = {
                "monitor_mode": False,
                "promiscuous_mode": False,
                "connections": []
            }
    
    def save_system_status(self):
        conn = sqlite3.connect('restart_os.db')
        c = conn.cursor()
        c.execute('''UPDATE system_status SET 
                     security_level=?, memory_protection=?, user_mode=?, 
                     network_monitor=?, promiscuous_mode=?
                     WHERE id=1''', 
                 (self.security_level, int(self.memory_protection), int(self.user_mode),
                 int(self.network_stack["monitor_mode"]), int(self.network_stack["promiscuous_mode"])))
        conn.commit()
        conn.close()
    
    def add_boot_processes(self):
        boot_processes = [
            (1, "System Kernel", 0, "Running", "Kernel"),
            (2, "Security Monitor", 0, "Running", "Kernel"),
            (3, "Memory Manager", 1, "Running", "Kernel"),
            (4, "Network Stack", 1, "Running", "Kernel"),
            (5, "Crypto Engine", 1, "Running", "Kernel"),
            (6, "Driver Manager", 2, "Running", "User")
        ]
        
        conn = sqlite3.connect('restart_os.db')
        c = conn.cursor()
        
        # Clear existing processes and add boot processes
        c.execute("DELETE FROM processes")
        c.executemany("INSERT INTO processes (pid, name, priority, state, security) VALUES (?, ?, ?, ?, ?)", boot_processes)
        
        conn.commit()
        conn.close()
    
    def create_process(self, name, priority=5, security="User"):
        conn = sqlite3.connect('restart_os.db')
        c = conn.cursor()
        
        # Find next available PID
        c.execute("SELECT MAX(pid) FROM processes")
        max_pid = c.fetchone()[0] or 100
        pid = max_pid + 1
        
        c.execute("INSERT INTO processes (pid, name, priority, state, security) VALUES (?, ?, ?, ?, ?)",
                 (pid, name, priority, "Running", security))
        
        conn.commit()
        conn.close()
        return pid
    
    def terminate_process(self, pid):
        conn = sqlite3.connect('restart_os.db')
        c = conn.cursor()
        c.execute("UPDATE processes SET state='Terminated' WHERE pid=?", (pid,))
        updated = c.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    
    def list_processes(self):
        conn = sqlite3.connect('restart_os.db')
        c = conn.cursor()
        c.execute("SELECT pid, name, priority, state, security FROM processes WHERE state='Running' ORDER BY pid")
        processes = c.fetchall()
        conn.close()
        return processes
    
    def toggle_network_monitor(self):
        self.network_stack["monitor_mode"] = not self.network_stack["monitor_mode"]
        self.save_system_status()
        self.log_network_event("MONITOR_MODE", 
                              f"Network monitor mode {'ENABLED' if self.network_stack['monitor_mode'] else 'DISABLED'}")
        return self.network_stack["monitor_mode"]
    
    def toggle_promiscuous_mode(self):
        self.network_stack["promiscuous_mode"] = not self.network_stack["promiscuous_mode"]
        self.save_system_status()
        self.log_network_event("PROMISCUOUS_MODE", 
                              f"Promiscuous mode {'ENABLED' if self.network_stack['promiscuous_mode'] else 'DISABLED'}")
        return self.network_stack["promiscuous_mode"]
    
    def log_network_event(self, event_type, details):
        conn = sqlite3.connect('restart_os.db')
        c = conn.cursor()
        c.execute("INSERT INTO network_logs (event_type, details) VALUES (?, ?)", (event_type, details))
        conn.commit()
        conn.close()
    
    def log_encryption(self, algorithm, plaintext, ciphertext):
        conn = sqlite3.connect('restart_os.db')
        c = conn.cursor()
        c.execute("INSERT INTO encryption_logs (algorithm, plaintext, ciphertext) VALUES (?, ?, ?)",
                 (algorithm, plaintext, ciphertext))
        conn.commit()
        conn.close()
    
    def log_pentest(self, tool, target, result):
        conn = sqlite3.connect('restart_os.db')
        c = conn.cursor()
        c.execute("INSERT INTO pentest_results (tool, target, result) VALUES (?, ?, ?)",
                 (tool, target, result))
        conn.commit()
        conn.close()
    
    def encrypt_data(self, data, algorithm="AES-256"):
        if algorithm == "AES-256":
            # Simulate encryption
            salt = os.urandom(16)
            key = hashlib.pbkdf2_hmac('sha256', b'secret_key', salt, 100000)
            cipher_text = hashlib.sha256(data.encode()).hexdigest()
            result = f"{algorithm}:{binascii.hexlify(salt).decode()}:{cipher_text}"
        elif algorithm == "RSA-4096":
            # Simulate RSA
            result = f"{algorithm}:RSA_ENCRYPTED_{hashlib.sha256(data.encode()).hexdigest()[:20]}"
        else:
            result = "Unsupported algorithm"
        
        self.log_encryption(algorithm, data, result)
        return result
    
    def run_pentest_tool(self, tool, target=""):
        if tool == "Port Scanner":
            ports = [21, 22, 80, 443, 8080, 8443, 3306, 5432]
            open_ports = random.sample(ports, random.randint(1, 4))
            result = f"Scanning {target}... Open ports: {', '.join(str(p) for p in open_ports)}"
        elif tool == "Vulnerability Scanner":
            vulns = ["Heartbleed", "Shellshock", "EternalBlue", "SQL Injection", "XSS", "CSRF"]
            found = random.sample(vulns, random.randint(0, 3))
            result = f"Scanning {target}... Vulnerabilities found: {', '.join(found) if found else 'None'}"
        elif tool == "Password Cracker":
            cracked = random.randint(1, 5)
            result = f"Cracking hashes on {target}... Found {cracked} weak passwords"
        elif tool == "Forensic Analyzer":
            artifacts = ["Browser History", "Deleted Files", "Registry Entries", "Log Files"]
            found = random.sample(artifacts, random.randint(2, 4))
            result = f"Analyzing {target}... Found artifacts: {', '.join(found)}"
        else:
            result = f"Running {tool} on {target}... Scan completed"
        
        self.log_pentest(tool, target, result)
        return result


class MatrixAnimation(Canvas):
    def __init__(self, parent, width, height, **kwargs):
        super().__init__(parent, width=width, height=height, **kwargs)
        self.configure(bg='black', highlightthickness=0)
        self.width = width
        self.height = height
        self.font_size = 14
        self.columns = width // self.font_size
        self.drops = [0] * self.columns
        self.chars = "01" * 100  # Only 0s and 1s for binary look
        self.running = True
        self.after(50, self.animate)
    
    def animate(self):
        if not self.running:
            return
            
        self.delete("matrix")
        
        # Set text color with some variation
        for i in range(len(self.drops)):
            char = random.choice(self.chars)
            x = i * self.font_size
            y = self.drops[i] * self.font_size
            
            # Create fading effect - characters further down are dimmer
            intensity = max(50, 255 - (y * 255 // self.height))
            color = f'#00{intensity:02x}00'  # Green with varying intensity
            
            self.create_text(x, y, text=char, fill=color, 
                           font=('Courier', self.font_size, 'bold'), 
                           anchor='nw', tag="matrix")
            
            # Reset drop if it reached the bottom or randomly
            if y > self.height or random.random() > 0.95:
                self.drops[i] = 0
            else:
                self.drops[i] += 1
        
        self.after(50, self.animate)
    
    def stop(self):
        self.running = False


class TerminalUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RE_start OS - Ethical Hacking Environment")
        self.root.geometry("1000x750")
        self.root.configure(bg="#001100")
        
        # Set icon (if available)
        try:
            self.root.iconbitmap("hacker.ico")  # Placeholder for actual icon
        except:
            pass
        
        self.os = REstartOS()
        self.current_dir = "/root"
        self.command_history = []
        self.history_index = -1
        
        # Create custom style
        self.style = ttk.Style()
        self.style.configure("Green.TFrame", background="#001100")
        self.style.configure("Green.TLabel", background="#001100", foreground="#00ff00")
        self.style.configure("Green.TButton", background="#002200", foreground="#00ff00")
        self.style.configure("Terminal.TEntry", fieldbackground="#002200", foreground="#00ff00")
        
        # Header with Matrix animation
        header_frame = Frame(root, bg="#001100")
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create Matrix animation canvas
        self.matrix = MatrixAnimation(header_frame, width=900, height=80)
        self.matrix.pack()
        
        # Add OS name label on top of the Matrix animation
        os_name = "RE_start"
        binary_name = ' '.join(format(ord(c), '08b') for c in os_name)
        
        self.os_label = tk.Label(
            header_frame, 
            text=f"{os_name} OS\n{binary_name}", 
            bg="#001100", fg="#00ff00",
            font=("Courier", 14, "bold"),
            justify="center"
        )
        self.os_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # System status bar
        status_frame = ttk.Frame(root, style="Green.TFrame")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_var = tk.StringVar()
        self.update_status()
        
        status = ttk.Label(
            status_frame, 
            textvariable=self.status_var,
            style="Green.TLabel",
            font=("Courier", 10)
        )
        status.pack(fill=tk.X)
        
        # Terminal output
        output_frame = ttk.Frame(root, style="Green.TFrame")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.output = scrolledtext.ScrolledText(
            output_frame,
            bg="#001100",
            fg="#00ff00",
            insertbackground="#00ff00",
            font=("Courier", 11),
            wrap=tk.WORD,
            relief=tk.FLAT
        )
        self.output.pack(fill=tk.BOTH, expand=True)
        self.output.config(state=tk.DISABLED)
        
        # Add realistic terminal header
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, "RE_start OS v1.0 - Security Research Environment\n")
        self.output.insert(tk.END, "Copyright (C) 2023 DeepSeek Security Labs\n\n")
        self.output.insert(tk.END, "Initializing security subsystems...\n")
        self.output.insert(tk.END, "Loading kernel modules...\n")
        self.output.insert(tk.END, "Activating memory protection...\n")
        self.output.insert(tk.END, "Starting network services...\n")
        self.output.insert(tk.END, "Crypto engine ready...\n")
        self.output.insert(tk.END, "Forensic toolkit initialized...\n\n")
        self.output.insert(tk.END, "System ready for security operations\n")
        self.output.insert(tk.END, "Type 'help' for available commands\n\n")
        self.output.config(state=tk.DISABLED)
        
        # Command input
        input_frame = ttk.Frame(root, style="Green.TFrame")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.prompt = ttk.Label(
            input_frame, 
            text=f"root@RE_start:{self.current_dir}# ",
            style="Green.TLabel",
            font=("Courier", 11)
        )
        self.prompt.pack(side=tk.LEFT)
        
        self.cmd_entry = ttk.Entry(
            input_frame, 
            width=80,
            style="Terminal.TEntry",
            font=("Courier", 11)
        )
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.cmd_entry.bind("<Return>", self.execute_command)
        self.cmd_entry.bind("<Up>", self.history_up)
        self.cmd_entry.bind("<Down>", self.history_down)
        self.cmd_entry.bind("<Tab>", self.tab_complete)
        self.cmd_entry.focus()
        
        # Configure tags for colored output
        self.output.tag_config("success", foreground="#00ff00")
        self.output.tag_config("error", foreground="#ff5555")
        self.output.tag_config("warning", foreground="#ffff00")
        self.output.tag_config("highlight", foreground="#00ffff")
        self.output.tag_config("system", foreground="#00aaff")
        
        # Start blinking cursor simulation
        self.cursor_visible = True
        self.blink_cursor()
    
    def update_status(self):
        status_text = (f"Security Level: {self.os.security_level} | "
                      f"Uptime: {self.get_uptime()} | "
                      f"Mode: {'User' if self.os.user_mode else 'Kernel'} | "
                      f"Processes: {len(self.os.list_processes())} | "
                      f"Network: {'MON' if self.os.network_stack['monitor_mode'] else ''} "
                      f"{'PROM' if self.os.network_stack['promiscuous_mode'] else ''}")
        self.status_var.set(status_text)
        self.root.after(1000, self.update_status)
    
    def get_uptime(self):
        delta = datetime.now() - self.os.boot_time
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def add_output(self, text, tag=None):
        self.output.config(state=tk.NORMAL)
        if tag:
            self.output.insert(tk.END, text, tag)
        else:
            self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)
    
    def blink_cursor(self):
        if self.cursor_visible:
            self.prompt.config(text=f"root@RE_start:{self.current_dir}# ")
        else:
            self.prompt.config(text=f"root@RE_start:{self.current_dir}$ ")
        
        self.cursor_visible = not self.cursor_visible
        self.root.after(500, self.blink_cursor)
    
    def execute_command(self, event=None):
        command = self.cmd_entry.get().strip()
        self.cmd_entry.delete(0, tk.END)
        
        if not command:
            return
        
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        self.add_output(f"root@RE_start:{self.current_dir}# {command}\n")
        
        # Process command
        cmd_parts = command.split()
        primary_cmd = cmd_parts[0].lower() if cmd_parts else ""
        
        if primary_cmd == "help":
            self.show_help()
        elif primary_cmd == "clear":
            self.output.config(state=tk.NORMAL)
            self.output.delete(1.0, tk.END)
            self.output.config(state=tk.DISABLED)
        elif primary_cmd == "ps":
            self.list_processes()
        elif primary_cmd == "start":
            self.start_process(cmd_parts[1:])
        elif primary_cmd == "kill":
            self.kill_process(cmd_parts[1:])
        elif primary_cmd == "drivers":
            self.list_drivers()
        elif primary_cmd == "fs":
            self.list_filesystems()
        elif primary_cmd == "mem":
            self.show_memory_status()
        elif primary_cmd == "mode":
            self.show_mode()
        elif primary_cmd == "net":
            self.network_commands(cmd_parts[1:])
        elif primary_cmd == "encrypt":
            self.encrypt_data(cmd_parts[1:])
        elif primary_cmd == "decrypt":
            self.decrypt_data(cmd_parts[1:])
        elif primary_cmd == "pentest":
            self.run_pentest(cmd_parts[1:])
        elif primary_cmd == "history":
            self.show_history()
        elif primary_cmd == "exit":
            self.shutdown_os()
        else:
            self.add_output(f"Command not found: {primary_cmd}\n", "error")
    
    def history_up(self, event):
        if self.command_history:
            if self.history_index > 0:
                self.history_index -= 1
            self.cmd_entry.delete(0, tk.END)
            self.cmd_entry.insert(0, self.command_history[self.history_index])
    
    def history_down(self, event):
        if self.command_history:
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.cmd_entry.delete(0, tk.END)
                self.cmd_entry.insert(0, self.command_history[self.history_index])
            else:
                self.history_index = len(self.command_history)
                self.cmd_entry.delete(0, tk.END)
    
    def tab_complete(self, event):
        current = self.cmd_entry.get().lower()
        commands = ["help", "clear", "ps", "start", "kill", "drivers", "fs", 
                   "mem", "mode", "net", "encrypt", "decrypt", "pentest", "history", "exit"]
        
        matches = [cmd for cmd in commands if cmd.startswith(current)]
        
        if matches:
            self.cmd_entry.delete(0, tk.END)
            self.cmd_entry.insert(0, matches[0])
        
        return "break"
    
    def show_help(self):
        help_text = """
        Available commands:
          help          - Show this help message
          clear         - Clear terminal screen
          ps            - List running processes
          start <name>  - Start a new process
          kill <pid>    - Terminate a process by PID
          drivers       - List loaded drivers
          fs            - Show filesystem information
          mem           - Show memory protection status
          mode          - Show current execution mode
          net [cmd]     - Network operations (monitor, promisc, scan)
          encrypt <text> - Encrypt text using AES-256
          decrypt <cipher> - Decrypt text (simulated)
          pentest [tool] [target] - Run penetration testing tools
          history       - Show command history
          exit          - Shutdown the OS
        """
        self.add_output(textwrap.dedent(help_text), "system")
    
    def list_processes(self):
        processes = self.os.list_processes()
        self.add_output("PID\tName\t\tPriority\tState\t\tSecurity\n", "highlight")
        self.add_output("="*60 + "\n")
        for p in processes:
            self.add_output(f"{p[0]}\t{p[1][:12]}\t{p[2]}\t\t{p[3]}\t{p[4]}\n")
    
    def start_process(self, args):
        if not args:
            self.add_output("Usage: start <process_name>\n", "error")
            return
            
        name = " ".join(args)
        pid = self.os.create_process(name)
        self.add_output(f"Started process '{name}' with PID {pid}\n", "success")
    
    def kill_process(self, args):
        if not args:
            self.add_output("Usage: kill <pid>\n", "error")
            return
            
        try:
            pid = int(args[0])
            if self.os.terminate_process(pid):
                self.add_output(f"Process {pid} terminated\n", "success")
            else:
                self.add_output(f"No running process with PID {pid}\n", "error")
        except ValueError:
            self.add_output("Invalid PID. Must be an integer.\n", "error")
    
    def list_drivers(self):
        drivers = [
            "Ethernet Controller", "Wireless (Monitor Mode)", 
            "Disk Controller", "USB 3.0", "TPM 2.0", "Crypto Accelerator"
        ]
        self.add_output("Loaded drivers:\n", "highlight")
        for driver in drivers:
            self.add_output(f" - {driver}\n")
    
    def list_filesystems(self):
        filesystems = ["SECFS (Encrypted)", "FORENSICFS (Write-Protected)", "TMPFS (Volatile)"]
        self.add_output("Supported filesystems:\n", "highlight")
        for fs in filesystems:
            self.add_output(f" - {fs}\n")
    
    def show_memory_status(self):
        status = "ACTIVE" if self.os.memory_protection else "DISABLED"
        self.add_output(f"Memory Protection: {status}\n", "highlight")
        self.add_output("Memory regions protected: Kernel space, Process isolation, Secure enclaves\n")
    
    def show_mode(self):
        mode = "User" if self.os.user_mode else "Kernel"
        self.add_output(f"Current execution mode: {mode}\n", "highlight")
        self.add_output("(System processes run in Kernel mode for security)\n")
    
    def network_commands(self, args):
        if not args:
            self.add_output("Network commands: monitor, promisc, scan\n", "error")
            return
            
        cmd = args[0].lower()
        
        if cmd == "monitor":
            mode = self.os.toggle_network_monitor()
            status = "ENABLED" if mode else "DISABLED"
            self.add_output(f"Network monitor mode {status}\n", "success")
        elif cmd == "promisc":
            mode = self.os.toggle_promiscuous_mode()
            status = "ENABLED" if mode else "DISABLED"
            self.add_output(f"Promiscuous mode {status}\n", "success")
        elif cmd == "scan":
            target = args[1] if len(args) > 1 else "192.168.1.0/24"
            self.add_output(f"Scanning network: {target}\n", "highlight")
            self.add_output("Discovering hosts...\n")
            
            # Simulate scanning with realistic output
            self.add_output("Starting Nmap 7.92 ( https://nmap.org ) at UTC\n")
            time.sleep(0.5)
            
            hosts = random.randint(5, 20)
            for i in range(hosts):
                ip = f"192.168.1.{random.randint(1, 254)}"
                mac = ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))
                self.add_output(f"Discovered host: {ip} [MAC: {mac}]\n")
                time.sleep(0.1)
            
            self.add_output(f"Nmap scan report for {target}\n", "highlight")
            self.add_output(f"Hosts: {hosts} up | Latency: {random.uniform(0.1, 5.0):.2f}ms\n")
            self.add_output("Scan complete.\n", "success")
        else:
            self.add_output(f"Unknown network command: {cmd}\n", "error")
    
    def encrypt_data(self, args):
        if not args:
            self.add_output("Usage: encrypt <text>\n", "error")
            return
            
        text = " ".join(args)
        encrypted = self.os.encrypt_data(text)
        self.add_output(f"Encrypted data: {encrypted}\n", "highlight")
        self.add_output("Algorithm: AES-256 with PBKDF2 key derivation\n")
    
    def decrypt_data(self, args):
        if not args:
            self.add_output("Usage: decrypt <ciphertext>\n", "error")
            return
            
        cipher = " ".join(args)
        self.add_output("Decrypting data...\n")
        
        # Simulate decryption process
        self.add_output("Accessing key vault...\n")
        time.sleep(0.5)
        self.add_output("Verifying key integrity...\n")
        time.sleep(0.3)
        self.add_output("Applying decryption algorithm...\n")
        time.sleep(0.7)
        
        # Generate fake plaintext
        texts = [
            "The quick brown fox jumps over the lazy dog",
            "Security is a process, not a product",
            "Encryption is the foundation of modern security",
            "Always verify before you trust",
            "RE_start OS provides unparalleled security"
        ]
        
        self.add_output(f"Decrypted text: {random.choice(texts)}\n", "success")
    
    def run_pentest(self, args):
        if not args:
            self.add_output("Available pentest tools:\n", "highlight")
            tools = [
                "Port Scanner", "Vulnerability Scanner", "Packet Analyzer", 
                "Exploit Framework", "Password Cracker", "Forensic Analyzer"
            ]
            for tool in tools:
                self.add_output(f" - {tool}\n")
            return
            
        tool = args[0]
        target = args[1] if len(args) > 1 else "localhost"
        
        tools = [
            "Port Scanner", "Vulnerability Scanner", "Packet Analyzer", 
            "Exploit Framework", "Password Cracker", "Forensic Analyzer"
        ]
        
        if tool not in tools:
            self.add_output(f"Unknown tool: {tool}\n", "error")
            return
            
        self.add_output(f"Starting {tool} on {target}...\n", "highlight")
        
        # Add realistic scanning animation
        self.add_output("[")
        for _ in range(20):
            self.add_output("#")
            self.root.update()
            time.sleep(0.05)
        self.add_output("]\n")
        
        result = self.os.run_pentest_tool(tool, target)
        self.add_output(result + "\n", "success")
        self.add_output("Operation completed successfully.\n")
    
    def show_history(self):
        self.add_output("Command history:\n", "highlight")
        for i, cmd in enumerate(self.command_history, 1):
            self.add_output(f"{i}: {cmd}\n")
    
    def shutdown_os(self):
        self.add_output("Initiating system shutdown...\n", "system")
        self.add_output("Terminating processes...\n")
        self.add_output("Saving system state...\n")
        self.add_output("Unmounting filesystems...\n")
        self.add_output("Stopping network services...\n")
        self.add_output("RE_start OS shutdown complete.\n\n", "highlight")
        self.matrix.stop()
        self.root.after(2000, self.root.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    app = TerminalUI(root)
    root.mainloop()
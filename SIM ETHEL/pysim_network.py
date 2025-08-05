import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import random
import json
import os
import uuid
from datetime import datetime
import math
import threading
import time
import socket
import webbrowser
import subprocess

# Xbox-inspired purple theme
PURPLE_THEME = {
    "dark_bg": "#1a1a1a",
    "darker_bg": "#0d0d0d",
    "card_bg": "#2d2d2d",
    "purple": "#8a2be2",
    "light_purple": "#9b4fff",
    "dark_purple": "#6a0dad",
    "accent": "#00b7eb",
    "text": "#ffffff",
    "secondary_text": "#b3b3b3",
    "success": "#4CAF50",
    "warning": "#FFC107",
    "error": "#F44336"
}

class AnimatedButton(tk.Canvas):
    def __init__(self, master, text, command, width=120, height=40, corner_radius=8, **kwargs):
        super().__init__(master, width=width, height=height, 
                         highlightthickness=0, bd=0, bg=PURPLE_THEME["dark_bg"])
        self.command = command
        self.corner_radius = corner_radius
        self.width = width
        self.height = height
        self.text = text
        
        # Draw button
        self.id = self.draw_button(PURPLE_THEME["purple"])
        self.text_id = self.create_text(width/2, height/2, text=text, 
                                       fill=PURPLE_THEME["text"], 
                                       font=("Segoe UI", 10, "bold"))
        
        # Bind events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
    def draw_button(self, color):
        return self.create_round_rect(0, 0, self.width, self.height, 
                                      self.corner_radius, fill=color)
    
    def create_round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y1+r,
            x1, y1,
            x1+r, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)
    
    def on_enter(self, event):
        self.itemconfig(self.id, fill=PURPLE_THEME["light_purple"])
        self.config(cursor="hand2")
        
    def on_leave(self, event):
        self.itemconfig(self.id, fill=PURPLE_THEME["purple"])
        
    def on_click(self, event):
        self.itemconfig(self.id, fill=PURPLE_THEME["dark_purple"])
        self.after(150, lambda: self.itemconfig(self.id, fill=PURPLE_THEME["light_purple"]))
        self.command()

class PySimApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PySIM Manager - Network Edition")
        self.root.geometry("1100x750")
        self.root.resizable(True, True)
        self.root.configure(bg=PURPLE_THEME["dark_bg"])
        
        # Configure style
        self.configure_styles()
        
        # Create header
        self.create_header()
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root, style="Purple.TNotebook")
        self.notebook.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create tabs
        self.tab_sim_info = ttk.Frame(self.notebook, style="Card.TFrame")
        self.tab_auth = ttk.Frame(self.notebook, style="Card.TFrame")
        self.tab_esim = ttk.Frame(self.notebook, style="Card.TFrame")
        self.tab_networking = ttk.Frame(self.notebook, style="Card.TFrame")
        self.tab_logs = ttk.Frame(self.notebook, style="Card.TFrame")
        
        self.notebook.add(self.tab_sim_info, text="SIM Information")
        self.notebook.add(self.tab_auth, text="Authentication")
        self.notebook.add(self.tab_esim, text="eSIM Management")
        self.notebook.add(self.tab_networking, text="Networking")
        self.notebook.add(self.tab_logs, text="Event Logs")
        
        # Initialize components
        self.create_sim_info_tab()
        self.create_auth_tab()
        self.create_esim_tab()
        self.create_networking_tab()
        self.create_logs_tab()
        
        # Current SIM data
        self.current_sim = self.generate_new_sim()
        self.load_sim_data()
        self.log_events = []
        self.log_event("Application started")
        
        # Status bar
        self.status_bar = ttk.Label(root, text="Ready", style="Status.TLabel")
        self.status_bar.pack(fill='x', padx=20, pady=(0, 10))
        
        # Network status
        self.network_status = "Disconnected"
        self.data_usage = {"upload": 0, "download": 0}
        self.network_speed = 0
        self.network_thread = None
        self.network_running = False
        
        # Animation
        self.animate_header()
    
    def configure_styles(self):
        style = ttk.Style()
        
        # Theme settings
        style.theme_create("purple_theme", parent="alt", settings={
            "TFrame": {"configure": {"background": PURPLE_THEME["dark_bg"]}},
            "TNotebook": {"configure": {"background": PURPLE_THEME["darker_bg"], "borderwidth": 0}},
            "TNotebook.Tab": {
                "configure": {
                    "background": PURPLE_THEME["card_bg"], 
                    "foreground": PURPLE_THEME["secondary_text"],
                    "padding": [15, 5],
                    "font": ("Segoe UI", 10)
                },
                "map": {
                    "background": [("selected", PURPLE_THEME["purple"])],
                    "foreground": [("selected", PURPLE_THEME["text"])],
                    "expand": [("selected", [1, 1, 1, 0])]
                }
            },
            "TLabel": {
                "configure": {
                    "background": PURPLE_THEME["dark_bg"],
                    "foreground": PURPLE_THEME["text"],
                    "font": ("Segoe UI", 9)
                }
            },
            "TEntry": {
                "configure": {
                    "fieldbackground": PURPLE_THEME["card_bg"],
                    "foreground": PURPLE_THEME["text"],
                    "insertcolor": PURPLE_THEME["text"],
                    "borderwidth": 1,
                    "relief": "flat",
                    "padding": 5
                }
            },
            "TCombobox": {
                "configure": {
                    "fieldbackground": PURPLE_THEME["card_bg"],
                    "foreground": PURPLE_THEME["text"],
                    "background": PURPLE_THEME["card_bg"],
                    "selectbackground": PURPLE_THEME["purple"],
                    "selectforeground": PURPLE_THEME["text"],
                    "arrowcolor": PURPLE_THEME["text"],
                    "borderwidth": 1,
                    "relief": "flat",
                    "padding": 5
                },
                "map": {
                    "fieldbackground": [("readonly", PURPLE_THEME["card_bg"])],
                    "background": [("readonly", PURPLE_THEME["card_bg"])]
                }
            },
            "Vertical.TScrollbar": {
                "configure": {
                    "background": PURPLE_THEME["purple"],
                    "troughcolor": PURPLE_THEME["darker_bg"],
                    "arrowcolor": PURPLE_THEME["text"],
                    "bordercolor": PURPLE_THEME["dark_bg"],
                    "lightcolor": PURPLE_THEME["purple"],
                    "darkcolor": PURPLE_THEME["dark_purple"]
                }
            }
        })
        style.theme_use("purple_theme")
        
        # Custom styles
        style.configure("Card.TFrame", background=PURPLE_THEME["card_bg"], borderwidth=0)
        style.configure("Header.TFrame", background=PURPLE_THEME["darker_bg"])
        style.configure("Purple.TNotebook", background=PURPLE_THEME["darker_bg"], borderwidth=0)
        style.configure("Status.TLabel", background=PURPLE_THEME["darker_bg"], 
                        foreground=PURPLE_THEME["secondary_text"], font=("Segoe UI", 8))
        style.configure("Header.TLabel", background=PURPLE_THEME["darker_bg"], 
                        foreground=PURPLE_THEME["text"], font=("Segoe UI", 24, "bold"))
        style.configure("Subheader.TLabel", background=PURPLE_THEME["darker_bg"], 
                        foreground=PURPLE_THEME["accent"], font=("Segoe UI", 10))
        style.configure("Purple.TLabelframe", background=PURPLE_THEME["card_bg"], 
                        foreground=PURPLE_THEME["light_purple"], font=("Segoe UI", 10, "bold"))
        style.configure("Purple.TLabelframe.Label", background=PURPLE_THEME["card_bg"], 
                        foreground=PURPLE_THEME["light_purple"])
        style.configure("TechLabel.TLabel", background=PURPLE_THEME["card_bg"], 
                        foreground=PURPLE_THEME["accent"], font=("Consolas", 9))
        style.configure("TechValue.TLabel", background=PURPLE_THEME["card_bg"], 
                        foreground=PURPLE_THEME["text"], font=("Consolas", 9, "bold"))
        style.configure("NetworkStatus.TLabel", background=PURPLE_THEME["card_bg"], 
                        foreground=PURPLE_THEME["success"], font=("Segoe UI", 10, "bold"))
        
        # Configure scrollbar
        style.configure("TScrollbar", gripcount=0, background=PURPLE_THEME["purple"], 
                        troughcolor=PURPLE_THEME["darker_bg"])
    
    def create_header(self):
        header = ttk.Frame(self.root, style="Header.TFrame", height=80)
        header.pack(fill='x', padx=20, pady=(20, 10))
        
        # Logo and title
        self.logo_canvas = tk.Canvas(header, width=50, height=50, bg=PURPLE_THEME["darker_bg"], 
                                     highlightthickness=0)
        self.logo_canvas.pack(side='left', padx=(20, 10), pady=10)
        self.draw_logo()
        
        ttk.Label(header, text="PySIM Manager", style="Header.TLabel").pack(side='left', pady=20)
        ttk.Label(header, text="Network Edition", style="Subheader.TLabel").pack(side='left', padx=(10, 0), pady=20)
        
        # Status indicators
        status_frame = ttk.Frame(header, style="Header.TFrame")
        status_frame.pack(side='right', padx=20, pady=20)
        
        ttk.Label(status_frame, text="SIM Status:", style="Header.TLabel").pack(side='left')
        self.status_indicator = tk.Canvas(status_frame, width=20, height=20, bg=PURPLE_THEME["darker_bg"], 
                                          highlightthickness=0)
        self.status_indicator.pack(side='left', padx=10)
        self.status_indicator.create_oval(2, 2, 18, 18, fill=PURPLE_THEME["success"], outline="")
        
        # Network status
        ttk.Label(status_frame, text="Network:", style="Header.TLabel").pack(side='left', padx=(20, 5))
        self.net_indicator = tk.Canvas(status_frame, width=20, height=20, bg=PURPLE_THEME["darker_bg"], 
                                          highlightthickness=0)
        self.net_indicator.pack(side='left')
        self.net_indicator.create_oval(2, 2, 18, 18, fill=PURPLE_THEME["error"], outline="")
    
    def draw_logo(self):
        # Draw Xbox-inspired logo
        self.logo_canvas.delete("all")
        size = 50
        center = size/2
        
        # Draw X symbol
        self.logo_canvas.create_line(center-10, center-10, center+10, center+10, 
                                     width=3, fill=PURPLE_THEME["accent"])
        self.logo_canvas.create_line(center+10, center-10, center-10, center+10, 
                                     width=3, fill=PURPLE_THEME["accent"])
        
        # Draw circle
        self.logo_canvas.create_oval(5, 5, size-5, size-5, 
                                     outline=PURPLE_THEME["purple"], width=2)
        
        # Draw SIM chip
        chip_size = 12
        self.logo_canvas.create_rectangle(center-chip_size/2, center-chip_size/2, 
                                          center+chip_size/2, center+chip_size/2, 
                                          fill=PURPLE_THEME["dark_purple"], outline="")
        
        # Draw chip contacts
        for i in range(4):
            offset = i * 3
            self.logo_canvas.create_rectangle(center-chip_size/2+offset, center-chip_size/2-3, 
                                              center-chip_size/2+offset+1, center-chip_size/2, 
                                              fill=PURPLE_THEME["accent"], outline="")
            self.logo_canvas.create_rectangle(center+chip_size/2, center-chip_size/2+offset, 
                                              center+chip_size/2+3, center-chip_size/2+offset+1, 
                                              fill=PURPLE_THEME["accent"], outline="")
            self.logo_canvas.create_rectangle(center+chip_size/2-offset-1, center+chip_size/2, 
                                              center+chip_size/2-offset, center+chip_size/2+3, 
                                              fill=PURPLE_THEME["accent"], outline="")
            self.logo_canvas.create_rectangle(center-chip_size/2-3, center+chip_size/2-offset-1, 
                                              center-chip_size/2, center+chip_size/2-offset, 
                                              fill=PURPLE_THEME["accent"], outline="")
    
    def animate_header(self):
        # Animate the logo with a pulsing effect
        self.pulse_phase = 0
        self.animate_pulse()
        
        # Animate the status indicator
        self.animate_status()
    
    def animate_pulse(self):
        size = 50
        self.pulse_phase = (self.pulse_phase + 0.1) % (2 * math.pi)
        pulse_size = 5 * math.sin(self.pulse_phase) + 55
        
        self.logo_canvas.delete("pulse")
        self.logo_canvas.create_oval(
            size/2 - pulse_size/2, 
            size/2 - pulse_size/2, 
            size/2 + pulse_size/2, 
            size/2 + pulse_size/2, 
            outline=PURPLE_THEME["purple"], 
            width=1, 
            tags="pulse"
        )
        
        self.root.after(50, self.animate_pulse)
    
    def animate_status(self):
        # Simulate network activity with status indicator
        current_color = self.status_indicator.itemcget(1, "fill")
        new_color = PURPLE_THEME["success"] if current_color != PURPLE_THEME["success"] else PURPLE_THEME["accent"]
        self.status_indicator.itemconfig(1, fill=new_color)
        
        # Update network indicator
        net_color = PURPLE_THEME["success"] if self.network_status == "Connected" else PURPLE_THEME["error"]
        self.net_indicator.itemconfig(1, fill=net_color)
        
        self.root.after(1000, self.animate_status)
    
    def generate_new_sim(self):
        """Generate a new SIM with random data"""
        return {
            "imsi": f"310{random.randint(100, 999)}{random.randint(1000000, 9999999)}",
            "iccid": f"89{random.randint(10, 99)}{random.randint(1000, 9999)}{random.randint(100000000, 999999999)}",
            "ki": ''.join(random.choices('0123456789ABCDEF', k=32)),
            "carrier": random.choice(["AT&T", "Verizon", "T-Mobile", "Vodafone", "Orange"]),
            "phone_number": f"+1{random.randint(200, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}",
            "form_factor": random.choice(["Mini SIM", "Micro SIM", "Nano SIM"]),
            "status": "Active",
            "pin": "1234",
            "puk": ''.join(random.choices('0123456789', k=8)),
            "contacts": []
        }
    
    def create_sim_info_tab(self):
        # Main container
        main_frame = ttk.Frame(self.tab_sim_info, style="Card.TFrame")
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left panel - SIM details
        left_frame = ttk.LabelFrame(main_frame, text="SIM Card Details", style="Purple.TLabelframe")
        left_frame.pack(side='left', fill='both', padx=(0, 10), pady=10)
        
        # Form factor selection
        ttk.Label(left_frame, text="Form Factor:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.form_factor = ttk.Combobox(left_frame, values=["Mini SIM", "Micro SIM", "Nano SIM", "eSIM"], width=15)
        self.form_factor.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        
        # Carrier selection
        ttk.Label(left_frame, text="Carrier:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.carrier = ttk.Combobox(left_frame, values=["AT&T", "Verizon", "T-Mobile", "Vodafone", "Orange", "Custom"], width=15)
        self.carrier.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        
        # Phone number
        ttk.Label(left_frame, text="Phone Number:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.phone_number = ttk.Entry(left_frame, width=18)
        self.phone_number.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        
        # Status
        ttk.Label(left_frame, text="Status:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        self.status = ttk.Label(left_frame, text="Active", foreground=PURPLE_THEME["success"], font=("Segoe UI", 9, "bold"))
        self.status.grid(row=3, column=1, padx=10, pady=5, sticky='w')
        
        # Buttons
        btn_frame = ttk.Frame(left_frame, style="Card.TFrame")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        button_data = [
            ("Generate New SIM", self.new_sim),
            ("Save SIM Data", self.save_sim_data),
            ("Lock SIM", self.lock_sim)
        ]
        
        for i, (text, command) in enumerate(button_data):
            AnimatedButton(btn_frame, text, command, width=140, height=35).pack(side='top', pady=5)
        
        # Right panel - Security and Data
        right_frame = ttk.Frame(main_frame, style="Card.TFrame")
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0), pady=10)
        
        # Security Frame
        sec_frame = ttk.LabelFrame(right_frame, text="Security Settings", style="Purple.TLabelframe")
        sec_frame.pack(fill='x', padx=10, pady=10)
        
        # PIN Management
        ttk.Label(sec_frame, text="PIN Code:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.pin_entry = ttk.Entry(sec_frame, width=8, show="*")
        self.pin_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        AnimatedButton(sec_frame, "Change PIN", self.change_pin, width=100, height=30).grid(row=0, column=2, padx=10)
        
        ttk.Label(sec_frame, text="PUK Code:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.puk_display = ttk.Label(sec_frame, text="********", font=("Consolas", 9))
        self.puk_display.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        AnimatedButton(sec_frame, "Reveal PUK", self.reveal_puk, width=100, height=30).grid(row=1, column=2, padx=10)
        
        # SIM Data Frame
        data_frame = ttk.LabelFrame(right_frame, text="Technical Details", style="Purple.TLabelframe")
        data_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create a grid for technical details
        details = [
            ("IMSI:", "imsi"),
            ("ICCID:", "iccid"),
            ("Ki:", "ki"),
            ("Carrier:", "carrier"),
            ("Phone:", "phone_number"),
            ("Form Factor:", "form_factor"),
            ("Status:", "status")
        ]
        
        for i, (label, key) in enumerate(details):
            ttk.Label(data_frame, text=label, style="TechLabel.TLabel").grid(row=i, column=0, padx=10, pady=2, sticky='e')
            value = ttk.Label(data_frame, text="", style="TechValue.TLabel")
            value.grid(row=i, column=1, padx=10, pady=2, sticky='w')
            setattr(self, f"{key}_label", value)
    
    def create_auth_tab(self):
        # Main container
        main_frame = ttk.Frame(self.tab_auth, style="Card.TFrame")
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left panel - Authentication process
        left_frame = ttk.LabelFrame(main_frame, text="Authentication Process", style="Purple.TLabelframe")
        left_frame.pack(side='left', fill='both', padx=(0, 10), pady=10)
        
        # Step-by-step authentication
        steps = [
            "1. Device sends IMSI to network",
            "2. Network generates RAND challenge",
            "3. SIM signs RAND with Ki to create SRES",
            "4. Network verifies SRES match"
        ]
        
        for i, step in enumerate(steps):
            step_frame = ttk.Frame(left_frame, style="Card.TFrame")
            step_frame.pack(fill='x', padx=10, pady=5)
            
            # Step indicator
            indicator = tk.Canvas(step_frame, width=24, height=24, bg=PURPLE_THEME["card_bg"], highlightthickness=0)
            indicator.pack(side='left', padx=(0, 10))
            indicator.create_oval(2, 2, 22, 22, outline=PURPLE_THEME["light_purple"], width=2)
            indicator.create_text(12, 12, text=str(i+1), fill=PURPLE_THEME["text"], font=("Segoe UI", 10, "bold"))
            
            ttk.Label(step_frame, text=step).pack(side='left', fill='x', expand=True)
            
            setattr(self, f"step_{i+1}_indicator", indicator)
        
        # Buttons
        btn_frame = ttk.Frame(left_frame, style="Card.TFrame")
        btn_frame.pack(fill='x', pady=20)
        
        AnimatedButton(btn_frame, "Start Authentication", self.start_auth, width=180, height=40).pack(side='left', padx=10)
        AnimatedButton(btn_frame, "Reset Process", self.reset_auth, width=140, height=40).pack(side='left', padx=10)
        
        # Security warning
        sec_frame = ttk.LabelFrame(left_frame, text="Security Simulation", style="Purple.TLabelframe")
        sec_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(sec_frame, text="SIM Swapping Attack Simulation:", foreground=PURPLE_THEME["warning"]).pack(padx=10, pady=5, anchor='w')
        AnimatedButton(sec_frame, "Simulate SIM Swap Attack", self.sim_swap_attack, width=220, height=35).pack(padx=10, pady=10)
        
        # Right panel - Results
        right_frame = ttk.LabelFrame(main_frame, text="Authentication Results", style="Purple.TLabelframe")
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0), pady=10)
        
        # Results display
        self.auth_result = ttk.Label(right_frame, text="Authentication not performed", 
                                   foreground=PURPLE_THEME["secondary_text"], font=("Segoe UI", 12))
        self.auth_result.pack(padx=20, pady=20)
        
        # Visual representation
        canvas_frame = ttk.Frame(right_frame, style="Card.TFrame")
        canvas_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.auth_canvas = tk.Canvas(canvas_frame, bg=PURPLE_THEME["darker_bg"], highlightthickness=0)
        self.auth_canvas.pack(fill='both', expand=True)
        
        # Draw initial state
        self.draw_auth_diagram()
    
    def draw_auth_diagram(self):
        w = self.auth_canvas.winfo_width()
        h = self.auth_canvas.winfo_height()
        
        if w < 10 or h < 10:
            return
        
        self.auth_canvas.delete("all")
        
        # Draw device
        device_x = w * 0.2
        device_y = h * 0.5
        self.auth_canvas.create_rectangle(device_x-50, device_y-70, device_x+50, device_y+70, 
                                         fill=PURPLE_THEME["card_bg"], outline=PURPLE_THEME["purple"], width=2)
        self.auth_canvas.create_text(device_x, device_y-50, text="Mobile Device", fill=PURPLE_THEME["text"])
        
        # Draw SIM chip
        sim_size = 30
        self.auth_canvas.create_rectangle(device_x-sim_size/2, device_y-sim_size/2, 
                                         device_x+sim_size/2, device_y+sim_size/2, 
                                         fill=PURPLE_THEME["dark_purple"], outline="")
        
        # Draw chip contacts
        for i in range(6):
            offset = i * 5
            self.auth_canvas.create_rectangle(device_x-sim_size/2+offset, device_y-sim_size/2-4, 
                                             device_x-sim_size/2+offset+2, device_y-sim_size/2, 
                                             fill=PURPLE_THEME["accent"], outline="")
        
        # Draw network
        network_x = w * 0.8
        network_y = h * 0.5
        self.auth_canvas.create_oval(network_x-60, network_y-60, network_x+60, network_y+60, 
                                     outline=PURPLE_THEME["accent"], width=2)
        self.auth_canvas.create_text(network_x, network_y, text="Network", fill=PURPLE_THEME["text"])
        
        # Draw connection line
        self.auth_canvas.create_line(device_x+50, device_y, network_x-60, network_y, 
                                     fill=PURPLE_THEME["purple"], width=2, dash=(5, 3))
        
        # Draw arrows
        arrow_size = 8
        self.auth_canvas.create_line(device_x+50, device_y, device_x+50+arrow_size, device_y-arrow_size, 
                                    fill=PURPLE_THEME["purple"], width=2)
        self.auth_canvas.create_line(device_x+50, device_y, device_x+50+arrow_size, device_y+arrow_size, 
                                    fill=PURPLE_THEME["purple"], width=2)
    
    def create_esim_tab(self):
        # Main container
        main_frame = ttk.Frame(self.tab_esim, style="Card.TFrame")
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left panel - eSIM activation
        left_frame = ttk.LabelFrame(main_frame, text="eSIM Provisioning", style="Purple.TLabelframe")
        left_frame.pack(side='left', fill='both', padx=(0, 10), pady=10)
        
        # Activation code
        ttk.Label(left_frame, text="Activation Code (QR Content):").pack(padx=10, pady=(10, 0), anchor='w')
        self.activation_code = ttk.Entry(left_frame)
        self.activation_code.pack(fill='x', padx=10, pady=5)
        
        AnimatedButton(left_frame, "Activate eSIM", self.activate_esim, width=140, height=35).pack(padx=10, pady=10)
        
        # Current eSIM status
        status_frame = ttk.LabelFrame(left_frame, text="Current eSIM Status", style="Purple.TLabelframe")
        status_frame.pack(fill='x', padx=10, pady=10)
        
        self.esim_status = ttk.Label(status_frame, text="No eSIM active", foreground=PURPLE_THEME["secondary_text"])
        self.esim_status.pack(padx=10, pady=10)
        
        # eSIM actions
        action_frame = ttk.Frame(left_frame, style="Card.TFrame")
        action_frame.pack(fill='x', padx=10, pady=10)
        
        button_data = [
            ("Download eSIM Profile", self.download_esim),
            ("Delete eSIM", self.delete_esim),
            ("Switch Carrier", self.switch_carrier)
        ]
        
        for text, command in button_data:
            AnimatedButton(action_frame, text, command, width=160, height=35).pack(side='top', pady=5)
        
        # Right panel - Carrier profiles
        right_frame = ttk.LabelFrame(main_frame, text="Available eSIM Profiles", style="Purple.TLabelframe")
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0), pady=10)
        
        profiles = [
            ("T-Mobile", "Unlimited Data + International Roaming", "#FF00FF"),
            ("AT&T", "50GB Data + Unlimited Talk", "#00B7EB"),
            ("Verizon", "Unlimited Premium Plan", "#FF0000"),
            ("Google Fi", "Flexible Pay-as-you-go", "#00FF00")
        ]
        
        for carrier, plan, color in profiles:
            profile_frame = ttk.Frame(right_frame, style="Card.TFrame")
            profile_frame.pack(fill='x', padx=10, pady=10)
            
            # Color indicator
            color_indicator = tk.Canvas(profile_frame, width=20, height=20, bg=color, highlightthickness=0)
            color_indicator.pack(side='left', padx=(0, 10))
            
            # Profile info
            info_frame = ttk.Frame(profile_frame, style="Card.TFrame")
            info_frame.pack(side='left', fill='x', expand=True)
            
            ttk.Label(info_frame, text=carrier, font=("Segoe UI", 10, "bold")).pack(anchor='w')
            ttk.Label(info_frame, text=plan, foreground=PURPLE_THEME["secondary_text"]).pack(anchor='w')
            
            # Select button
            AnimatedButton(profile_frame, "Select", 
                           lambda c=carrier: self.select_profile(c), 
                           width=80, height=30).pack(side='right', padx=5)
    
    def create_networking_tab(self):
        # Main container
        main_frame = ttk.Frame(self.tab_networking, style="Card.TFrame")
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Network Control Panel
        control_frame = ttk.LabelFrame(main_frame, text="Network Control", style="Purple.TLabelframe")
        control_frame.pack(fill='x', padx=10, pady=10)
        
        # Connection controls
        btn_frame = ttk.Frame(control_frame, style="Card.TFrame")
        btn_frame.pack(fill='x', pady=5)
        
        AnimatedButton(btn_frame, "Connect to Network", self.connect_network, width=180, height=40).pack(side='left', padx=5)
        AnimatedButton(btn_frame, "Disconnect", self.disconnect_network, width=120, height=40).pack(side='left', padx=5)
        
        # Network status
        status_frame = ttk.Frame(control_frame, style="Card.TFrame")
        status_frame.pack(fill='x', pady=10)
        
        ttk.Label(status_frame, text="Network Status:", font=("Segoe UI", 10)).pack(side='left', padx=(10, 5))
        self.net_status_label = ttk.Label(status_frame, text="Disconnected", style="NetworkStatus.TLabel")
        self.net_status_label.pack(side='left')
        
        # Data Usage
        usage_frame = ttk.LabelFrame(main_frame, text="Data Usage", style="Purple.TLabelframe")
        usage_frame.pack(fill='x', padx=10, pady=10)
        
        # Upload/download stats
        ttk.Label(usage_frame, text="Uploaded:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.upload_label = ttk.Label(usage_frame, text="0.0 MB", style="TechValue.TLabel")
        self.upload_label.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        
        ttk.Label(usage_frame, text="Downloaded:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.download_label = ttk.Label(usage_frame, text="0.0 MB", style="TechValue.TLabel")
        self.download_label.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        
        ttk.Label(usage_frame, text="Speed:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.speed_label = ttk.Label(usage_frame, text="0.0 Mbps", style="TechValue.TLabel")
        self.speed_label.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        
        # Network tools
        tools_frame = ttk.LabelFrame(main_frame, text="Network Tools", style="Purple.TLabelframe")
        tools_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Ping tool
        ping_frame = ttk.Frame(tools_frame, style="Card.TFrame")
        ping_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(ping_frame, text="Ping Test:").pack(side='left', padx=(0, 10))
        self.ping_target = ttk.Entry(ping_frame, width=30)
        self.ping_target.insert(0, "google.com")
        self.ping_target.pack(side='left', fill='x', expand=True, padx=(0, 10))
        AnimatedButton(ping_frame, "Ping", self.ping_host, width=80, height=30).pack(side='right')
        
        # Port scanner
        port_frame = ttk.Frame(tools_frame, style="Card.TFrame")
        port_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(port_frame, text="Port Scan:").pack(side='left', padx=(0, 10))
        self.scan_target = ttk.Entry(port_frame, width=20)
        self.scan_target.insert(0, "localhost")
        self.scan_target.pack(side='left', padx=(0, 10))
        
        ttk.Label(port_frame, text="Ports:").pack(side='left', padx=(0, 5))
        self.port_range = ttk.Entry(port_frame, width=15)
        self.port_range.insert(0, "80-100")
        self.port_range.pack(side='left', padx=(0, 10))
        AnimatedButton(port_frame, "Scan", self.scan_ports, width=80, height=30).pack(side='right')
        
        # Results area
        self.net_results = scrolledtext.ScrolledText(
            tools_frame, 
            height=8,
            bg=PURPLE_THEME["darker_bg"], 
            fg=PURPLE_THEME["text"],
            insertbackground=PURPLE_THEME["text"],
            font=("Consolas", 9),
            padx=10,
            pady=10
        )
        self.net_results.pack(fill='both', expand=True, padx=10, pady=10)
        self.net_results.config(state='disabled')
    
    def create_logs_tab(self):
        # Main container
        main_frame = ttk.Frame(self.tab_logs, style="Card.TFrame")
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Log display
        log_frame = ttk.LabelFrame(main_frame, text="Event Logs", style="Purple.TLabelframe")
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.log_display = scrolledtext.ScrolledText(
            log_frame, 
            bg=PURPLE_THEME["darker_bg"], 
            fg=PURPLE_THEME["text"],
            insertbackground=PURPLE_THEME["text"],
            font=("Consolas", 9),
            padx=10,
            pady=10
        )
        self.log_display.pack(fill='both', expand=True)
        self.log_display.config(state='disabled')
        
        # Log controls
        btn_frame = ttk.Frame(main_frame, style="Card.TFrame")
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        AnimatedButton(btn_frame, "Clear Logs", self.clear_logs, width=120, height=35).pack(side='left', padx=10)
        AnimatedButton(btn_frame, "Save Logs", self.save_logs, width=120, height=35).pack(side='left', padx=10)
        AnimatedButton(btn_frame, "Export Data", self.export_data, width=120, height=35).pack(side='left', padx=10)
    
    def load_sim_data(self):
        """Load current SIM data into UI"""
        self.form_factor.set(self.current_sim["form_factor"])
        self.carrier.set(self.current_sim["carrier"])
        self.phone_number.delete(0, tk.END)
        self.phone_number.insert(0, self.current_sim["phone_number"])
        self.status.config(
            text=self.current_sim["status"], 
            foreground=PURPLE_THEME["success"] if self.current_sim["status"] == "Active" else PURPLE_THEME["error"]
        )
        
        # Update SIM data display
        self.imsi_label.config(text=self.current_sim['imsi'])
        self.iccid_label.config(text=self.current_sim['iccid'])
        self.ki_label.config(text="[Hidden for security]")
        self.carrier_label.config(text=self.current_sim['carrier'])
        self.phone_number_label.config(text=self.current_sim['phone_number'])
        self.form_factor_label.config(text=self.current_sim['form_factor'])
        self.status_label.config(text=self.current_sim['status'])
        
        # Update eSIM tab if applicable
        if self.current_sim["form_factor"] == "eSIM":
            self.esim_status.config(text=f"Active eSIM: {self.current_sim['carrier']}")
    
    def log_event(self, event):
        """Add event to log system"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {event}"
        self.log_events.append(log_entry)
        
        # Update log display
        self.log_display.config(state='normal')
        self.log_display.insert(tk.END, log_entry + "\n")
        self.log_display.config(state='disabled')
        self.log_display.see(tk.END)
        
        # Update status bar
        self.status_bar.config(text=f"Last event: {event}")
    
    # ======================
    # SIM Info Tab Functions
    # ======================
    def new_sim(self):
        self.current_sim = self.generate_new_sim()
        self.load_sim_data()
        self.log_event("Generated new SIM card")
        messagebox.showinfo("New SIM", "New SIM card generated successfully!")
    
    def save_sim_data(self):
        with open("sim_data.json", "w") as f:
            json.dump(self.current_sim, f, indent=2)
        self.log_event("SIM data saved to file")
        messagebox.showinfo("Save", "SIM data saved to sim_data.json")
    
    def lock_sim(self):
        self.current_sim["status"] = "Locked"
        self.status.config(text="Locked", foreground=PURPLE_THEME["error"])
        self.log_event("SIM locked")
        messagebox.showwarning("SIM Locked", "SIM card has been locked. Enter PIN to unlock.")
    
    def change_pin(self):
        new_pin = self.pin_entry.get()
        if len(new_pin) != 4 or not new_pin.isdigit():
            messagebox.showerror("Invalid PIN", "PIN must be 4 digits")
            return
        
        self.current_sim["pin"] = new_pin
        self.pin_entry.delete(0, tk.END)
        self.log_event("PIN changed successfully")
        messagebox.showinfo("Success", "PIN code updated")
    
    def reveal_puk(self):
        self.puk_display.config(text=self.current_sim["puk"])
        self.log_event("PUK code revealed")
        messagebox.showinfo("PUK Code", f"Your PUK code is: {self.current_sim['puk']}\nKeep this secure!")
    
    # ======================
    # Authentication Functions
    # ======================
    def start_auth(self):
        """Simulate SIM authentication process"""
        self.log_event("Starting authentication process...")
        
        # Visual step 1: Send IMSI
        self.animate_auth_step(1, "Device sends IMSI")
        self.log_event(f"1. Device sends IMSI: {self.current_sim['imsi']}")
        
        # Visual step 2: Generate RAND
        self.root.after(1000, lambda: self.animate_auth_step(2, "Network generates RAND"))
        self.root.after(1000, lambda: self.log_event(f"2. Network generates RAND"))
        
        # Step 2: Generate RAND
        rand = random.randint(10000000, 99999999)
        self.root.after(1000, lambda: self.log_event(f"   RAND: {rand}"))
        
        # Visual step 3: Compute SRES
        self.root.after(2000, lambda: self.animate_auth_step(3, "SIM computes SRES"))
        self.root.after(2000, lambda: self.log_event(f"3. SIM computes SRES"))
        
        # Step 3: Compute SRES (simplified)
        sres = (rand ^ int(self.current_sim['ki'][:8], 16)) % 10000
        self.root.after(2000, lambda: self.log_event(f"   SRES: {sres}"))
        
        # Visual step 4: Verify
        self.root.after(3000, lambda: self.animate_auth_step(4, "Network verification"))
        self.root.after(3000, lambda: self.log_event(f"4. Network verification"))
        
        # Step 4: Verify
        network_sres = (rand ^ int(self.current_sim['ki'][:8], 16)) % 10000
        if sres == network_sres:
            self.root.after(4000, lambda: self.auth_result.config(
                text="Authentication SUCCESS", 
                foreground=PURPLE_THEME["success"]
            ))
            self.root.after(4000, lambda: self.log_event("   Authentication SUCCESS: SRES matches"))
            self.root.after(4000, lambda: messagebox.showinfo("Success", "Authentication successful!\nDevice connected to network."))
        else:
            self.root.after(4000, lambda: self.auth_result.config(
                text="Authentication FAILED", 
                foreground=PURPLE_THEME["error"]
            ))
            self.root.after(4000, lambda: self.log_event("   Authentication FAILED: SRES mismatch"))
            self.root.after(4000, lambda: messagebox.showerror("Failure", "Authentication failed!\nConnection blocked."))
    
    def animate_auth_step(self, step, text):
        """Animate the authentication step"""
        # Highlight current step
        for i in range(1, 5):
            indicator = getattr(self, f"step_{i}_indicator")
            if i == step:
                indicator.itemconfig(1, outline=PURPLE_THEME["accent"], width=3)
                indicator.itemconfig(2, fill=PURPLE_THEME["accent"])
            else:
                indicator.itemconfig(1, outline=PURPLE_THEME["light_purple"], width=2)
                indicator.itemconfig(2, fill=PURPLE_THEME["text"])
        
        # Update status
        self.status_bar.config(text=f"Authentication: {text}")
    
    def reset_auth(self):
        self.auth_result.config(text="Authentication not performed", foreground=PURPLE_THEME["secondary_text"])
        self.log_event("Authentication reset")
        
        # Reset step indicators
        for i in range(1, 5):
            indicator = getattr(self, f"step_{i}_indicator")
            indicator.itemconfig(1, outline=PURPLE_THEME["light_purple"], width=2)
            indicator.itemconfig(2, fill=PURPLE_THEME["text"])
    
    def sim_swap_attack(self):
        """Simulate SIM swapping attack"""
        self.log_event("WARNING: Simulating SIM swap attack!")
        if messagebox.askyesno(
            "SIM Swap Attack", 
            "This will simulate a successful SIM swap attack!\nContinue?"
        ):
            self.current_sim["phone_number"] = f"+1{random.randint(200,999)}{random.randint(100,999)}{random.randint(1000,9999)}"
            self.load_sim_data()
            self.log_event("SIM SWAP ATTACK SUCCESSFUL: Number ported to attacker's device")
            messagebox.showwarning(
                "Security Breach", 
                "SIM swap attack successful!\n"
                "Your phone number has been transferred to another device."
            )
    
    # ======================
    # eSIM Functions
    # ======================
    def select_profile(self, carrier):
        self.carrier.set(carrier)
        self.log_event(f"Selected eSIM profile: {carrier}")
    
    def activate_esim(self):
        code = self.activation_code.get()
        if not code:
            messagebox.showerror("Error", "Enter activation code")
            return
        
        self.current_sim["form_factor"] = "eSIM"
        self.current_sim["carrier"] = self.carrier.get()
        self.form_factor.set("eSIM")
        self.load_sim_data()
        self.log_event(f"eSIM activated with {self.carrier.get()}")
        messagebox.showinfo("Success", "eSIM activated successfully!")
    
    def download_esim(self):
        self.log_event("Downloading eSIM profile...")
        # Simulate download progress
        self.status_bar.config(text="Downloading eSIM profile...")
        self.root.after(2000, lambda: self.log_event("   Download complete"))
        self.root.after(2000, lambda: self.status_bar.config(text="Download complete"))
        self.root.after(2000, lambda: messagebox.showinfo("Download", "eSIM profile downloaded successfully"))
    
    def delete_esim(self):
        if messagebox.askyesno("Confirm", "Delete current eSIM profile?"):
            self.current_sim["form_factor"] = random.choice(["Mini SIM", "Micro SIM", "Nano SIM"])
            self.form_factor.set(self.current_sim["form_factor"])
            self.esim_status.config(text="No eSIM active")
            self.load_sim_data()
            self.log_event("eSIM profile deleted")
    
    def switch_carrier(self):
        new_carrier = random.choice(["AT&T", "Verizon", "T-Mobile", "Google Fi"])
        self.carrier.set(new_carrier)
        self.current_sim["carrier"] = new_carrier
        self.load_sim_data()
        self.log_event(f"Switched carrier to {new_carrier}")
        messagebox.showinfo("Carrier Switch", f"Now using {new_carrier} network")
    
    # ======================
    # Networking Functions
    # ======================
    def connect_network(self):
        if self.network_status == "Connected":
            messagebox.showinfo("Info", "Already connected to network")
            return
            
        self.log_event("Connecting to network...")
        self.network_status = "Connecting"
        self.net_status_label.config(text="Connecting...", foreground=PURPLE_THEME["warning"])
        
        # Start network simulation in background
        self.network_running = True
        self.network_thread = threading.Thread(target=self.simulate_network, daemon=True)
        self.network_thread.start()
    
    def disconnect_network(self):
        if self.network_status == "Disconnected":
            return
            
        self.log_event("Disconnecting from network...")
        self.network_running = False
        self.network_status = "Disconnected"
        self.net_status_label.config(text="Disconnected", foreground=PURPLE_THEME["error"])
        self.status_bar.config(text="Network disconnected")
    
    def simulate_network(self):
        """Simulate network connection in background thread"""
        # Simulate connection process
        time.sleep(2)
        
        if not self.network_running:
            return
            
        self.network_status = "Connected"
        self.root.after(0, lambda: self.net_status_label.config(
            text="Connected", 
            foreground=PURPLE_THEME["success"]
        ))
        self.root.after(0, lambda: self.log_event("Network connection established"))
        self.root.after(0, lambda: self.status_bar.config(text="Connected to network"))
        
        # Simulate data transfer
        while self.network_running:
            # Simulate some data transfer
            upload = random.uniform(0.1, 5.0)
            download = random.uniform(0.5, 10.0)
            speed = random.uniform(1.0, 100.0)
            
            self.data_usage["upload"] += upload
            self.data_usage["download"] += download
            self.network_speed = speed
            
            # Update UI
            self.root.after(0, lambda u=upload, d=download, s=speed: self.update_network_stats(u, d, s))
            
            time.sleep(1)
    
    def update_network_stats(self, upload, download, speed):
        """Update network statistics in UI"""
        self.upload_label.config(text=f"{self.data_usage['upload']:.2f} MB")
        self.download_label.config(text=f"{self.data_usage['download']:.2f} MB")
        self.speed_label.config(text=f"{speed:.1f} Mbps")
    
    def ping_host(self):
        target = self.ping_target.get()
        if not target:
            messagebox.showerror("Error", "Enter a host to ping")
            return
            
        self.log_event(f"Pinging {target}...")
        
        # Run ping in background
        threading.Thread(target=self.run_ping, args=(target,), daemon=True).start()
    
    def run_ping(self, target):
        try:
            # Simulate ping
            time.sleep(1)
            response_time = random.uniform(10, 100)
            
            self.root.after(0, lambda: self.show_net_result(f"Pinging {target}...\nReply received in {response_time:.2f} ms\n"))
            self.root.after(0, lambda: self.log_event(f"Ping to {target}: {response_time:.2f} ms"))
        except Exception as e:
            self.root.after(0, lambda: self.show_net_result(f"Ping failed: {str(e)}"))
    
    def scan_ports(self):
        target = self.scan_target.get()
        ports = self.port_range.get()
        
        if not target or not ports:
            messagebox.showerror("Error", "Enter target and port range")
            return
            
        try:
            # Parse port range
            if '-' in ports:
                start, end = map(int, ports.split('-'))
            else:
                start = end = int(ports)
                
            self.log_event(f"Scanning ports {start}-{end} on {target}...")
            
            # Run scan in background
            threading.Thread(target=self.run_port_scan, args=(target, start, end), daemon=True).start()
        except ValueError:
            messagebox.showerror("Error", "Invalid port range format. Use 'start-end' or single port")
    
    def run_port_scan(self, target, start, end):
        try:
            result = f"Scanning {target} ports {start}-{end}...\n"
            self.root.after(0, lambda: self.show_net_result(result))
            
            # Simulate port scan
            for port in range(start, end + 1):
                if not self.network_running:
                    break
                    
                time.sleep(0.1)
                
                # Randomly decide if port is open
                is_open = random.random() > 0.8
                if is_open:
                    result = f"Port {port} is open\n"
                    self.root.after(0, lambda r=result: self.show_net_result(r))
                    self.root.after(0, lambda: self.log_event(f"Discovered open port: {port}"))
                    
            self.root.after(0, lambda: self.show_net_result("\nScan completed\n"))
        except Exception as e:
            self.root.after(0, lambda: self.show_net_result(f"Scan error: {str(e)}"))
    
    def show_net_result(self, text):
        self.net_results.config(state='normal')
        self.net_results.insert(tk.END, text)
        self.net_results.config(state='disabled')
        self.net_results.see(tk.END)
    
    # ======================
    # Logs Functions
    # ======================
    def clear_logs(self):
        self.log_events = []
        self.log_display.config(state='normal')
        self.log_display.delete(1.0, tk.END)
        self.log_display.config(state='disabled')
        self.log_event("Logs cleared")
    
    def save_logs(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, "w") as f:
                f.write("\n".join(self.log_events))
            self.log_event(f"Logs saved to {filename}")
            messagebox.showinfo("Saved", f"Logs saved to {filename}")
    
    def export_data(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            data = {
                "sim_data": self.current_sim,
                "logs": self.log_events,
                "network_stats": {
                    "status": self.network_status,
                    "data_usage": self.data_usage,
                    "last_speed": self.network_speed
                }
            }
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            self.log_event(f"Data exported to {filename}")
            messagebox.showinfo("Exported", f"All data exported to {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PySimApp(root)
    root.mainloop()
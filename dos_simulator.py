import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import requests
from flask import Flask, request
from collections import deque
import csv
import datetime

# Excel handling
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("pandas not available. Using CSV logging only.")

# Image handling
try:
    from PIL import Image, ImageTk, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available. Logo display disabled.")

# Try to import psutil for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class DoSSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.show_landing_page()
    
    def show_landing_page(self):
        """Display the landing page before the main application"""
        self.root.title("GATE & CRASHER - Welcome")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Landing page frame
        landing_frame = tk.Frame(self.root, bg='#2c3e50', padx=50, pady=30)
        landing_frame.pack(expand=True)
        
        # Try to load and display logo in circular frame
        self.logo_photo = None
        if PIL_AVAILABLE:
            try:
                # Load the logo image
                logo_image = Image.open("DOSRL logo.png")
                
                # Resize to appropriate size
                logo_size = 150
                logo_image = logo_image.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                
                # Create circular mask
                mask = Image.new('L', (logo_size, logo_size), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, logo_size, logo_size), fill=255)
                
                # Apply circular mask
                output = Image.new('RGBA', (logo_size, logo_size), (0, 0, 0, 0))
                output.paste(logo_image, mask=mask)
                
                self.logo_photo = ImageTk.PhotoImage(output)
                
                # Display logo
                logo_label = tk.Label(landing_frame, image=self.logo_photo, bg='#2c3e50')
                logo_label.pack(pady=(0, 20))
            except Exception as e:
                print(f"Failed to load logo: {e}")
                # Continue without logo if it fails to load
        
        # Title
        title_label = tk.Label(
            landing_frame,
            text="GATE & CRASHER",
            font=("Arial", 48, "bold"),
            fg="white",
            bg='#2c3e50'
        )
        title_label.pack(pady=(0, 30))
        
        # Tagline
        tagline_label = tk.Label(
            landing_frame,
            text="DOS Attacker and Rate Limiter",
            font=("Arial", 24),
            fg="#ecf0f1",
            bg='#2c3e50'
        )
        tagline_label.pack(pady=(0, 50))
        
        # Description
        desc_text = """A comprehensive cybersecurity simulation tool designed for educational purposes.

Features:
• DoS Simulation with realistic attack patterns
• Advanced Rate Limiting mechanisms
• Auto-Blacklist defense systems
• Real-time System Resource Monitoring
• Detailed Attack Logging in Excel format"""
        
        desc_label = tk.Label(
            landing_frame,
            text=desc_text,
            font=("Arial", 16),
            fg="#bdc3c7",
            bg='#2c3e50',
            justify=tk.LEFT
        )
        desc_label.pack(pady=(0, 30))
        
        # Buttons Frame
        buttons_frame = tk.Frame(landing_frame, bg='#2c3e50')
        buttons_frame.pack(pady=(0, 40))
        
        # Project Info Button
        info_btn = tk.Button(
            buttons_frame,
            text="PROJECT INFO",
            command=self.show_project_info,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 14, "bold"),
            padx=25,
            pady=12,
            relief=tk.RAISED,
            bd=3
        )
        info_btn.pack(side=tk.LEFT, padx=(0, 20))
        
        # Start Button
        start_btn = tk.Button(
            buttons_frame,
            text="START APPLICATION",
            command=self.start_main_app,
            bg="#3498db",
            fg="white",
            font=("Arial", 14, "bold"),
            padx=25,
            pady=12,
            relief=tk.RAISED,
            bd=3
        )
        start_btn.pack(side=tk.LEFT)
        
        # Footer
        footer_label = tk.Label(
            landing_frame,
            text="Cybersecurity Education Tool • For Research and Learning Purposes Only",
            font=("Arial", 12),
            fg="#95a5a6",
            bg='#2c3e50'
        )
        footer_label.pack(side=tk.BOTTOM, pady=(40, 0))
    
    def show_project_info(self):
        """Open the project info HTML page in the default web browser"""
        try:
            import webbrowser
            import os
            
            # Get the absolute path to the HTML file
            html_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Project_info.html')
            
            if os.path.exists(html_file):
                # Open in the default web browser
                webbrowser.open(f'file://{html_file}')
            else:
                # Fallback message if file doesn't exist
                print("Project info file not found.")
        except Exception as e:
            print(f"Failed to open project info: {e}")
    
    def start_main_app(self):
        """Initialize and display the main application"""
        # Clear landing page
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Set up main application
        self.root.title("DOS Simulator & Rate Limiter")
        self.root.geometry("1200x1200")
        self.root.configure(bg='white')
        
        # Initialize variables
        self.server_thread = None
        self.attack_thread = None
        self.server_running = False
        self.attack_running = False
        self.request_count = 0
        self.success_count = 0
        self.blocked_count = 0
        self.attack_start_time = None
        self.attack_end_time = None
        
        # Rate limiter variables
        self.request_window = deque()
        self.max_requests = 5
        self.window_duration = 10  # seconds
        
        # Blacklist variables
        self.blacklist = {}  # ip -> expiration time
        self.rate_limit_violations = {}  # ip -> count
        
        # Setup GUI
        self.setup_gui()
        
        # Setup Flask app
        self.flask_app = Flask(__name__)
        self.setup_flask_routes()
        
        # Initialize logging (Excel if available)
        self.init_logging()
    
    def create_text_header(self, parent):
        """Create text-based header as fallback"""
        # Center the title and tagline
        center_frame = tk.Frame(parent, bg='#4a90e2')
        center_frame.pack(expand=True)
        
        # Title
        header_label = tk.Label(
            center_frame, 
            text="GATE & CRASHER",
            font=("Arial", 24, "bold"),
            fg="white",
            bg='#4a90e2'
        )
        header_label.pack()
        
        # Tagline
        tagline_label = tk.Label(
            center_frame,
            text="DOS Attacker and Rate Limiter",
            font=("Arial", 14),
            fg="white",
            bg='#4a90e2'
        )
        tagline_label.pack(pady=(5, 0))
    
    def setup_gui(self):
        # Header with background image - extended to fill entire width
        header_frame = tk.Frame(self.root, bg='white', padx=0, pady=0)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # Set header image if PIL is available
        self.header_photo = None
        if PIL_AVAILABLE:
            try:
                # Load the header image
                header_image = Image.open("GATE & CRASHER.png")
                
                # Get the original image dimensions
                img_width, img_height = header_image.size
                
                # Calculate aspect ratio
                aspect_ratio = img_width / img_height
                
                # Dimensions to extend to both ends
                desired_width = 1500  # Extended width to fill both sides completely
                desired_height = int(desired_width / aspect_ratio)  # Original height
                
                # Resize to fill the header
                header_image = header_image.resize((desired_width, desired_height), Image.Resampling.LANCZOS)
                
                self.header_photo = ImageTk.PhotoImage(header_image)
                
                # Create a label with the header image that stretches to fill completely
                header_label = tk.Label(header_frame, image=self.header_photo, bg='white', bd=0)
                header_label.pack(fill=tk.BOTH, expand=True)
                
            except Exception as e:
                print(f"Failed to load header image: {e}")
                # Fallback to text if image fails to load
                self.create_text_header(header_frame)
        else:
            # Fallback to text if PIL is not available
            self.create_text_header(header_frame)
        
        # Combined Control Section (Server and Attacker in one row)
        control_frame = tk.Frame(self.root, bg='white')
        control_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Server Control Box
        server_frame = tk.LabelFrame(control_frame, text="Server Control", padx=15, pady=15, bg='#f0f0f0')
        server_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        server_inner_frame = tk.Frame(server_frame, bg='#f0f0f0')
        server_inner_frame.pack(fill=tk.BOTH, expand=True)
        
        self.server_status_var = tk.StringVar(value="Server Status: Offline")
        self.server_status_label = tk.Label(
            server_inner_frame,
            textvariable=self.server_status_var,
            font=("Arial", 14, "bold"),
            fg="red",
            bg='#f0f0f0'
        )
        self.server_status_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.start_server_btn = tk.Button(
            server_inner_frame,
            text="Start Server",
            command=self.toggle_server,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=8,
            relief=tk.RAISED,
            bd=3
        )
        self.start_server_btn.pack(side=tk.LEFT)
        
        # Blacklist Status
        self.blacklist_status_var = tk.StringVar(value="Blacklist Status: Inactive")
        self.blacklist_status_label = tk.Label(
            server_inner_frame,
            textvariable=self.blacklist_status_var,
            font=("Arial", 12, "bold"),
            fg="gray",
            bg='#f0f0f0'
        )
        self.blacklist_status_label.pack(side=tk.RIGHT, padx=(20, 0))
        
        # Attacker Control Box
        attacker_frame = tk.LabelFrame(control_frame, text="Attacker Control", padx=15, pady=15, bg='#f0f0f0')
        attacker_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        attacker_inner_frame = tk.Frame(attacker_frame, bg='#f0f0f0')
        attacker_inner_frame.pack(fill=tk.BOTH, expand=True)
        
        self.attacker_status_var = tk.StringVar(value="Attacker Status: Inactive")
        self.attacker_status_label = tk.Label(
            attacker_inner_frame,
            textvariable=self.attacker_status_var,
            font=("Arial", 14, "bold"),
            fg="gray",
            bg='#f0f0f0'
        )
        self.attacker_status_label.pack(side=tk.LEFT, padx=(0, 20))
        
        buttons_frame = tk.Frame(attacker_inner_frame, bg='#f0f0f0')
        buttons_frame.pack(side=tk.LEFT)
        
        self.start_attack_btn = tk.Button(
            buttons_frame,
            text="Start Attack",
            command=self.toggle_attack,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=8,
            relief=tk.RAISED,
            bd=3
        )
        self.start_attack_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.stop_attack_btn = tk.Button(
            buttons_frame,
            text="Stop Attack",
            command=self.stop_attack,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=8,
            relief=tk.RAISED,
            bd=3,
            state=tk.DISABLED
        )
        self.stop_attack_btn.pack(side=tk.LEFT)
        
        # Combined Monitoring and Statistics Section (side by side)
        monitoring_stats_frame = tk.Frame(self.root, bg='white')
        monitoring_stats_frame.pack(fill=tk.X, padx=15, pady=8)
        
        # System Resource Monitoring Box
        if PSUTIL_AVAILABLE:
            health_frame = tk.LabelFrame(monitoring_stats_frame, text="System Resource Monitoring", padx=15, pady=15, bg='#f0f0f0')
            health_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
            
            # CPU and RAM Indicators in Same Row
            metrics_frame = tk.Frame(health_frame, bg='#f0f0f0')
            metrics_frame.pack(side=tk.TOP, pady=5)
            
            # CPU Indicator
            cpu_frame = tk.Frame(metrics_frame, bg='#f0f0f0')
            cpu_frame.pack(side=tk.LEFT, padx=(0, 20))
            
            cpu_title = tk.Label(cpu_frame, text="CPU USAGE:", font=("Arial", 11, "bold"), bg='#f0f0f0', fg='#2c3e50')
            cpu_title.pack(side=tk.LEFT)
            
            self.cpu_label = tk.Label(cpu_frame, text="0%", font=("Arial", 14, "bold"), bg='#f0f0f0', fg='#e74c3c')
            self.cpu_label.pack(side=tk.LEFT, padx=(5, 0))
            
            # RAM Indicator
            ram_frame = tk.Frame(metrics_frame, bg='#f0f0f0')
            ram_frame.pack(side=tk.LEFT)
            
            ram_title = tk.Label(ram_frame, text="RAM USAGE:", font=("Arial", 11, "bold"), bg='#f0f0f0', fg='#2c3e50')
            ram_title.pack(side=tk.LEFT)
            
            self.ram_label = tk.Label(ram_frame, text="0%", font=("Arial", 14, "bold"), bg='#f0f0f0', fg='#3498db')
            self.ram_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Live Stats Box
        stats_frame = tk.LabelFrame(monitoring_stats_frame, text="Live Statistics", padx=15, pady=20, bg='#f0f0f0')
        stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Increase font size for better visibility
        self.requests_sent_var = tk.StringVar(value="Requests Sent: 0")
        self.successful_var = tk.StringVar(value="Successful (200 OK): 0")
        self.blocked_var = tk.StringVar(value="Blocked (429): 0")
        
        requests_label = tk.Label(stats_frame, textvariable=self.requests_sent_var, bg='#f0f0f0', font=("Arial", 16, "bold"))
        requests_label.pack(side=tk.LEFT, padx=(0, 30))
        
        success_label = tk.Label(stats_frame, textvariable=self.successful_var, bg='#f0f0f0', font=("Arial", 16, "bold"), fg="#27ae60")
        success_label.pack(side=tk.LEFT, padx=(0, 30))
        
        blocked_label = tk.Label(stats_frame, textvariable=self.blocked_var, bg='#f0f0f0', font=("Arial", 16, "bold"), fg="#e74c3c")
        blocked_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Refresh Button (larger and more prominent)
        refresh_btn = tk.Button(
            stats_frame,
            text="Refresh",
            command=self.refresh_stats,
            bg="#3498db",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=8,
            relief=tk.RAISED,
            bd=3
        )
        refresh_btn.pack(side=tk.RIGHT)
        
        # Defense Chain Visualization
        defense_frame = tk.LabelFrame(self.root, text="Defense Chain", padx=15, pady=15, bg='#f0f0f0')
        defense_frame.pack(fill=tk.X, padx=15, pady=8)
        
        # Create a frame for the defense chain visualization
        chain_frame = tk.Frame(defense_frame, bg='#f0f0f0')
        chain_frame.pack(fill=tk.X, pady=10)
        
        # Firewall Component
        firewall_frame = tk.Frame(chain_frame, bg='#e3f2fd', relief=tk.RAISED, bd=2)
        firewall_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        firewall_title = tk.Label(firewall_frame, text="FIREWALL", font=("Arial", 10, "bold"), bg='#e3f2fd', fg='#1976d2')
        firewall_title.pack(pady=(5, 2))
        
        firewall_desc = tk.Label(firewall_frame, text="First Line of Defense", font=("Arial", 8), bg='#e3f2fd', fg='#555')
        firewall_desc.pack(pady=(0, 5))
        
        self.firewall_status = tk.Label(firewall_frame, text="ACTIVE", font=("Arial", 9, "bold"), bg='#e3f2fd', fg='green')
        self.firewall_status.pack(pady=(0, 5))
        
        # Arrow
        arrow1 = tk.Label(chain_frame, text=">", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#666')
        arrow1.pack(side=tk.LEFT, padx=5)
        
        # Rate Limiter Component
        limiter_frame = tk.Frame(chain_frame, bg='#f3e5f5', relief=tk.RAISED, bd=2)
        limiter_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        limiter_title = tk.Label(limiter_frame, text="RATE LIMITER", font=("Arial", 10, "bold"), bg='#f3e5f5', fg='#7b1fa2')
        limiter_title.pack(pady=(5, 2))
        
        limiter_desc = tk.Label(limiter_frame, text="Traffic Control", font=("Arial", 8), bg='#f3e5f5', fg='#555')
        limiter_desc.pack(pady=(0, 5))
        
        self.limiter_status = tk.Label(limiter_frame, text="5 req/10 sec", font=("Arial", 9, "bold"), bg='#f3e5f5', fg='#7b1fa2')
        self.limiter_status.pack(pady=(0, 5))
        
        # Arrow
        arrow2 = tk.Label(chain_frame, text=">", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#666')
        arrow2.pack(side=tk.LEFT, padx=5)
        
        # Application Component
        app_frame = tk.Frame(chain_frame, bg='#e8f5e9', relief=tk.RAISED, bd=2)
        app_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        app_title = tk.Label(app_frame, text="APPLICATION", font=("Arial", 10, "bold"), bg='#e8f5e9', fg='#388e3c')
        app_title.pack(pady=(5, 2))
        
        app_desc = tk.Label(app_frame, text="Core Service", font=("Arial", 8), bg='#e8f5e9', fg='#555')
        app_desc.pack(pady=(0, 5))
        
        self.app_status = tk.Label(app_frame, text="PROTECTED", font=("Arial", 9, "bold"), bg='#e8f5e9', fg='#388e3c')
        self.app_status.pack(pady=(0, 5))
        
        # Request Log Section (maximized height and padding)
        log_frame = tk.LabelFrame(self.root, text="Request Log", padx=25, pady=25, bg='#f0f0f0')
        log_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # View Log Details Button (moved to top to eliminate empty space)
        view_log_btn = tk.Button(
            log_frame,
            text="View Log Details",
            command=self.view_log_details,
            bg="#8e44ad",
            fg="white",
            font=("Arial", 9, "bold"),
            padx=12,
            pady=4,
            relief=tk.RAISED,
            bd=1
        )
        view_log_btn.pack(side=tk.TOP, pady=(0, 5))
        
        # Request Log Text Area (maximized to utilize all available space)
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=75,  # Maximized height to utilize all available space
            state=tk.DISABLED,
            bg='white',
            font=('Courier', 12)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
    
    def setup_flask_routes(self):
        @self.flask_app.route('/', methods=['GET'])
        def index():
            # Get client IP
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            
            # Check if IP is blacklisted
            current_time = time.time()
            if client_ip in self.blacklist and self.blacklist[client_ip] > current_time:
                # Log the blocked request
                self.log_request_to_csv(client_ip, 403, "Forbidden - IP Blacklisted")
                self.update_defense_chain_status("BLOCKED", f"IP {client_ip} blocked by firewall")
                return "Forbidden - IP Blacklisted", 403
            
            # Clean up expired blacklist entries
            expired_ips = [ip for ip, expiry in self.blacklist.items() if expiry <= current_time]
            for ip in expired_ips:
                del self.blacklist[ip]
            
            # Check rate limit
            # Remove requests outside the window
            while self.request_window and current_time - self.request_window[0] > self.window_duration:
                self.request_window.popleft()
            
            # Check if we're at the limit
            if len(self.request_window) >= self.max_requests:
                # Increment violation count
                self.rate_limit_violations[client_ip] = self.rate_limit_violations.get(client_ip, 0) + 1
                
                # If violations exceed threshold, blacklist IP
                if self.rate_limit_violations[client_ip] > 3:
                    self.blacklist[client_ip] = current_time + 60  # Blacklist for 60 seconds
                    self.update_blacklist_status(True, client_ip)
                    # Log the forbidden request
                    self.log_request_to_csv(client_ip, 403, "Forbidden - IP Blacklisted")
                    self.update_defense_chain_status("BLACKLISTED", f"IP {client_ip} blacklisted by rate limiter")
                    return "Forbidden - IP Blacklisted", 403
                else:
                    # Log the rate limit violation
                    self.log_request_to_csv(client_ip, 429, "Too Many Requests")
                    self.update_defense_chain_status("RATE_LIMITED", f"IP {client_ip} rate limited")
                    return "Too Many Requests", 429
            
            # Add current request to window
            self.request_window.append(current_time)
            # Log the successful request
            self.log_request_to_csv(client_ip, 200, "OK")
            self.update_defense_chain_status("ALLOWED", f"IP {client_ip} request allowed to application")
            return "OK", 200
    
    def toggle_server(self):
        if not self.server_running:
            self.start_server()
        else:
            self.stop_server()
    
    def start_server(self):
        if not self.server_running:
            self.server_running = True
            self.server_status_var.set("Server Status: Online")
            self.server_status_label.configure(fg="green")
            self.start_server_btn.configure(text="Stop Server", bg="#e74c3c")
            
            # Start Flask server in a separate thread
            self.server_thread = threading.Thread(target=self.run_flask_server, daemon=True)
            self.server_thread.start()
            
            # Start health monitoring if psutil is available
            if PSUTIL_AVAILABLE:
                self.health_monitor_thread = threading.Thread(target=self.monitor_health, daemon=True)
                self.health_monitor_thread.start()
            
            self.log_message("Server started on http://127.0.0.1:5000/")
    
    def stop_server(self):
        if self.server_running:
            self.server_running = False
            self.server_status_var.set("Server Status: Offline")
            self.server_status_label.configure(fg="red")
            self.start_server_btn.configure(text="Start Server", bg="#27ae60")
            
            # Stop the Flask server
            if hasattr(self, 'server'):
                self.server.shutdown()
            
            # Reset blacklist status
            self.update_blacklist_status(False, None)
            
            self.log_message("Server stopped")
    
    def run_flask_server(self):
        from werkzeug.serving import make_server
        
        # Create a server
        self.server = make_server('127.0.0.1', 5000, self.flask_app)
        self.server.serve_forever()
    
    def toggle_attack(self):
        if not self.attack_running:
            self.start_attack()
        else:
            self.stop_attack()
    
    def start_attack(self):
        if not self.attack_running:
            self.attack_running = True
            self.attack_start_time = datetime.datetime.now()
            self.attacker_status_var.set("Attacker Status: Active")
            self.attacker_status_label.configure(fg="red")
            # Disable Start Attack button when attack is running
            self.start_attack_btn.configure(state=tk.DISABLED)
            self.stop_attack_btn.configure(state=tk.NORMAL)
            
            # Add a gap in Excel log to differentiate attacks (if there's existing data)
            if PANDAS_AVAILABLE and hasattr(self, 'excel_data') and len(self.excel_data) > 0:
                self.excel_data.append({
                    'Timestamp': '',
                    'Event_Type': '--- GAP BETWEEN ATTACKS ---',
                    'Details': '',
                    'Duration_Seconds': ''
                })
                self.save_excel_log()
            
            # Log attack start
            start_time_str = self.attack_start_time.strftime("%Y-%m-%d %H:%M:%S")
            self.log_message(f"Attack started at {start_time_str}")
            self.log_attack_event_to_csv("ATTACK_START", f"Attack started at {start_time_str}")
            
            # Start attack in a separate thread
            self.attack_thread = threading.Thread(target=self.run_attack, daemon=True)
            self.attack_thread.start()
    
    def stop_attack(self):
        if self.attack_running:
            self.attack_running = False
            self.attack_end_time = datetime.datetime.now()
            self.attacker_status_var.set("Attacker Status: Inactive")
            self.attacker_status_label.configure(fg="gray")
            # Re-enable Start Attack button when attack stops
            self.start_attack_btn.configure(state=tk.NORMAL)
            self.stop_attack_btn.configure(state=tk.DISABLED)
            
            # Log attack end and duration
            end_time_str = self.attack_end_time.strftime("%Y-%m-%d %H:%M:%S")
            self.log_message(f"Attack stopped at {end_time_str}")
            self.log_attack_event_to_csv("ATTACK_STOP", f"Attack stopped at {end_time_str}")
            
            # Calculate and log duration if start time is available
            if self.attack_start_time:
                duration = self.attack_end_time - self.attack_start_time
                duration_seconds = duration.total_seconds()
                self.log_message(f"Attack duration: {duration_seconds:.1f} seconds")
                self.log_attack_event_to_csv("ATTACK_DURATION", f"Attack duration: {duration_seconds:.1f} seconds", duration_seconds)
                
                # Log summary statistics
                self.log_message(f"Total requests sent: {self.request_count}")
                self.log_message(f"Successful requests (200): {self.success_count}")
                self.log_message(f"Blocked requests (429): {self.blocked_count}")
                
                # Log summary to Excel
                self.log_attack_event_to_csv("ATTACK_SUMMARY", f"Total: {self.request_count}, Successful: {self.success_count}, Blocked: {self.blocked_count}")
    
    def run_attack(self):
        while self.attack_running:
            try:
                # Send request to server
                response = requests.get('http://127.0.0.1:5000/', timeout=5)
                
                # Update counters
                self.request_count += 1
                
                if response.status_code == 200:
                    self.success_count += 1
                elif response.status_code == 429:
                    self.blocked_count += 1
                
                # Update GUI
                self.update_stats()
                # Highlight 429 responses for better visibility
                if response.status_code == 429:
                    self.log_message(f"[REQ #{self.request_count}] >>> RATE LIMITED <<< {response.status_code} {response.reason}")
                else:
                    self.log_message(f"[REQ #{self.request_count}] {response.status_code} {response.reason}")
                
                # Small delay to control request rate (slower to show 429 responses)
                time.sleep(0.3)
            except requests.exceptions.ConnectionError:
                self.log_message("[ERROR] Cannot connect to server. Is it running?")
                time.sleep(1)
            except requests.exceptions.RequestException as e:
                self.log_message(f"[ERROR] Request failed: {str(e)}")
                time.sleep(1)
            except Exception as e:
                self.log_message(f"[ERROR] Unexpected error: {str(e)}")
                time.sleep(1)
    
    def update_stats(self):
        # Schedule GUI update on main thread
        self.root.after(0, self._update_stats_gui)
    
    def _update_stats_gui(self):
        self.requests_sent_var.set(f"Requests Sent: {self.request_count}")
        self.successful_var.set(f"Successful (200 OK): {self.success_count}")
        self.blocked_var.set(f"Blocked (429): {self.blocked_count}")
    
    def refresh_stats(self):
        """Reset statistics and clear logs"""
        # Reset counters
        self.request_count = 0
        self.success_count = 0
        self.blocked_count = 0
        
        # Update GUI
        self._update_stats_gui()
        
        # Clear log text
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state=tk.DISABLED)
        
        # Reset system monitoring if available
        if PSUTIL_AVAILABLE:
            self.cpu_label.config(text="CPU: 0%")
            self.ram_label.config(text="RAM: 0%")
        
        # Note: We don't clear Excel data buffer or file on refresh to maintain persistent logs
        # Only clear the in-memory buffer, not the saved file
        if PANDAS_AVAILABLE and hasattr(self, 'excel_data'):
            # Keep existing excel_data for persistence, just continue appending to it
            pass
        
        self.log_message("Statistics and logs refreshed")
    
    def view_log_details(self):
        """Open the Excel log file to view detailed logs"""
        try:
            import os
            import platform
            import subprocess
            
            log_file = 'attack_log.xlsx'
            if os.path.exists(log_file):
                # Open the file with the default application
                if platform.system() == 'Windows':
                    os.startfile(log_file)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(['open', log_file])
                else:  # Linux
                    subprocess.call(['xdg-open', log_file])
                self.log_message("Opening log details in Excel...")
            else:
                self.log_message("No log file found. Start an attack to generate logs.")
        except Exception as e:
            self.log_message(f"Failed to open log file: {str(e)}")
    
    def log_message(self, message):
        # Schedule log update on main thread
        self.root.after(0, self._log_message_gui, message)
    
    def _log_message_gui(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
    
    def init_logging(self):
        """Initialize Excel logging if available"""
        # Initialize Excel logging if pandas is available
        if PANDAS_AVAILABLE:
            try:
                import os
                # Check if log file already exists and load existing data
                if os.path.exists('attack_log.xlsx'):
                    # Load existing data
                    try:
                        existing_df = pd.read_excel('attack_log.xlsx')
                        self.excel_data = existing_df.to_dict('records')
                    except Exception:
                        # If we can't read existing file, start with empty data
                        self.excel_data = []
                else:
                    # Create empty Excel file with headers if it doesn't exist
                    self.excel_data = []
                    df = pd.DataFrame(columns=['Timestamp', 'Event_Type', 'Details', 'Duration_Seconds'])
                    df.to_excel('attack_log.xlsx', index=False)
            except Exception as e:
                print(f"Failed to initialize Excel log file: {e}")
                self.excel_data = []
        else:
            self.excel_data = None
    
    def log_request_to_csv(self, ip, status_code, message):
        """Log request details to Excel if available"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Log to Excel data buffer if available
            if PANDAS_AVAILABLE:
                if hasattr(self, 'excel_data'):
                    self.excel_data.append({
                        'Timestamp': timestamp,
                        'Event_Type': 'REQUEST',
                        'Details': f'{ip} - {status_code} {message}',
                        'Duration_Seconds': ''
                    })
                    
                    # Save to Excel file immediately
                    self.save_excel_log()
                else:
                    print("excel_data attribute not found")
        except Exception as e:
            print(f"Error in log_request_to_csv: {e}")
    
    def log_attack_event_to_csv(self, event_type, details, duration=None):
        """Log attack events (start, stop, duration) to Excel if available"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Log to Excel data buffer if available
            if PANDAS_AVAILABLE:
                if hasattr(self, 'excel_data'):
                    duration_str = str(duration) if duration is not None else ''
                    self.excel_data.append({
                        'Timestamp': timestamp,
                        'Event_Type': event_type,
                        'Details': details,
                        'Duration_Seconds': duration_str
                    })
                    
                    # Save to Excel file immediately
                    self.save_excel_log()
                else:
                    print("excel_data attribute not found for attack event")
        except Exception as e:
            print(f"Error in log_attack_event_to_csv: {e}")
    
    def save_excel_log(self):
        """Save accumulated log data to Excel file"""
        if PANDAS_AVAILABLE and hasattr(self, 'excel_data'):
            try:
                # Save to Excel file
                df = pd.DataFrame(self.excel_data)
                df.to_excel('attack_log.xlsx', index=False)
            except Exception as e:
                print(f"Failed to save Excel log: {e}")
    
    def monitor_health(self):
        """Monitor server health (CPU and RAM usage)"""
        if not PSUTIL_AVAILABLE:
            return
            
        while self.server_running:
            try:
                # Get CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Get RAM usage
                ram_percent = psutil.virtual_memory().percent
                
                # Update GUI
                self.root.after(0, self.update_health_display, cpu_percent, ram_percent)
                
                time.sleep(1)  # Update every second
            except Exception:
                pass  # Ignore errors in health monitoring
    
    def update_health_display(self, cpu_percent, ram_percent):
        """Update the health display in the GUI"""
        self.cpu_label.config(text=f"CPU: {cpu_percent:.1f}%")
        self.ram_label.config(text=f"RAM: {ram_percent:.1f}%")
    
    def update_blacklist_status(self, active, ip):
        """Update the blacklist status display"""
        if active:
            self.blacklist_status_var.set(f"Blacklist Status: Active (IP {ip} Banned)")
            self.blacklist_status_label.configure(fg="red")
        else:
            self.blacklist_status_var.set("Blacklist Status: Inactive")
            self.blacklist_status_label.configure(fg="gray")
    
    def update_defense_chain_status(self, event_type, details):
        """Update the defense chain visualization based on events"""
        # This method updates the visual status of defense components based on events
        try:
            if hasattr(self, 'firewall_status') and hasattr(self, 'limiter_status') and hasattr(self, 'app_status'):
                if event_type == "BLOCKED":
                    # Update firewall status
                    self.firewall_status.config(text="BLOCKING", fg="red")
                    # Reset after a short delay
                    self.root.after(1000, lambda: self.firewall_status.config(text="ACTIVE", fg="green"))
                elif event_type == "RATE_LIMITED":
                    # Update rate limiter status
                    self.limiter_status.config(text="LIMITING", fg="orange")
                    # Reset after a short delay
                    self.root.after(1000, lambda: self.limiter_status.config(text="5 req/10 sec", fg="#7b1fa2"))
                elif event_type == "BLACKLISTED":
                    # Update both rate limiter and firewall
                    self.limiter_status.config(text="BLACKLISTING", fg="red")
                    self.firewall_status.config(text="BLOCKING", fg="red")
                    # Reset after a short delay
                    self.root.after(1000, lambda: self.limiter_status.config(text="5 req/10 sec", fg="#7b1fa2"))
                    self.root.after(1000, lambda: self.firewall_status.config(text="ACTIVE", fg="green"))
                elif event_type == "ALLOWED":
                    # Update application status
                    self.app_status.config(text="PROCESSING", fg="blue")
                    # Reset after a short delay
                    self.root.after(1000, lambda: self.app_status.config(text="PROTECTED", fg="#388e3c"))
        except Exception:
            # Silently ignore visualization errors
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = DoSSimulatorApp(root)
    root.mainloop()
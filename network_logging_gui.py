#!/usr/bin/env python3
"""
Network Logging GUI - Cross-Platform Network Monitoring Dashboard
Main GUI application with status monitoring, log viewing, and scheduler setup
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import subprocess
import platform
import os
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import re

# Import the main monitoring module
try:
    import netLogging
except ImportError:
    print("Error: netLogging.py must be in the same directory")
    sys.exit(1)


class NetworkMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🌐 Network Logging Monitor v3.1")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # State variables
        self.monitoring_active = False
        self.monitoring_thread = None
        self.stop_monitoring_flag = False
        self.last_check_time = None
        self.stats = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'last_status': 'Unknown'
        }
        
        # Get project directory
        self.project_dir = Path(__file__).parent.absolute()
        self.logs_dir = self.project_dir / "logs"
        self.config_file = self.project_dir / "config.json"
        
        # Load configuration
        self.load_config()
        
        # Setup GUI
        self.setup_ui()
        
        # Start status update loop
        self.update_status_display()
        
    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            messagebox.showerror("Config Error", f"Failed to load config.json:\n{e}")
            self.config = {}
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🌐 Network Logging Monitor", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Status Frame
        self.create_status_frame(main_frame)
        
        # Quick Stats Frame
        self.create_stats_frame(main_frame)
        
        # Recent Activity Frame
        self.create_activity_frame(main_frame)
        
        # Control Buttons Frame
        self.create_control_frame(main_frame)
        
        # Configuration Frame
        self.create_config_frame(main_frame)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        
    def create_status_frame(self, parent):
        """Create status display frame"""
        frame = ttk.LabelFrame(parent, text="📊 Current Status", padding="10")
        frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Monitoring status
        status_frame = ttk.Frame(frame)
        status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Label(status_frame, text="Monitoring:").grid(row=0, column=0, sticky=tk.W)
        self.status_label = ttk.Label(status_frame, text="● Stopped", 
                                     foreground="red", font=('Arial', 10, 'bold'))
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Start/Stop buttons
        self.start_button = ttk.Button(status_frame, text="▶ Start", 
                                       command=self.start_monitoring)
        self.start_button.grid(row=0, column=2, padx=5)
        
        self.stop_button = ttk.Button(status_frame, text="⏹ Stop", 
                                      command=self.stop_monitoring, state='disabled')
        self.stop_button.grid(row=0, column=3, padx=5)
        
        # Last check time
        ttk.Label(frame, text="Last Check:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.last_check_label = ttk.Label(frame, text="Never", font=('Arial', 9))
        self.last_check_label.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # Gateway status
        ttk.Label(frame, text="Gateway:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.gateway_label = ttk.Label(frame, text="Unknown", font=('Arial', 9))
        self.gateway_label.grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        
        # Internet status
        ttk.Label(frame, text="Internet:").grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        self.internet_label = ttk.Label(frame, text="Unknown", font=('Arial', 9))
        self.internet_label.grid(row=3, column=1, sticky=tk.W, pady=(5, 0))
        
    def create_stats_frame(self, parent):
        """Create quick statistics frame"""
        frame = ttk.LabelFrame(parent, text="📈 Quick Statistics", padding="10")
        frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Total checks
        ttk.Label(frame, text="Total Checks:").grid(row=0, column=0, sticky=tk.W)
        self.total_checks_label = ttk.Label(frame, text="0", font=('Arial', 10, 'bold'))
        self.total_checks_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Success rate
        ttk.Label(frame, text="Success Rate:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.success_rate_label = ttk.Label(frame, text="0.0%", font=('Arial', 10, 'bold'))
        self.success_rate_label.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # Session uptime
        ttk.Label(frame, text="Session Uptime:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.uptime_label = ttk.Label(frame, text="Not running", font=('Arial', 9))
        self.uptime_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=(5, 0))
        
        # Last result
        ttk.Label(frame, text="Last Result:").grid(row=1, column=2, sticky=tk.W, padx=(20, 0), pady=(5, 0))
        self.last_result_label = ttk.Label(frame, text="—", font=('Arial', 9))
        self.last_result_label.grid(row=1, column=3, sticky=tk.W, padx=5, pady=(5, 0))
        
    def create_activity_frame(self, parent):
        """Create recent activity log frame"""
        frame = ttk.LabelFrame(parent, text="📝 Recent Activity", padding="10")
        frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        parent.rowconfigure(3, weight=1)
        
        # Activity log text area
        self.activity_log = scrolledtext.ScrolledText(frame, height=10, width=80, 
                                                       wrap=tk.WORD, font=('Consolas', 9))
        self.activity_log.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # Add context menu (right-click menu)
        self.activity_context_menu = tk.Menu(self.activity_log, tearoff=0)
        self.activity_context_menu.add_command(label="Copy", command=self.copy_activity_selection)
        self.activity_context_menu.add_command(label="Select All", command=self.select_all_activity)
        self.activity_context_menu.add_separator()
        self.activity_context_menu.add_command(label="Clear Log", command=self.clear_activity)
        
        self.activity_log.bind("<Button-3>", self.show_activity_context_menu)  # Right-click
        
        # Add welcome message
        self.log_activity("🚀 Network Logging Monitor started")
        self.log_activity(f"📁 Logs directory: {self.logs_dir}")
        self.log_activity("ℹ️  Click 'Start' to begin monitoring")
        
    def create_control_frame(self, parent):
        """Create control buttons frame"""
        frame = ttk.Frame(parent, padding="5")
        frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Manual test button
        ttk.Button(frame, text="🔬 Run Manual Test", 
                  command=self.run_manual_test).grid(row=0, column=0, padx=5)
        
        # View logs button
        ttk.Button(frame, text="📄 View MTR Logs", 
                  command=self.open_log_viewer).grid(row=0, column=1, padx=5)
        
        # Open logs folder button
        ttk.Button(frame, text="📁 Open Logs Folder", 
                  command=self.open_logs_folder).grid(row=0, column=2, padx=5)
        
        # Analyze logs button
        ttk.Button(frame, text="📊 Analyze Logs", 
                  command=self.analyze_logs).grid(row=0, column=3, padx=5)
        
        # Clear activity button
        ttk.Button(frame, text="🗑️ Clear Activity", 
                  command=self.clear_activity).grid(row=0, column=4, padx=5)
        
    def create_config_frame(self, parent):
        """Create configuration buttons frame"""
        frame = ttk.LabelFrame(parent, text="⚙️ Configuration", padding="10")
        frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Edit config button
        ttk.Button(frame, text="📝 Edit config.json", 
                  command=self.edit_config).grid(row=0, column=0, padx=5)
        
        # Setup scheduler button (admin rights)
        ttk.Button(frame, text="⏰ Setup Scheduler (Admin)", 
                  command=self.setup_scheduler).grid(row=0, column=1, padx=5)
        
        # Discover ISP hops button
        ttk.Button(frame, text="🔍 Discover ISP Hops", 
                  command=self.discover_isp_hops).grid(row=0, column=2, padx=5)
        
        # Probe TCP hosts button
        ttk.Button(frame, text="🔌 Probe TCP Hosts", 
                  command=self.probe_tcp_hosts).grid(row=0, column=3, padx=5)
        
    def log_activity(self, message):
        """Add message to activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activity_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.activity_log.see(tk.END)
        
    def clear_activity(self):
        """Clear activity log"""
        self.activity_log.delete(1.0, tk.END)
        self.log_activity("🗑️ Activity log cleared")
    
    def show_activity_context_menu(self, event):
        """Show context menu on right-click"""
        try:
            self.activity_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.activity_context_menu.grab_release()
    
    def copy_activity_selection(self):
        """Copy selected text to clipboard"""
        try:
            selected_text = self.activity_log.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
            self.log_activity("📋 Text copied to clipboard")
        except tk.TclError:
            # No selection
            self.log_activity("⚠️ No text selected to copy")
    
    def select_all_activity(self):
        """Select all text in activity log"""
        self.activity_log.tag_add(tk.SEL, "1.0", tk.END)
        self.activity_log.mark_set(tk.INSERT, "1.0")
        self.activity_log.see(tk.INSERT)
        
    def start_monitoring(self):
        """Start continuous monitoring in background thread"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.stop_monitoring_flag = False
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(text="● Running", foreground="green")
        
        self.log_activity("▶️ Starting continuous monitoring...")
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        if not self.monitoring_active:
            return
            
        self.stop_monitoring_flag = True
        self.monitoring_active = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="● Stopped", foreground="red")
        
        self.log_activity("⏹️ Monitoring stopped")
        
    def monitoring_loop(self):
        """Background monitoring loop"""
        self.session_start_time = time.time()
        
        while not self.stop_monitoring_flag:
            try:
                # Run a monitoring cycle
                self.log_activity("🔄 Running monitoring check...")
                
                # Check gateway
                gateway = netLogging.get_gateway_ip()
                if gateway:
                    self.gateway_label.config(text=f"{gateway} ✓", foreground="green")
                    self.log_activity(f"✓ Gateway reachable: {gateway}")
                else:
                    self.gateway_label.config(text="Not found ✗", foreground="red")
                    self.log_activity("✗ Gateway not reachable")
                
                # Check internet (ping Cloudflare)
                # Note: netLogging.ping() returns (success, avg_latency_ms) or just success
                ping_result = netLogging.ping("1.1.1.1")
                internet_ok = ping_result if isinstance(ping_result, bool) else ping_result[0] if isinstance(ping_result, tuple) else bool(ping_result)
                
                if internet_ok:
                    self.internet_label.config(text="Connected ✓", foreground="green")
                    self.log_activity("✓ Internet connection OK")
                    self.stats['successful_checks'] += 1
                    self.stats['last_status'] = 'Success'
                else:
                    self.internet_label.config(text="Disconnected ✗", foreground="red")
                    self.log_activity("✗ Internet connection FAILED")
                    self.stats['failed_checks'] += 1
                    self.stats['last_status'] = 'Failed'
                
                self.stats['total_checks'] += 1
                self.last_check_time = datetime.now()
                
                # Wait before next check (default 60 seconds)
                interval = self.config.get('check_interval_seconds', 60)
                for _ in range(interval):
                    if self.stop_monitoring_flag:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.log_activity(f"❌ Error in monitoring loop: {e}")
                time.sleep(5)
                
    def update_status_display(self):
        """Update status display periodically"""
        if self.last_check_time:
            self.last_check_label.config(text=self.last_check_time.strftime("%Y-%m-%d %H:%M:%S"))
        
        # Update stats
        self.total_checks_label.config(text=str(self.stats['total_checks']))
        
        if self.stats['total_checks'] > 0:
            success_rate = (self.stats['successful_checks'] / self.stats['total_checks']) * 100
            self.success_rate_label.config(text=f"{success_rate:.1f}%")
            
            if success_rate >= 95:
                self.success_rate_label.config(foreground="green")
            elif success_rate >= 80:
                self.success_rate_label.config(foreground="orange")
            else:
                self.success_rate_label.config(foreground="red")
        
        self.last_result_label.config(text=self.stats['last_status'])
        
        # Update session uptime
        if self.monitoring_active and hasattr(self, 'session_start_time'):
            uptime = time.time() - self.session_start_time
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            seconds = int(uptime % 60)
            self.uptime_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Schedule next update
        self.root.after(1000, self.update_status_display)
        
    def run_manual_test(self):
        """Run a manual network test"""
        self.log_activity("🔬 Running manual test...")
        
        def run_test():
            try:
                # Run the main netLogging script
                result = subprocess.run(
                    [sys.executable, str(self.project_dir / "netLogging.py")],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    self.log_activity("✓ Manual test completed successfully")
                    self.log_activity(f"Output: {result.stdout[:200]}...")
                else:
                    self.log_activity(f"✗ Test failed with code {result.returncode}")
                    if result.stderr:
                        self.log_activity(f"Error: {result.stderr[:200]}")
                        
            except subprocess.TimeoutExpired:
                self.log_activity("⏱️ Test timed out after 120 seconds")
            except Exception as e:
                self.log_activity(f"❌ Test error: {e}")
                
        # Run in background thread
        threading.Thread(target=run_test, daemon=True).start()
        
    def open_log_viewer(self):
        """Open log viewer window"""
        LogViewerWindow(self.root, self.logs_dir)
        
    def open_logs_folder(self):
        """Open logs folder in file explorer"""
        try:
            if platform.system() == 'Windows':
                os.startfile(self.logs_dir)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(self.logs_dir)])
            else:  # Linux
                subprocess.run(['xdg-open', str(self.logs_dir)])
            self.log_activity(f"📁 Opened logs folder: {self.logs_dir}")
        except Exception as e:
            self.log_activity(f"❌ Failed to open folder: {e}")
            messagebox.showerror("Error", f"Could not open logs folder:\n{e}")
            
    def analyze_logs(self):
        """Run log analysis"""
        self.log_activity("📊 Running log analysis...")
        
        def run_analysis():
            try:
                result = subprocess.run(
                    [sys.executable, str(self.project_dir / "analyze_netlog.py")],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    self.log_activity("✓ Analysis completed")
                    # Show results in a new window
                    self.show_analysis_results(result.stdout)
                else:
                    self.log_activity(f"✗ Analysis failed: {result.stderr}")
                    
            except Exception as e:
                self.log_activity(f"❌ Analysis error: {e}")
                
        threading.Thread(target=run_analysis, daemon=True).start()
        
    def show_analysis_results(self, results):
        """Show analysis results in popup window"""
        window = tk.Toplevel(self.root)
        window.title("📊 Log Analysis Results")
        window.geometry("700x500")
        
        text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=('Consolas', 9))
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_area.insert(tk.END, results)
        text_area.config(state='disabled')
        
        ttk.Button(window, text="Close", command=window.destroy).pack(pady=5)
        
    def edit_config(self):
        """Open config.json in default editor"""
        try:
            if platform.system() == 'Windows':
                os.startfile(self.config_file)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', str(self.config_file)])
            else:
                subprocess.run(['xdg-open', str(self.config_file)])
            self.log_activity("📝 Opened config.json in editor")
        except Exception as e:
            self.log_activity(f"❌ Failed to open config: {e}")
            messagebox.showerror("Error", f"Could not open config.json:\n{e}")
            
    def setup_scheduler(self):
        """Setup automated scheduler with admin rights"""
        system = platform.system()
        
        if system == 'Windows':
            self.setup_windows_scheduler()
        elif system == 'Darwin':
            self.setup_macos_scheduler()
        else:
            self.setup_linux_scheduler()
            
    def setup_windows_scheduler(self):
        """Setup Windows Task Scheduler with UAC elevation"""
        script_path = self.project_dir / "setup_windows_scheduler.ps1"
        
        if not script_path.exists():
            messagebox.showerror("Error", "setup_windows_scheduler.ps1 not found!")
            return
            
        self.log_activity("⏰ Launching Windows Task Scheduler setup (requires admin)...")
        
        try:
            # Run PowerShell script with admin elevation
            subprocess.run([
                'powershell.exe',
                '-Command',
                f'Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File \'{script_path}\'" -Verb RunAs'
            ])
            self.log_activity("✓ Scheduler setup launched (check PowerShell window)")
        except Exception as e:
            self.log_activity(f"❌ Failed to launch scheduler: {e}")
            messagebox.showerror("Error", f"Failed to setup scheduler:\n{e}")
            
    def setup_macos_scheduler(self):
        """Setup macOS launchd with admin rights"""
        script_path = self.project_dir / "setup_macos_launchd.sh"
        
        if not script_path.exists():
            messagebox.showerror("Error", "setup_macos_launchd.sh not found!")
            return
            
        self.log_activity("⏰ Launching macOS launchd setup...")
        
        try:
            # Run with osascript for admin prompt
            subprocess.run([
                'osascript',
                '-e',
                f'do shell script "bash \'{script_path}\'" with administrator privileges'
            ])
            self.log_activity("✓ Scheduler setup completed")
        except Exception as e:
            self.log_activity(f"❌ Failed to setup scheduler: {e}")
            messagebox.showerror("Error", f"Failed to setup scheduler:\n{e}")
            
    def setup_linux_scheduler(self):
        """Setup Linux cron with sudo"""
        script_path = self.project_dir / "setup_linux_cron.sh"
        
        if not script_path.exists():
            messagebox.showerror("Error", "setup_linux_cron.sh not found!")
            return
            
        self.log_activity("⏰ Launching Linux cron setup...")
        
        try:
            # Try with pkexec (graphical sudo)
            if self.command_exists('pkexec'):
                subprocess.run(['pkexec', 'bash', str(script_path)])
            else:
                # Fallback to terminal
                subprocess.run(['x-terminal-emulator', '-e', f'sudo bash {script_path}'])
            self.log_activity("✓ Scheduler setup completed")
        except Exception as e:
            self.log_activity(f"❌ Failed to setup scheduler: {e}")
            messagebox.showerror("Error", f"Failed to setup scheduler:\n{e}")
            
    def command_exists(self, cmd):
        """Check if command exists"""
        return subprocess.run(['which', cmd], capture_output=True).returncode == 0
        
    def discover_isp_hops(self):
        """Run ISP hop discovery"""
        self.log_activity("🔍 Discovering ISP hops...")
        
        def run_discovery():
            try:
                result = subprocess.run(
                    [sys.executable, str(self.project_dir / "discover_isp_hops.py")],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    self.log_activity("✓ ISP discovery completed")
                    self.show_analysis_results(result.stdout)
                else:
                    self.log_activity(f"✗ Discovery failed: {result.stderr}")
                    
            except Exception as e:
                self.log_activity(f"❌ Discovery error: {e}")
                
        threading.Thread(target=run_discovery, daemon=True).start()
        
    def probe_tcp_hosts(self):
        """Run TCP host probing"""
        self.log_activity("🔌 Probing TCP hosts...")
        
        def run_probe():
            try:
                result = subprocess.run(
                    [sys.executable, str(self.project_dir / "probe_tcp_hosts.py"), "--from-config", "--tls"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    # Extract summary from output
                    output_lines = result.stdout.strip().split("\n")
                    summary = "Done"
                    for line in output_lines:
                        if "Summary:" in line:
                            summary = line.split("📊", 1)[-1].strip() if "📊" in line else line.split("Summary:", 1)[-1].strip()
                            break
                    
                    self.log_activity(f"✓ TCP probing completed - {summary}")
                    self.show_analysis_results(result.stdout)
                else:
                    error_msg = result.stderr.strip() if result.stderr.strip() else result.stdout.strip()
                    self.log_activity(f"✗ Probing failed: {error_msg}")
                    
            except Exception as e:
                self.log_activity(f"❌ Probe error: {e}")
                
        threading.Thread(target=run_probe, daemon=True).start()


class LogViewerWindow:
    """Separate window for viewing and filtering log files"""
    
    def __init__(self, parent, logs_dir):
        self.window = tk.Toplevel(parent)
        self.window.title("📄 MTR Log Viewer")
        self.window.geometry("1000x600")
        self.logs_dir = Path(logs_dir)
        
        self.setup_ui()
        self.load_log_files()
        
    def setup_ui(self):
        """Setup log viewer UI"""
        # Control frame
        control_frame = ttk.Frame(self.window, padding="10")
        control_frame.pack(fill=tk.X)
        
        # File selection
        ttk.Label(control_frame, text="Select Log File:").pack(side=tk.LEFT, padx=5)
        self.file_combo = ttk.Combobox(control_frame, width=50, state='readonly')
        self.file_combo.pack(side=tk.LEFT, padx=5)
        self.file_combo.bind('<<ComboboxSelected>>', self.on_file_selected)
        
        # Refresh button
        ttk.Button(control_frame, text="🔄 Refresh", 
                  command=self.load_log_files).pack(side=tk.LEFT, padx=5)
        
        # Search frame
        search_frame = ttk.Frame(self.window, padding="10")
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="Search/Filter:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        ttk.Button(search_frame, text="🔍 Search", 
                  command=self.on_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Clear", 
                  command=self.clear_search).pack(side=tk.LEFT, padx=5)
        
        # Log display
        log_frame = ttk.Frame(self.window, padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.NONE, 
                                                   font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Context menu for log viewer
        self.log_context_menu = tk.Menu(self.log_text, tearoff=0)
        self.log_context_menu.add_command(label="Copy", command=self.copy_log_selection)
        self.log_context_menu.add_command(label="Select All", command=self.select_all_log)
        self.log_context_menu.add_separator()
        self.log_context_menu.add_command(label="Export Selection", command=self.export_log_selection)
        
        self.log_text.bind("<Button-3>", self.show_log_context_menu)
        
        # Syntax highlighting tags
        self.log_text.tag_config('ip', foreground='blue')
        self.log_text.tag_config('timestamp', foreground='green')
        self.log_text.tag_config('error', foreground='red')
        self.log_text.tag_config('separator', foreground='purple', font=('Consolas', 9, 'bold'))
        
        # Status bar
        self.status_bar = ttk.Label(self.window, text="Select a log file to view", 
                                    relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def load_log_files(self):
        """Load list of log files"""
        try:
            log_files = sorted(self.logs_dir.glob("*.log"), reverse=True)
            file_names = [f.name for f in log_files]
            self.file_combo['values'] = file_names
            
            if file_names:
                self.file_combo.current(0)
                self.on_file_selected()
                
            self.status_bar.config(text=f"Found {len(file_names)} log files")
        except Exception as e:
            self.status_bar.config(text=f"Error loading files: {e}")
            
    def on_file_selected(self, event=None):
        """Handle file selection"""
        selected = self.file_combo.get()
        if not selected:
            return
            
        file_path = self.logs_dir / selected
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            self.display_log_content(content)
            self.status_bar.config(text=f"Loaded: {selected} ({len(content)} bytes)")
        except Exception as e:
            self.status_bar.config(text=f"Error reading file: {e}")
            
    def display_log_content(self, content):
        """Display log content with syntax highlighting"""
        self.log_text.delete(1.0, tk.END)
        
        lines = content.split('\n')
        for line in lines:
            # Insert line
            start_idx = self.log_text.index(tk.END)
            self.log_text.insert(tk.END, line + '\n')
            end_idx = self.log_text.index(tk.END)
            
            # Apply syntax highlighting
            if '=======' in line or '-------' in line:
                self.log_text.tag_add('separator', start_idx, end_idx)
            elif re.search(r'\d{4}-\d{2}-\d{2}', line):
                self.log_text.tag_add('timestamp', start_idx, end_idx)
            
            # Highlight IP addresses
            for match in re.finditer(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', line):
                ip_start = f"{start_idx}+{match.start()}c"
                ip_end = f"{start_idx}+{match.end()}c"
                self.log_text.tag_add('ip', ip_start, ip_end)
                
            # Highlight errors
            if 'error' in line.lower() or 'failed' in line.lower() or '100.0% packet loss' in line:
                self.log_text.tag_add('error', start_idx, end_idx)
                
    def on_search(self, event=None):
        """Search/filter log content"""
        search_term = self.search_entry.get().strip()
        if not search_term:
            return
            
        # Remove previous highlights
        self.log_text.tag_remove('search_highlight', 1.0, tk.END)
        
        # Search and highlight
        start_pos = '1.0'
        count = 0
        while True:
            pos = self.log_text.search(search_term, start_pos, tk.END, nocase=True)
            if not pos:
                break
            end_pos = f"{pos}+{len(search_term)}c"
            self.log_text.tag_add('search_highlight', pos, end_pos)
            start_pos = end_pos
            count += 1
            
        self.log_text.tag_config('search_highlight', background='yellow')
        self.status_bar.config(text=f"Found {count} matches for '{search_term}'")
        
        # Scroll to first match
        if count > 0:
            first_match = self.log_text.search(search_term, '1.0', tk.END, nocase=True)
            self.log_text.see(first_match)
            
    def clear_search(self):
        """Clear search highlighting"""
        self.search_entry.delete(0, tk.END)
        self.log_text.tag_remove('search_highlight', 1.0, tk.END)
        self.status_bar.config(text="Search cleared")
    
    def show_log_context_menu(self, event):
        """Show context menu on right-click in log viewer"""
        try:
            self.log_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.log_context_menu.grab_release()
    
    def copy_log_selection(self):
        """Copy selected text from log to clipboard"""
        try:
            selected_text = self.log_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.window.clipboard_clear()
            self.window.clipboard_append(selected_text)
            self.status_bar.config(text="Text copied to clipboard")
        except tk.TclError:
            self.status_bar.config(text="No text selected to copy")
    
    def select_all_log(self):
        """Select all text in log viewer"""
        self.log_text.tag_add(tk.SEL, "1.0", tk.END)
        self.log_text.mark_set(tk.INSERT, "1.0")
        self.log_text.see(tk.INSERT)
    
    def export_log_selection(self):
        """Export selected text to file"""
        try:
            selected_text = self.log_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w') as f:
                    f.write(selected_text)
                self.status_bar.config(text=f"Exported to {filename}")
        except tk.TclError:
            self.status_bar.config(text="No text selected to export")
        except Exception as e:
            self.status_bar.config(text=f"Export failed: {e}")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = NetworkMonitorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

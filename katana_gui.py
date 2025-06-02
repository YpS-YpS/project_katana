import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import threading
import yaml
import os
import logging
import time
from pathlib import Path
from datetime import datetime

class KatanaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🗡️ Project Katana - Game Automation Tool")
        self.root.geometry("1000x800")
        self.root.minsize(1000, 800)
        
        # Set modern theme and styling
        self._setup_styling()
        
        # Initialize variables
        self.game_finder = None
        self.game_controller = None
        self.workflow_engine = None
        self.screen_analyzer = None
        self.games = {}
        self.selected_game = None
        
        # Enhanced logging variables
        self.current_run_folder = None
        self.current_game_name = None
        
        # Set up logging first
        self._setup_logging()
        
        # Try to initialize components
        self._initialize_components()
        
        # Create the GUI
        self.create_widgets()
    
    def _setup_styling(self):
        """Set up modern styling for the GUI"""
        # Configure ttk styles
        style = ttk.Style()
        
        # Use a modern theme
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'vista' in available_themes:
            style.theme_use('vista')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Segoe UI', 14, 'bold'))
        style.configure('Subtitle.TLabel', font=('Segoe UI', 10, 'bold'))
        style.configure('Status.TLabel', font=('Segoe UI', 9))
        
        # Configure button styles
        style.configure('Action.TButton', font=('Segoe UI', 9, 'bold'))
        style.configure('Success.TButton', font=('Segoe UI', 9, 'bold'))
        style.configure('Warning.TButton', font=('Segoe UI', 9, 'bold'))
        
        # Set window background
        self.root.configure(bg='#f0f0f0')
    
    def _setup_logging(self):
        """Set up enhanced logging with game-specific and run-specific folders"""
        try:
            # Create base log directory
            base_log_dir = Path("output/logs")
            base_log_dir.mkdir(parents=True, exist_ok=True)
            
            # Create main session log (for general GUI operations)
            session_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            session_log_file = base_log_dir / f"katana_session_{session_timestamp}.log"
            
            # Create formatters
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            
            # Set up file handler with UTF-8 encoding
            file_handler = logging.FileHandler(session_log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(file_formatter)
            
            # Set up console handler with UTF-8 encoding
            import sys
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(console_formatter)
            
            # Configure logger
            logging.basicConfig(
                level=logging.INFO,
                handlers=[file_handler, console_handler],
                force=True  # Override any existing configuration
            )
            
            self.logger = logging.getLogger(__name__)
            self.logger.info("Enhanced Katana logging initialized")
            self.logger.info(f"Session log: {session_log_file}")
            
        except Exception as e:
            print(f"Failed to setup logging: {e}")
            self.logger = logging.getLogger(__name__)
    
    def _create_run_specific_logging(self, game_name):
        """Create game-specific and run-specific logging folders"""
        try:
            # Create run timestamp
            run_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Create folder structure: output/logs/[game_name]/[timestamp]/
            game_folder = game_name.lower().replace(' ', '_').replace(':', '')
            self.current_run_folder = Path("output") / "logs" / game_folder / run_timestamp
            self.current_run_folder.mkdir(parents=True, exist_ok=True)
            
            # Create subfolders for organization
            screenshot_folder = self.current_run_folder / "screenshots"
            screenshot_folder.mkdir(exist_ok=True)
            (self.current_run_folder / "debug").mkdir(exist_ok=True)
            
            # Create run-specific log file
            run_log_file = self.current_run_folder / f"workflow_{run_timestamp}.log"
            
            # Create run-specific file handler
            run_file_handler = logging.FileHandler(run_log_file, encoding='utf-8')
            run_file_handler.setLevel(logging.INFO)
            run_file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            run_file_handler.setFormatter(run_file_formatter)
            
            # Add handler to root logger
            logging.getLogger().addHandler(run_file_handler)
            
            # Store reference for cleanup
            self.run_file_handler = run_file_handler
            
            self.logger.info(f"🗂️ Created run-specific logging for {game_name}")
            self.logger.info(f"📁 Run folder: {self.current_run_folder}")
            self.logger.info(f"📝 Workflow log: {run_log_file}")
            
            # CRITICAL: Update screen analyzer to use run-specific screenshot folder
            if self.screen_analyzer:
                old_dir = self.screen_analyzer.screenshot_dir
                new_dir = str(screenshot_folder)
                self.screen_analyzer.screenshot_dir = new_dir
                self.logger.info(f"📸 Screenshot dir changed: {old_dir} → {new_dir}")
                
                # Also update workflow_engine's screen_analyzer if it exists
                if hasattr(self, 'workflow_engine') and self.workflow_engine and hasattr(self.workflow_engine, 'screen_analyzer'):
                    self.workflow_engine.screen_analyzer.screenshot_dir = new_dir
                    self.logger.info(f"📸 Workflow engine screenshot dir updated: {new_dir}")
                
            return self.current_run_folder
            
        except Exception as e:
            self.logger.error(f"Failed to create run-specific logging: {e}")
            return None
    
    def _cleanup_run_logging(self):
        """Clean up run-specific logging handlers"""
        try:
            if hasattr(self, 'run_file_handler'):
                logging.getLogger().removeHandler(self.run_file_handler)
                self.run_file_handler.close()
                delattr(self, 'run_file_handler')
                
            # Reset screenshot directory to default
            default_dir = 'output/screenshots'
            if self.screen_analyzer:
                self.screen_analyzer.screenshot_dir = default_dir
                self.logger.info(f"📸 Screenshot dir reset to default: {default_dir}")
                
                # Also reset workflow_engine's screen_analyzer
                if hasattr(self, 'workflow_engine') and self.workflow_engine and hasattr(self.workflow_engine, 'screen_analyzer'):
                    self.workflow_engine.screen_analyzer.screenshot_dir = default_dir
                    self.logger.info(f"📸 Workflow engine screenshot dir reset to default: {default_dir}")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up run logging: {e}")
    
    def _initialize_components(self):
        """Initialize Katana components with error handling"""
        try:
            # Check if config directory exists
            if not os.path.exists("config"):
                self._create_default_config()
            
            # Check if settings.yaml exists
            if not os.path.exists("config/settings.yaml"):
                self._create_default_settings()
            
            # Import and initialize components
            from katana.core.game_finder import GameFinder
            from katana.core.game_controller import GameController
            from katana.core.workflow_engine import WorkflowEngine
            from katana.core.screen_analyzer import ScreenAnalyzer
            
            self.game_finder = GameFinder()
            self.game_controller = GameController()
            self.workflow_engine = WorkflowEngine()
            self.screen_analyzer = ScreenAnalyzer()
            
            # Find installed games
            self.games = self.game_finder.find_all_games()
            self.logger.info(f"Initialization successful. Found {len(self.games)} games.")
            
        except Exception as e:
            error_msg = f"Failed to initialize: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("Initialization Error", error_msg)
            # Continue with empty games dict
            self.games = {}
    
    def _create_default_config(self):
        """Create default configuration directory and files"""
        try:
            os.makedirs("config/games", exist_ok=True)
            os.makedirs("templates/screens", exist_ok=True)
            os.makedirs("output/logs", exist_ok=True)
            os.makedirs("output/screenshots", exist_ok=True)
            self.logger.info("Created config directory structure")
        except Exception as e:
            self.logger.error(f"Failed to create config directory: {e}")
    
    def _create_default_settings(self):
        """Create default settings.yaml file"""
        default_settings = {
            'steam_path': 'C:/Program Files (x86)/Steam',
            'epic_path': 'C:/Program Files/Epic Games',
            'steam_launch_options': '',
            'screenshot_dir': 'output/screenshots',
            'log_level': 'INFO',
            'template_matching_threshold': 0.8,
            'input_delay': 0.5,
            'timeout': 300,
            'mouse_move_duration': 0.6,
            'pre_click_delay': 0.4,
            'post_click_delay': 0.8
        }
        
        try:
            with open("config/settings.yaml", "w") as f:
                yaml.dump(default_settings, f, default_flow_style=False)
            self.logger.info("Created default settings.yaml")
        except Exception as e:
            self.logger.error(f"Failed to create settings.yaml: {e}")
    
    def create_widgets(self):
        # Create main header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🗡️ PROJECT KATANA", 
                              font=('Segoe UI', 18, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        subtitle_label = tk.Label(header_frame, text="Game Automation & Benchmarking Framework", 
                                 font=('Segoe UI', 10), 
                                 fg='#bdc3c7', bg='#2c3e50')
        subtitle_label.pack(side=tk.LEFT, padx=(0, 20), pady=15)
        
        # Version info
        version_label = tk.Label(header_frame, text="v1.0.0", 
                                font=('Segoe UI', 8), 
                                fg='#95a5a6', bg='#2c3e50')
        version_label.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Create notebook for tabs with modern styling
        style = ttk.Style()
        style.configure('Modern.TNotebook', tabposition='n')
        style.configure('Modern.TNotebook.Tab', padding=[20, 10])
        
        self.notebook = ttk.Notebook(self.root, style='Modern.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Create tabs with icons
        self.main_tab = ttk.Frame(self.notebook)
        self.template_tab = ttk.Frame(self.notebook)
        self.workflow_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.main_tab, text="🎮 Games & Control")
        self.notebook.add(self.template_tab, text="🎯 Template Tools")
        self.notebook.add(self.workflow_tab, text="⚙️ Workflow Editor")
        
        # Setup each tab
        self.setup_main_tab()
        self.setup_template_tab()
        self.setup_workflow_tab()
        
        # Status bar with modern styling
        status_frame = tk.Frame(self.root, bg='#34495e', height=30)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready" if self.games else "No games found - Check configuration")
        
        self.status_bar = tk.Label(status_frame, textvariable=self.status_var, 
                                  font=('Segoe UI', 9), fg='white', bg='#34495e', 
                                  anchor=tk.W, padx=10)
        self.status_bar.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
        
        # Add status icons
        time_label = tk.Label(status_frame, text=datetime.now().strftime("%H:%M"), 
                             font=('Segoe UI', 9), fg='#bdc3c7', bg='#34495e')
        time_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def setup_main_tab(self):
        # Create main container with modern styling
        main_container = tk.Frame(self.main_tab, bg='#ecf0f1')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create game selection frame with enhanced styling
        game_frame = tk.LabelFrame(main_container, text=" 🎮 Game Selection ", 
                                  font=('Segoe UI', 11, 'bold'), 
                                  fg='#2c3e50', bg='#ecf0f1',
                                  relief=tk.RIDGE, bd=2)
        game_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        # Game list with modern styling
        list_container = tk.Frame(game_frame, bg='#ecf0f1')
        list_container.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(list_container, text="📋 Available Games:", 
                font=('Segoe UI', 10, 'bold'), 
                fg='#34495e', bg='#ecf0f1').pack(anchor=tk.W, pady=(0, 5))
        
        # Game listbox with scrollbar
        list_frame = tk.Frame(list_container, bg='#ecf0f1')
        list_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.game_listbox = tk.Listbox(list_frame, height=6, 
                                      font=('Segoe UI', 9),
                                      selectbackground='#3498db',
                                      selectforeground='white',
                                      bg='white', fg='#2c3e50',
                                      relief=tk.FLAT, bd=1)
        self.game_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        game_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                      command=self.game_listbox.yview)
        game_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.game_listbox.config(yscrollcommand=game_scrollbar.set)
        
        # Populate game list
        self._populate_game_list()
        
        # Game details with modern styling
        tk.Label(list_container, text="ℹ️ Game Details:", 
                font=('Segoe UI', 10, 'bold'), 
                fg='#34495e', bg='#ecf0f1').pack(anchor=tk.W, pady=(10, 5))
        
        self.details_text = tk.Text(list_container, height=4, wrap=tk.WORD,
                                   font=('Segoe UI', 9), bg='white', fg='#2c3e50',
                                   relief=tk.FLAT, bd=1)
        self.details_text.pack(fill=tk.X, pady=(0, 10))
        self.details_text.config(state=tk.DISABLED)
        
        # Action buttons with modern styling (ENHANCED WITH OUTPUT FOLDER)
        button_frame = tk.Frame(list_container, bg='#ecf0f1')
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="🖥️ Test Monitors", 
                  command=self.test_monitor_detection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Refresh", 
                  command=self.refresh_games).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🔧 Test Components", 
                  command=self.test_components).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📊 Check Status", 
                  command=self.check_game_status).pack(side=tk.LEFT, padx=5)
        
        # NEW: Output folder button
        ttk.Button(button_frame, text="📁 Output Folder", 
                  command=self.open_output_folder).pack(side=tk.LEFT, padx=5)
        
        # Workflow control frame
        workflow_frame = tk.LabelFrame(main_container, text=" ⚡ Workflow Control ", 
                                      font=('Segoe UI', 11, 'bold'), 
                                      fg='#2c3e50', bg='#ecf0f1',
                                      relief=tk.RIDGE, bd=2)
        workflow_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0), padx=5)
        
        # Control buttons with enhanced styling
        control_container = tk.Frame(workflow_frame, bg='#ecf0f1')
        control_container.pack(fill=tk.X, padx=10, pady=10)
        
        wf_button_frame = tk.Frame(control_container, bg='#ecf0f1')
        wf_button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Main action buttons
        self.start_button = ttk.Button(wf_button_frame, text="▶️ Start Workflow", 
                                      command=self.start_workflow)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.launch_button = ttk.Button(wf_button_frame, text="🚀 Launch Game", 
                                       command=self.launch_game)
        self.launch_button.pack(side=tk.LEFT, padx=5)
        
        self.close_button = ttk.Button(wf_button_frame, text="🛑 Close Game", 
                                      command=self.close_game)
        self.close_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(wf_button_frame, text="⏹️ Stop Workflow", 
                                     command=self.stop_workflow)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.stop_button.config(state=tk.DISABLED)
        
        # Workflow log with modern styling
        tk.Label(control_container, text="📝 Workflow Log:", 
                font=('Segoe UI', 10, 'bold'), 
                fg='#34495e', bg='#ecf0f1').pack(anchor=tk.W, pady=(10, 5))
        
        log_frame = tk.Frame(control_container, bg='#ecf0f1')
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, 
                               font=('Consolas', 9), bg='#2c3e50', fg='#ecf0f1',
                               relief=tk.FLAT, bd=1)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, 
                                     command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        # Log control buttons (ENHANCED WITH RUN FOLDER)
        log_control_frame = tk.Frame(control_container, bg='#ecf0f1')
        log_control_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(log_control_frame, text="🗑️ Clear", 
                  command=self.clear_log).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(log_control_frame, text="💾 Save", 
                  command=self.save_log).pack(side=tk.RIGHT, padx=5)
        
        # NEW: Open current run folder button
        self.run_folder_button = ttk.Button(log_control_frame, text="📂 Run Folder", 
                                           command=self.open_current_run_folder, state=tk.DISABLED)
        self.run_folder_button.pack(side=tk.RIGHT, padx=5)
        
        # Set up game selection event
        self.game_listbox.bind('<<ListboxSelect>>', self.on_game_select)
    
    def setup_template_tab(self):
        """Setup the enhanced template tools tab"""
        template_container = tk.Frame(self.template_tab, bg='#ecf0f1')
        template_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Template capture section with modern styling
        capture_frame = tk.LabelFrame(template_container, text=" 🎯 Template Capture & Testing ", 
                                     font=('Segoe UI', 11, 'bold'), 
                                     fg='#2c3e50', bg='#ecf0f1',
                                     relief=tk.RIDGE, bd=2)
        capture_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        capture_content = tk.Frame(capture_frame, bg='#ecf0f1')
        capture_content.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(capture_content, text="📸 Capture UI elements for template matching:", 
                font=('Segoe UI', 10), fg='#34495e', bg='#ecf0f1').pack(anchor=tk.W, pady=(0, 10))
        
        # Capture buttons with enhanced styling
        capture_button_frame = tk.Frame(capture_content, bg='#ecf0f1')
        capture_button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(capture_button_frame, text="📷 Quick Screenshot", 
                  command=self.take_quick_screenshot).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(capture_button_frame, text="🎯 Capture Template", 
                  command=self.capture_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(capture_button_frame, text="🧪 Test Template", 
                  command=self.test_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(capture_button_frame, text="👁️ Monitor Template", 
                  command=self.monitor_template).pack(side=tk.LEFT, padx=5)
        
        # Template management section
        manage_frame = tk.LabelFrame(template_container, text=" 📁 Template Management ", 
                                    font=('Segoe UI', 11, 'bold'), 
                                    fg='#2c3e50', bg='#ecf0f1',
                                    relief=tk.RIDGE, bd=2)
        manage_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0), padx=5)
        
        manage_content = tk.Frame(manage_frame, bg='#ecf0f1')
        manage_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Template list with modern styling
        tk.Label(manage_content, text="📋 Available Templates:", 
                font=('Segoe UI', 10, 'bold'), 
                fg='#34495e', bg='#ecf0f1').pack(anchor=tk.W, pady=(0, 5))
        
        list_frame = tk.Frame(manage_content, bg='#ecf0f1')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.template_listbox = tk.Listbox(list_frame, font=('Segoe UI', 9),
                                          selectbackground='#e74c3c',
                                          selectforeground='white',
                                          bg='white', fg='#2c3e50',
                                          relief=tk.FLAT, bd=1)
        self.template_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        template_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                          command=self.template_listbox.yview)
        template_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.template_listbox.config(yscrollcommand=template_scrollbar.set)
        
        # Template management buttons
        template_button_frame = tk.Frame(manage_content, bg='#ecf0f1')
        template_button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(template_button_frame, text="🔄 Refresh", 
                  command=self.refresh_templates).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(template_button_frame, text="📂 Open Folder", 
                  command=self.open_templates_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(template_button_frame, text="👀 View Template", 
                  command=self.view_template).pack(side=tk.LEFT, padx=5)
        
        # Refresh template list initially
        self.refresh_templates()
    
    def setup_workflow_tab(self):
        """Setup the workflow editor tab"""
        workflow_container = tk.Frame(self.workflow_tab, bg='#ecf0f1')
        workflow_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Coming soon section with modern styling
        coming_soon_frame = tk.LabelFrame(workflow_container, text=" ⚙️ Workflow Editor ", 
                                         font=('Segoe UI', 11, 'bold'), 
                                         fg='#2c3e50', bg='#ecf0f1',
                                         relief=tk.RIDGE, bd=2)
        coming_soon_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        content_frame = tk.Frame(coming_soon_frame, bg='#ecf0f1')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Center content
        center_frame = tk.Frame(content_frame, bg='#ecf0f1')
        center_frame.pack(expand=True)
        
        tk.Label(center_frame, text="🚧 Visual Workflow Editor", 
                font=('Segoe UI', 18, 'bold'), 
                fg='#e67e22', bg='#ecf0f1').pack(pady=10)
        
        tk.Label(center_frame, text="Coming Soon!", 
                font=('Segoe UI', 14), 
                fg='#95a5a6', bg='#ecf0f1').pack(pady=5)
        
        tk.Label(center_frame, text="For now, edit YAML files directly using the button below:", 
                font=('Segoe UI', 10), 
                fg='#7f8c8d', bg='#ecf0f1').pack(pady=10)
        
        ttk.Button(center_frame, text="📁 Open Config Folder", 
                  command=self.open_config_folder).pack(pady=10)
        
        ttk.Button(center_frame, text="🔧 Visual Workflow Builder", 
                  command=self.open_workflow_builder).pack(pady=10)
        
        # Add workflow preview area
        preview_frame = tk.LabelFrame(content_frame, text=" 📋 Current Workflow Preview ", 
                                     font=('Segoe UI', 10, 'bold'), 
                                     fg='#34495e', bg='#ecf0f1')
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        self.workflow_preview = tk.Text(preview_frame, height=15, wrap=tk.WORD,
                                       font=('Consolas', 9), bg='white', fg='#2c3e50',
                                       relief=tk.FLAT, bd=1, state=tk.DISABLED)
        self.workflow_preview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # ==================== ENHANCED OUTPUT MANAGEMENT ====================
    
    def open_output_folder(self):
        """Open the main output folder in file explorer"""
        output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.run(['explorer', str(output_dir.resolve())])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['open', str(output_dir.resolve())])
            else:  # Linux
                subprocess.run(['xdg-open', str(output_dir.resolve())])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open output folder: {e}")
    
    def open_current_run_folder(self):
        """Open the current run-specific folder if available"""
        if self.current_run_folder and self.current_run_folder.exists():
            try:
                import subprocess
                import platform
                
                if platform.system() == "Windows":
                    subprocess.run(['explorer', str(self.current_run_folder.resolve())])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(['open', str(self.current_run_folder.resolve())])
                else:  # Linux
                    subprocess.run(['xdg-open', str(self.current_run_folder.resolve())])
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open run folder: {e}")
        else:
            messagebox.showinfo("Info", "No active run folder. Start a workflow to create one.")

    # ==================== CORE METHODS ====================
    
    def _populate_game_list(self):
        """Populate the game list"""
        self.game_listbox.delete(0, tk.END)
        
        if not self.games:
            self.game_listbox.insert(tk.END, "No games found")
            return
        
        for game_name in sorted(self.games.keys()):
            self.game_listbox.insert(tk.END, game_name)

    def refresh_games(self):
        """Refresh the list of installed games"""
        try:
            if self.game_finder:
                self.games = self.game_finder.find_all_games()
                self._populate_game_list()
                self.status_var.set(f"Found {len(self.games)} games")
                
                # Clear selection details
                self.details_text.config(state=tk.NORMAL)
                self.details_text.delete(1.0, tk.END)
                self.details_text.config(state=tk.DISABLED)
                self.selected_game = None
            else:
                messagebox.showwarning("Warning", "Game finder not initialized")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh games: {e}")
            self.logger.error(f"Error refreshing games: {e}")

    def on_game_select(self, event):
        """Handle game selection"""
        selection = self.game_listbox.curselection()
        if selection and self.games:
            game_name = self.game_listbox.get(selection[0])
            
            if game_name == "No games found":
                return
                
            self.selected_game = self.games.get(game_name)
            
            if self.selected_game:
                # Update details
                self.details_text.config(state=tk.NORMAL)
                self.details_text.delete(1.0, tk.END)
                
                details = f"Name: {game_name}\n"
                details += f"Platform: {self.selected_game.get('platform', 'Unknown')}\n"
                details += f"Path: {self.selected_game.get('path', 'Unknown')}\n"
                
                if self.selected_game.get('platform') == 'steam':
                    details += f"Steam App ID: {self.selected_game.get('app_id', 'Unknown')}\n"
                
                # Check if workflow exists
                workflow = self.selected_game.get('config', {}).get('workflow', [])
                details += f"Workflow steps: {len(workflow)}\n"
                
                self.details_text.insert(tk.END, details)
                self.details_text.config(state=tk.DISABLED)
                
                self.status_var.set(f"Selected {game_name}")

    def test_components(self):
        """Test that all components are working"""
        test_results = []
        
        # Test 1: Configuration loading
        try:
            with open("config/settings.yaml", "r") as f:
                settings = yaml.safe_load(f)
            test_results.append("✓ Settings loaded successfully")
        except Exception as e:
            test_results.append(f"✗ Settings error: {e}")
        
        # Test 2: Component initialization
        try:
            if self.game_finder:
                test_results.append("✓ Game finder initialized")
            else:
                test_results.append("✗ Game finder not initialized")
                
            if self.game_controller:
                test_results.append("✓ Game controller initialized")
            else:
                test_results.append("✗ Game controller not initialized")
                
            if self.workflow_engine:
                test_results.append("✓ Workflow engine initialized")
            else:
                test_results.append("✗ Workflow engine not initialized")
                
            if self.screen_analyzer:
                test_results.append("✓ Screen analyzer initialized")
            else:
                test_results.append("✗ Screen analyzer not initialized")
        except Exception as e:
            test_results.append(f"✗ Component test error: {e}")
        
        # Test 3: Directory structure
        dirs_to_check = ["config", "config/games", "output", "output/logs", "output/screenshots", "templates/screens"]
        for dir_path in dirs_to_check:
            if os.path.exists(dir_path):
                test_results.append(f"✓ Directory exists: {dir_path}")
            else:
                test_results.append(f"✗ Directory missing: {dir_path}")
        
        # Test 4: Steam path
        try:
            steam_path = self.game_finder.settings.get('steam_path') if self.game_finder else None
            if steam_path and os.path.exists(steam_path):
                test_results.append(f"✓ Steam path found: {steam_path}")
            else:
                test_results.append(f"✗ Steam path not found: {steam_path}")
        except Exception as e:
            test_results.append(f"✗ Steam path test error: {e}")
        
        # Test 5: Game configs
        config_dir = Path("config/games")
        if config_dir.exists():
            config_files = list(config_dir.glob("*.yaml"))
            test_results.append(f"✓ Found {len(config_files)} game config(s)")
            for config_file in config_files:
                test_results.append(f"  - {config_file.name}")
        else:
            test_results.append("✗ No game configs directory")
        
        # Test 6: Screen capture
        try:
            if self.screen_analyzer:
                screen = self.screen_analyzer.capture_screen()
                test_results.append(f"✓ Screen capture working ({screen.shape[1]}x{screen.shape[0]})")
            else:
                test_results.append("✗ Screen analyzer not available")
        except Exception as e:
            test_results.append(f"✗ Screen capture test error: {e}")
        
        # Show results
        result_msg = "\n".join(test_results)
        messagebox.showinfo("Component Test Results", result_msg)
        
        # Also log to console
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, "=== Component Test Results ===\n")
        self.log_text.insert(tk.END, result_msg + "\n\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def check_game_status(self):
        """Check if the selected game is running"""
        if not self.selected_game:
            messagebox.showwarning("Warning", "Please select a game first")
            return
        
        if not self.game_controller:
            messagebox.showerror("Error", "Game controller not initialized")
            return
        
        try:
            process_name = self.selected_game['config'].get('process_name')
            game_name = self.selected_game['config']['name']
            
            if self.game_controller.is_game_running(process_name):
                messagebox.showinfo("Game Status", f"{game_name} is currently running")
                self.status_var.set(f"{game_name} is running")
            else:
                messagebox.showinfo("Game Status", f"{game_name} is not running")
                self.status_var.set(f"{game_name} is not running")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check game status: {e}")

    def start_workflow(self):
        """Start the benchmark workflow for the selected game with enhanced logging"""
        if not self.selected_game:
            messagebox.showwarning("Warning", "Please select a game first")
            return
        
        if not self.workflow_engine:
            messagebox.showerror("Error", "Workflow engine not initialized")
            return
        
        # Check if workflow exists
        if not self.selected_game['config'].get('workflow'):
            messagebox.showwarning("Warning", f"No workflow defined for {self.selected_game['config']['name']}")
            return
        
        # Set current game name and create run-specific logging
        game_name = self.selected_game['config']['name']
        self.current_game_name = game_name
        run_folder = self._create_run_specific_logging(game_name)
        
        if run_folder:
            # Enable run folder button
            self.run_folder_button.config(state=tk.NORMAL)
            self.logger.info(f"📁 Run folder created: {run_folder}")
            
            # CRITICAL: Update workflow engine's screen analyzer screenshot directory
            if hasattr(self.workflow_engine, 'screen_analyzer') and self.workflow_engine.screen_analyzer:
                screenshot_dir = str(run_folder / "screenshots")
                self.workflow_engine.screen_analyzer.screenshot_dir = screenshot_dir
                self.logger.info(f"📸 Workflow engine screenshot directory set: {screenshot_dir}")
        
        # Disable buttons during workflow
        self.start_button.config(state=tk.DISABLED)
        self.launch_button.config(state=tk.DISABLED)
        self.close_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Clear log
        self.clear_log()
        
        # Add a handler to update the log text widget with workflow logs
        self.log_handler = LogTextHandler(self.log_text)
        self.log_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(self.log_handler)
        
        # Start workflow in a separate thread
        self.workflow_thread = threading.Thread(target=self._run_workflow)
        self.workflow_thread.daemon = True
        self.workflow_thread.start()

    def _run_workflow(self):
        """Run the workflow in a separate thread with enhanced logging"""
        try:
            game_name = self.selected_game['config']['name']
            self.root.after(0, lambda: self.status_var.set(f"Running workflow for {game_name}..."))
            
            # Log workflow start with enhanced details
            self.logger.info("=" * 80)
            self.logger.info(f"🚀 STARTING WORKFLOW: {game_name}")
            self.logger.info(f"📅 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.info(f"📁 Run Folder: {self.current_run_folder}")
            self.logger.info("=" * 80)
            
            # Run the workflow
            success = self.workflow_engine.run_workflow(self.selected_game)
            
            # Log workflow completion with enhanced details
            self.logger.info("=" * 80)
            if success:
                self.logger.info(f"✅ WORKFLOW COMPLETED SUCCESSFULLY: {game_name}")
                self.logger.info(f"📁 Results saved to: {self.current_run_folder}")
                self.root.after(0, lambda: self.status_var.set(f"Workflow completed successfully for {game_name}"))
            else:
                self.logger.info(f"❌ WORKFLOW FAILED: {game_name}")
                self.logger.info(f"📁 Check logs in: {self.current_run_folder}")
                self.root.after(0, lambda: self.status_var.set(f"Workflow failed for {game_name}"))
            
            self.logger.info(f"📅 End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.info("=" * 80)
        
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set("Error running workflow"))
            self.logger.error(f"Error running workflow: {str(e)}")
            self.logger.error(f"📁 Check logs in: {self.current_run_folder}")
        
        finally:
            # Re-enable buttons
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.launch_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.close_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
            
            # Remove the log handler and cleanup run-specific logging
            if hasattr(self, 'log_handler'):
                logging.getLogger().removeHandler(self.log_handler)
            
            # Note: Don't cleanup run logging here so logs remain accessible
            # self._cleanup_run_logging()

    def stop_workflow(self):
        """Stop the currently running workflow"""
        if self.workflow_engine:
            self.workflow_engine.stop_workflow()
            self.logger.info("Workflow stop requested")
            self.status_var.set("Stopping workflow...")

    def launch_game(self):
        """Launch the selected game without running the workflow"""
        if not self.selected_game:
            messagebox.showwarning("Warning", "Please select a game first")
            return
        
        if not self.game_controller:
            messagebox.showerror("Error", "Game controller not initialized")
            return
        
        # Check if game is already running
        process_name = self.selected_game['config'].get('process_name')
        if self.game_controller.is_game_running(process_name):
            messagebox.showinfo("Info", f"{self.selected_game['config']['name']} is already running")
            return
        
        # Clear log and setup logging
        self.clear_log()
        self.log_handler = LogTextHandler(self.log_text)
        self.log_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(self.log_handler)
        
        # Launch the game in a separate thread
        threading.Thread(target=self._launch_game_thread, daemon=True).start()

    def _launch_game_thread(self):
        """Launch game in a separate thread"""
        try:
            game_name = self.selected_game['config']['name']
            self.root.after(0, lambda: self.status_var.set(f"Launching {game_name}..."))
            
            # Disable launch button
            self.root.after(0, lambda: self.launch_button.config(state=tk.DISABLED))
            
            # Launch the game
            process = self.game_controller.launch_game(self.selected_game)
            
            if process:
                self.logger.info(f"Game launch initiated: {game_name}")
                
                # Wait a bit to see if the game starts
                process_name = self.selected_game['config'].get('process_name')
                startup_time = self.selected_game['config'].get('startup_time', 30)
                
                self.logger.info(f"Waiting up to {startup_time} seconds for {game_name} to start...")
                
                if self.game_controller.wait_for_game_to_start(startup_time, process_name):
                    self.root.after(0, lambda: self.status_var.set(f"{game_name} launched successfully"))
                    self.root.after(0, lambda: messagebox.showinfo("Success", f"{game_name} launched successfully!"))
                else:
                    self.root.after(0, lambda: self.status_var.set(f"{game_name} launch may have failed"))
                    self.root.after(0, lambda: messagebox.showwarning("Warning", f"{game_name} was launched but the process wasn't detected. Check if the game is running."))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to launch {game_name}"))
                
        except Exception as e:
            error_msg = f"Error launching game: {str(e)}"
            self.logger.error(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Launch Error", error_msg))
            self.root.after(0, lambda: self.status_var.set("Launch failed"))
        
        finally:
            # Re-enable launch button
            self.root.after(0, lambda: self.launch_button.config(state=tk.NORMAL))
            
            # Remove the log handler
            if hasattr(self, 'log_handler'):
                logging.getLogger().removeHandler(self.log_handler)

    def close_game(self):
        """Close the selected game"""
        if not self.selected_game:
            messagebox.showwarning("Warning", "Please select a game first")
            return
        
        if not self.game_controller:
            messagebox.showerror("Error", "Game controller not initialized")
            return
        
        # Check if game is running
        process_name = self.selected_game['config'].get('process_name')
        if not self.game_controller.is_game_running(process_name):
            messagebox.showinfo("Info", f"{self.selected_game['config']['name']} is not running")
            return
        
        # Ask for confirmation
        game_name = self.selected_game['config']['name']
        if not messagebox.askyesno("Confirm", f"Are you sure you want to close {game_name}?"):
            return
        
        # Clear log and setup logging
        self.clear_log()
        self.log_handler = LogTextHandler(self.log_text)
        self.log_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(self.log_handler)
        
        # Close the game in a separate thread
        threading.Thread(target=self._close_game_thread, daemon=True).start()

    def _close_game_thread(self):
        """Close game in a separate thread"""
        try:
            game_name = self.selected_game['config']['name']
            process_name = self.selected_game['config'].get('process_name')
            
            self.root.after(0, lambda: self.status_var.set(f"Closing {game_name}..."))
            self.root.after(0, lambda: self.close_button.config(state=tk.DISABLED))
            
            # Try graceful close first
            success = self.game_controller.close_game(process_name, force=False)
            
            if success:
                self.logger.info(f"Close signal sent to {game_name}")
                
                # Wait for the game to close
                if self.game_controller.wait_for_game_to_close(30, process_name):
                    self.root.after(0, lambda: self.status_var.set(f"{game_name} closed successfully"))
                    self.root.after(0, lambda: messagebox.showinfo("Success", f"{game_name} closed successfully"))
                else:
                    # If graceful close didn't work, try force close
                    self.logger.warning(f"Graceful close failed, trying force close for {game_name}")
                    force_success = self.game_controller.close_game(process_name, force=True)
                    
                    if force_success:
                        self.root.after(0, lambda: self.status_var.set(f"{game_name} force closed"))
                        self.root.after(0, lambda: messagebox.showinfo("Success", f"{game_name} was force closed"))
                    else:
                        self.root.after(0, lambda: self.status_var.set(f"Failed to close {game_name}"))
                        self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to close {game_name}. You may need to close it manually."))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Could not find running process for {game_name}"))
                
        except Exception as e:
            error_msg = f"Error closing game: {str(e)}"
            self.logger.error(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Close Error", error_msg))
            self.root.after(0, lambda: self.status_var.set("Close failed"))
        
        finally:
            # Re-enable close button
            self.root.after(0, lambda: self.close_button.config(state=tk.NORMAL))
            
            # Remove the log handler
            if hasattr(self, 'log_handler'):
                logging.getLogger().removeHandler(self.log_handler)

    # ==================== TEMPLATE METHODS (Truncated for space) ====================
    
    def take_quick_screenshot(self):
        """Take a quick screenshot"""
        if not self.screen_analyzer:
            messagebox.showerror("Error", "Screen analyzer not initialized")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quick_screenshot_{timestamp}"
            
            #messagebox.showinfo("Screenshot", "Click OK and switch to the window you want to capture.\nScreenshot will be taken in 3 seconds.")
            
            # Take screenshot after delay - update no delay - 2/6/2025
            self.root.after(0, lambda: self._take_delayed_screenshot(filename))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to take screenshot: {e}")

    def _take_delayed_screenshot(self, filename):
        """Take screenshot after delay"""
        try:
            path = self.screen_analyzer.save_screenshot(filename)
            if path:
                messagebox.showinfo("Success", f"Screenshot saved to:\n{path}")
                self.logger.info(f"Quick screenshot saved: {path}")
            else:
                messagebox.showerror("Error", "Failed to save screenshot")
        except Exception as e:
            messagebox.showerror("Error", f"Screenshot failed: {e}")

    # [Additional template methods would continue here...]
    
    def refresh_templates(self):
        """Refresh the template list"""
        self.template_listbox.delete(0, tk.END)
        
        templates_dir = Path("templates/screens")
        if not templates_dir.exists():
            self.template_listbox.insert(tk.END, "No templates directory found")
            return
        
        # Find all template files
        template_files = []
        for game_dir in templates_dir.iterdir():
            if game_dir.is_dir():
                for template_file in game_dir.glob("*.png"):
                    relative_path = template_file.relative_to(templates_dir)
                    template_files.append(str(relative_path))
        
        if not template_files:
            self.template_listbox.insert(tk.END, "No template files found")
            return
        
        for template in sorted(template_files):
            self.template_listbox.insert(tk.END, template)

    def open_templates_folder(self):
        """Open the templates folder in file explorer"""
        templates_dir = Path("templates/screens")
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.run(['explorer', str(templates_dir.resolve())])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['open', str(templates_dir.resolve())])
            else:  # Linux
                subprocess.run(['xdg-open', str(templates_dir.resolve())])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open templates folder: {e}")

    def view_template(self):
        """View the selected template"""
        selection = self.template_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a template to view")
            return
        
        template_name = self.template_listbox.get(selection[0])
        if template_name in ["No templates directory found", "No template files found"]:
            return
        
        template_path = Path("templates/screens") / template_name
        
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.run(['start', str(template_path.resolve())], shell=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['open', str(template_path.resolve())])
            else:  # Linux
                subprocess.run(['xdg-open', str(template_path.resolve())])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open template: {e}")

    def open_config_folder(self):
        """Open the config folder"""
        config_dir = Path("config")
        config_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.run(['explorer', str(config_dir.resolve())])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['open', str(config_dir.resolve())])
            else:  # Linux
                subprocess.run(['xdg-open', str(config_dir.resolve())])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open config folder: {e}")
    
    def open_workflow_builder(self):
        """Open the visual workflow builder"""
        try:
            from workflow_builder import WorkflowBuilder
            
            # Get current game's workflow if selected
            existing_workflow = None
            game_name = None
            
            if self.selected_game:
                game_name = self.selected_game['config']['name']
                existing_workflow = self.selected_game['config'].get('workflow', [])
            
            # Open workflow builder
            builder = WorkflowBuilder(
                parent=self.root,
                game_name=game_name,
                existing_workflow=existing_workflow
            )
            
        except ImportError:
            messagebox.showerror("Error", "Workflow builder module not found. Make sure workflow_builder.py is in the same directory.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open workflow builder: {e}")

    def clear_log(self):
        """Clear the log text widget"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def save_log(self):
        """Save the current log to a file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"katana_gui_log_{timestamp}.txt"
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialname=filename
            )
            
            if filepath:
                log_content = self.log_text.get(1.0, tk.END)
                with open(filepath, 'w') as f:
                    f.write(log_content)
                messagebox.showinfo("Success", f"Log saved to {filepath}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save log: {e}")

    def capture_template(self):
        """Capture a template with name and game association"""
        if not self.screen_analyzer:
            messagebox.showerror("Error", "Screen analyzer not initialized")
            return
        
        # Get template name
        template_name = simpledialog.askstring("Template Name", "Enter template name (e.g., 'play_button'):")
        if not template_name:
            return
        
        # Get game name
        game_names = list(self.games.keys()) + ["general"]
        game_name = self._show_choice_dialog("Select Game", "Choose which game this template is for:", game_names)
        if not game_name:
            return
        
        try:
            # Create game-specific template directory
            template_dir = Path("templates/screens") / game_name.lower().replace(" ", "_")
            template_dir.mkdir(parents=True, exist_ok=True)
            
            messagebox.showinfo("Capture Template", 
                               f"Click OK and switch to your game.\n"
                               f"Position the UI element you want to capture.\n"
                               f"Screenshot will be taken in 5 seconds.")
            
            # Take screenshot after delay
            template_path = template_dir / f"{template_name}.png"
            self.root.after(5000, lambda: self._capture_template_delayed(template_path, template_name))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture template: {e}")

    def _capture_template_delayed(self, template_path, template_name):
        """Capture template after delay"""
        try:
            # Take full screenshot first
            screen = self.screen_analyzer.capture_screen()
            
            # Save the screenshot
            import cv2
            success = cv2.imwrite(str(template_path), screen)
            
            if success:
                messagebox.showinfo("Success", 
                                   f"Template '{template_name}' captured!\n"
                                   f"Saved to: {template_path}\n\n"
                                   f"Note: You may need to crop this image to just the UI element you want to match.")
                self.logger.info(f"Template captured: {template_path}")
                self.refresh_templates()
            else:
                messagebox.showerror("Error", "Failed to save template")
                
        except Exception as e:
            messagebox.showerror("Error", f"Template capture failed: {e}")

    def test_template(self):
        """Test a template against current screen with game switching"""
        if not self.screen_analyzer:
            messagebox.showerror("Error", "Screen analyzer not initialized")
            return
        
        # Get template file
        template_file = filedialog.askopenfilename(
            title="Select Template to Test",
            initialdir="templates/screens",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if not template_file:
            return
        
        # Ask if user wants to switch to game window
        switch_to_game = messagebox.askyesno(
            "Switch to Game?", 
            "Do you want to automatically switch to the game window?\n\n"
            "Click 'Yes' to use Alt+Tab with 5 second delay\n"
            "Click 'No' to test current screen immediately"
        )
        
        if switch_to_game:
            self._test_template_with_switch(template_file)
        else:
            self._test_template_immediate(template_file)

    def _test_template_with_switch(self, template_file):
        """Test template with Alt+Tab switch and delay"""
        try:
            # Show countdown dialog
            countdown_dialog = self._show_countdown_dialog()
            
            # Start the switching process in a thread
            threading.Thread(
                target=self._template_test_with_switch_thread, 
                args=(template_file, countdown_dialog), 
                daemon=True
            ).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Template test failed: {e}")

    def _template_test_with_switch_thread(self, template_file, countdown_dialog):
        """Run template test with Alt+Tab in separate thread"""
        try:
            # Wait 2 seconds, then Alt+Tab
            time.sleep(2)
            
            # Update countdown
            self.root.after(0, lambda: self._update_countdown(countdown_dialog, "Switching to game..."))
            
            # Simulate Alt+Tab to switch to game
            import pyautogui
            pyautogui.hotkey('alt', 'tab')
            
            # Wait 3 more seconds for game to come to foreground
            for i in range(3, 0, -1):
                self.root.after(0, lambda i=i: self._update_countdown(countdown_dialog, f"Testing in {i} seconds..."))
                time.sleep(1)
            
            # Close countdown dialog
            self.root.after(0, lambda: countdown_dialog.destroy())
            
            # Now test the template
            self.root.after(0, lambda: self._test_template_immediate(template_file))
            
        except Exception as e:
            self.root.after(0, lambda: countdown_dialog.destroy())
            self.root.after(0, lambda: messagebox.showerror("Error", f"Template test failed: {e}"))

    def _show_countdown_dialog(self):
        """Show countdown dialog during template test"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Template Test in Progress")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        # Make it stay on top
        dialog.attributes('-topmost', True)
        
        # Add content
        dialog.label = ttk.Label(dialog, text="Preparing to test template...", font=("Arial", 12))
        dialog.label.pack(expand=True)
        
        # Add cancel button
        def cancel_test():
            dialog.destroy()
        
        ttk.Button(dialog, text="Cancel", command=cancel_test).pack(pady=10)
        
        return dialog

    def _update_countdown(self, dialog, message):
        """Update countdown dialog message"""
        try:
            if dialog.winfo_exists():
                dialog.label.config(text=message)
        except tk.TclError:
            # Dialog was destroyed
            pass

    def _test_template_immediate(self, template_file):
        """Test template against current screen immediately"""
        try:
            # Get threshold from settings
            threshold = 0.8
            if hasattr(self, 'screen_analyzer') and hasattr(self.screen_analyzer, 'threshold'):
                threshold = self.screen_analyzer.threshold
            
            # Test the template with lower thresholds for detailed analysis
            results = []
            thresholds_to_try = [0.9, 0.8, 0.7, 0.6, 0.5]
            
            for test_threshold in thresholds_to_try:
                matched, location = self.screen_analyzer.match_template(
                    template_file, 
                    threshold=test_threshold
                )
                
                if matched:
                    # Get the actual confidence score
                    confidence = self._get_template_confidence(template_file)
                    results.append({
                        'threshold': test_threshold,
                        'matched': True,
                        'location': location,
                        'confidence': confidence
                    })
                    break  # Found match, no need to try lower thresholds
                else:
                    # Get confidence even if no match
                    confidence = self._get_template_confidence(template_file)
                    results.append({
                        'threshold': test_threshold,
                        'matched': False,
                        'location': None,
                        'confidence': confidence
                    })
            
            # Show comprehensive results
            self._show_template_test_results(template_file, results)
            
        except Exception as e:
            messagebox.showerror("Error", f"Template test failed: {e}")

    def _get_template_confidence(self, template_file):
        """Get the actual confidence score for template matching"""
        try:
            import cv2
            
            # Load template
            template = cv2.imread(template_file)
            if template is None:
                return 0.0
            
            # Capture current screen
            screen = self.screen_analyzer.capture_screen()
            
            # Ensure template isn't larger than screen
            if template.shape[0] > screen.shape[0] or template.shape[1] > screen.shape[1]:
                return 0.0
            
            # Perform template matching
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            return max_val
            
        except Exception as e:
            self.logger.error(f"Error getting template confidence: {e}")
            return 0.0

    def _show_template_test_results(self, template_file, results):
        """Show detailed template test results"""
        template_name = Path(template_file).name
        
        # Find the best result
        best_result = max(results, key=lambda x: x['confidence'])
        
        # Create results dialog
        results_dialog = tk.Toplevel(self.root)
        results_dialog.title("Template Test Results")
        results_dialog.geometry("500x400")
        results_dialog.transient(self.root)
        
        # Center the dialog
        results_dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Main frame
        main_frame = ttk.Frame(results_dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"Template: {template_name}", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Best result summary
        summary_frame = ttk.LabelFrame(main_frame, text="Best Match Result", padding=10)
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        confidence = best_result['confidence']
        confidence_percent = confidence * 100
        
        if best_result['matched']:
            x, y = best_result['location']
            status_text = f"✅ MATCH FOUND"
            status_color = "green"
            details_text = f"Location: ({x}, {y})\nConfidence: {confidence_percent:.1f}%"
        else:
            status_text = f"❌ NO MATCH"
            status_color = "red"
            details_text = f"Best confidence: {confidence_percent:.1f}%\nThreshold needed: {confidence:.2f}"
        
        status_label = ttk.Label(summary_frame, text=status_text, font=("Arial", 12, "bold"))
        status_label.pack()
        
        details_label = ttk.Label(summary_frame, text=details_text, font=("Arial", 10))
        details_label.pack(pady=(5, 0))
        
        # Confidence interpretation
        interpretation_frame = ttk.LabelFrame(main_frame, text="Confidence Analysis", padding=10)
        interpretation_frame.pack(fill=tk.X, pady=(0, 10))
        
        if confidence_percent >= 90:
            interp_text = "🟢 Excellent match - Template should work reliably"
            interp_color = "green"
        elif confidence_percent >= 80:
            interp_text = "🟡 Good match - Template should work in most cases"
            interp_color = "orange"
        elif confidence_percent >= 70:
            interp_text = "🟠 Fair match - May work but could be unreliable"
            interp_color = "orange"
        elif confidence_percent >= 60:
            interp_text = "🔴 Poor match - Template needs improvement"
            interp_color = "red"
        else:
            interp_text = "⛔ Very poor match - Template likely won't work"
            interp_color = "red"
        
        interp_label = ttk.Label(interpretation_frame, text=interp_text, font=("Arial", 10))
        interp_label.pack()
        
        # Detailed results
        details_frame = ttk.LabelFrame(main_frame, text="Detailed Results", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create treeview for detailed results
        columns = ("Threshold", "Match", "Confidence")
        tree = ttk.Treeview(details_frame, columns=columns, show="headings", height=6)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor=tk.CENTER)
        
        # Add results to tree
        for result in results:
            match_text = "✅ Yes" if result['matched'] else "❌ No"
            confidence_text = f"{result['confidence']*100:.1f}%"
            threshold_text = f"{result['threshold']*100:.0f}%"
            
            tree.insert("", tk.END, values=(threshold_text, match_text, confidence_text))
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for tree
        tree_scroll = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=tree_scroll.set)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def take_reference_screenshot():
            """Take a screenshot for comparison"""
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"template_test_reference_{timestamp}"
                path = self.screen_analyzer.save_screenshot(filename)
                if path:
                    messagebox.showinfo("Screenshot Saved", f"Reference screenshot saved:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save screenshot: {e}")
        
        def close_dialog():
            results_dialog.destroy()
        
        ttk.Button(button_frame, text="Take Reference Screenshot", command=take_reference_screenshot).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=close_dialog).pack(side=tk.RIGHT, padx=5)

    def monitor_template(self):
        """Monitor a template continuously with real-time confidence updates"""
        if not self.screen_analyzer:
            messagebox.showerror("Error", "Screen analyzer not initialized")
            return
        
        # Get template file
        template_file = filedialog.askopenfilename(
            title="Select Template to Monitor",
            initialdir="templates/screens",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if not template_file:
            return
        
        # Get monitoring parameters
        params = self._get_monitoring_parameters()
        if not params:
            return
        
        # Start monitoring
        self._start_template_monitoring(template_file, params)

    def _get_monitoring_parameters(self):
        """Get monitoring parameters from user with modern styling"""
        dialog = tk.Toplevel(self.root)
        dialog.title("👁️ Template Monitoring Settings")
        dialog.geometry("600x600")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg='#ecf0f1')
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        # Variables for parameters
        poll_interval = tk.DoubleVar(value=1.0)
        duration = tk.IntVar(value=30)
        threshold = tk.DoubleVar(value=0.8)
        switch_to_game = tk.BooleanVar(value=True)
        
        result = [None]  # Store result
        
        # Create UI with modern styling
        main_frame = tk.Frame(dialog, bg='#ecf0f1', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="👁️ Template Monitoring Setup", 
                              font=('Segoe UI', 14, 'bold'), 
                              fg='#2c3e50', bg='#ecf0f1')
        title_label.pack(pady=(0, 20))
        
        # Poll interval section
        poll_frame = tk.LabelFrame(main_frame, text=" ⏱️ Poll Interval ", 
                                  font=('Segoe UI', 10, 'bold'), 
                                  fg='#34495e', bg='#ecf0f1')
        poll_frame.pack(fill=tk.X, pady=(0, 15))
        
        poll_content = tk.Frame(poll_frame, bg='#ecf0f1')
        poll_content.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(poll_content, text="Check every:", 
                font=('Segoe UI', 9), fg='#34495e', bg='#ecf0f1').pack(anchor=tk.W)
        
        poll_scale = ttk.Scale(poll_content, from_=0.5, to=5.0, variable=poll_interval, 
                              orient=tk.HORIZONTAL, length=300)
        poll_scale.pack(fill=tk.X, pady=5)
        
        poll_label = tk.Label(poll_content, text="1.0 seconds", 
                             font=('Segoe UI', 9), fg='#7f8c8d', bg='#ecf0f1')
        poll_label.pack(anchor=tk.W)
        
        def update_poll_label(val):
            poll_label.config(text=f"{float(val):.1f} seconds")
        poll_scale.config(command=update_poll_label)
        
        # Duration section
        duration_frame = tk.LabelFrame(main_frame, text=" 🕐 Duration ", 
                                      font=('Segoe UI', 10, 'bold'), 
                                      fg='#34495e', bg='#ecf0f1')
        duration_frame.pack(fill=tk.X, pady=(0, 15))
        
        duration_content = tk.Frame(duration_frame, bg='#ecf0f1')
        duration_content.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(duration_content, text="Monitor for:", 
                font=('Segoe UI', 9), fg='#34495e', bg='#ecf0f1').pack(side=tk.LEFT)
        
        duration_spin = ttk.Spinbox(duration_content, from_=10, to=300, textvariable=duration, width=10)
        duration_spin.pack(side=tk.LEFT, padx=(10, 5))
        
        tk.Label(duration_content, text="seconds", 
                font=('Segoe UI', 9), fg='#34495e', bg='#ecf0f1').pack(side=tk.LEFT)
        
        # Threshold section
        threshold_frame = tk.LabelFrame(main_frame, text=" 🎯 Detection Threshold ", 
                                       font=('Segoe UI', 10, 'bold'), 
                                       fg='#34495e', bg='#ecf0f1')
        threshold_frame.pack(fill=tk.X, pady=(0, 15))
        
        threshold_content = tk.Frame(threshold_frame, bg='#ecf0f1')
        threshold_content.pack(fill=tk.X, padx=10, pady=10)
        
        threshold_scale = ttk.Scale(threshold_content, from_=0.1, to=1.0, variable=threshold, 
                                   orient=tk.HORIZONTAL, length=300)
        threshold_scale.pack(fill=tk.X, pady=5)
        
        threshold_label = tk.Label(threshold_content, text="0.8 (80%)", 
                                  font=('Segoe UI', 9), fg='#7f8c8d', bg='#ecf0f1')
        threshold_label.pack(anchor=tk.W)
        
        def update_threshold_label(val):
            threshold_label.config(text=f"{float(val):.2f} ({float(val)*100:.0f}%)")
        threshold_scale.config(command=update_threshold_label)
        
        # Options section
        options_frame = tk.LabelFrame(main_frame, text=" ⚙️ Options ", 
                                     font=('Segoe UI', 10, 'bold'), 
                                     fg='#34495e', bg='#ecf0f1')
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        options_content = tk.Frame(options_frame, bg='#ecf0f1')
        options_content.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Checkbutton(options_content, text="🔄 Switch to game window first (Alt+Tab)", 
                      variable=switch_to_game, font=('Segoe UI', 9),
                      fg='#34495e', bg='#ecf0f1', selectcolor='#3498db').pack(anchor=tk.W)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#ecf0f1')
        button_frame.pack(fill=tk.X)
        
        def on_start():
            result[0] = {
                'poll_interval': poll_interval.get(),
                'duration': duration.get(),
                'threshold': threshold.get(),
                'switch_to_game': switch_to_game.get()
            }
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        ttk.Button(button_frame, text="▶️ Start Monitoring", 
                  command=on_start).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="❌ Cancel", 
                  command=on_cancel).pack(side=tk.RIGHT)
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return result[0]

    def _start_template_monitoring(self, template_file, params):
        """Start template monitoring with real-time updates and modern UI"""
        template_name = Path(template_file).name
        
        # Create monitoring dialog with modern styling
        monitor_dialog = tk.Toplevel(self.root)
        monitor_dialog.title(f"👁️ Monitoring: {template_name}")
        monitor_dialog.geometry("600x500")
        monitor_dialog.transient(self.root)
        monitor_dialog.configure(bg='#ecf0f1')
        
        # Center the dialog
        monitor_dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Make it stay on top
        monitor_dialog.attributes('-topmost', True)
        
        # Create monitoring UI with modern styling
        main_frame = tk.Frame(monitor_dialog, bg='#ecf0f1', padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title and status
        title_label = tk.Label(main_frame, text=f"👁️ Monitoring: {template_name}", 
                              font=('Segoe UI', 14, 'bold'), 
                              fg='#2c3e50', bg='#ecf0f1')
        title_label.pack(pady=(0, 10))
        
        status_label = tk.Label(main_frame, text="🔄 Preparing to monitor...", 
                               font=('Segoe UI', 11), 
                               fg='#34495e', bg='#ecf0f1')
        status_label.pack()
        
        # Current confidence display with modern styling
        confidence_frame = tk.LabelFrame(main_frame, text=" 🎯 Real-time Detection ", 
                                        font=('Segoe UI', 10, 'bold'), 
                                        fg='#2c3e50', bg='#ecf0f1',
                                        relief=tk.RIDGE, bd=2)
        confidence_frame.pack(fill=tk.X, pady=15)
        
        conf_content = tk.Frame(confidence_frame, bg='#ecf0f1')
        conf_content.pack(fill=tk.X, padx=15, pady=15)
        
        confidence_label = tk.Label(conf_content, text="Confidence: --", 
                                    font=('Segoe UI', 18, 'bold'), 
                                    fg='#e74c3c', bg='#ecf0f1')
        confidence_label.pack()
        
        match_label = tk.Label(conf_content, text="Status: Waiting...", 
                              font=('Segoe UI', 12), 
                              fg='#95a5a6', bg='#ecf0f1')
        match_label.pack(pady=(5, 0))
        
        # Progress bar with modern styling
        progress_var = tk.DoubleVar()
        progress = ttk.Progressbar(main_frame, variable=progress_var, maximum=100, 
                                  length=400, style='Modern.Horizontal.TProgressbar')
        progress.pack(fill=tk.X, pady=10)
        
        # Log area with modern styling
        log_frame = tk.LabelFrame(main_frame, text=" 📝 Detection Log ", 
                                 font=('Segoe UI', 10, 'bold'), 
                                 fg='#2c3e50', bg='#ecf0f1',
                                 relief=tk.RIDGE, bd=2)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        log_container = tk.Frame(log_frame, bg='#ecf0f1')
        log_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        log_text = tk.Text(log_container, height=10, wrap=tk.WORD,
                          font=('Consolas', 9), bg='#2c3e50', fg='#ecf0f1',
                          relief=tk.FLAT, bd=1)
        log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        log_scroll = ttk.Scrollbar(log_container, orient=tk.VERTICAL, command=log_text.yview)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        log_text.config(yscrollcommand=log_scroll.set)
        
        # Control buttons with modern styling
        button_frame = tk.Frame(main_frame, bg='#ecf0f1')
        button_frame.pack(fill=tk.X, pady=10)
        
        stop_monitoring = [False]  # Use list for closure
        
        def stop_monitor():
            stop_monitoring[0] = True
            monitor_dialog.destroy()
        
        def take_reference():
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"monitor_reference_{timestamp}"
                path = self.screen_analyzer.save_screenshot(filename)
                if path:
                    log_text.insert(tk.END, f"📸 {datetime.now().strftime('%H:%M:%S')} - Reference screenshot: {filename}.png\n")
                    log_text.see(tk.END)
            except Exception as e:
                log_text.insert(tk.END, f"❌ {datetime.now().strftime('%H:%M:%S')} - Screenshot failed: {e}\n")
                log_text.see(tk.END)
        
        ttk.Button(button_frame, text="⏹️ Stop Monitoring", 
                  command=stop_monitor).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="📸 Take Reference", 
                  command=take_reference).pack(side=tk.LEFT)
        
        # Start monitoring in separate thread
        threading.Thread(
            target=self._template_monitoring_thread,
            args=(template_file, params, monitor_dialog, status_label, confidence_label, 
                  match_label, progress_var, log_text, stop_monitoring),
            daemon=True
        ).start()

    def _template_monitoring_thread(self, template_file, params, dialog, status_label, 
                                   confidence_label, match_label, progress_var, log_text, stop_monitoring):
        """Run template monitoring in separate thread"""
        try:
            template_name = Path(template_file).name
            poll_interval = params['poll_interval']
            duration = params['duration']
            threshold = params['threshold']
            switch_to_game = params['switch_to_game']
            
            # Switch to game if requested
            if switch_to_game:
                self.root.after(0, lambda: status_label.config(text="🔄 Switching to game..."))
                time.sleep(2)
                
                import pyautogui
                pyautogui.hotkey('alt', 'tab')
                time.sleep(3)
            
            # Start monitoring
            start_time = time.time()
            detection_count = 0
            total_polls = 0
            best_confidence = 0
            
            self.root.after(0, lambda: status_label.config(text="👁️ Monitoring active..."))
            self.root.after(0, lambda: log_text.insert(tk.END, f"🔍 {datetime.now().strftime('%H:%M:%S')} - Started monitoring {template_name}\n"))
            self.root.after(0, lambda: log_text.insert(tk.END, f"⚙️ {datetime.now().strftime('%H:%M:%S')} - Poll: {poll_interval}s, Duration: {duration}s, Threshold: {threshold:.2f}\n\n"))
            
            while time.time() - start_time < duration and not stop_monitoring[0]:
                try:
                    # Calculate progress
                    elapsed = time.time() - start_time
                    progress = (elapsed / duration) * 100
                    self.root.after(0, lambda p=progress: progress_var.set(p))
                    
                    # Get confidence
                    confidence = self._get_template_confidence(template_file)
                    total_polls += 1
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                    
                    # Check if detected
                    detected = confidence >= threshold
                    if detected:
                        detection_count += 1
                    
                    # Update UI
                    confidence_percent = confidence * 100
                    self.root.after(0, lambda c=confidence_percent: confidence_label.config(
                        text=f"Confidence: {c:.1f}%",
                        fg="#27ae60" if c >= threshold * 100 else "#e74c3c"
                    ))
                    
                    status_text = "✅ DETECTED!" if detected else "❌ Not detected"
                    status_color = "#27ae60" if detected else "#e74c3c"
                    self.root.after(0, lambda s=status_text, c=status_color: match_label.config(
                        text=f"Status: {s}", fg=c
                    ))
                    
                    # Log significant events
                    if detected:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        self.root.after(0, lambda t=timestamp, c=confidence_percent: log_text.insert(
                            tk.END, f"✅ {t} - DETECTED! Confidence: {c:.1f}%\n"
                        ))
                        self.root.after(0, lambda: log_text.see(tk.END))
                    elif confidence > 0.5:  # Log near misses
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        self.root.after(0, lambda t=timestamp, c=confidence_percent: log_text.insert(
                            tk.END, f"🟡 {t} - Near miss: {c:.1f}%\n"
                        ))
                        self.root.after(0, lambda: log_text.see(tk.END))
                    
                    # Wait for next poll
                    time.sleep(poll_interval)
                    
                except Exception as e:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.root.after(0, lambda t=timestamp, err=str(e): log_text.insert(tk.END, f"⚠️ {t} - Error: {err}\n"))
                    self.root.after(0, lambda: log_text.see(tk.END))
                    time.sleep(poll_interval)
            
            # Monitoring complete
            detection_rate = (detection_count / total_polls * 100) if total_polls > 0 else 0
            
            self.root.after(0, lambda: status_label.config(text="✅ Monitoring complete"))
            self.root.after(0, lambda: log_text.insert(tk.END, f"\n📊 MONITORING SUMMARY:\n"))
            self.root.after(0, lambda: log_text.insert(tk.END, f"   Duration: {duration}s\n"))
            self.root.after(0, lambda: log_text.insert(tk.END, f"   Total polls: {total_polls}\n"))
            self.root.after(0, lambda: log_text.insert(tk.END, f"   Detections: {detection_count}\n"))
            self.root.after(0, lambda: log_text.insert(tk.END, f"   Detection rate: {detection_rate:.1f}%\n"))
            self.root.after(0, lambda: log_text.insert(tk.END, f"   Best confidence: {best_confidence*100:.1f}%\n"))
            self.root.after(0, lambda: log_text.see(tk.END))
            
            # Show summary dialog
            if not stop_monitoring[0]:
                summary_msg = (f"👁️ Monitoring Complete!\n\n"
                             f"Template: {template_name}\n"
                             f"Duration: {duration}s\n"
                             f"Detections: {detection_count}/{total_polls} polls\n"
                             f"Detection rate: {detection_rate:.1f}%\n"
                             f"Best confidence: {best_confidence*100:.1f}%")
                
                self.root.after(0, lambda: messagebox.showinfo("Monitoring Complete", summary_msg))
            
        except Exception as e:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.root.after(0, lambda t=timestamp: log_text.insert(tk.END, f"❌ {t} - Monitoring failed: {str(e)}\n"))
            self.root.after(0, lambda: log_text.see(tk.END))

    def _show_choice_dialog(self, title, message, choices):
        """Show a dialog with multiple choices"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        result = [None]  # Use list to store result from closure
        
        ttk.Label(dialog, text=message).pack(pady=10)
        
        # Create listbox for choices
        listbox = tk.Listbox(dialog, height=6)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for choice in choices:
            listbox.insert(tk.END, choice)
        
        def on_ok():
            selection = listbox.curselection()
            if selection:
                result[0] = choices[selection[0]]
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="OK", command=on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return result[0]
    
    def test_monitor_detection(self):
        """Test and display monitor information"""
        try:
            import mss
            import tkinter as tk
            from tkinter import messagebox
            
            with mss.mss() as sct:
                monitor_info = []
                
                for i, monitor in enumerate(sct.monitors):
                    if i == 0:  # Skip the "all monitors" entry
                        continue
                        
                    width = monitor['width']
                    height = monitor['height']
                    left = monitor['left']
                    top = monitor['top']
                    
                    monitor_info.append(f"Monitor {i}:")
                    monitor_info.append(f"  Resolution: {width}x{height}")
                    monitor_info.append(f"  Position: ({left}, {top})")
                    monitor_info.append(f"  Right edge: {left + width}")
                    monitor_info.append(f"  Bottom edge: {top + height}")
                    monitor_info.append("")
            
            messagebox.showinfo("Monitor Information", "\n".join(monitor_info))

            
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to detect monitors: {e}")


class LogTextHandler(logging.Handler):
    """Handler to redirect logging output to a tkinter Text widget"""
    
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    def emit(self, record):
        msg = self.format(record)
        
        def append():
            try:
                self.text_widget.config(state=tk.NORMAL)
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)
                self.text_widget.config(state=tk.DISABLED)
            except tk.TclError:
                # Widget has been destroyed
                pass
        
        # Schedule the append to happen in the main thread
        try:
            self.text_widget.after(0, append)
        except tk.TclError:
            # Widget has been destroyed
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = KatanaGUI(root)
    root.mainloop()
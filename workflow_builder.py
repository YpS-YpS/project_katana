import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yaml
import os
from pathlib import Path
from datetime import datetime

class WorkflowBuilder:
    def __init__(self, parent=None, game_name=None, existing_workflow=None):
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title("🛠️ Project Katana - Workflow Builder")
        self.root.geometry("1200x900")
        self.root.minsize(1200, 900)
        
        # Data structures
        self.game_config = {
            'name': game_name or "New Game",
            'type': "steam",
            'app_id': "",
            'exe_name': "",
            'process_name': "",
            'launch_options': "",
            'startup_time': 60
        }
        
        self.workflow_steps = existing_workflow or []
        self.step_counter = len(self.workflow_steps)
        
        # Available actions with their parameters
        self.action_definitions = {
            "launch_game": {
                "description": "🚀 Launch the configured game",
                "parameters": []
            },
            "wait_for_game": {
                "description": "⏳ Wait for game process to start",
                "parameters": ["timeout", "process_name"]
            },
            "exit_game": {
                "description": "🛑 Close the game process",
                "parameters": ["force", "process_name"]
            },
            "wait_for_template": {
                "description": "🎯 Wait for UI template to appear",
                "parameters": ["template", "timeout", "region", "threshold"]
            },
            "wait_for_any_template": {
                "description": "🎯 Wait for any of multiple templates",
                "parameters": ["templates", "timeout", "region", "threshold"]
            },
            "wait_for_template_disappear": {
                "description": "👻 Wait for template to disappear",
                "parameters": ["template", "timeout", "region", "threshold"]
            },
            "click_template": {
                "description": "🖱️ Find and click on template",
                "parameters": ["template", "timeout", "region", "threshold", "button", "offset", "move_duration", "pre_click_delay", "post_click_delay"]
            },
            "click_template_if_exists": {
                "description": "🖱️ Click template if it exists (optional)",
                "parameters": ["template", "region", "threshold", "button", "delay", "offset"]
            },
            "check_template": {
                "description": "🔍 Check if template exists",
                "parameters": ["template", "region", "threshold"]
            },
            "press_key": {
                "description": "⌨️ Press and release a key",
                "parameters": ["key", "delay"]
            },
            "hold_key": {
                "description": "⌨️ Hold a key for duration",
                "parameters": ["key", "duration"]
            },
            "type_text": {
                "description": "📝 Type text string",
                "parameters": ["text", "delay"]
            },
            "click": {
                "description": "🖱️ Click at coordinates",
                "parameters": ["x", "y", "button", "delay"]
            },
            "take_screenshot": {
                "description": "📸 Capture screenshot",
                "parameters": ["name", "region"]
            },
            "wait_for_screen_change": {
                "description": "🔄 Wait for screen to change",
                "parameters": ["timeout", "region", "threshold"]
            },
            "wait": {
                "description": "⏰ Wait for specified time",
                "parameters": ["seconds"]
            },
            "log_message": {
                "description": "📝 Log timestamped message",
                "parameters": ["message"]
            },
            "retry_action": {
                "description": "🔄 Retry a sub-action",
                "parameters": ["action_to_retry", "max_retries", "retry_delay"]
            }
        }
        
        self.setup_ui()
        
        if existing_workflow:
            self.load_existing_workflow()
    
    def setup_ui(self):
        """Set up the main UI"""
        # Create main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Game config and controls
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=1)
        
        # Right panel - Workflow steps
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=2)
        
        self.setup_left_panel(left_panel)
        self.setup_right_panel(right_panel)
    
    def setup_left_panel(self, parent):
        """Set up the left panel with game config and controls"""
        # Game Configuration Section
        game_frame = ttk.LabelFrame(parent, text="🎮 Game Configuration", padding=10)
        game_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Game config fields
        config_fields = [
            ("Game Name:", "name", "text"),
            ("Type:", "type", "combo", ["steam", "epic", "other"]),
            ("Steam App ID:", "app_id", "text"),
            ("Executable Name:", "exe_name", "text"),
            ("Process Name:", "process_name", "text"),
            ("Launch Options:", "launch_options", "text"),
            ("Startup Time (s):", "startup_time", "number")
        ]
        
        self.config_vars = {}
        for i, field_info in enumerate(config_fields):
            label_text, key, field_type = field_info[:3]
            
            ttk.Label(game_frame, text=label_text).grid(row=i, column=0, sticky="w", pady=2)
            
            if field_type == "text":
                var = tk.StringVar(value=str(self.game_config.get(key, "")))
                entry = ttk.Entry(game_frame, textvariable=var, width=30)
                entry.grid(row=i, column=1, sticky="ew", pady=2, padx=(5, 0))
            elif field_type == "combo":
                var = tk.StringVar(value=self.game_config.get(key, field_info[3][0]))
                combo = ttk.Combobox(game_frame, textvariable=var, values=field_info[3], width=27, state="readonly")
                combo.grid(row=i, column=1, sticky="ew", pady=2, padx=(5, 0))
            elif field_type == "number":
                var = tk.IntVar(value=self.game_config.get(key, 60))
                entry = ttk.Entry(game_frame, textvariable=var, width=30)
                entry.grid(row=i, column=1, sticky="ew", pady=2, padx=(5, 0))
            
            self.config_vars[key] = var
        
        game_frame.grid_columnconfigure(1, weight=1)
        
        # Action Selection Section
        action_frame = ttk.LabelFrame(parent, text="➕ Add New Step", padding=10)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(action_frame, text="Action Type:").pack(anchor="w")
        self.action_var = tk.StringVar()
        self.action_combo = ttk.Combobox(action_frame, textvariable=self.action_var, 
                                        values=list(self.action_definitions.keys()), 
                                        state="readonly", width=40)
        self.action_combo.pack(fill=tk.X, pady=(2, 5))
        self.action_combo.bind('<<ComboboxSelected>>', self.on_action_selected)
        
        # Action description
        self.action_desc = ttk.Label(action_frame, text="Select an action to see description", 
                                    foreground="gray", wraplength=300)
        self.action_desc.pack(anchor="w", pady=(0, 10))
        
        # Comment field
        ttk.Label(action_frame, text="Comment (optional):").pack(anchor="w")
        self.comment_var = tk.StringVar()
        comment_entry = ttk.Entry(action_frame, textvariable=self.comment_var, width=40)
        comment_entry.pack(fill=tk.X, pady=(2, 5))
        
        # Template browser
        template_frame = ttk.Frame(action_frame)
        template_frame.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Label(template_frame, text="Available Templates:").pack(anchor="w")
        self.template_listbox = tk.Listbox(template_frame, height=4, font=('Segoe UI', 8))
        self.template_listbox.pack(fill=tk.X, pady=(2, 5))
        self.template_listbox.bind('<Double-Button-1>', self.on_template_double_click)
        
        template_btn_frame = ttk.Frame(template_frame)
        template_btn_frame.pack(fill=tk.X)
        ttk.Button(template_btn_frame, text="🔄 Refresh", command=self.refresh_templates).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(template_btn_frame, text="📁 Browse", command=self.browse_templates).pack(side=tk.LEFT)
        
        self.refresh_templates()
        
        # Add step button
        add_button = ttk.Button(action_frame, text="➕ Add Step", command=self.add_step)
        add_button.pack(pady=5)
        
        # File Operations Section
        file_frame = ttk.LabelFrame(parent, text="💾 File Operations", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        file_buttons = [
            ("📂 Load Workflow", self.load_workflow),
            ("💾 Save Workflow", self.save_workflow),
            ("🆕 New Workflow", self.new_workflow),
            ("👀 Preview YAML", self.preview_yaml)
        ]
        
        for text, command in file_buttons:
            ttk.Button(file_frame, text=text, command=command).pack(fill=tk.X, pady=2)
        
        # Step Operations Section
        step_frame = ttk.LabelFrame(parent, text="🔧 Step Operations", padding=10)
        step_frame.pack(fill=tk.BOTH, expand=True)
        
        step_buttons = [
            ("⬆️ Move Up", self.move_step_up),
            ("⬇️ Move Down", self.move_step_down),
            ("✏️ Edit Step", self.edit_step),
            ("🗑️ Delete Step", self.delete_step),
            ("📋 Duplicate Step", self.duplicate_step),
            ("🔢 Renumber Steps", self.renumber_steps)
        ]
        
        for text, command in step_buttons:
            ttk.Button(step_frame, text=text, command=command).pack(fill=tk.X, pady=2)
    
    def setup_right_panel(self, parent):
        """Set up the right panel with workflow steps"""
        # Workflow steps section
        workflow_frame = ttk.LabelFrame(parent, text="⚙️ Workflow Steps", padding=10)
        workflow_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for steps
        columns = ("Step", "Action", "Parameters", "Comment")
        self.tree = ttk.Treeview(workflow_frame, columns=columns, show="headings", height=25)
        
        # Configure columns
        self.tree.heading("Step", text="Step")
        self.tree.heading("Action", text="Action")
        self.tree.heading("Parameters", text="Parameters")
        self.tree.heading("Comment", text="Comment")
        
        self.tree.column("Step", width=60, anchor="center")
        self.tree.column("Action", width=150)
        self.tree.column("Parameters", width=300)
        self.tree.column("Comment", width=200)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(workflow_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(workflow_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        workflow_frame.grid_rowconfigure(0, weight=1)
        workflow_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click to edit
        self.tree.bind("<Double-1>", lambda e: self.edit_step())
        
        self.refresh_tree()
    
    def on_action_selected(self, event=None):
        """Update description when action is selected"""
        action = self.action_var.get()
        if action in self.action_definitions:
            desc = self.action_definitions[action]["description"]
            self.action_desc.config(text=desc, foreground="black")
    
    def add_step(self):
        """Add a new step to the workflow"""
        action = self.action_var.get()
        if not action:
            messagebox.showwarning("Warning", "Please select an action type")
            return
        
        comment = self.comment_var.get().strip()
        
        # Create step dialog for parameters
        step_data = self.create_step_dialog(action, comment)
        if step_data:
            self.step_counter += 1
            step_data['step_number'] = self.step_counter
            if comment:
                step_data['comment'] = comment
            
            self.workflow_steps.append(step_data)
            self.refresh_tree()
            
            # Clear comment field
            self.comment_var.set("")
    
    def create_step_dialog(self, action, comment="", existing_step=None):
        """Create a dialog for step parameters"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Configure Step: {action}")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text=f"Configure: {action}", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # Description
        desc = self.action_definitions[action]["description"]
        ttk.Label(main_frame, text=desc, foreground="gray").pack(pady=(0, 15))
        
        # Comment field
        ttk.Label(main_frame, text="Comment:").pack(anchor="w")
        comment_var = tk.StringVar(value=comment)
        comment_entry = ttk.Entry(main_frame, textvariable=comment_var, width=60)
        comment_entry.pack(fill=tk.X, pady=(2, 15))
        
        # Parameters frame with scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Parameters
        param_vars = {}
        parameters = self.action_definitions[action]["parameters"]
        
        for param in parameters:
            param_frame = ttk.Frame(scrollable_frame)
            param_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(param_frame, text=f"{param}:", width=20).pack(side=tk.LEFT)
            
            # Get existing value if editing
            existing_value = ""
            if existing_step and param in existing_step:
                existing_value = existing_step[param]
            
            # Create appropriate widget based on parameter
            if param in ["templates"]:
                # Multiple templates - text area
                var = tk.StringVar(value=str(existing_value) if existing_value else "")
                entry = ttk.Entry(param_frame, textvariable=var, width=40)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                ttk.Label(param_frame, text="(comma-separated)", foreground="gray").pack(side=tk.RIGHT)
            elif param in ["timeout", "duration", "seconds", "x", "y", "max_retries", "retry_delay"]:
                # Numeric fields
                var = tk.StringVar(value=str(existing_value) if existing_value else "")
                entry = ttk.Entry(param_frame, textvariable=var, width=40)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif param in ["threshold", "move_duration", "pre_click_delay", "post_click_delay"]:
                # Float fields
                var = tk.StringVar(value=str(existing_value) if existing_value else "")
                entry = ttk.Entry(param_frame, textvariable=var, width=40)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif param == "button":
                # Button type dropdown
                var = tk.StringVar(value=existing_value or "left")
                combo = ttk.Combobox(param_frame, textvariable=var, 
                                   values=["left", "right", "middle"], state="readonly", width=37)
                combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif param == "force":
                # Boolean checkbox
                var = tk.BooleanVar(value=existing_value or False)
                check = ttk.Checkbutton(param_frame, variable=var)
                check.pack(side=tk.LEFT)
            elif param in ["region", "offset"]:
                # List/tuple fields
                var = tk.StringVar(value=str(existing_value) if existing_value else "")
                entry = ttk.Entry(param_frame, textvariable=var, width=40)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                ttk.Label(param_frame, text="[x1,y1,x2,y2]" if param == "region" else "[x,y]", 
                         foreground="gray").pack(side=tk.RIGHT)
            else:
                # Default text field
                var = tk.StringVar(value=str(existing_value) if existing_value else "")
                entry = ttk.Entry(param_frame, textvariable=var, width=40)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            param_vars[param] = var
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Global parameters
        global_frame = ttk.LabelFrame(main_frame, text="Global Parameters")
        global_frame.pack(fill=tk.X, pady=(15, 10))
        
        optional_var = tk.BooleanVar(value=existing_step.get('optional', False) if existing_step else False)
        ttk.Checkbutton(global_frame, text="Optional (don't stop workflow on failure)", 
                       variable=optional_var).pack(anchor="w", padx=5, pady=2)
        
        step_delay_var = tk.StringVar(value=str(existing_step.get('step_delay', '')) if existing_step else "")
        delay_frame = ttk.Frame(global_frame)
        delay_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(delay_frame, text="Step delay (seconds):").pack(side=tk.LEFT)
        ttk.Entry(delay_frame, textvariable=step_delay_var, width=10).pack(side=tk.LEFT, padx=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        result = [None]
        
        def on_ok():
            step_data = {"action": action}
            
            # Add comment if provided
            comment_text = comment_var.get().strip()
            if comment_text:
                step_data["comment"] = comment_text
            
            # Add parameters
            for param, var in param_vars.items():
                value = var.get()
                if value:  # Only add non-empty values
                    # Convert values to appropriate types
                    if param in ["timeout", "duration", "seconds", "x", "y", "max_retries", "retry_delay", "startup_time"]:
                        try:
                            step_data[param] = int(value)
                        except ValueError:
                            messagebox.showerror("Error", f"Invalid number for {param}: {value}")
                            return
                    elif param in ["threshold", "move_duration", "pre_click_delay", "post_click_delay"]:
                        try:
                            step_data[param] = float(value)
                        except ValueError:
                            messagebox.showerror("Error", f"Invalid decimal for {param}: {value}")
                            return
                    elif param in ["region", "offset"]:
                        try:
                            # Parse list/tuple
                            import ast
                            step_data[param] = ast.literal_eval(value)
                        except:
                            messagebox.showerror("Error", f"Invalid format for {param}: {value}")
                            return
                    elif param == "templates":
                        # Split comma-separated values
                        step_data[param] = [t.strip() for t in value.split(",") if t.strip()]
                    else:
                        step_data[param] = value
            
            # Add global parameters
            if optional_var.get():
                step_data["optional"] = True
            
            step_delay = step_delay_var.get().strip()
            if step_delay:
                try:
                    step_data["step_delay"] = float(step_delay)
                except ValueError:
                    messagebox.showerror("Error", f"Invalid step delay: {step_delay}")
                    return
            
            result[0] = step_data
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        ttk.Button(button_frame, text="OK", command=on_ok).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.RIGHT)
        
        # Wait for dialog to close
        dialog.wait_window()
        return result[0]
    
    def refresh_tree(self):
        """Refresh the workflow tree display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add steps
        for i, step in enumerate(self.workflow_steps):
            step_num = step.get('step_number', i + 1)
            action = step.get('action', '')
            comment = step.get('comment', '')
            
            # Build parameters string
            params = []
            for key, value in step.items():
                if key not in ['action', 'comment', 'step_number']:
                    params.append(f"{key}: {value}")
            params_str = ", ".join(params)
            
            self.tree.insert("", "end", values=(step_num, action, params_str, comment))
    
    def get_selected_step_index(self):
        """Get the index of the currently selected step"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a step")
            return None
        
        item = selection[0]
        return self.tree.index(item)
    
    def move_step_up(self):
        """Move selected step up"""
        index = self.get_selected_step_index()
        if index is None or index == 0:
            return
        
        # Swap steps
        self.workflow_steps[index], self.workflow_steps[index - 1] = \
            self.workflow_steps[index - 1], self.workflow_steps[index]
        
        self.refresh_tree()
        # Reselect the moved item
        children = self.tree.get_children()
        if index - 1 < len(children):
            self.tree.selection_set(children[index - 1])
    
    def move_step_down(self):
        """Move selected step down"""
        index = self.get_selected_step_index()
        if index is None or index >= len(self.workflow_steps) - 1:
            return
        
        # Swap steps
        self.workflow_steps[index], self.workflow_steps[index + 1] = \
            self.workflow_steps[index + 1], self.workflow_steps[index]
        
        self.refresh_tree()
        # Reselect the moved item
        children = self.tree.get_children()
        if index + 1 < len(children):
            self.tree.selection_set(children[index + 1])
    
    def edit_step(self):
        """Edit the selected step"""
        index = self.get_selected_step_index()
        if index is None:
            return
        
        step = self.workflow_steps[index]
        action = step['action']
        comment = step.get('comment', '')
        
        # Open edit dialog
        updated_step = self.create_step_dialog(action, comment, step)
        if updated_step:
            # Preserve step number
            updated_step['step_number'] = step.get('step_number', index + 1)
            self.workflow_steps[index] = updated_step
            self.refresh_tree()
    
    def delete_step(self):
        """Delete the selected step"""
        index = self.get_selected_step_index()
        if index is None:
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this step?"):
            del self.workflow_steps[index]
            self.refresh_tree()
    
    def duplicate_step(self):
        """Duplicate the selected step"""
        index = self.get_selected_step_index()
        if index is None:
            return
        
        step = self.workflow_steps[index].copy()
        self.step_counter += 1
        step['step_number'] = self.step_counter
        
        # Insert after current step
        self.workflow_steps.insert(index + 1, step)
        self.refresh_tree()
    
    def renumber_steps(self):
        """Renumber all steps sequentially"""
        for i, step in enumerate(self.workflow_steps):
            step['step_number'] = i + 1
        
        self.step_counter = len(self.workflow_steps)
        self.refresh_tree()
        messagebox.showinfo("Success", "Steps renumbered successfully!")
    
    def new_workflow(self):
        """Create a new workflow"""
        if messagebox.askyesno("New Workflow", "This will clear the current workflow. Continue?"):
            self.workflow_steps = []
            self.step_counter = 0
            
            # Reset game config
            for key, var in self.config_vars.items():
                if key == "type":
                    var.set("steam")
                elif key == "startup_time":
                    var.set(60)
                else:
                    var.set("")
            
            self.refresh_tree()
    
    def load_workflow(self):
        """Load workflow from YAML file"""
        file_path = filedialog.askopenfilename(
            title="Load Workflow",
            initialdir="config/games",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            if not isinstance(data, dict):
                messagebox.showerror("Error", "Invalid YAML format - expected dictionary")
                return
            
            # Load game config with type conversion
            for key, var in self.config_vars.items():
                if key in data:
                    value = data[key]
                    # Convert all values to strings for tkinter variables
                    var.set(str(value) if value is not None else "")
            
            # Load workflow steps
            workflow_data = data.get('workflow', [])
            if not isinstance(workflow_data, list):
                messagebox.showerror("Error", "Workflow must be a list of steps")
                return
            
            # Clean and process workflow steps
            self.workflow_steps = []
            for i, step in enumerate(workflow_data):
                # Skip non-dictionary entries (comments, etc.)
                if isinstance(step, dict) and 'action' in step:
                    # Ensure step has required fields
                    clean_step = step.copy()
                    if 'step_number' not in clean_step:
                        clean_step['step_number'] = i + 1
                    self.workflow_steps.append(clean_step)
            
            self.step_counter = len(self.workflow_steps)
            self.refresh_tree()
            
            messagebox.showinfo("Success", f"Workflow loaded from {file_path}")
            
        except yaml.YAMLError as e:
            messagebox.showerror("Error", f"Invalid YAML file: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load workflow: {e}")
    
    def save_workflow(self):
        """Save workflow to YAML file"""
        # Update game config from UI
        for key, var in self.config_vars.items():
            self.game_config[key] = var.get()
        
        # Generate YAML
        yaml_content = self.generate_yaml()
        
        # Get save path
        game_name = self.config_vars['name'].get() or "new_game"
        filename = f"{game_name.lower().replace(' ', '_')}.yaml"
        
        file_path = filedialog.asksaveasfilename(
            title="Save Workflow",
            initialdir="config/games",
            initialfile=filename,
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w') as f:
                f.write(yaml_content)
            
            messagebox.showinfo("Success", f"Workflow saved to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save workflow: {e}")
    
    def preview_yaml(self):
        """Preview the generated YAML"""
        # Update game config from UI
        for key, var in self.config_vars.items():
            self.game_config[key] = var.get()
        
        yaml_content = self.generate_yaml()
        
        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("YAML Preview")
        preview_window.geometry("800x600")
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(preview_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        text_widget.insert("1.0", yaml_content)
        text_widget.config(state="disabled")
        
        # Copy button
        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(yaml_content)
            messagebox.showinfo("Copied", "YAML content copied to clipboard!")
        
        ttk.Button(preview_window, text="📋 Copy to Clipboard", 
                  command=copy_to_clipboard).pack(pady=5)
    
    def generate_yaml(self):
        """Generate YAML content from current configuration"""
        lines = []
        
        # Add game configuration
        for key, var in self.config_vars.items():
            value = var.get()
            if key == "startup_time":
                lines.append(f"{key}: {int(value) if value else 60}")
            elif key in ["app_id"]:
                lines.append(f'{key}: "{value}"')
            else:
                lines.append(f'{key}: "{value}"')
        
        lines.append("\nworkflow:")
        
        # Add workflow steps with proper comment formatting
        for i, step in enumerate(self.workflow_steps):
            # Add comment if exists - preserve exact spacing
            comment = step.get('comment', '').strip()
            if comment:
                lines.append(f"  # {comment}")
            
            # Add step number comment
            step_num = step.get('step_number', i + 1)
            lines.append(f"  #{step_num}")
            
            # Build step
            lines.append(f"  - action: \"{step['action']}\"")
            
            # Add parameters in logical order
            param_order = ["template", "templates", "timeout", "threshold", "region", "button", "offset",
                          "move_duration", "pre_click_delay", "post_click_delay", "key", "duration", 
                          "text", "x", "y", "seconds", "name", "message", "force", "process_name",
                          "action_to_retry", "max_retries", "retry_delay", "optional", "step_delay"]
            
            # Add parameters
            for param in param_order:
                if param in step and param not in ['action', 'comment', 'step_number']:
                    value = step[param]
                    if isinstance(value, str):
                        lines.append(f'    {param}: "{value}"')
                    elif isinstance(value, list):
                        if param == "templates":
                            lines.append(f'    {param}: {value}')
                        else:
                            lines.append(f'    {param}: {value}')
                    else:
                        lines.append(f'    {param}: {value}')
            
            # Add any remaining parameters
            for key, value in step.items():
                if key not in param_order and key not in ['action', 'comment', 'step_number']:
                    if isinstance(value, str):
                        lines.append(f'    {key}: "{value}"')
                    else:
                        lines.append(f'    {key}: {value}')
            
            lines.append("")  # Empty line between steps
        
        return '\n'.join(lines)
    
    def load_existing_workflow(self):
        """Load existing workflow into the builder"""
        self.refresh_tree()
    
    def refresh_templates(self):
        """Refresh the template list from the templates directory"""
        self.template_listbox.delete(0, tk.END)
        
        templates_dir = Path("templates/screens")
        if not templates_dir.exists():
            self.template_listbox.insert(tk.END, "No templates directory found")
            return
        
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
    
    def on_template_double_click(self, event):
        """Handle double-click on template to preview it"""
        selection = self.template_listbox.curselection()
        if not selection:
            return
        
        template_name = self.template_listbox.get(selection[0])
        if template_name in ["No templates directory found", "No template files found"]:
            return
        
        self.preview_template(template_name)
    
    def browse_templates(self):
        """Open templates folder in file explorer"""
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
    
    def preview_template(self, template_name):
        """Preview a template image"""
        try:
            import PIL.Image
            import PIL.ImageTk
            
            template_path = Path("templates/screens") / template_name
            if not template_path.exists():
                messagebox.showerror("Error", f"Template not found: {template_path}")
                return
            
            # Create preview window
            preview_window = tk.Toplevel(self.root)
            preview_window.title(f"Template Preview: {template_name}")
            preview_window.geometry("600x500")
            
            # Load and display image
            image = PIL.Image.open(template_path)
            
            # Resize if too large
            max_size = (550, 400)
            image.thumbnail(max_size, PIL.Image.Resampling.LANCZOS)
            
            photo = PIL.ImageTk.PhotoImage(image)
            
            # Create image label
            image_label = tk.Label(preview_window, image=photo)
            image_label.image = photo  # Keep a reference
            image_label.pack(padx=10, pady=10)
            
            # Info frame
            info_frame = ttk.Frame(preview_window)
            info_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(info_frame, text=f"File: {template_name}").pack(anchor="w")
            ttk.Label(info_frame, text=f"Size: {image.size[0]}x{image.size[1]} pixels").pack(anchor="w")
            ttk.Label(info_frame, text=f"Path: {template_path}").pack(anchor="w")
            
            # Copy filename button
            def copy_filename():
                filename = Path(template_name).name
                self.root.clipboard_clear()
                self.root.clipboard_append(filename)
                messagebox.showinfo("Copied", f"Filename '{filename}' copied to clipboard!")
            
            ttk.Button(info_frame, text="📋 Copy Filename", 
                      command=copy_filename).pack(pady=5)
                      
        except ImportError:
            messagebox.showerror("Error", "PIL/Pillow is required for template preview. Install with: pip install Pillow")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview template: {e}")

# Main function to run the workflow builder
def main():
    app = WorkflowBuilder()
    app.root.mainloop()

if __name__ == "__main__":
    main()
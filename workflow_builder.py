import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yaml
import os
from pathlib import Path
from datetime import datetime

class WorkflowBuilder:
    def __init__(self, parent=None, game_name=None, existing_workflow=None):
        self.parent = parent
        self.game_name = game_name
        self.workflow_steps = existing_workflow or []
        self.templates = self._load_templates()
        
        # Create main window
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title(f"🔧 Workflow Builder - {game_name or 'New Workflow'}")
        self.window.geometry("1200x800")
        self.window.minsize(1000, 600)
        
        # Available actions with their parameters
        self.action_definitions = {
            "launch_game": {
                "name": "Launch Game",
                "icon": "🚀",
                "params": {}
            },
            "wait_for_game": {
                "name": "Wait for Game",
                "icon": "⏳",
                "params": {
                    "timeout": {"type": "int", "default": 60, "label": "Timeout (seconds)"}
                }
            },
            "wait_for_template": {
                "name": "Wait for Template",
                "icon": "👁️",
                "params": {
                    "template": {"type": "template", "default": "", "label": "Template"},
                    "timeout": {"type": "int", "default": 30, "label": "Timeout (seconds)"},
                    "threshold": {"type": "float", "default": 0.8, "label": "Threshold", "min": 0.1, "max": 1.0}
                }
            },
            "click_template": {
                "name": "Click Template", 
                "icon": "🖱️",
                "params": {
                    "template": {"type": "template", "default": "", "label": "Template"},
                    "timeout": {"type": "int", "default": 10, "label": "Timeout (seconds)"},
                    "button": {"type": "choice", "default": "left", "choices": ["left", "right", "middle"], "label": "Mouse Button"},
                    "move_duration": {"type": "float", "default": 0.5, "label": "Move Duration", "min": 0.1, "max": 3.0},
                    "pre_click_delay": {"type": "float", "default": 0.3, "label": "Pre-click Delay", "min": 0.0, "max": 2.0},
                    "post_click_delay": {"type": "float", "default": 0.5, "label": "Post-click Delay", "min": 0.0, "max": 2.0}
                }
            },
            "click_template_if_exists": {
                "name": "Click Template (Optional)",
                "icon": "🖱️",
                "params": {
                    "template": {"type": "template", "default": "", "label": "Template"},
                    "optional": {"type": "bool", "default": True, "label": "Optional"},
                    "button": {"type": "choice", "default": "left", "choices": ["left", "right", "middle"], "label": "Mouse Button"}
                }
            },
            "press_key": {
                "name": "Press Key",
                "icon": "⌨️", 
                "params": {
                    "key": {"type": "string", "default": "escape", "label": "Key"},
                    "delay": {"type": "float", "default": 0.5, "label": "Delay (seconds)", "min": 0.0, "max": 5.0}
                }
            },
            "hold_key": {
                "name": "Hold Key",
                "icon": "⌨️",
                "params": {
                    "key": {"type": "string", "default": "space", "label": "Key"},
                    "duration": {"type": "float", "default": 1.0, "label": "Duration (seconds)", "min": 0.1, "max": 10.0}
                }
            },
            "type_text": {
                "name": "Type Text",
                "icon": "📝",
                "params": {
                    "text": {"type": "string", "default": "", "label": "Text to Type"},
                    "delay": {"type": "float", "default": 0.5, "label": "Delay (seconds)", "min": 0.0, "max": 5.0}
                }
            },
            "take_screenshot": {
                "name": "Take Screenshot",
                "icon": "📸",
                "params": {
                    "name": {"type": "string", "default": "screenshot", "label": "Screenshot Name"}
                }
            },
            "wait": {
                "name": "Wait",
                "icon": "⏱️",
                "params": {
                    "seconds": {"type": "float", "default": 1.0, "label": "Seconds", "min": 0.1, "max": 300.0}
                }
            },
            "log_message": {
                "name": "Log Message",
                "icon": "📝",
                "params": {
                    "message": {"type": "string", "default": "LOG_MESSAGE", "label": "Message"}
                }
            }
        }
        
        self.setup_ui()
    
    def _load_templates(self):
        """Load available templates"""
        templates = {}
        templates_dir = Path("templates/screens")
        
        if templates_dir.exists():
            for game_dir in templates_dir.iterdir():
                if game_dir.is_dir():
                    game_templates = []
                    for template_file in game_dir.glob("*.png"):
                        game_templates.append(template_file.name)
                    if game_templates:
                        templates[game_dir.name] = sorted(game_templates)
        
        return templates
    
    def setup_ui(self):
        # Configure window style
        style = ttk.Style()
        style.configure('Builder.TLabelframe', font=('Segoe UI', 10, 'bold'))
        
        # Create main paned window
        main_paned = ttk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Actions and Templates
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Right panel - Workflow
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)
        
        self.setup_left_panel(left_frame)
        self.setup_right_panel(right_frame)
        self.setup_menu()
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Workflow", command=self.new_workflow)
        file_menu.add_command(label="Open Workflow", command=self.open_workflow)
        file_menu.add_command(label="Save Workflow", command=self.save_workflow)
        file_menu.add_command(label="Save As...", command=self.save_workflow_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export YAML", command=self.export_yaml)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Refresh Templates", command=self.refresh_templates)
        tools_menu.add_command(label="Validate Workflow", command=self.validate_workflow)
    
    def setup_left_panel(self, parent):
        """Setup left panel with actions and templates"""
        # Actions section
        actions_frame = ttk.LabelFrame(parent, text="🎯 Available Actions", style='Builder.TLabelframe')
        actions_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Search actions
        search_frame = ttk.Frame(actions_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(search_frame, text="🔍 Search:").pack(side=tk.LEFT)
        self.action_search = ttk.Entry(search_frame)
        self.action_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.action_search.bind('<KeyRelease>', self.filter_actions)
        
        # Actions list
        actions_list_frame = ttk.Frame(actions_frame)
        actions_list_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.actions_listbox = tk.Listbox(actions_list_frame, font=('Segoe UI', 9), height=6)
        self.actions_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        actions_scroll = ttk.Scrollbar(actions_list_frame, orient=tk.VERTICAL, command=self.actions_listbox.yview)
        actions_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.actions_listbox.config(yscrollcommand=actions_scroll.set)
        
        # Add action button
        ttk.Button(actions_frame, text="➕ Add Action", command=self.add_action).pack(pady=(0, 10))
        
        # Templates section
        templates_frame = ttk.LabelFrame(parent, text="🎯 Available Templates", style='Builder.TLabelframe')
        templates_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Template tree
        template_tree_frame = ttk.Frame(templates_frame)
        template_tree_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.template_tree = ttk.Treeview(template_tree_frame, height=6)
        self.template_tree.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        template_scroll = ttk.Scrollbar(template_tree_frame, orient=tk.VERTICAL, command=self.template_tree.yview)
        template_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.template_tree.config(yscrollcommand=template_scroll.set)
        
        # Bind template selection
        self.template_tree.bind('<<TreeviewSelect>>', self.on_template_select)
        
        # Template preview section
        preview_frame = ttk.LabelFrame(templates_frame, text="👁️ Template Preview", style='Builder.TLabelframe')
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 10))
        
        # Preview canvas
        self.preview_canvas = tk.Canvas(preview_frame, bg='white', height=150)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Preview info label
        self.preview_info = ttk.Label(preview_frame, text="Select a template to preview", 
                                    font=('Segoe UI', 8), foreground='gray')
        self.preview_info.pack(pady=(0, 5))
        
        # Populate initial data
        self.populate_actions()
        self.populate_templates()
    
    def on_template_select(self, event):
        """Handle template selection"""
        selection = self.template_tree.selection()
        if not selection:
            self.clear_preview()
            return
        
        item = selection[0]
        item_text = self.template_tree.item(item, 'text')
        
        # Check if it's a template (has 🎯 icon)
        if '🎯' in item_text:
            template_name = item_text.replace('🎯 ', '')
            self.show_template_preview(template_name)
        else:
            self.clear_preview()

    def show_template_preview(self, template_name):
        """Show preview of selected template"""
        try:
            from PIL import Image, ImageTk
            
            # Find template file
            template_path = None
            for game, templates in self.templates.items():
                if template_name in templates:
                    template_path = Path("templates/screens") / game / template_name
                    break
            
            if not template_path or not template_path.exists():
                self.clear_preview()
                return
            
            # Load and resize image
            image = Image.open(template_path)
            
            # Calculate scaling to fit canvas
            canvas_width = self.preview_canvas.winfo_width() or 150
            canvas_height = self.preview_canvas.winfo_height() or 100
            
            # Scale image to fit
            img_ratio = image.width / image.height
            canvas_ratio = canvas_width / canvas_height
            
            if img_ratio > canvas_ratio:
                # Image is wider
                new_width = canvas_width - 10
                new_height = int(new_width / img_ratio)
            else:
                # Image is taller
                new_height = canvas_height - 10
                new_width = int(new_height * img_ratio)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert for tkinter
            self.preview_image = ImageTk.PhotoImage(image)
            
            # Clear canvas and show image
            self.preview_canvas.delete("all")
            x = canvas_width // 2
            y = canvas_height // 2
            self.preview_canvas.create_image(x, y, image=self.preview_image)
            
            # Update info
            self.preview_info.config(text=f"{template_name} ({image.width}x{image.height})")
            
        except Exception as e:
            self.clear_preview()
            self.preview_info.config(text=f"Preview error: {str(e)}")

    def clear_preview(self):
        """Clear template preview"""
        self.preview_canvas.delete("all")
        self.preview_canvas.create_text(100, 75, text="No template selected", 
                                    fill='gray', font=('Segoe UI', 10))
        self.preview_info.config(text="Select a template to preview")
    
    def setup_right_panel(self, parent):
        """Setup right panel with workflow editor"""
        # Workflow header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="⚙️ Workflow Steps", font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)
        
        # Control buttons
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side=tk.RIGHT)
        
        ttk.Button(controls_frame, text="🔼", command=self.move_up, width=3).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(controls_frame, text="🔽", command=self.move_down, width=3).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(controls_frame, text="✏️", command=self.edit_step, width=3).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(controls_frame, text="🗑️", command=self.delete_step, width=3).pack(side=tk.LEFT)
        
        # Workflow list
        workflow_frame = ttk.Frame(parent)
        workflow_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for workflow steps
        columns = ("Step", "Action", "Parameters")
        self.workflow_tree = ttk.Treeview(workflow_frame, columns=columns, show="tree headings", height=15)
        
        # Configure columns
        self.workflow_tree.column("#0", width=50, minwidth=30)
        self.workflow_tree.column("Step", width=60, minwidth=50)
        self.workflow_tree.column("Action", width=200, minwidth=150)
        self.workflow_tree.column("Parameters", width=300, minwidth=200)
        
        # Configure headings
        self.workflow_tree.heading("#0", text="#")
        self.workflow_tree.heading("Step", text="Step")
        self.workflow_tree.heading("Action", text="Action")
        self.workflow_tree.heading("Parameters", text="Parameters")
        
        self.workflow_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        workflow_scroll = ttk.Scrollbar(workflow_frame, orient=tk.VERTICAL, command=self.workflow_tree.yview)
        workflow_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.workflow_tree.config(yscrollcommand=workflow_scroll.set)
        
        # Bind double-click to edit
        self.workflow_tree.bind("<Double-1>", lambda e: self.edit_step())
        
        # Populate workflow if existing
        self.refresh_workflow_display()
    
    def populate_actions(self):
        """Populate the actions listbox"""
        self.actions_listbox.delete(0, tk.END)
        for action_id, action_def in self.action_definitions.items():
            display_text = f"{action_def['icon']} {action_def['name']}"
            self.actions_listbox.insert(tk.END, display_text)
    
    def filter_actions(self, event=None):
        """Filter actions based on search"""
        search_text = self.action_search.get().lower()
        self.actions_listbox.delete(0, tk.END)
        
        for action_id, action_def in self.action_definitions.items():
            if search_text in action_def['name'].lower() or search_text in action_id.lower():
                display_text = f"{action_def['icon']} {action_def['name']}"
                self.actions_listbox.insert(tk.END, display_text)
    
    def populate_templates(self):
        """Populate the templates tree"""
        self.template_tree.delete(*self.template_tree.get_children())
        
        for game, templates in self.templates.items():
            game_node = self.template_tree.insert("", "end", text=f"🎮 {game}")
            for template in templates:
                self.template_tree.insert(game_node, "end", text=f"🎯 {template}")
    
    def add_action(self):
        """Add selected action to workflow"""
        selection = self.actions_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an action to add")
            return
        
        # Get action ID from selection
        action_keys = list(self.action_definitions.keys())
        action_id = action_keys[selection[0]]
        action_def = self.action_definitions[action_id]
        
        # Create step with default parameters
        step = {"action": action_id}
        for param_name, param_def in action_def["params"].items():
            step[param_name] = param_def["default"]
        
        # Add to workflow
        self.workflow_steps.append(step)
        self.refresh_workflow_display()
    
    def refresh_workflow_display(self):
        """Refresh the workflow display"""
        self.workflow_tree.delete(*self.workflow_tree.get_children())
        
        for i, step in enumerate(self.workflow_steps):
            action_id = step.get("action", "unknown")
            action_def = self.action_definitions.get(action_id, {"name": action_id, "icon": "❓"})
            
            # Build parameters string
            params = []
            for key, value in step.items():
                if key != "action":
                    if isinstance(value, str) and len(value) > 30:
                        value = value[:27] + "..."
                    params.append(f"{key}: {value}")
            
            params_str = ", ".join(params) if params else "No parameters"
            
            # Insert into tree
            self.workflow_tree.insert("", "end", 
                                    text=str(i+1),
                                    values=(i+1, f"{action_def['icon']} {action_def['name']}", params_str))
    
    def move_up(self):
        """Move selected step up"""
        selection = self.workflow_tree.selection()
        if not selection:
            return
        
        # Get index
        item = selection[0]
        index = self.workflow_tree.index(item)
        
        if index > 0:
            # Swap in list
            self.workflow_steps[index], self.workflow_steps[index-1] = \
                self.workflow_steps[index-1], self.workflow_steps[index]
            
            self.refresh_workflow_display()
            
            # Reselect moved item
            new_item = self.workflow_tree.get_children()[index-1]
            self.workflow_tree.selection_set(new_item)
    
    def move_down(self):
        """Move selected step down"""
        selection = self.workflow_tree.selection()
        if not selection:
            return
        
        # Get index
        item = selection[0]
        index = self.workflow_tree.index(item)
        
        if index < len(self.workflow_steps) - 1:
            # Swap in list
            self.workflow_steps[index], self.workflow_steps[index+1] = \
                self.workflow_steps[index+1], self.workflow_steps[index]
            
            self.refresh_workflow_display()
            
            # Reselect moved item
            new_item = self.workflow_tree.get_children()[index+1]
            self.workflow_tree.selection_set(new_item)
    
    def edit_step(self):
        """Edit selected step"""
        selection = self.workflow_tree.selection()
        if not selection:
            return
        
        # Get index
        item = selection[0]
        index = self.workflow_tree.index(item)
        step = self.workflow_steps[index]
        
        # Open parameter editor
        self.open_parameter_editor(step, index)
    
    def delete_step(self):
        """Delete selected step"""
        selection = self.workflow_tree.selection()
        if not selection:
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this step?"):
            # Get index BEFORE showing dialog (dialog can change selection)
            item = selection[0]
            try:
                index = self.workflow_tree.index(item)
                # Remove from list
                del self.workflow_steps[index]
                self.refresh_workflow_display()
            except tk.TclError:
                # Item no longer exists, just refresh
                self.refresh_workflow_display()
    
    def open_parameter_editor(self, step, index):
        """Open parameter editor dialog"""
        action_id = step.get("action")
        action_def = self.action_definitions.get(action_id)
        
        if not action_def:
            messagebox.showerror("Error", f"Unknown action: {action_id}")
            return
        
        # Create editor window
        editor = tk.Toplevel(self.window)
        editor.title(f"Edit {action_def['name']}")
        editor.geometry("500x600")
        editor.transient(self.window)
        editor.grab_set()
        
        # Center the dialog
        editor.geometry("+%d+%d" % (self.window.winfo_rootx() + 100, self.window.winfo_rooty() + 100))
        
        # Main frame
        main_frame = ttk.Frame(editor, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"{action_def['icon']} {action_def['name']}", 
                               font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Parameters frame
        params_frame = ttk.Labelframe(main_frame, text="Parameters", padding=10)
        params_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create parameter widgets
        param_widgets = {}
        
        for param_name, param_def in action_def["params"].items():
            param_frame = ttk.Frame(params_frame)
            param_frame.pack(fill=tk.X, pady=5)
            
            # Label
            ttk.Label(param_frame, text=param_def["label"] + ":").pack(anchor=tk.W)
            
            # Widget based on type
            current_value = step.get(param_name, param_def["default"])
            
            if param_def["type"] == "string":
                widget = ttk.Entry(param_frame)
                widget.insert(0, str(current_value))
                widget.pack(fill=tk.X, pady=(2, 0))
                param_widgets[param_name] = widget
                
            elif param_def["type"] == "int":
                widget = ttk.Spinbox(param_frame, from_=0, to=9999, value=current_value)
                widget.pack(fill=tk.X, pady=(2, 0))
                param_widgets[param_name] = widget
                
            elif param_def["type"] == "float":
                widget = ttk.Spinbox(param_frame, 
                                   from_=param_def.get("min", 0.0), 
                                   to=param_def.get("max", 999.0),
                                   increment=0.1, value=current_value)
                widget.pack(fill=tk.X, pady=(2, 0))
                param_widgets[param_name] = widget
                
            elif param_def["type"] == "bool":
                var = tk.BooleanVar(value=current_value)
                widget = ttk.Checkbutton(param_frame, variable=var)
                widget.pack(anchor=tk.W, pady=(2, 0))
                param_widgets[param_name] = var
                
            elif param_def["type"] == "choice":
                widget = ttk.Combobox(param_frame, values=param_def["choices"], state="readonly")
                widget.set(current_value)
                widget.pack(fill=tk.X, pady=(2, 0))
                param_widgets[param_name] = widget
                
            elif param_def["type"] == "template":
                # Template selector with browse
                template_frame = ttk.Frame(param_frame)
                template_frame.pack(fill=tk.X, pady=(2, 0))
                
                widget = ttk.Combobox(template_frame, state="readonly")
                widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Populate with available templates
                all_templates = []
                for game, templates in self.templates.items():
                    for template in templates:
                        all_templates.append(template)
                widget['values'] = all_templates
                widget.set(current_value)
                
                ttk.Button(template_frame, text="📁", width=3,
                          command=lambda w=widget: self.browse_template(w)).pack(side=tk.RIGHT, padx=(5, 0))
                
                param_widgets[param_name] = widget
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def save_parameters():
            # Update step with new values
            for param_name, widget in param_widgets.items():
                if isinstance(widget, tk.BooleanVar):
                    step[param_name] = widget.get()
                else:
                    value = widget.get()
                    param_def = action_def["params"][param_name]
                    
                    # Convert types
                    if param_def["type"] == "int":
                        try:
                            value = int(value)
                        except ValueError:
                            value = param_def["default"]
                    elif param_def["type"] == "float":
                        try:
                            value = float(value)
                        except ValueError:
                            value = param_def["default"]
                    
                    step[param_name] = value
            
            # Update display
            self.refresh_workflow_display()
            editor.destroy()
        
        ttk.Button(button_frame, text="💾 Save", command=save_parameters).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="❌ Cancel", command=editor.destroy).pack(side=tk.RIGHT)
    
    def browse_template(self, widget):
        """Browse for template file"""
        filename = filedialog.askopenfilename(
            title="Select Template",
            initialdir="templates/screens",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if filename:
            # Extract just the filename
            template_name = Path(filename).name
            widget.set(template_name)
    
    def refresh_templates(self):
        """Refresh template list"""
        self.templates = self._load_templates()
        self.populate_templates()
        messagebox.showinfo("Templates Refreshed", "Template list has been updated")
    
    def validate_workflow(self):
        """Validate the current workflow"""
        errors = []
        warnings = []
        
        if not self.workflow_steps:
            errors.append("Workflow is empty")
        
        for i, step in enumerate(self.workflow_steps):
            step_num = i + 1
            action_id = step.get("action")
            
            if not action_id:
                errors.append(f"Step {step_num}: No action specified")
                continue
            
            action_def = self.action_definitions.get(action_id)
            if not action_def:
                errors.append(f"Step {step_num}: Unknown action '{action_id}'")
                continue
            
            # Check required parameters
            for param_name, param_def in action_def["params"].items():
                if param_name not in step:
                    warnings.append(f"Step {step_num}: Missing parameter '{param_name}'")
                elif param_def["type"] == "template":
                    template = step[param_name]
                    if template and not self._template_exists(template):
                        warnings.append(f"Step {step_num}: Template '{template}' not found")
        
        # Show results
        if errors:
            messagebox.showerror("Validation Errors", "\n".join(errors))
        elif warnings:
            messagebox.showwarning("Validation Warnings", "\n".join(warnings))
        else:
            messagebox.showinfo("Validation Passed", "Workflow validation completed successfully!")
    
    def _template_exists(self, template_name):
        """Check if template exists"""
        for game, templates in self.templates.items():
            if template_name in templates:
                return True
        return False
    
    def new_workflow(self):
        """Create new workflow"""
        if self.workflow_steps and messagebox.askyesno("Confirm", "Clear current workflow?"):
            self.workflow_steps = []
            self.refresh_workflow_display()
    
    def open_workflow(self):
        """Open workflow from file"""
        filename = filedialog.askopenfilename(
            title="Open Workflow",
            initialdir="config/games",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = yaml.safe_load(f)
                
                workflow = data.get('workflow', [])
                if workflow:
                    self.workflow_steps = workflow
                    self.refresh_workflow_display()
                    messagebox.showinfo("Success", f"Loaded {len(workflow)} steps")
                else:
                    messagebox.showwarning("No Workflow", "No workflow found in file")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load workflow: {e}")
    
    def save_workflow(self):
        """Save workflow to current game config"""
        if not self.game_name:
            self.save_workflow_as()
            return
        
        config_path = Path("config/games") / f"{self.game_name.lower().replace(' ', '_')}.yaml"
        
        try:
            # Load existing config
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f) or {}
            else:
                config = {"name": self.game_name}
            
            # Update workflow
            config['workflow'] = self.workflow_steps
            
            # Save
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            messagebox.showinfo("Success", f"Workflow saved to {config_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save workflow: {e}")
    
    def save_workflow_as(self):
        """Save workflow as new file"""
        filename = filedialog.asksaveasfilename(
            title="Save Workflow As",
            initialdir="config/games",
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                config = {
                    "name": Path(filename).stem,
                    "workflow": self.workflow_steps
                }
                
                with open(filename, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
                
                messagebox.showinfo("Success", f"Workflow saved to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save workflow: {e}")
    
    def export_yaml(self):
        """Export just the workflow as YAML"""
        filename = filedialog.asksaveasfilename(
            title="Export Workflow YAML",
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    yaml.dump({"workflow": self.workflow_steps}, f, default_flow_style=False)
                
                messagebox.showinfo("Success", f"Workflow exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export workflow: {e}")


def main():
    """Run workflow builder standalone"""
    app = WorkflowBuilder()
    app.window.mainloop()

if __name__ == "__main__":
    main()
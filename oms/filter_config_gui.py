"""
GUI for configuring filter patterns based on project structure.
Provides folder and extension selection with search functionality.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
from typing import Optional, List, Dict
from oms.project_scanner import ProjectScanner
from oms.local_db import LocalDB


class FilterConfigGUI:
    """GUI for configuring include/exclude filter patterns."""
    
    def __init__(self, project_root: str, db: LocalDB):
        """
        Initialize GUI.
        
        Args:
            project_root: Project root directory
            db: LocalDB instance for saving configurations
        """
        self.project_root = project_root
        self.db = db
        self.scanner = ProjectScanner(project_root)
        
        # Initialize scanner
        print("Scanning project structure...")
        self.scanner.scan(max_depth=10)
        print("Scan complete!")
        
        self.window = tk.Tk()
        self.window.title(f"Filter Configuration - {os.path.basename(project_root)}")
        self.window.geometry("1200x800")
        
        # Configuration variables
        self.current_config_name = tk.StringVar(value="default")
        self.filter_mode = tk.StringVar(value="exclude")  # exclude or include
        
        # Selection tracking
        self.selected_folders = set()
        self.selected_extensions = set()
        
        # Tree item tracking for folders
        self.folder_item_map = {}  # Maps folder path to tree item id
        self.item_folder_map = {}  # Maps tree item id to folder path
        
        self._create_widgets()
        self._load_existing_config()
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Top frame - Configuration selection
        top_frame = ttk.Frame(self.window, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Configuration:").pack(side=tk.LEFT, padx=5)
        
        self.config_combo = ttk.Combobox(top_frame, textvariable=self.current_config_name, width=30)
        self.config_combo.pack(side=tk.LEFT, padx=5)
        self._refresh_config_list()
        
        ttk.Button(top_frame, text="New Config", command=self._create_new_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Load", command=self._load_existing_config).pack(side=tk.LEFT, padx=5)
        
        # Filter mode selection
        ttk.Label(top_frame, text="Mode:").pack(side=tk.LEFT, padx=(20, 5))
        ttk.Radiobutton(top_frame, text="Skip (Exclude)", variable=self.filter_mode, 
                       value="exclude").pack(side=tk.LEFT)
        ttk.Radiobutton(top_frame, text="Include Only", variable=self.filter_mode, 
                       value="include").pack(side=tk.LEFT)
        
        # Main content frame - Notebook with tabs
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Folders tab
        folder_frame = ttk.Frame(notebook)
        notebook.add(folder_frame, text="Folders")
        self._create_folder_tab(folder_frame)
        
        # Extensions tab
        extension_frame = ttk.Frame(notebook)
        notebook.add(extension_frame, text="Extensions")
        self._create_extension_tab(extension_frame)
        
        # Preview tab
        preview_frame = ttk.Frame(notebook)
        notebook.add(preview_frame, text="Preview")
        self._create_preview_tab(preview_frame)
        
        # Bottom frame - Action buttons
        bottom_frame = ttk.Frame(self.window, padding="10")
        bottom_frame.pack(fill=tk.X)
        
        ttk.Button(bottom_frame, text="Save Configuration", 
                  command=self._save_configuration).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bottom_frame, text="Apply Filters", 
                  command=self._apply_filters).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bottom_frame, text="Clear Selection", 
                  command=self._clear_selection).pack(side=tk.RIGHT, padx=5)
    
    def _create_folder_tab(self, parent):
        """Create folder selection tab."""
        # Search frame
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.folder_search_var = tk.StringVar()
        self.folder_search_var.trace('w', lambda *args: self._filter_folders())
        search_entry = ttk.Entry(search_frame, textvariable=self.folder_search_var, width=50)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Selection buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Select All", 
                  command=self._select_all_folders).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Deselect All", 
                  command=self._deselect_all_folders).pack(side=tk.LEFT, padx=5)
        
        # Folder list with checkboxes
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(list_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview for folders
        self.folder_tree = ttk.Treeview(list_frame, 
                                        yscrollcommand=y_scrollbar.set,
                                        xscrollcommand=x_scrollbar.set)
        self.folder_tree.pack(fill=tk.BOTH, expand=True)
        
        y_scrollbar.config(command=self.folder_tree.yview)
        x_scrollbar.config(command=self.folder_tree.xview)
        
        # Configure columns
        self.folder_tree['columns'] = ('count',)
        self.folder_tree.heading('#0', text='Folder Path')
        self.folder_tree.heading('count', text='Files')
        self.folder_tree.column('count', width=100)
        
        # Bind checkbox toggle
        self.folder_tree.bind('<Button-1>', self._on_folder_click)
        
        # Populate folders
        self._populate_folders()
    
    def _create_extension_tab(self, parent):
        """Create extension selection tab."""
        # Selection buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Select All", 
                  command=self._select_all_extensions).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Deselect All", 
                  command=self._deselect_all_extensions).pack(side=tk.LEFT, padx=5)
        
        # Extension list with checkboxes
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview for extensions
        self.extension_tree = ttk.Treeview(list_frame, yscrollcommand=scrollbar.set)
        self.extension_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.extension_tree.yview)
        
        # Configure columns
        self.extension_tree['columns'] = ('count',)
        self.extension_tree.heading('#0', text='Extension')
        self.extension_tree.heading('count', text='File Count')
        self.extension_tree.column('count', width=150)
        
        # Bind checkbox toggle
        self.extension_tree.bind('<Button-1>', self._on_extension_click)
        
        # Populate extensions
        self._populate_extensions()
    
    def _create_preview_tab(self, parent):
        """Create preview tab showing filtered files."""
        # Stats frame
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="Click 'Preview' to see results")
        self.stats_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(stats_frame, text="Preview", 
                  command=self._update_preview).pack(side=tk.RIGHT, padx=5)
        
        # Preview text
        self.preview_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=30)
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def _populate_folders(self):
        """Populate folder tree with hierarchical structure."""
        # Clear existing items
        self.folder_tree.delete(*self.folder_tree.get_children())
        self.folder_item_map.clear()
        self.item_folder_map.clear()
        
        folder_stats = self.scanner.get_folder_stats()
        search_term = self.folder_search_var.get()
        
        # Get hierarchy
        hierarchy = self.scanner.get_folder_hierarchy(search_term)
        
        # Build tree recursively starting from root
        self._build_folder_tree('', '', hierarchy, folder_stats)
    
    def _build_folder_tree(self, parent_path: str, parent_item: str, 
                           hierarchy: Dict[str, List[str]], folder_stats: Dict[str, int]):
        """
        Recursively build folder tree.
        
        Args:
            parent_path: Parent folder path
            parent_item: Parent tree item id
            hierarchy: Folder hierarchy dictionary
            folder_stats: Folder statistics dictionary
        """
        if parent_path not in hierarchy:
            return
        
        # Get children for this parent
        children = sorted(hierarchy[parent_path])
        
        for folder in children:
            # Get just the folder name (not full path)
            folder_name = os.path.basename(folder)
            count = folder_stats.get(folder, 0)
            
            # Determine checkbox state
            checkbox = self._get_folder_checkbox_state(folder)
            
            # Insert into tree
            if parent_item:
                item_id = self.folder_tree.insert(parent_item, 'end', 
                                                  text=f'{checkbox} {folder_name}',
                                                  values=(count,), 
                                                  tags=(folder,))
            else:
                item_id = self.folder_tree.insert('', 'end', 
                                                  text=f'{checkbox} {folder_name}',
                                                  values=(count,), 
                                                  tags=(folder,))
            
            # Store mappings
            self.folder_item_map[folder] = item_id
            self.item_folder_map[item_id] = folder
            
            # Recursively add children
            self._build_folder_tree(folder, item_id, hierarchy, folder_stats)
    
    def _get_folder_checkbox_state(self, folder: str) -> str:
        """
        Get checkbox state for a folder (checked, unchecked, or partial).
        
        Args:
            folder: Folder path
            
        Returns:
            Checkbox character
        """
        if folder in self.selected_folders:
            return '☑'
        
        # Check if any children are selected (partial state)
        children = self.scanner.get_all_children(folder)
        if children and any(child in self.selected_folders for child in children):
            return '☐'  # Could use '◫' for partial, but keeping simple for now
        
        return '☐'
    
    def _populate_extensions(self):
        """Populate extension tree."""
        self.extension_tree.delete(*self.extension_tree.get_children())
        
        ext_stats = self.scanner.get_extension_stats()
        extensions = self.scanner.get_extensions()
        
        for ext in extensions:
            count = ext_stats.get(ext, 0)
            checkbox = '☑' if ext in self.selected_extensions else '☐'
            self.extension_tree.insert('', 'end', text=f'{checkbox} {ext}', 
                                      values=(count,), tags=(ext,))
    
    def _filter_folders(self):
        """Filter folder list based on search."""
        self._populate_folders()
    
    def _on_folder_click(self, event):
        """Handle folder checkbox click with parent-child selection."""
        item = self.folder_tree.identify('item', event.x, event.y)
        if item:
            tags = self.folder_tree.item(item, 'tags')
            if tags:
                folder = tags[0]
                
                # Toggle selection
                if folder in self.selected_folders:
                    # Deselect this folder and all children
                    self._deselect_folder_and_children(folder)
                else:
                    # Select this folder and all children
                    self._select_folder_and_children(folder)
                
                self._populate_folders()
    
    def _select_folder_and_children(self, folder: str):
        """
        Select a folder and all its children.
        
        Args:
            folder: Folder path to select
        """
        # Select the folder
        self.selected_folders.add(folder)
        
        # Select all children
        children = self.scanner.get_all_children(folder)
        for child in children:
            self.selected_folders.add(child)
    
    def _deselect_folder_and_children(self, folder: str):
        """
        Deselect a folder and all its children.
        
        Args:
            folder: Folder path to deselect
        """
        # Deselect the folder
        self.selected_folders.discard(folder)
        
        # Deselect all children
        children = self.scanner.get_all_children(folder)
        for child in children:
            self.selected_folders.discard(child)
    
    def _on_extension_click(self, event):
        """Handle extension checkbox click."""
        item = self.extension_tree.identify('item', event.x, event.y)
        if item:
            tags = self.extension_tree.item(item, 'tags')
            if tags:
                ext = tags[0]
                if ext in self.selected_extensions:
                    self.selected_extensions.remove(ext)
                else:
                    self.selected_extensions.add(ext)
                self._populate_extensions()
    
    def _select_all_folders(self):
        """Select all folders."""
        search_term = self.folder_search_var.get()
        folders = self.scanner.get_folders(search_term)
        self.selected_folders.update(folders)
        self._populate_folders()
    
    def _deselect_all_folders(self):
        """Deselect all folders."""
        self.selected_folders.clear()
        self._populate_folders()
    
    def _select_all_extensions(self):
        """Select all extensions."""
        self.selected_extensions.update(self.scanner.get_extensions())
        self._populate_extensions()
    
    def _deselect_all_extensions(self):
        """Deselect all extensions."""
        self.selected_extensions.clear()
        self._populate_extensions()
    
    def _clear_selection(self):
        """Clear all selections."""
        self.selected_folders.clear()
        self.selected_extensions.clear()
        self._populate_folders()
        self._populate_extensions()
    
    def _update_preview(self):
        """Update preview of filtered files."""
        # Generate patterns
        folder_patterns = self.scanner.generate_folder_patterns(
            list(self.selected_folders), self.filter_mode.get())
        ext_patterns = self.scanner.generate_extension_patterns(
            list(self.selected_extensions), self.filter_mode.get())
        
        all_patterns = folder_patterns + ext_patterns
        
        if self.filter_mode.get() == 'exclude':
            include_patterns = []
            exclude_patterns = all_patterns
        else:
            include_patterns = all_patterns
            exclude_patterns = []
        
        # Preview
        result = self.scanner.preview_filter(include_patterns, exclude_patterns)
        
        # Update stats
        included_count = len(result['included'])
        excluded_count = len(result['excluded'])
        total = result['total']
        
        self.stats_label.config(
            text=f"Total: {total} files | Included: {included_count} | Excluded: {excluded_count}")
        
        # Update preview text
        self.preview_text.delete('1.0', tk.END)
        
        self.preview_text.insert(tk.END, "=== INCLUDED FILES ===\n", 'header')
        for file in result['included'][:100]:  # Show first 100
            self.preview_text.insert(tk.END, f"  ✓ {file}\n")
        if len(result['included']) > 100:
            self.preview_text.insert(tk.END, f"\n  ... and {len(result['included']) - 100} more\n")
        
        self.preview_text.insert(tk.END, "\n=== EXCLUDED FILES ===\n", 'header')
        for file in result['excluded'][:100]:  # Show first 100
            self.preview_text.insert(tk.END, f"  ✗ {file}\n")
        if len(result['excluded']) > 100:
            self.preview_text.insert(tk.END, f"\n  ... and {len(result['excluded']) - 100} more\n")
        
        self.preview_text.tag_config('header', font=('TkDefaultFont', 10, 'bold'))
    
    def _refresh_config_list(self):
        """Refresh the list of available configurations."""
        configs = self.db.list_filter_configs()
        config_names = [c['name'] for c in configs]
        self.config_combo['values'] = config_names
        if config_names and not self.current_config_name.get():
            self.current_config_name.set(config_names[0])
    
    def _create_new_config(self):
        """Create a new filter configuration."""
        dialog = tk.Toplevel(self.window)
        dialog.title("New Configuration")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="Configuration Name:").pack(pady=10)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=40).pack(pady=5)
        
        ttk.Label(dialog, text="Description:").pack(pady=10)
        desc_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=desc_var, width=40).pack(pady=5)
        
        def create():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter a configuration name")
                return
            
            try:
                self.db.create_filter_config(name, desc_var.get())
                self._refresh_config_list()
                self.current_config_name.set(name)
                dialog.destroy()
                messagebox.showinfo("Success", f"Configuration '{name}' created")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create configuration: {e}")
        
        ttk.Button(dialog, text="Create", command=create).pack(pady=20)
    
    def _load_existing_config(self):
        """Load existing configuration patterns."""
        config_name = self.current_config_name.get()
        if not config_name:
            return
        
        config_id = self.db.get_filter_config_id(config_name)
        if not config_id:
            return
        
        # Get patterns for this config
        patterns = self.db.get_patterns_for_config(config_id)
        
        # Parse patterns to determine selections
        self.selected_folders.clear()
        self.selected_extensions.clear()
        
        # Analyze exclude patterns
        for pattern in patterns.get('exclude', []):
            if pattern.startswith('**/') and pattern.endswith('/**'):
                # Folder pattern
                folder = pattern[3:-3]
                if folder in self.scanner.get_folders():
                    self.selected_folders.add(folder)
            elif pattern.startswith('**/*'):
                # Extension pattern
                ext = pattern[4:]
                if ext in self.scanner.get_extensions():
                    self.selected_extensions.add(ext)
        
        # Analyze include patterns
        for pattern in patterns.get('include', []):
            if pattern.startswith('**/') and pattern.endswith('/**'):
                folder = pattern[3:-3]
                if folder in self.scanner.get_folders():
                    self.selected_folders.add(folder)
            elif pattern.startswith('**/*'):
                ext = pattern[4:]
                if ext in self.scanner.get_extensions():
                    self.selected_extensions.add(ext)
        
        # Update UI
        self._populate_folders()
        self._populate_extensions()
        
        messagebox.showinfo("Loaded", f"Configuration '{config_name}' loaded")
    
    def _save_configuration(self):
        """Save current configuration."""
        config_name = self.current_config_name.get()
        if not config_name:
            messagebox.showerror("Error", "Please select or create a configuration")
            return
        
        config_id = self.db.get_filter_config_id(config_name)
        if not config_id:
            messagebox.showerror("Error", f"Configuration '{config_name}' not found")
            return
        
        # Generate patterns
        folder_patterns = self.scanner.generate_folder_patterns(
            list(self.selected_folders), self.filter_mode.get())
        ext_patterns = self.scanner.generate_extension_patterns(
            list(self.selected_extensions), self.filter_mode.get())
        
        # Clear existing patterns for this config
        cursor = self.db.conn.cursor()
        cursor.execute("DELETE FROM filter_patterns WHERE config_set_id = ?", (config_id,))
        
        # Add new patterns
        filter_type = self.filter_mode.get()
        for pattern in folder_patterns:
            self.db.add_pattern_to_config(config_id, pattern, filter_type, 'folder')
        for pattern in ext_patterns:
            self.db.add_pattern_to_config(config_id, pattern, filter_type, 'extension')
        
        messagebox.showinfo("Saved", f"Configuration '{config_name}' saved successfully")
    
    def _apply_filters(self):
        """Apply filters and close window."""
        self._save_configuration()
        config_name = self.current_config_name.get()
        self.db.set_active_filter_config(config_name)
        messagebox.showinfo("Applied", f"Configuration '{config_name}' is now active")
    
    def run(self):
        """Run the GUI."""
        self.window.mainloop()


def launch_filter_gui(project_root: str, db: LocalDB):
    """
    Launch the filter configuration GUI.
    
    Args:
        project_root: Project root directory
        db: LocalDB instance
    """
    gui = FilterConfigGUI(project_root, db)
    gui.run()

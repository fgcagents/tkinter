"""
Widget personalitzat per mostrar taules de dades amb Treeview
"""
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Optional, Callable
import config


class DataTable(ttk.Frame):
    """Taula de dades amb funcionalitats avançades"""
    
    def __init__(self, parent, columns: List[Dict], 
                 show_scrollbars=True,
                 selectable=True,
                 on_select: Optional[Callable] = None,
                 **kwargs):
        """
        Inicialitza la taula
        
        Args:
            parent: Widget pare
            columns: Llista de diccionaris amb configuració de columnes
                     Format: [{'id': 'col1', 'text': 'Columna 1', 'width': 100}, ...]
            show_scrollbars: Mostrar barres de desplaçament
            selectable: Permetre selecció de files
            on_select: Callback quan es selecciona una fila
        """
        super().__init__(parent, **kwargs)
        
        self.columns = columns
        self.on_select_callback = on_select
        self.data = []
        
        # Frame per la taula i scrollbars
        self.tree_frame = ttk.Frame(self)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        if show_scrollbars:
            self.vsb = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL)
            self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.hsb = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL)
            self.hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        column_ids = [col['id'] for col in columns]
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=column_ids,
            show='headings',
            selectmode='browse' if selectable else 'none'
        )
        
        if show_scrollbars:
            self.tree.configure(
                yscrollcommand=self.vsb.set,
                xscrollcommand=self.hsb.set
            )
            self.vsb.configure(command=self.tree.yview)
            self.hsb.configure(command=self.tree.xview)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Configurar columnes
        for col in columns:
            col_id = col['id']
            col_text = col['text']
            col_width = col.get('width', 100)
            col_anchor = col.get('anchor', tk.W)
            
            self.tree.heading(col_id, text=col_text, 
                            command=lambda c=col_id: self._sort_by_column(c))
            self.tree.column(col_id, width=col_width, anchor=col_anchor)
        
        # Bind events
        if selectable and on_select:
            self.tree.bind('<<TreeviewSelect>>', self._on_select)
        
        # Colors alternats per files
        self.tree.tag_configure('oddrow', background='white')
        self.tree.tag_configure('evenrow', background='#f0f0f0')
    
    def _sort_by_column(self, col_id: str):
        """Ordena la taula per una columna"""
        items = [(self.tree.set(item, col_id), item) for item in self.tree.get_children('')]
        items.sort()
        
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)
    
    def _on_select(self, event):
        """Callback quan es selecciona una fila"""
        selection = self.tree.selection()
        if selection and self.on_select_callback:
            item_id = selection[0]
            values = self.tree.item(item_id, 'values')
            
            # Crear diccionari amb els valors
            row_data = {}
            for idx, col in enumerate(self.columns):
                if idx < len(values):
                    row_data[col['id']] = values[idx]
            
            self.on_select_callback(row_data)
    
    def insert_row(self, values: Dict, tags=None):
        """
        Insereix una fila a la taula
        
        Args:
            values: Diccionari amb valors per cada columna
            tags: Tags per aplicar a la fila
        """
        row_values = []
        for col in self.columns:
            col_id = col['id']
            row_values.append(values.get(col_id, ''))
        
        if tags is None:
            # Tag alternat
            row_count = len(self.tree.get_children())
            tags = ('evenrow',) if row_count % 2 == 0 else ('oddrow',)
        
        self.tree.insert('', tk.END, values=row_values, tags=tags)
    
    def load_data(self, data: List[Dict]):
        """
        Carrega dades a la taula
        
        Args:
            data: Llista de diccionaris amb dades
        """
        self.clear()
        self.data = data
        
        for row in data:
            self.insert_row(row)
    
    def clear(self):
        """Neteja totes les files de la taula"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.data = []
    
    def get_selected(self) -> Optional[Dict]:
        """
        Retorna la fila seleccionada
        
        Returns:
            Diccionari amb dades de la fila o None
        """
        selection = self.tree.selection()
        if not selection:
            return None
        
        item_id = selection[0]
        values = self.tree.item(item_id, 'values')
        
        row_data = {}
        for idx, col in enumerate(self.columns):
            if idx < len(values):
                row_data[col['id']] = values[idx]
        
        return row_data
    
    def get_all_data(self) -> List[Dict]:
        """Retorna totes les dades de la taula"""
        return self.data.copy()
    
    def update_row(self, item_id: str, values: Dict):
        """Actualitza una fila existent"""
        row_values = []
        for col in self.columns:
            col_id = col['id']
            row_values.append(values.get(col_id, ''))
        
        self.tree.item(item_id, values=row_values)
    
    def highlight_row(self, condition: Callable):
        """
        Ressalta files que compleixin una condició
        
        Args:
            condition: Funció que rep un diccionari i retorna bool
        """
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            
            row_data = {}
            for idx, col in enumerate(self.columns):
                if idx < len(values):
                    row_data[col['id']] = values[idx]
            
            if condition(row_data):
                self.tree.item(item, tags=('highlight',))
        
        self.tree.tag_configure('highlight', background=config.COLORS['warning'])

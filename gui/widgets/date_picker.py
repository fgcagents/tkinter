"""
Widget personalitzat per seleccionar dates
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, date
from tkcalendar import Calendar, DateEntry
import config


class DatePicker(ttk.Frame):
    """Widget per seleccionar una data amb calendari"""
    
    def __init__(self, parent, label_text="Data:", default_date=None, **kwargs):
        """
        Inicialitza el DatePicker
        
        Args:
            parent: Widget pare
            label_text: Text de l'etiqueta
            default_date: Data per defecte (si None, usa avui)
        """
        super().__init__(parent, **kwargs)
        
        self.selected_date = default_date or date.today()
        
        # Label
        self.label = ttk.Label(self, text=label_text)
        self.label.pack(side=tk.LEFT, padx=(0, 5))
        
        # DateEntry amb calendari
        self.date_entry = DateEntry(
            self,
            width=12,
            background=config.COLORS['primary'],
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy',
            locale='ca_ES'
        )
        self.date_entry.set_date(self.selected_date)
        self.date_entry.pack(side=tk.LEFT)
        
        # Bind event
        self.date_entry.bind('<<DateEntrySelected>>', self._on_date_selected)
    
    def _on_date_selected(self, event=None):
        """Callback quan es selecciona una data"""
        self.selected_date = self.date_entry.get_date()
    
    def get_date(self) -> date:
        """Retorna la data seleccionada"""
        return self.date_entry.get_date()
    
    def set_date(self, new_date: date):
        """Estableix una nova data"""
        self.date_entry.set_date(new_date)
        self.selected_date = new_date


class DateRangePicker(ttk.Frame):
    """Widget per seleccionar un rang de dates"""
    
    def __init__(self, parent, **kwargs):
        """Inicialitza el DateRangePicker"""
        super().__init__(parent, **kwargs)
        
        # Data inici
        self.date_inici_frame = ttk.Frame(self)
        self.date_inici_frame.pack(side=tk.LEFT, padx=5)
        
        self.date_inici_picker = DatePicker(
            self.date_inici_frame,
            label_text="Data inici:",
            default_date=date.today()
        )
        self.date_inici_picker.pack()
        
        # Separador
        ttk.Label(self, text="→").pack(side=tk.LEFT, padx=5)
        
        # Data fi
        self.date_fi_frame = ttk.Frame(self)
        self.date_fi_frame.pack(side=tk.LEFT, padx=5)
        
        self.date_fi_picker = DatePicker(
            self.date_fi_frame,
            label_text="Data fi:",
            default_date=date.today()
        )
        self.date_fi_picker.pack()
    
    def get_date_range(self) -> tuple:
        """
        Retorna el rang de dates seleccionat
        
        Returns:
            Tuple (data_inici, data_fi)
        """
        return (
            self.date_inici_picker.get_date(),
            self.date_fi_picker.get_date()
        )
    
    def set_date_range(self, data_inici: date, data_fi: date):
        """Estableix el rang de dates"""
        self.date_inici_picker.set_date(data_inici)
        self.date_fi_picker.set_date(data_fi)
    
    def validate(self) -> tuple:
        """
        Valida que el rang sigui correcte
        
        Returns:
            Tuple (es_valid, missatge_error)
        """
        data_inici, data_fi = self.get_date_range()
        
        if data_inici > data_fi:
            return False, "La data d'inici ha de ser anterior a la data fi"
        
        dies = (data_fi - data_inici).days + 1
        if dies > 365:
            return False, "El rang no pot superar 365 dies"
        
        return True, ""

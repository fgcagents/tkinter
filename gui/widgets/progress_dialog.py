"""
Diàleg modal per mostrar progrés de tasques llargues
"""
import tkinter as tk
from tkinter import ttk
import config


class ProgressDialog(tk.Toplevel):
    """Finestra modal per mostrar progrés"""
    
    def __init__(self, parent, title="Processant...", cancelable=False):
        """
        Inicialitza el diàleg de progrés
        
        Args:
            parent: Finestra pare
            title: Títol del diàleg
            cancelable: Permetre cancel·lar
        """
        super().__init__(parent)
        
        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)
        
        # Centrar en pantalla
        self.transient(parent)
        self.grab_set()
        
        self.cancelled = False
        
        # Frame principal
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Títol
        self.title_label = ttk.Label(
            main_frame,
            text=title,
            style='Title.TLabel'
        )
        self.title_label.pack(pady=(0, 10))
        
        # Missatge de progrés
        self.message_label = ttk.Label(
            main_frame,
            text="Iniciant...",
            style='Info.TLabel'
        )
        self.message_label.pack(pady=(0, 10))
        
        # Barra de progrés
        self.progress_var = tk.IntVar()
        self.progressbar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            length=350
        )
        self.progressbar.pack(pady=(0, 10))
        
        # Percentatge
        self.percent_label = ttk.Label(
            main_frame,
            text="0%",
            style='Info.TLabel'
        )
        self.percent_label.pack()
        
        # Botó cancel·lar
        if cancelable:
            self.cancel_button = ttk.Button(
                main_frame,
                text="Cancel·lar",
                command=self._on_cancel,
                style='Danger.TButton'
            )
            self.cancel_button.pack(pady=(10, 0))
        
        # Protocol de tancament
        self.protocol("WM_DELETE_WINDOW", self._on_cancel if cancelable else lambda: None)
        
        # Centrar
        self._center_window()
    
    def _center_window(self):
        """Centra la finestra en pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _on_cancel(self):
        """Callback quan es cancel·la"""
        self.cancelled = True
        self.destroy()
    
    def update_progress(self, percent: int, message: str = None):
        """
        Actualitza el progrés
        
        Args:
            percent: Percentatge (0-100)
            message: Missatge opcional
        """
        self.progress_var.set(percent)
        self.percent_label.config(text=f"{percent}%")
        
        if message:
            self.message_label.config(text=message)
        
        self.update()
    
    def is_cancelled(self) -> bool:
        """Retorna si s'ha cancel·lat"""
        return self.cancelled
    
    def close(self):
        """Tanca el diàleg"""
        self.destroy()

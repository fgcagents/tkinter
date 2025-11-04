"""
Configuració d'estils i tema visual per a l'aplicació
"""
import tkinter as tk
from tkinter import ttk
import config


class AppStyles:
    """Gestiona els estils visuals de l'aplicació"""
    
    @staticmethod
    def configure_styles():
        """Configura els estils globals de ttk"""
        style = ttk.Style()
        
        # Tema base
        try:
            style.theme_use('clam')  # Tema modern
        except:
            pass  # Si no està disponible, usa el per defecte
        
        # Colors
        colors = config.COLORS
        
        # ====================================================================
        # ESTILS DE BUTTONS
        # ====================================================================
        
        # Botó primari
        style.configure(
            'Primary.TButton',
            background=colors['primary'],
            foreground='white',
            borderwidth=0,
            focuscolor='none',
            padding=(10, 5)
        )
        style.map('Primary.TButton',
            background=[('active', colors['primary']), ('pressed', colors['primary'])]
        )
        
        # Botó de perill
        style.configure(
            'Danger.TButton',
            background=colors['danger'],
            foreground='white',
            borderwidth=0,
            focuscolor='none',
            padding=(10, 5)
        )
        style.map('Danger.TButton',
            background=[('active', colors['danger']), ('pressed', colors['danger'])]
        )
        
        # Botó d'èxit
        style.configure(
            'Success.TButton',
            background=colors['success'],
            foreground='white',
            borderwidth=0,
            focuscolor='none',
            padding=(10, 5)
        )
        
        # ====================================================================
        # ESTILS DE LABELS
        # ====================================================================
        
        style.configure(
            'Title.TLabel',
            font=('Segoe UI', 14, 'bold'),
            foreground=colors['text']
        )
        
        style.configure(
            'Subtitle.TLabel',
            font=('Segoe UI', 11, 'bold'),
            foreground=colors['info']
        )
        
        style.configure(
            'Info.TLabel',
            font=('Segoe UI', 9),
            foreground=colors['info']
        )
        
        # ====================================================================
        # ESTILS DE FRAMES
        # ====================================================================
        
        style.configure(
            'Card.TFrame',
            background=colors['light'],
            relief='raised',
            borderwidth=1
        )
        
        # ====================================================================
        # ESTILS DE NOTEBOOK (PESTANYES)
        # ====================================================================
        
        style.configure(
            'TNotebook',
            background=colors['background'],
            borderwidth=0
        )
        
        style.configure(
            'TNotebook.Tab',
            padding=(20, 10),
            font=('Segoe UI', 10)
        )
        
        # ====================================================================
        # TREEVIEW (TAULES)
        # ====================================================================
        
        style.configure(
            'Treeview',
            background='white',
            foreground=colors['text'],
            fieldbackground='white',
            rowheight=25
        )
        
        style.configure(
            'Treeview.Heading',
            font=('Segoe UI', 10, 'bold'),
            background=colors['light'],
            foreground=colors['text']
        )
        
        style.map('Treeview',
            background=[('selected', colors['primary'])],
            foreground=[('selected', 'white')]
        )
        
        # ====================================================================
        # PROGRESSBAR
        # ====================================================================
        
        style.configure(
            'TProgressbar',
            troughcolor=colors['light'],
            background=colors['primary'],
            thickness=20
        )
        
        return style


class Colors:
    """Classe auxiliar per accedir fàcilment als colors"""
    
    def __init__(self):
        self.primary = config.COLORS['primary']
        self.secondary = config.COLORS['secondary']
        self.success = config.COLORS['success']
        self.warning = config.COLORS['warning']
        self.danger = config.COLORS['danger']
        self.info = config.COLORS['info']
        self.light = config.COLORS['light']
        self.dark = config.COLORS['dark']
        self.background = config.COLORS['background']
        self.text = config.COLORS['text']

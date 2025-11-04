"""
Finestra principal de l'aplicació amb pestanyes
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from models.database import DatabaseManager
from controllers.descansos_controller import DescansosController
from controllers.disponibilitat_controller import DisponibilitatController
from controllers.genetic_controller import GeneticController
from gui.styles import AppStyles
from gui.views.descansos_view import DescansosView
from gui.views.disponibilitat_view import DisponibilitatView
from gui.views.genetic_view import GeneticView
from gui.views.estadistiques_view import EstadistiquesView
import config

logger = logging.getLogger(__name__)


class MainWindow(tk.Tk):
    """Finestra principal de l'aplicació"""
    
    def __init__(self):
        """Inicialitza la finestra principal"""
        super().__init__()
        
        # Configuració de la finestra
        self.title(config.WINDOW_TITLE)
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.minsize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
        
        # Aplicar estils
        AppStyles.configure_styles()
        
        # Inicialitzar base de dades i controllers
        self._init_controllers()
        
        # Crear interfície
        self._create_ui()
        
        # Protocol de tancament
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Verificar connexió a BD
        self._check_database()
        
        logger.info("MainWindow inicialitzada")
    
    def _init_controllers(self):
        """Inicialitza els controllers"""
        try:
            self.db_manager = DatabaseManager(str(config.DB_PATH))
            self.descansos_controller = DescansosController(self.db_manager)
            self.disponibilitat_controller = DisponibilitatController(self.db_manager)
            self.genetic_controller = GeneticController(self.db_manager)
            logger.info("Controllers inicialitzats correctament")
        except Exception as e:
            logger.error(f"Error inicialitzant controllers: {e}")
            messagebox.showerror("Error", f"Error inicialitzant l'aplicació:\n{e}")
            self.quit()
    
    def _create_ui(self):
        """Crea la interfície d'usuari"""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Capçalera
        self._create_header(main_frame)
        
        # Notebook amb pestanyes
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Crear pestanyes
        self._create_tabs()
        
        # Barra d'estat
        self._create_status_bar(main_frame)
    
    def _create_header(self, parent):
        """Crea la capçalera de l'aplicació"""
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Títol
        title_label = ttk.Label(
            header_frame,
            text="🚇 Gestor de Treballadors",
            style='Title.TLabel'
        )
        title_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Informació de BD
        db_info = ttk.Label(
            header_frame,
            text=f"BD: {config.DB_PATH.name}",
            style='Info.TLabel'
        )
        db_info.pack(side=tk.RIGHT, padx=10)
    
    def _create_tabs(self):
        """Crea les pestanyes principals"""
        # Pestanya 1: Gestió de Descansos
        self.descansos_view = DescansosView(
            self.notebook,
            self.descansos_controller
        )
        self.notebook.add(self.descansos_view, text="📅 Descansos")
        
        # Pestanya 2: Disponibilitat de Serveis
        self.disponibilitat_view = DisponibilitatView(
            self.notebook,
            self.disponibilitat_controller
        )
        self.notebook.add(self.disponibilitat_view, text="🔍 Disponibilitat")
        
        # Pestanya 3: Algorisme Genètic
        self.genetic_view = GeneticView(
            self.notebook,
            self.genetic_controller
        )
        self.notebook.add(self.genetic_view, text="🧬 Algorisme Genètic")
        
        # Pestanya 4: Estadístiques
        self.estadistiques_view = EstadistiquesView(
            self.notebook,
            self.descansos_controller,
            self.genetic_controller
        )
        self.notebook.add(self.estadistiques_view, text="📊 Estadístiques")
    
    def _create_status_bar(self, parent):
        """Crea la barra d'estat"""
        self.status_bar = ttk.Frame(parent, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(
            self.status_bar,
            text="Llest",
            style='Info.TLabel'
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
    
    def _check_database(self):
        """Verifica la connexió a la base de dades"""
        try:
            if self.db_manager.test_connection():
                self.set_status("✅ Connexió a BD correcta")
                logger.info("Connexió a BD verificada")
            else:
                self.set_status("❌ Error de connexió a BD")
                messagebox.showerror(
                    "Error",
                    config.MESSAGES['db_connection_error']
                )
        except Exception as e:
            logger.error(f"Error verificant BD: {e}")
            self.set_status("❌ Error de connexió")
            messagebox.showerror("Error", f"Error de connexió:\n{e}")
    
    def set_status(self, message: str):
        """
        Estableix el missatge de la barra d'estat
        
        Args:
            message: Missatge a mostrar
        """
        self.status_label.config(text=message)
        self.update_idletasks()
    
    def _on_closing(self):
        """Callback quan es tanca l'aplicació"""
        # Verificar si hi ha processos en execució
        if self.genetic_controller.is_running():
            result = messagebox.askyesno(
                "Confirmar tancament",
                "L'algorisme genètic s'està executant.\n"
                "Vols tancar igualment?"
            )
            if not result:
                return
            
            self.genetic_controller.cancel_lar_execucio()
        
        logger.info("Tancant aplicació")
        self.quit()

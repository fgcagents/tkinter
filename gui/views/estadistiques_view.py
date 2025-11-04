"""
Vista per visualitzar estadístiques
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import logging
from gui.widgets.data_table import DataTable
import config

logger = logging.getLogger(__name__)


class EstadistiquesView(ttk.Frame):
    """Vista d'estadístiques i reports"""
    
    def __init__(self, parent, descansos_controller, genetic_controller):
        """
        Inicialitza la vista
        
        Args:
            parent: Widget pare
            descansos_controller: Controller de descansos
            genetic_controller: Controller genètic
        """
        super().__init__(parent)
        self.descansos_controller = descansos_controller
        self.genetic_controller = genetic_controller
        
        self._create_ui()
        logger.info("EstadistiquesView inicialitzada")
    
    def _create_ui(self):
        """Crea la interfície"""
        main_container = ttk.Frame(self, padding=10)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Notebook amb diferents tipus d'estadístiques
        self.stats_notebook = ttk.Notebook(main_container)
        self.stats_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestanya 1: Estadístiques de Descansos
        self.descansos_tab = ttk.Frame(self.stats_notebook)
        self.stats_notebook.add(self.descansos_tab, text="Descansos")
        self._create_descansos_stats(self.descansos_tab)
        
        # Pestanya 2: Estadístiques d'Assignacions
        self.assignacions_tab = ttk.Frame(self.stats_notebook)
        self.stats_notebook.add(self.assignacions_tab, text="Assignacions")
        self._create_assignacions_stats(self.assignacions_tab)
        
        # Pestanya 3: Baixes Actives
        self.baixes_tab = ttk.Frame(self.stats_notebook)
        self.stats_notebook.add(self.baixes_tab, text="Baixes Actives")
        self._create_baixes_stats(self.baixes_tab)
    
    def _create_descansos_stats(self, parent):
        """Crea estadístiques de descansos"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Controls
        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(controls_frame, text="Any:", style='Subtitle.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        
        self.descansos_year_var = tk.IntVar(value=datetime.now().year)
        ttk.Spinbox(
            controls_frame,
            from_=2020,
            to=2030,
            textvariable=self.descansos_year_var,
            width=10
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            controls_frame,
            text="🔄 Actualitzar",
            command=self._load_descansos_stats,
            style='Primary.TButton'
        ).pack(side=tk.LEFT)
        
        # Resum global
        summary_frame = ttk.LabelFrame(frame, text="Resum Global", padding=10)
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.descansos_summary = ttk.Label(
            summary_frame,
            text="Selecciona un any i actualitza",
            style='Info.TLabel',
            justify=tk.LEFT
        )
        self.descansos_summary.pack(anchor=tk.W)
        
        # Taula de descansos per treballador
        table_frame = ttk.LabelFrame(frame, text="Descansos per Treballador", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = [
            {'id': 'treballador', 'text': 'Treballador', 'width': 150},
            {'id': 'total_descansos', 'text': 'Total', 'width': 80, 'anchor': tk.CENTER},
            {'id': 'base', 'text': 'Base', 'width': 70, 'anchor': tk.CENTER},
            {'id': 'temporal', 'text': 'Temporal', 'width': 70, 'anchor': tk.CENTER},
            {'id': 'baixa', 'text': 'Baixa', 'width': 70, 'anchor': tk.CENTER},
            {'id': 'manual', 'text': 'Manual', 'width': 70, 'anchor': tk.CENTER}
        ]
        
        self.descansos_table = DataTable(table_frame, columns=columns)
        self.descansos_table.pack(fill=tk.BOTH, expand=True)
        
        # Carregar estadístiques inicials
        self._load_descansos_stats()
    
    def _create_assignacions_stats(self, parent):
        """Crea estadístiques d'assignacions"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Controls
        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            controls_frame,
            text="🔄 Actualitzar",
            command=self._load_assignacions_stats,
            style='Primary.TButton'
        ).pack(side=tk.LEFT)
        
        # Resum global
        summary_frame = ttk.LabelFrame(frame, text="Resum d'Assignacions", padding=10)
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.assignacions_summary = tk.Text(
            summary_frame,
            height=6,
            wrap=tk.WORD,
            font=('Segoe UI', 10),
            state='disabled'
        )
        self.assignacions_summary.pack(fill=tk.X)
        
        # Gràfic conceptual (text)
        chart_frame = ttk.LabelFrame(frame, text="Distribució", padding=10)
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        self.assignacions_chart = tk.Text(
            chart_frame,
            height=15,
            wrap=tk.WORD,
            font=('Courier', 9),
            state='disabled'
        )
        self.assignacions_chart.pack(fill=tk.BOTH, expand=True)
        
        # Carregar estadístiques inicials
        self._load_assignacions_stats()
    
    def _create_baixes_stats(self, parent):
        """Crea vista de baixes actives"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Controls
        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            controls_frame,
            text="⚠️ Baixes llargues actives o futures",
            style='Subtitle.TLabel'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            controls_frame,
            text="🔄 Actualitzar",
            command=self._load_baixes_stats,
            style='Primary.TButton'
        ).pack(side=tk.LEFT)
        
        # Taula de baixes
        table_frame = ttk.LabelFrame(frame, text="Baixes Pendents", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = [
            {'id': 'treballador', 'text': 'Treballador', 'width': 150},
            {'id': 'plaza', 'text': 'Plaça', 'width': 80},
            {'id': 'data_inici', 'text': 'Inici', 'width': 100},
            {'id': 'data_fi', 'text': 'Fi', 'width': 100},
            {'id': 'dies_totals', 'text': 'Dies', 'width': 70, 'anchor': tk.CENTER},
            {'id': 'motiu', 'text': 'Motiu', 'width': 200}
        ]
        
        self.baixes_table = DataTable(table_frame, columns=columns)
        self.baixes_table.pack(fill=tk.BOTH, expand=True)
        
        # Missatge informatiu
        info_label = ttk.Label(
            frame,
            text="💡 Aquestes baixes poden afectar la planificació futura",
            style='Info.TLabel'
        )
        info_label.pack(pady=(10, 0))
        
        # Carregar baixes
        self._load_baixes_stats()
    
    # ========================================================================
    # CÀRREGA DE DADES
    # ========================================================================
    
    def _load_descansos_stats(self):
        """Carrega estadístiques de descansos"""
        try:
            any = self.descansos_year_var.get()
            stats = self.descansos_controller.get_estadistiques_descansos(any)
            
            if 'error' in stats:
                messagebox.showerror("Error", stats['error'])
                return
            
            # Actualitzar resum
            summary_text = (
                f"Any: {stats['any']}\n"
                f"Treballadors amb descansos: {stats['total_treballadors']}\n"
                f"Total descansos registrats: {stats['total_descansos']}"
            )
            self.descansos_summary.config(text=summary_text)
            
            # Carregar taula
            self.descansos_table.load_data(stats['descansos_per_treballador'])
            
            # Ressaltar treballadors amb molts descansos
            self.descansos_table.highlight_row(
                lambda row: int(row.get('total_descansos', 0)) > config.MAX_DESCANSOS_ANY
            )
            
        except Exception as e:
            logger.error(f"Error carregant estadístiques descansos: {e}")
            messagebox.showerror("Error", f"Error:\n{e}")
    
    def _load_assignacions_stats(self):
        """Carrega estadístiques d'assignacions"""
        try:
            stats = self.genetic_controller.get_estadistiques_assignacions()
            
            if not stats:
                self.assignacions_summary.config(state='normal')
                self.assignacions_summary.delete('1.0', tk.END)
                self.assignacions_summary.insert('1.0', "No hi ha assignacions registrades")
                self.assignacions_summary.config(state='disabled')
                return
            
            # Actualitzar resum
            self.assignacions_summary.config(state='normal')
            self.assignacions_summary.delete('1.0', tk.END)
            
            summary = (
                f"📊 Estadístiques d'Assignacions\n\n"
                f"Total assignacions: {stats.get('total_assignacions', 0)}\n"
                f"Treballadors assignats: {stats.get('treballadors_assignats', 0)}\n"
                f"Dies coberts: {stats.get('dies_coberts', 0)}\n"
                f"Serveis coberts: {stats.get('serveis_coberts', 0)}\n"
            )
            
            self.assignacions_summary.insert('1.0', summary)
            self.assignacions_summary.config(state='disabled')
            
            # Gràfic simple (ASCII art conceptual)
            self._draw_simple_chart(stats)
            
        except Exception as e:
            logger.error(f"Error carregant estadístiques assignacions: {e}")
            messagebox.showerror("Error", f"Error:\n{e}")
    
    def _draw_simple_chart(self, stats):
        """Dibuixa un gràfic simple amb ASCII"""
        self.assignacions_chart.config(state='normal')
        self.assignacions_chart.delete('1.0', tk.END)
        
        total = stats.get('total_assignacions', 0)
        treballadors = stats.get('treballadors_assignats', 0)
        dies = stats.get('dies_coberts', 0)
        serveis = stats.get('serveis_coberts', 0)
        
        if total > 0:
            chart_text = (
                "Visualització de Dades:\n\n"
                f"Assignacions:  {'█' * min(50, total // 10)}\n"
                f"               ({total})\n\n"
                f"Treballadors:  {'█' * min(50, treballadors * 5)}\n"
                f"               ({treballadors})\n\n"
                f"Dies:          {'█' * min(50, dies // 2)}\n"
                f"               ({dies})\n\n"
                f"Serveis:       {'█' * min(50, serveis)}\n"
                f"               ({serveis})\n"
            )
        else:
            chart_text = "No hi ha dades per visualitzar"
        
        self.assignacions_chart.insert('1.0', chart_text)
        self.assignacions_chart.config(state='disabled')
    
    def _load_baixes_stats(self):
        """Carrega baixes actives"""
        try:
            baixes = self.descansos_controller.alertar_baixes_pendents()
            
            if not baixes:
                messagebox.showinfo("Info", "No hi ha baixes pendents")
                self.baixes_table.clear()
                return
            
            # Formatació de dates
            for baixa in baixes:
                baixa['data_inici'] = baixa['data_inici'].strftime(config.DATE_FORMAT_DISPLAY)
                baixa['data_fi'] = baixa['data_fi'].strftime(config.DATE_FORMAT_DISPLAY)
            
            self.baixes_table.load_data(baixes)
            
            # Missatge si hi ha baixes
            if len(baixes) > 0:
                messagebox.showwarning(
                    "Baixes Detectades",
                    f"Hi ha {len(baixes)} baixes llargues actives o futures"
                )
            
        except Exception as e:
            logger.error(f"Error carregant baixes: {e}")
            messagebox.showerror("Error", f"Error:\n{e}")

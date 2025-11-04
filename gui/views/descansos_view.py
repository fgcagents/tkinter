"""
Vista per gestionar descansos dels treballadors
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import logging
from gui.widgets.date_picker import DatePicker, DateRangePicker
from gui.widgets.data_table import DataTable
import config

logger = logging.getLogger(__name__)


class DescansosView(ttk.Frame):
    """Vista de gestió de descansos"""
    
    def __init__(self, parent, controller):
        """
        Inicialitza la vista
        
        Args:
            parent: Widget pare
            controller: DescansosController
        """
        super().__init__(parent)
        self.controller = controller
        self.treballador_seleccionat = None
        
        self._create_ui()
        logger.info("DescansosView inicialitzada")
    
    def _create_ui(self):
        """Crea la interfície"""
        # Frame principal amb dues columnes
        main_container = ttk.Frame(self, padding=10)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Columna esquerra: Cerca i selecció de treballador
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self._create_search_section(left_frame)
        self._create_descansos_section(left_frame)
        
        # Columna dreta: Accions
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        
        self._create_actions_section(right_frame)
    
    def _create_search_section(self, parent):
        """Crea la secció de cerca de treballadors"""
        search_frame = ttk.LabelFrame(parent, text="Cerca de Treballador", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Camp de cerca
        search_container = ttk.Frame(search_frame)
        search_container.pack(fill=tk.X)
        
        ttk.Label(search_container, text="Cerca:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            search_container,
            textvariable=self.search_var,
            width=30
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.search_entry.bind('<KeyRelease>', self._on_search)
        
        ttk.Button(
            search_container,
            text="🔍",
            command=self._do_search,
            width=3
        ).pack(side=tk.LEFT)
        
        # Resultats de cerca
        results_frame = ttk.Frame(search_frame)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Taula de resultats
        columns = [
            {'id': 'id', 'text': 'ID', 'width': 80},
            {'id': 'treballador', 'text': 'Nom', 'width': 150},
            {'id': 'plaza', 'text': 'Plaça', 'width': 80},
            {'id': 'rotacio', 'text': 'Rotació', 'width': 80},
            {'id': 'zona', 'text': 'Zona', 'width': 60}
        ]
        
        self.results_table = DataTable(
            results_frame,
            columns=columns,
            on_select=self._on_treballador_selected
        )
        self.results_table.pack(fill=tk.BOTH, expand=True)
        
        # Info del treballador seleccionat
        self.selected_info_label = ttk.Label(
            search_frame,
            text="Cap treballador seleccionat",
            style='Info.TLabel'
        )
        self.selected_info_label.pack(pady=(10, 0))
    
    def _create_descansos_section(self, parent):
        """Crea la secció de visualització de descansos"""
        descansos_frame = ttk.LabelFrame(parent, text="Descansos", padding=10)
        descansos_frame.pack(fill=tk.BOTH, expand=True)
        
        # Selector d'any
        year_frame = ttk.Frame(descansos_frame)
        year_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(year_frame, text="Any:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.year_var = tk.IntVar(value=datetime.now().year)
        self.year_spinbox = ttk.Spinbox(
            year_frame,
            from_=2020,
            to=2030,
            textvariable=self.year_var,
            width=10,
            command=self._load_descansos
        )
        self.year_spinbox.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            year_frame,
            text="Actualitzar",
            command=self._load_descansos,
            style='Primary.TButton'
        ).pack(side=tk.LEFT)
        
        # Taula de descansos
        columns = [
            {'id': 'data', 'text': 'Data', 'width': 100},
            {'id': 'origen', 'text': 'Origen', 'width': 80},
            {'id': 'motiu', 'text': 'Motiu', 'width': 200}
        ]
        
        self.descansos_table = DataTable(
            descansos_frame,
            columns=columns
        )
        self.descansos_table.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Estadístiques
        self.stats_label = ttk.Label(
            descansos_frame,
            text="Total descansos: 0",
            style='Info.TLabel'
        )
        self.stats_label.pack()
    
    def _create_actions_section(self, parent):
        """Crea la secció d'accions"""
        actions_frame = ttk.LabelFrame(parent, text="Accions", padding=10)
        actions_frame.pack(fill=tk.BOTH, expand=True)
        
        # Afegir descans individual
        single_frame = ttk.LabelFrame(actions_frame, text="Afegir Descans Individual", padding=10)
        single_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.single_date_picker = DatePicker(single_frame, label_text="Data:")
        self.single_date_picker.pack(pady=5)
        
        ttk.Label(single_frame, text="Motiu (opcional):").pack(pady=(5, 0))
        self.single_motiu_var = tk.StringVar()
        ttk.Entry(
            single_frame,
            textvariable=self.single_motiu_var,
            width=25
        ).pack(pady=5)
        
        ttk.Button(
            single_frame,
            text="➕ Afegir Descans",
            command=self._afegir_descans_individual,
            style='Success.TButton'
        ).pack(pady=5)
        
        # Afegir període de descansos
        period_frame = ttk.LabelFrame(actions_frame, text="Afegir Període", padding=10)
        period_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.period_date_picker = DateRangePicker(period_frame)
        self.period_date_picker.pack(pady=5)
        
        ttk.Label(period_frame, text="Origen:").pack(pady=(5, 0))
        self.origen_var = tk.StringVar(value='temporal')
        origen_combo = ttk.Combobox(
            period_frame,
            textvariable=self.origen_var,
            values=['temporal', 'baixa', 'manual', 'base'],
            state='readonly',
            width=22
        )
        origen_combo.pack(pady=5)
        
        ttk.Label(period_frame, text="Motiu (opcional):").pack(pady=(5, 0))
        self.period_motiu_var = tk.StringVar()
        ttk.Entry(
            period_frame,
            textvariable=self.period_motiu_var,
            width=25
        ).pack(pady=5)
        
        ttk.Button(
            period_frame,
            text="➕ Afegir Període",
            command=self._afegir_periode,
            style='Success.TButton'
        ).pack(pady=5)
        
        # Eliminar descansos
        delete_frame = ttk.LabelFrame(actions_frame, text="Eliminar", padding=10)
        delete_frame.pack(fill=tk.X)
        
        ttk.Button(
            delete_frame,
            text="🗑️ Eliminar Seleccionat",
            command=self._eliminar_descans_seleccionat,
            style='Danger.TButton'
        ).pack(pady=5, fill=tk.X)
        
        ttk.Button(
            delete_frame,
            text="🗑️ Eliminar Període",
            command=self._eliminar_periode,
            style='Danger.TButton'
        ).pack(pady=5, fill=tk.X)
    
    # ========================================================================
    # CALLBACKS
    # ========================================================================
    
    def _on_search(self, event=None):
        """Callback per cerca automàtica"""
        terme = self.search_var.get().strip()
        if len(terme) >= 2:
            self._do_search()
    
    def _do_search(self):
        """Executa la cerca"""
        terme = self.search_var.get().strip()
        
        if not terme:
            messagebox.showwarning("Cerca", "Introdueix un terme de cerca")
            return
        
        try:
            resultats = self.controller.buscar_treballador(terme)
            self.results_table.load_data(resultats)
            
            if not resultats:
                messagebox.showinfo("Cerca", "No s'han trobat treballadors")
        except Exception as e:
            logger.error(f"Error en cerca: {e}")
            messagebox.showerror("Error", f"Error en cerca:\n{e}")
    
    def _on_treballador_selected(self, row_data):
        """Callback quan es selecciona un treballador"""
        self.treballador_seleccionat = row_data
        
        info_text = (f"✅ Seleccionat: {row_data['treballador']} "
                    f"(ID: {row_data['id']}, Plaça: {row_data['plaza']})")
        self.selected_info_label.config(text=info_text)
        
        # Carregar descansos
        self._load_descansos()
    
    def _load_descansos(self):
        """Carrega els descansos del treballador seleccionat"""
        if not self.treballador_seleccionat:
            return
        
        try:
            treballador_id = self.treballador_seleccionat['id']
            any = self.year_var.get()
            
            descansos = self.controller.veure_descansos(treballador_id, any)
            
            # Convertir dates a format display
            for d in descansos:
                data_obj = datetime.strptime(d['data'], config.DATE_FORMAT).date()
                d['data'] = data_obj.strftime(config.DATE_FORMAT_DISPLAY)
            
            self.descansos_table.load_data(descansos)
            
            # Actualitzar estadístiques
            total = len(descansos)
            self.stats_label.config(text=f"Total descansos ({any}): {total}")
            
        except Exception as e:
            logger.error(f"Error carregant descansos: {e}")
            messagebox.showerror("Error", f"Error carregant descansos:\n{e}")
    
    def _afegir_descans_individual(self):
        """Afegeix un descans individual"""
        if not self.treballador_seleccionat:
            messagebox.showwarning("Avís", "Selecciona primer un treballador")
            return
        
        try:
            treballador_id = self.treballador_seleccionat['id']
            data = self.single_date_picker.get_date()
            motiu = self.single_motiu_var.get().strip() or None
            
            success, message = self.controller.afegir_descans(
                treballador_id, data, 'manual', motiu
            )
            
            if success:
                messagebox.showinfo("Èxit", message)
                self._load_descansos()
                self.single_motiu_var.set('')
            else:
                messagebox.showwarning("Avís", message)
                
        except Exception as e:
            logger.error(f"Error afegint descans: {e}")
            messagebox.showerror("Error", f"Error:\n{e}")
    
    def _afegir_periode(self):
        """Afegeix un període de descansos"""
        if not self.treballador_seleccionat:
            messagebox.showwarning("Avís", "Selecciona primer un treballador")
            return
        
        try:
            # Validar dates
            is_valid, error_msg = self.period_date_picker.validate()
            if not is_valid:
                messagebox.showwarning("Validació", error_msg)
                return
            
            treballador_id = self.treballador_seleccionat['id']
            data_inici, data_fi = self.period_date_picker.get_date_range()
            origen = self.origen_var.get()
            motiu = self.period_motiu_var.get().strip() or None
            
            # Confirmació
            dies = (data_fi - data_inici).days + 1
            confirm = messagebox.askyesno(
                "Confirmar",
                f"Afegir {dies} dies de descans?\n"
                f"Del {data_inici.strftime(config.DATE_FORMAT_DISPLAY)} "
                f"al {data_fi.strftime(config.DATE_FORMAT_DISPLAY)}"
            )
            
            if not confirm:
                return
            
            success, message = self.controller.afegir_periode_descansos(
                treballador_id, data_inici, data_fi, origen, motiu
            )
            
            if success:
                messagebox.showinfo("Èxit", message)
                self._load_descansos()
                self.period_motiu_var.set('')
            else:
                messagebox.showwarning("Avís", message)
                
        except Exception as e:
            logger.error(f"Error afegint període: {e}")
            messagebox.showerror("Error", f"Error:\n{e}")
    
    def _eliminar_descans_seleccionat(self):
        """Elimina el descans seleccionat a la taula"""
        if not self.treballador_seleccionat:
            messagebox.showwarning("Avís", "Selecciona primer un treballador")
            return
        
        selected = self.descansos_table.get_selected()
        if not selected:
            messagebox.showwarning("Avís", "Selecciona un descans de la llista")
            return
        
        try:
            # Convertir data
            data_str = selected['data']
            data_obj = datetime.strptime(data_str, config.DATE_FORMAT_DISPLAY).date()
            
            # Confirmació
            confirm = messagebox.askyesno(
                "Confirmar eliminació",
                f"Eliminar descans del {data_str}?"
            )
            
            if not confirm:
                return
            
            treballador_id = self.treballador_seleccionat['id']
            success, message = self.controller.eliminar_descans(treballador_id, data_obj)
            
            if success:
                messagebox.showinfo("Èxit", message)
                self._load_descansos()
            else:
                messagebox.showwarning("Avís", message)
                
        except Exception as e:
            logger.error(f"Error eliminant descans: {e}")
            messagebox.showerror("Error", f"Error:\n{e}")
    
    def _eliminar_periode(self):
        """Elimina un període de descansos"""
        if not self.treballador_seleccionat:
            messagebox.showwarning("Avís", "Selecciona primer un treballador")
            return
        
        try:
            # Validar dates
            is_valid, error_msg = self.period_date_picker.validate()
            if not is_valid:
                messagebox.showwarning("Validació", error_msg)
                return
            
            treballador_id = self.treballador_seleccionat['id']
            data_inici, data_fi = self.period_date_picker.get_date_range()
            
            # Confirmació
            dies = (data_fi - data_inici).days + 1
            confirm = messagebox.askyesno(
                "Confirmar eliminació",
                f"Eliminar {dies} dies de descans?\n"
                f"Del {data_inici.strftime(config.DATE_FORMAT_DISPLAY)} "
                f"al {data_fi.strftime(config.DATE_FORMAT_DISPLAY)}"
            )
            
            if not confirm:
                return
            
            success, message = self.controller.eliminar_periode_descansos(
                treballador_id, data_inici, data_fi
            )
            
            if success:
                messagebox.showinfo("Èxit", message)
                self._load_descansos()
            else:
                messagebox.showinfo("Info", message)
                
        except Exception as e:
            logger.error(f"Error eliminant període: {e}")
            messagebox.showerror("Error", f"Error:\n{e}")

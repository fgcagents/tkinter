"""
Vista per executar l'algorisme genètic
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date, timedelta
import logging
from gui.widgets.date_picker import DateRangePicker
from gui.widgets.data_table import DataTable
import config

logger = logging.getLogger(__name__)


class GeneticView(ttk.Frame):
    """Vista per executar l'algorisme genètic"""
    
    def __init__(self, parent, controller):
        """
        Inicialitza la vista
        
        Args:
            parent: Widget pare
            controller: GeneticController
        """
        super().__init__(parent)
        self.controller = controller
        self.running = False
        
        self._create_ui()
        logger.info("GeneticView inicialitzada")
    
    def _create_ui(self):
        """Crea la interfície"""
        main_container = ttk.Frame(self, padding=10)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Columna esquerra: Configuració
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self._create_config_section(left_frame)
        self._create_progress_section(left_frame)
        
        # Columna dreta: Resultats
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self._create_results_section(right_frame)
    
    def _create_config_section(self, parent):
        """Crea la secció de configuració"""
        config_frame = ttk.LabelFrame(parent, text="Configuració", padding=15)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Rang de dates
        ttk.Label(config_frame, text="Període d'Assignació:", 
                 style='Subtitle.TLabel').pack(anchor=tk.W, pady=(0, 5))
        
        self.date_range_picker = DateRangePicker(config_frame)
        self.date_range_picker.pack(fill=tk.X, pady=(0, 15))
        
        # Configurar dates per defecte (proper mes)
        avui = date.today()
        if avui.month == 12:
            inici = date(avui.year + 1, 1, 1)
            fi = date(avui.year + 1, 1, 31)
        else:
            inici = (avui.replace(day=1) + timedelta(days=32)).replace(day=1)
            if inici.month == 12:
                fi = inici.replace(day=31)
            else:
                fi = (inici.replace(month=inici.month + 1, day=1) - timedelta(days=1))
        
        self.date_range_picker.set_date_range(inici, fi)
        
        # Paràmetres de l'algorisme
        params_frame = ttk.Frame(config_frame)
        params_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Mida població
        pop_frame = ttk.Frame(params_frame)
        pop_frame.pack(fill=tk.X, pady=3)
        ttk.Label(pop_frame, text="Mida Població:", width=20).pack(side=tk.LEFT)
        self.poblacio_var = tk.IntVar(value=config.AG_MIDA_POBLACIO)
        ttk.Spinbox(
            pop_frame,
            from_=10,
            to=200,
            textvariable=self.poblacio_var,
            width=15
        ).pack(side=tk.LEFT)
        
        # Generacions
        gen_frame = ttk.Frame(params_frame)
        gen_frame.pack(fill=tk.X, pady=3)
        ttk.Label(gen_frame, text="Generacions:", width=20).pack(side=tk.LEFT)
        self.generacions_var = tk.IntVar(value=config.AG_GENERACIONS)
        ttk.Spinbox(
            gen_frame,
            from_=50,
            to=500,
            textvariable=self.generacions_var,
            width=15
        ).pack(side=tk.LEFT)
        
        # Comportament en duplicats
        dup_frame = ttk.Frame(params_frame)
        dup_frame.pack(fill=tk.X, pady=3)
        ttk.Label(dup_frame, text="Duplicats:", width=20).pack(side=tk.LEFT)
        self.duplicats_var = tk.StringVar(value='replace_all')
        ttk.Combobox(
            dup_frame,
            textvariable=self.duplicats_var,
            values=['replace_all', 'add_new_only'],
            state='readonly',
            width=13
        ).pack(side=tk.LEFT)
        
        # Botó d'execució
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X)
        
        self.run_button = ttk.Button(
            button_frame,
            text="▶️ Executar Algorisme",
            command=self._executar,
            style='Primary.TButton'
        )
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_button = ttk.Button(
            button_frame,
            text="⏹️ Cancel·lar",
            command=self._cancel_lar,
            style='Danger.TButton',
            state='disabled'
        )
        self.cancel_button.pack(side=tk.LEFT)
    
    def _create_progress_section(self, parent):
        """Crea la secció de progrés"""
        progress_frame = ttk.LabelFrame(parent, text="Progrés", padding=15)
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        # Missatge de progrés
        self.progress_label = ttk.Label(
            progress_frame,
            text="Llest per executar",
            style='Info.TLabel'
        )
        self.progress_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Barra de progrés
        self.progress_var = tk.IntVar()
        self.progressbar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progressbar.pack(fill=tk.X, pady=(0, 5))
        
        # Percentatge
        self.percent_label = ttk.Label(
            progress_frame,
            text="0%",
            style='Info.TLabel'
        )
        self.percent_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Resum de resultats
        self.summary_text = tk.Text(
            progress_frame,
            height=8,
            wrap=tk.WORD,
            font=('Segoe UI', 9),
            state='disabled'
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True)
    
    def _create_results_section(self, parent):
        """Crea la secció de resultats"""
        results_frame = ttk.LabelFrame(parent, text="Últimes Assignacions", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Botons d'accions
        actions_frame = ttk.Frame(results_frame)
        actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            actions_frame,
            text="🔄 Actualitzar",
            command=self._carregar_assignacions
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            actions_frame,
            text="💾 Exportar",
            command=self._exportar,
            style='Success.TButton'
        ).pack(side=tk.LEFT, padx=2)
        
        # Taula d'assignacions
        columns = [
            {'id': 'data', 'text': 'Data', 'width': 100},
            {'id': 'treballador', 'text': 'Treballador', 'width': 120},
            {'id': 'plaza', 'text': 'Plaça', 'width': 60},
            {'id': 'servei', 'text': 'Servei', 'width': 80},
            {'id': 'zona', 'text': 'Zona', 'width': 60},
            {'id': 'inici', 'text': 'Inici', 'width': 60},
            {'id': 'fi', 'text': 'Fi', 'width': 60}
        ]
        
        self.results_table = DataTable(
            results_frame,
            columns=columns
        )
        self.results_table.pack(fill=tk.BOTH, expand=True)
        
        # Carregar assignacions inicials
        self._carregar_assignacions()
    
    # ========================================================================
    # CALLBACKS
    # ========================================================================
    
    def _executar(self):
        """Executa l'algorisme genètic"""
        if self.running:
            messagebox.showwarning("Avís", "L'algorisme ja s'està executant")
            return
        
        # Validar dates
        is_valid, error_msg = self.date_range_picker.validate()
        if not is_valid:
            messagebox.showwarning("Validació", error_msg)
            return
        
        data_inici, data_fi = self.date_range_picker.get_date_range()
        dies = (data_fi - data_inici).days + 1
        
        if dies > 90:
            messagebox.showwarning(
                "Validació",
                "El període no pot superar 90 dies"
            )
            return
        
        # Confirmació
        confirm = messagebox.askyesno(
            "Confirmar Execució",
            f"Executar algorisme genètic per {dies} dies?\n\n"
            f"Període: {data_inici.strftime(config.DATE_FORMAT_DISPLAY)} - "
            f"{data_fi.strftime(config.DATE_FORMAT_DISPLAY)}\n"
            f"Població: {self.poblacio_var.get()}\n"
            f"Generacions: {self.generacions_var.get()}\n\n"
            f"Això pot trigar diversos minuts."
        )
        
        if not confirm:
            return
        
        # Configurar UI per execució
        self.running = True
        self.run_button.config(state='disabled')
        self.cancel_button.config(state='normal')
        self.progress_var.set(0)
        self.progress_label.config(text="Iniciant...")
        
        # Netejar resum anterior
        self.summary_text.config(state='normal')
        self.summary_text.delete('1.0', tk.END)
        self.summary_text.config(state='disabled')
        
        # Executar
        try:
            self.controller.executar_algorisme(
                data_inici=data_inici,
                data_fi=data_fi,
                mida_poblacio=self.poblacio_var.get(),
                generacions=self.generacions_var.get(),
                on_duplicate=self.duplicats_var.get(),
                progress_callback=self._update_progress,
                finish_callback=self._on_finish
            )
        except Exception as e:
            logger.error(f"Error executant algorisme: {e}")
            messagebox.showerror("Error", f"Error:\n{e}")
            self._reset_ui()
    
    def _update_progress(self, percent, message=None):
        """Actualitza el progrés"""
        self.progress_var.set(percent)
        self.percent_label.config(text=f"{percent}%")
        
        if message:
            self.progress_label.config(text=message)
        
        self.update_idletasks()
    
    def _on_finish(self, success, result):
        """Callback quan finalitza l'execució"""
        self.running = False
        self._reset_ui()
        
        if success:
            # Mostrar resum
            self.summary_text.config(state='normal')
            self.summary_text.delete('1.0', tk.END)
            
            summary = (
                f"✅ Algorisme completat correctament!\n\n"
                f"Període: {result['data_inici'].strftime(config.DATE_FORMAT_DISPLAY)} - "
                f"{result['data_fi'].strftime(config.DATE_FORMAT_DISPLAY)}\n"
                f"Generacions: {result['generacions']}\n"
                f"Mida població: {result['mida_poblacio']}\n"
                f"Fitness final: {result['fitness_final']:.2f}\n"
                f"Assignacions generades: {result['assignacions']}\n"
            )
            
            self.summary_text.insert('1.0', summary)
            self.summary_text.config(state='disabled')
            
            # Carregar resultats
            self._carregar_assignacions()
            
            messagebox.showinfo(
                "Èxit",
                f"Algorisme completat!\n\n"
                f"Fitness: {result['fitness_final']:.2f}\n"
                f"Assignacions: {result['assignacions']}"
            )
        else:
            # Error
            self.progress_label.config(text=f"❌ Error: {result}")
            messagebox.showerror("Error", f"Error durant l'execució:\n{result}")
    
    def _cancel_lar(self):
        """Cancel·la l'execució"""
        if self.running:
            confirm = messagebox.askyesno(
                "Confirmar Cancel·lació",
                "Vols cancel·lar l'execució de l'algorisme?"
            )
            
            if confirm:
                self.controller.cancel_lar_execucio()
                self.progress_label.config(text="❌ Cancel·lat per l'usuari")
                self._reset_ui()
    
    def _reset_ui(self):
        """Reseteja la UI després de l'execució"""
        self.running = False
        self.run_button.config(state='normal')
        self.cancel_button.config(state='disabled')
    
    def _carregar_assignacions(self):
        """Carrega les últimes assignacions"""
        try:
            assignacions = self.controller.get_ultimes_assignacions(limit=500)
            
            # Formatació
            for a in assignacions:
                if a.get('data'):
                    try:
                        data_obj = datetime.strptime(a['data'], config.DATE_FORMAT).date()
                        a['data'] = data_obj.strftime(config.DATE_FORMAT_DISPLAY)
                    except:
                        pass
            
            self.results_table.load_data(assignacions)
            
        except Exception as e:
            logger.error(f"Error carregant assignacions: {e}")
    
    def _exportar(self):
        """Exporta les assignacions a CSV"""
        # Demanar rang de dates
        export_window = tk.Toplevel(self.winfo_toplevel())
        export_window.title("Exportar Assignacions")
        export_window.geometry("400x200")
        export_window.transient(self.winfo_toplevel())
        export_window.grab_set()
        
        frame = ttk.Frame(export_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Rang de dates a exportar:", 
                 style='Subtitle.TLabel').pack(pady=(0, 10))
        
        date_picker = DateRangePicker(frame)
        date_picker.pack(pady=10)
        
        def do_export():
            data_inici, data_fi = date_picker.get_date_range()
            export_window.destroy()
            
            # Demanar nom de fitxer
            nom_fitxer = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"assignacions_{date.today().strftime('%Y%m%d')}.csv"
            )
            
            if not nom_fitxer:
                return
            
            try:
                success, message = self.controller.exportar_assignacions(
                    nom_fitxer,
                    data_inici,
                    data_fi
                )
                
                if success:
                    messagebox.showinfo("Èxit", message)
                else:
                    messagebox.showwarning("Avís", message)
                    
            except Exception as e:
                logger.error(f"Error exportant: {e}")
                messagebox.showerror("Error", f"Error:\n{e}")
        
        ttk.Button(
            frame,
            text="Exportar",
            command=do_export,
            style='Primary.TButton'
        ).pack(pady=10)

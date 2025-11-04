"""
Vista per analitzar disponibilitat de serveis
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date, timedelta
import logging
from gui.widgets.date_picker import DateRangePicker
from gui.widgets.data_table import DataTable
from gui.widgets.progress_dialog import ProgressDialog
import config

logger = logging.getLogger(__name__)


class DisponibilitatView(ttk.Frame):
    """Vista d'anàlisi de disponibilitat"""
    
    def __init__(self, parent, controller):
        """
        Inicialitza la vista
        
        Args:
            parent: Widget pare
            controller: DisponibilitatController
        """
        super().__init__(parent)
        self.controller = controller
        self.resultats_analisi = None
        
        self._create_ui()
        logger.info("DisponibilitatView inicialitzada")
    
    def _create_ui(self):
        """Crea la interfície"""
        main_container = ttk.Frame(self, padding=10)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Secció de configuració
        self._create_config_section(main_container)
        
        # Secció de resultats
        self._create_results_section(main_container)
        
        # Secció d'accions
        self._create_actions_section(main_container)
    
    def _create_config_section(self, parent):
        """Crea la secció de configuració"""
        config_frame = ttk.LabelFrame(parent, text="Configuració de l'Anàlisi", padding=15)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Selector de rang de dates
        date_frame = ttk.Frame(config_frame)
        date_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.date_range_picker = DateRangePicker(date_frame)
        self.date_range_picker.pack(side=tk.LEFT)
        
        # Configurar dates per defecte (mes actual)
        avui = date.today()
        primer_dia_mes = avui.replace(day=1)
        if avui.month == 12:
            ultim_dia_mes = avui.replace(day=31)
        else:
            ultim_dia_mes = (avui.replace(month=avui.month + 1, day=1) - timedelta(days=1))
        
        self.date_range_picker.set_date_range(primer_dia_mes, ultim_dia_mes)
        
        # Botons d'accés ràpid
        quick_frame = ttk.Frame(config_frame)
        quick_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(quick_frame, text="Accés ràpid:").pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            quick_frame,
            text="Aquest Mes",
            command=lambda: self._set_quick_range('mes')
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            quick_frame,
            text="Proper Mes",
            command=lambda: self._set_quick_range('proper_mes')
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            quick_frame,
            text="Proper Trimestre",
            command=lambda: self._set_quick_range('trimestre')
        ).pack(side=tk.LEFT, padx=2)
        
        # Botó d'anàlisi
        analyze_frame = ttk.Frame(config_frame)
        analyze_frame.pack(fill=tk.X)
        
        self.analyze_button = ttk.Button(
            analyze_frame,
            text="🔍 Analitzar Disponibilitat",
            command=self._analitzar,
            style='Primary.TButton'
        )
        self.analyze_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_label = ttk.Label(
            analyze_frame,
            text="",
            style='Info.TLabel'
        )
        self.status_label.pack(side=tk.LEFT)
    
    def _create_results_section(self, parent):
        """Crea la secció de resultats"""
        results_frame = ttk.LabelFrame(parent, text="Resultats de l'Anàlisi", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Resum
        summary_frame = ttk.Frame(results_frame, style='Card.TFrame')
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.summary_text = tk.Text(
            summary_frame,
            height=4,
            wrap=tk.WORD,
            font=('Segoe UI', 10),
            state='disabled'
        )
        self.summary_text.pack(fill=tk.X, padx=10, pady=10)
        
        # Taula de resultats
        columns = [
            {'id': 'data', 'text': 'Data', 'width': 100},
            {'id': 'dia_setmana', 'text': 'Dia', 'width': 100},
            {'id': 'servei', 'text': 'Servei', 'width': 100},
            {'id': 'zona', 'text': 'Zona', 'width': 80},
            {'id': 'disponibles', 'text': 'Disponibles', 'width': 100},
            {'id': 'estat', 'text': 'Estat', 'width': 100}
        ]
        
        self.results_table = DataTable(
            results_frame,
            columns=columns
        )
        self.results_table.pack(fill=tk.BOTH, expand=True)
        
        # Ressaltar files amb problemes
        self.results_table.tree.tag_configure('descobert', background='#ffcccc')
        self.results_table.tree.tag_configure('cobert', background='#ccffcc')
    
    def _create_actions_section(self, parent):
        """Crea la secció d'accions"""
        actions_frame = ttk.LabelFrame(parent, text="Accions", padding=10)
        actions_frame.pack(fill=tk.X)
        
        ttk.Button(
            actions_frame,
            text="💾 Guardar a Base de Dades",
            command=self._guardar_a_bd,
            style='Success.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            actions_frame,
            text="📄 Exportar a CSV",
            command=self._exportar_csv
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            actions_frame,
            text="🗑️ Netejar Resultats",
            command=self._netejar_resultats
        ).pack(side=tk.LEFT, padx=5)

    
    # ========================================================================
    # CALLBACKS
    # ========================================================================
    
    def _set_quick_range(self, range_type):
        """Estableix un rang de dates ràpid"""
        avui = date.today()
        
        if range_type == 'mes':
            inici = avui.replace(day=1)
            if avui.month == 12:
                fi = avui.replace(day=31)
            else:
                fi = (avui.replace(month=avui.month + 1, day=1) - timedelta(days=1))
        
        elif range_type == 'proper_mes':
            if avui.month == 12:
                inici = date(avui.year + 1, 1, 1)
                fi = date(avui.year + 1, 1, 31)
            else:
                inici = (avui.replace(day=1) + timedelta(days=32)).replace(day=1)
                if inici.month == 12:
                    fi = inici.replace(day=31)
                else:
                    fi = (inici.replace(month=inici.month + 1, day=1) - timedelta(days=1))
        
        elif range_type == 'trimestre':
            inici = avui
            fi = avui + timedelta(days=90)
        
        self.date_range_picker.set_date_range(inici, fi)
    
    def _analitzar(self):
        """Executa l'anàlisi de disponibilitat"""
        # Validar dates
        is_valid, error_msg = self.date_range_picker.validate()
        if not is_valid:
            messagebox.showwarning("Validació", error_msg)
            return
        
        data_inici, data_fi = self.date_range_picker.get_date_range()
        dies = (data_fi - data_inici).days + 1
        
        # Confirmació si són molts dies
        if dies > 60:
            confirm = messagebox.askyesno(
                "Confirmar",
                f"Analitzar {dies} dies pot trigar uns minuts.\nContinuar?"
            )
            if not confirm:
                return
        
        # Crear diàleg de progrés
        progress_dialog = ProgressDialog(
            self.winfo_toplevel(),
            title="Analitzant Disponibilitat",
            cancelable=False
        )
        
        def progress_callback(percent):
            progress_dialog.update_progress(percent, f"Processant... {percent}%")
        
        # Executar anàlisi en thread (simplifiquem executant directament)
        try:
            self.analyze_button.config(state='disabled')
            self.status_label.config(text="⏳ Analitzant...")
            self.update()
            
            resultats = self.controller.analitzar_disponibilitat(
                data_inici,
                data_fi,
                progress_callback=progress_callback
            )
            
            progress_dialog.close()
            
            if 'error' in resultats:
                messagebox.showerror("Error", resultats['error'])
                return
            
            self.resultats_analisi = resultats
            self._mostrar_resultats(resultats)
            
            self.status_label.config(text="✅ Anàlisi completada")
            messagebox.showinfo("Èxit", "Anàlisi completada correctament")
            
        except Exception as e:
            progress_dialog.close()
            logger.error(f"Error en anàlisi: {e}")
            messagebox.showerror("Error", f"Error durant l'anàlisi:\n{e}")
            self.status_label.config(text="❌ Error")
        
        finally:
            self.analyze_button.config(state='normal')
    
    def _mostrar_resultats(self, resultats):
        """Mostra els resultats de l'anàlisi"""
        resum = resultats['resum']
        dades = resultats['resultats']
        
        # Actualitzar resum
        self.summary_text.config(state='normal')
        self.summary_text.delete('1.0', tk.END)
        
        summary_text = (
            f"📅 Període: {resum['data_inici'].strftime(config.DATE_FORMAT_DISPLAY)} - "
            f"{resum['data_fi'].strftime(config.DATE_FORMAT_DISPLAY)} "
            f"({resum['dies_analitzats']} dies)\n"
            f"✅ Serveis coberts: {resum['total_coberts']} / {resum['total_serveis']} "
            f"({resum['percentatge_cobertura']:.1f}%)\n"
            f"❌ Serveis descoberts: {resum['total_descoberts']}\n"
        )
        
        self.summary_text.insert('1.0', summary_text)
        self.summary_text.config(state='disabled')
        
        # Carregar dades a la taula
        self.results_table.clear()
        
        for row in dades:
            # Formatació
            row_display = {
                'data': row['data'].strftime(config.DATE_FORMAT_DISPLAY),
                'dia_setmana': row['dia_setmana'],
                'servei': row['servei'],
                'zona': row['zona'],
                'disponibles': row['disponibles'],
                'estat': row['estat']
            }
            
            # Tag segons estat
            tag = 'descobert' if row['estat'] == 'Descobert' else 'cobert'
            
            self.results_table.tree.insert(
                '',
                tk.END,
                values=list(row_display.values()),
                tags=(tag,)
            )
    
    def _exportar_csv(self):
        """Exporta els resultats a CSV"""
        if not self.resultats_analisi:
            messagebox.showwarning("Avís", "No hi ha resultats per exportar")
            return
        
        # Demanar nom de fitxer
        nom_fitxer = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"disponibilitat_{date.today().strftime('%Y%m%d')}.csv"
        )
        
        if not nom_fitxer:
            return
        
        try:
            import csv
            
            with open(nom_fitxer, 'w', newline='', encoding=config.CSV_ENCODING) as f:
                fieldnames = ['data', 'dia_setmana', 'servei', 'zona', 
                            'disponibles', 'estat']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                for row in self.resultats_analisi['resultats']:
                    writer.writerow({
                        'data': row['data'].strftime(config.DATE_FORMAT),
                        'dia_setmana': row['dia_setmana'],
                        'servei': row['servei'],
                        'zona': row['zona'],
                        'disponibles': row['disponibles'],
                        'estat': row['estat']
                    })
            
            messagebox.showinfo("Èxit", f"Fitxer exportat:\n{nom_fitxer}")
            
        except Exception as e:
            logger.error(f"Error exportant CSV: {e}")
            messagebox.showerror("Error", f"Error exportant:\n{e}")
    
    def _netejar_resultats(self):
        """Neteja els resultats"""
        self.results_table.clear()
        self.resultats_analisi = None
        
        self.summary_text.config(state='normal')
        self.summary_text.delete('1.0', tk.END)
        self.summary_text.config(state='disabled')
        
        self.status_label.config(text="")

    def _guardar_a_bd(self):
        """Guarda els resultats a la base de dades"""
        if not self.resultats_analisi:
            messagebox.showwarning("Avís", "No hi ha resultats per guardar")
            return
        
        # Confirmació
        confirm = messagebox.askyesno(
            "Confirmar Guardar",
            "⚠️ ATENCIÓ: Les taules assig_grup_A i cobertura "
            "s'esborraran COMPLETAMENT abans de guardar.\n\n"
            "Vols continuar?"
        )
        
        if not confirm:
            return
        
        try:
            # Netejar taules
            self.status_label.config(text="⏳ Netejant taules...")
            self.update()
            
            registres_assig, registres_cobertura = self.controller.netejar_taules()
            logger.info(f"Taules netejades: {registres_assig}, {registres_cobertura}")
            
            # Guardar assignacions
            self.status_label.config(text="⏳ Guardant assignacions...")
            self.update()
            
            assignacions_per_dia = self.resultats_analisi.get('assignacions_per_dia', {})
            success, message = self.controller.guardar_assignacions_db(assignacions_per_dia)
            
            if success:
                self.status_label.config(text="✅ Guardat correctament")
                messagebox.showinfo("Èxit", message)
            else:
                self.status_label.config(text="❌ Error guardant")
                messagebox.showerror("Error", message)
                
        except Exception as e:
            logger.error(f"Error guardant a BD: {e}")
            messagebox.showerror("Error", f"Error:\n{e}")
            self.status_label.config(text="❌ Error")

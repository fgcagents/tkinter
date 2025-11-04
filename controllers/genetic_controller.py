"""
Controller per executar l'algorisme genètic
Integra genetic_algorithm.py i main.py amb la GUI
"""
import logging
from datetime import date, datetime
from typing import Dict, Optional, Callable, List
import threading
import queue
from models.database import DatabaseManager
import config

logger = logging.getLogger(__name__)


class GeneticController:
    """Gestiona l'execució de l'algorisme genètic"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        """Inicialitza el controller"""
        self.db = db_manager or DatabaseManager()
        self.running = False
        self.thread = None
        self.progress_queue = queue.Queue()
        logger.info("GeneticController inicialitzat")
    
    # ========================================================================
    # EXECUCIÓ DE L'ALGORISME
    # ========================================================================
    
    def executar_algorisme(self,
                          data_inici: date,
                          data_fi: date,
                          mida_poblacio: int = None,
                          generacions: int = None,
                          on_duplicate: str = 'replace_all',
                          progress_callback: Optional[Callable] = None,
                          finish_callback: Optional[Callable] = None):
        """
        Executa l'algorisme genètic en un thread separat
        
        Args:
            data_inici: Data d'inici del període
            data_fi: Data fi del període
            mida_poblacio: Mida de la població (si None, usa config)
            generacions: Nombre de generacions (si None, usa config)
            on_duplicate: Comportament en duplicats ('replace_all', 'add_new_only')
            progress_callback: Funció per notificar progrés
            finish_callback: Funció per notificar finalització
        """
        if self.running:
            logger.warning("L'algorisme ja està executant-se")
            if finish_callback:
                finish_callback(False, "L'algorisme ja s'està executant")
            return
        
        # Validacions
        if data_inici > data_fi:
            error = "La data d'inici ha de ser anterior a la data fi"
            logger.error(error)
            if finish_callback:
                finish_callback(False, error)
            return
        
        dies_totals = (data_fi - data_inici).days + 1
        if dies_totals > 90:
            error = "El període no pot superar 90 dies"
            logger.error(error)
            if finish_callback:
                finish_callback(False, error)
            return
        
        # Paràmetres per defecte
        if mida_poblacio is None:
            mida_poblacio = config.AG_MIDA_POBLACIO
        if generacions is None:
            generacions = config.AG_GENERACIONS
        
        # Executar en thread separat
        self.running = True
        self.thread = threading.Thread(
            target=self._executar_thread,
            args=(data_inici, data_fi, mida_poblacio, generacions, 
                  on_duplicate, progress_callback, finish_callback),
            daemon=True
        )
        self.thread.start()
        logger.info(f"Thread d'algorisme genètic iniciat: {data_inici} - {data_fi}")
    
    def _executar_thread(self, data_inici, data_fi, mida_poblacio, generacions,
                        on_duplicate, progress_callback, finish_callback):
        """Mètode privat que s'executa en el thread"""
        try:
            logger.info("Iniciant càrrega de dades...")
            
            # Importar els mòduls necessaris
            # Assumim que genetic_algorithm.py, data_loader.py, constraints.py, etc.
            # estan al directori core/
            try:
                from core.data_loader import DataLoader
                from core.data_structures import EstadistiquesGlobals
                from core.genetic_algorithm import AlgorismeGenetic
                from core.constraints import RestriccionManager
                from core import constraints
            except ImportError as e:
                logger.error(f"Error important mòduls core: {e}")
                if finish_callback:
                    finish_callback(False, f"Error important mòduls: {e}")
                self.running = False
                return
            
            # Notificar progrés inicial
            if progress_callback:
                progress_callback(5, "Carregant dades...")
            
            # Carregar dades des de SQLite
            loader = DataLoader(db_path=str(config.DB_PATH))
            
            treballadors = loader.carrega_treballadors()
            torns = loader.carrega_torns()
            necessitats = loader.carrega_necessitats_cobertura()
            calendari = loader.carrega_calendari()
            exclude_map = loader.carrega_descansos_dies()
            
            if progress_callback:
                progress_callback(15, "Dades carregades. Configurant restriccions...")
            
            # Estadístiques globals
            estadistiques = EstadistiquesGlobals()
            
            # Configurar restriccions
            restriccions = RestriccionManager()
            
            # Afegir restriccions rígides (pes infinit)
            restriccions.afegeix_restriccio(
                constraints.restriccio_unica_assignacio_per_dia_rigida, 
                float('inf'), 
                "Única assignació per dia"
            )
            restriccions.afegeix_restriccio(
                constraints.restriccio_sense_solapaments_rigida, 
                float('inf'),
                "Sense solapaments"
            )
            restriccions.afegeix_restriccio(
                constraints.restriccio_descans_minim_12h_rigida, 
                float('inf'),
                "Descans mínim 12h"
            )
            restriccions.afegeix_restriccio(
                constraints.restriccio_divendres_cap_setmana_rigida, 
                float('inf'),
                "Divendres cap de setmana"
            )
            
            # Afegir restriccions toves (pes configurable)
            restriccions.afegeix_restriccio(constraints.restriccio_grup_T, 100.0, "Grup T")
            restriccions.afegeix_restriccio(constraints.restriccio_sense_descans, 80.0, "Sense descans")
            restriccions.afegeix_restriccio(constraints.restriccio_formacio_requerida, 100.0, "Formació requerida")
            restriccions.afegeix_restriccio(constraints.restriccio_linia_correcta, 90.0, "Línia correcta")
            restriccions.afegeix_restriccio(constraints.restriccio_hores_anuals, 70.0, "Hores anuals")
            restriccions.afegeix_restriccio(constraints.restriccio_dies_consecutius, 60.0, "Dies consecutius")
            restriccions.afegeix_restriccio(constraints.restriccio_equitat_canvis_zona, 50.0, "Equitat canvis zona")
            restriccions.afegeix_restriccio(constraints.restriccio_equitat_canvis_torn, 50.0, "Equitat canvis torn")
            restriccions.afegeix_restriccio(constraints.restriccio_cobertura_completa, 120.0, "Cobertura completa")
            restriccions.afegeix_restriccio(constraints.restriccio_distribucio_equilibrada, 40.0, "Distribució equilibrada")
            
            if progress_callback:
                progress_callback(20, "Iniciant algorisme genètic...")
            
            # Crear i executar l'algorisme genètic
            ag = AlgorismeGenetic(
                treballadors=treballadors,
                torns=torns,
                necessitats=necessitats,
                calendari=calendari,
                restriccions=restriccions,
                estadistiques=estadistiques,
                mida_poblacio=mida_poblacio,
                exclude_map=exclude_map
            )
            
            # Executar l'algorisme
            millor_individu = ag.executa(generacions=generacions)
            
            if progress_callback:
                progress_callback(95, "Guardant resultats...")
            
            # Guardar resultats a la base de dades
            success = self._guardar_resultats(
                millor_individu, 
                treballadors, 
                torns, 
                on_duplicate
            )
            
            if progress_callback:
                progress_callback(100, "Completat!")
            
            # Preparar resum
            assignacions, info = millor_individu if millor_individu else ([], {})
            resum = {
                'data_inici': data_inici,
                'data_fi': data_fi,
                'generacions': generacions,
                'mida_poblacio': mida_poblacio,
                'fitness_final': info.get('fitness', 0),
                'assignacions': len(assignacions)
            }
            
            logger.info(f"Algorisme completat. Fitness: {resum['fitness_final']:.2f}")
            
            if finish_callback:
                finish_callback(True, resum)
            
        except Exception as e:
            logger.error(f"Error executant algorisme: {e}", exc_info=True)
            if finish_callback:
                finish_callback(False, f"Error: {str(e)}")
        
        finally:
            self.running = False
    
    def _progress_ag(self, generacio: int, total_generacions: int, 
                    fitness: float, callback: Optional[Callable]):
        """Notifica el progrés de l'algorisme genètic"""
        if callback:
            # Progrés entre 20% i 95%
            progress = 20 + int((generacio / total_generacions) * 75)
            missatge = f"Generació {generacio}/{total_generacions} - Fitness: {fitness:.2f}"
            callback(progress, missatge)
    
    def _guardar_resultats(self, individu, treballadors: Dict, 
                          torns: Dict, on_duplicate: str) -> bool:
        """
        Guarda els resultats a la base de dades
        
        Args:
            individu: Millor individu trobat
            treballadors: Diccionari de treballadors
            torns: Diccionari de torns
            on_duplicate: Comportament en duplicats
            
        Returns:
            True si s'ha guardat correctament
        """
        if not individu:
            logger.warning("No hi ha resultat per guardar")
            return False
            
        assignacions, info = individu
        if not assignacions:
            logger.warning("No hi ha assignacions per guardar")
            return False
        
        try:
            # Si replace_all, netejar taula primer
            if on_duplicate == 'replace_all':
                self.db.clear_assignacions()
                logger.info("Taula d'assignacions netejada")
            
            # Preparar dades per inserir
            assignacions_db = []
            for assignacio in assignacions:
                treballador = treballadors.get(assignacio.treballador_id)
                torn = torns.get(assignacio.torn_id)
                
                if not treballador or not torn:
                    continue
                
                assignacions_db.append((
                    assignacio.treballador_id,
                    assignacio.data.strftime(config.DATE_FORMAT),
                    assignacio.torn_id,
                    assignacio.hora_inici.strftime('%H:%M') if assignacio.hora_inici else None,
                    assignacio.hora_fi.strftime('%H:%M') if assignacio.hora_fi else None,
                    torn.zona if hasattr(torn, 'zona') else None,
                    torn.linia if hasattr(torn, 'linia') else None,
                    datetime.now().strftime(config.DATETIME_FORMAT)
                ))
            
            # Inserir en batch
            if on_duplicate == 'replace_all':
                query = """
                    INSERT INTO assig_grup_T 
                    (treballador_id, data, torn_id, inici, fi, zona, linia, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
            else:  # add_new_only
                query = """
                    INSERT OR IGNORE INTO assig_grup_T 
                    (treballador_id, data, torn_id, inici, fi, zona, linia, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
            
            rows_affected = self.db.execute_many(query, assignacions_db)
            logger.info(f"Guardades {rows_affected} assignacions")
            
            # Guardar també a assignacions_finals per històric
            self._guardar_historic(assignacions_db)
            
            return True
            
        except Exception as e:
            logger.error(f"Error guardant resultats: {e}")
            return False
    
    def _guardar_historic(self, assignacions: List[tuple]):
        """Guarda les assignacions a la taula d'històric"""
        try:
            query = """
                INSERT OR REPLACE INTO assignacions_finals
                (treballador_id, data, servei, inici, fi, zona, linia, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.db.execute_many(query, assignacions)
            logger.info("Històric d'assignacions actualitzat")
        except Exception as e:
            logger.error(f"Error guardant històric: {e}")
    
    # ========================================================================
    # CONTROL D'EXECUCIÓ
    # ========================================================================
    
    def cancel_lar_execucio(self):
        """Cancel·la l'execució de l'algorisme"""
        if self.running:
            self.running = False
            logger.info("Cancel·lació d'algorisme sol·licitada")
            # Nota: El thread acabarà quan acabi la generació actual
    
    def is_running(self) -> bool:
        """Retorna si l'algorisme està executant-se"""
        return self.running
    
    # ========================================================================
    # CONSULTA DE RESULTATS
    # ========================================================================
    
    def get_ultimes_assignacions(self, limit: int = 100) -> List[Dict]:
        """
        Obté les últimes assignacions generades
        
        Args:
            limit: Nombre màxim de resultats
            
        Returns:
            Llista d'assignacions
        """
        try:
            query = """
                SELECT 
                    a.treballador_id,
                    t.treballador,
                    t.plaza,
                    a.data,
                    a.servei,
                    a.inici,
                    a.fi,
                    a.zona,
                    a.linia,
                    a.created_at
                FROM assig_grup_T a
                LEFT JOIN treballadors t ON a.treballador_id = t.id
                ORDER BY a.data DESC, a.servei
                LIMIT ?
            """
            rows = self.db.execute_query(query, (limit,))
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error obtenint assignacions: {e}")
            return []
    
    def get_estadistiques_assignacions(self, data_inici: date = None,
                                      data_fi: date = None) -> Dict:
        """
        Obté estadístiques de les assignacions
        
        Returns:
            Diccionari amb estadístiques
        """
        try:
            query = """
                SELECT 
                    COUNT(*) as total_assignacions,
                    COUNT(DISTINCT treballador_id) as treballadors_assignats,
                    COUNT(DISTINCT data) as dies_coberts,
                    COUNT(DISTINCT servei) as serveis_coberts
                FROM assig_grup_T
                WHERE 1=1
            """
            params = []
            
            if data_inici:
                query += " AND data >= ?"
                params.append(data_inici.strftime(config.DATE_FORMAT))
            
            if data_fi:
                query += " AND data <= ?"
                params.append(data_fi.strftime(config.DATE_FORMAT))
            
            rows = self.db.execute_query(query, tuple(params) if params else None)
            
            if rows:
                return dict(rows[0])
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error obtenint estadístiques: {e}")
            return {}
    
    def exportar_assignacions(self, fitxer: str, 
                             data_inici: date = None,
                             data_fi: date = None) -> tuple:
        """
        Exporta les assignacions a CSV
        
        Args:
            fitxer: Nom del fitxer
            data_inici: Filtre data inici
            data_fi: Filtre data fi
            
        Returns:
            Tuple (èxit, missatge)
        """
        import csv
        import os
        
        try:
            assignacions = self.db.get_assignacions(data_inici, data_fi)
            
            if not assignacions:
                return False, "No hi ha assignacions per exportar"
            
            # Assegurar directori
            os.makedirs(config.EXPORT_DIR, exist_ok=True)
            
            if not fitxer.endswith('.csv'):
                fitxer += '.csv'
            
            ruta_completa = config.EXPORT_DIR / fitxer
            
            # Escriure CSV
            with open(ruta_completa, 'w', newline='', encoding=config.CSV_ENCODING) as f:
                fieldnames = ['treballador_id', 'treballador', 'plaza', 'data', 
                            'servei', 'inici', 'fi', 'zona', 'linia']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(assignacions)
            
            logger.info(f"Assignacions exportades a {ruta_completa}")
            return True, f"Fitxer guardat: {ruta_completa}"
            
        except Exception as e:
            logger.error(f"Error exportant assignacions: {e}")
            return False, f"Error: {str(e)}"

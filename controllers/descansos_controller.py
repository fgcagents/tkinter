"""
Controller per gestionar descansos
Migra la lògica de descans_sqlite_interactiu_v4.py
"""
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from models.database import DatabaseManager
import config

logger = logging.getLogger(__name__)


class DescansosController:
    """Gestiona totes les operacions relacionades amb descansos"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        """
        Inicialitza el controller
        
        Args:
            db_manager: Gestor de base de dades. Si no s'especifica, crea un nou
        """
        self.db = db_manager or DatabaseManager()
        logger.info("DescansosController inicialitzat")
    
    # ========================================================================
    # CERCA DE TREBALLADORS
    # ========================================================================
    
    def buscar_treballador(self, terme: str) -> List[Dict]:
        """
        Busca treballadors per nom, ID o plaça
        
        Args:
            terme: Text a buscar
            
        Returns:
            Llista de treballadors que coincideixen
        """
        if not terme or len(terme) < 2:
            return []
        
        try:
            treballadors = self.db.buscar_treballadors(terme)
            logger.info(f"Cerca '{terme}': {len(treballadors)} resultats")
            return treballadors
        except Exception as e:
            logger.error(f"Error en cerca de treballadors: {e}")
            return []
    
    def get_treballador_by_id(self, treballador_id: str) -> Optional[Dict]:
        """Obté un treballador per ID"""
        try:
            return self.db.get_treballador_by_id(treballador_id)
        except Exception as e:
            logger.error(f"Error obtenint treballador {treballador_id}: {e}")
            return None
    
    # ========================================================================
    # GESTIÓ DE DESCANSOS
    # ========================================================================
    
    def veure_descansos(self, treballador_id: str, any: int = None) -> List[Dict]:
        """
        Mostra els descansos d'un treballador per any
        
        Args:
            treballador_id: ID del treballador
            any: Any a consultar (si no s'especifica, any actual)
            
        Returns:
            Llista de descansos ordenats per data
        """
        if any is None:
            any = datetime.now().year
        
        try:
            descansos = self.db.get_descansos(
                treballador_id=treballador_id,
                any=any
            )
            logger.info(f"Descansos de {treballador_id} ({any}): {len(descansos)}")
            return descansos
        except Exception as e:
            logger.error(f"Error obtenint descansos: {e}")
            return []
    
    def get_descansos_periode(self, treballador_id: str,
                             data_inici: date, data_fi: date) -> List[Dict]:
        """Obté descansos en un període específic"""
        try:
            return self.db.get_descansos(
                treballador_id=treballador_id,
                data_inici=data_inici,
                data_fi=data_fi
            )
        except Exception as e:
            logger.error(f"Error obtenint descansos per període: {e}")
            return []
    
    def afegir_descans(self, treballador_id: str, data: date,
                      origen: str = 'manual', motiu: str = None) -> Tuple[bool, str]:
        """
        Afegeix un descans individual
        
        Args:
            treballador_id: ID del treballador
            data: Data del descans
            origen: Origen (manual, temporal, baixa, base)
            motiu: Motiu opcional
            
        Returns:
            Tuple (èxit, missatge)
        """
        # Validació
        if not treballador_id:
            return False, "ID de treballador no vàlid"
        
        # Verificar que el treballador existeix
        treballador = self.get_treballador_by_id(treballador_id)
        if not treballador:
            return False, f"Treballador {treballador_id} no trobat"
        
        # Afegir el descans
        try:
            success = self.db.add_descans(treballador_id, data, origen, motiu)
            if success:
                return True, f"Descans afegit: {data.strftime(config.DATE_FORMAT_DISPLAY)}"
            else:
                return False, "El descans ja existeix"
        except Exception as e:
            logger.error(f"Error afegint descans: {e}")
            return False, f"Error: {str(e)}"
    
    def afegir_periode_descansos(self, treballador_id: str,
                                data_inici: date, data_fi: date,
                                origen: str = 'temporal',
                                motiu: str = None) -> Tuple[bool, str]:
        """
        Afegeix un període de descansos
        
        Args:
            treballador_id: ID del treballador
            data_inici: Data d'inici
            data_fi: Data fi
            origen: Origen (temporal, baixa, base)
            motiu: Motiu opcional
            
        Returns:
            Tuple (èxit, missatge)
        """
        # Validacions
        if data_inici > data_fi:
            return False, "La data d'inici ha de ser anterior a la data fi"
        
        if not treballador_id:
            return False, "ID de treballador no vàlid"
        
        # Verificar treballador
        treballador = self.get_treballador_by_id(treballador_id)
        if not treballador:
            return False, f"Treballador {treballador_id} no trobat"
        
        # Calcular nombre de dies
        dies_totals = (data_fi - data_inici).days + 1
        
        # Validar nombre màxim de dies
        if dies_totals > 365:
            return False, "El període no pot superar 365 dies"
        
        try:
            dies_afegits = self.db.add_periode_descansos(
                treballador_id, data_inici, data_fi, origen, motiu
            )
            
            if dies_afegits > 0:
                msg = f"Període afegit: {dies_afegits} de {dies_totals} dies"
                if dies_afegits < dies_totals:
                    msg += f" ({dies_totals - dies_afegits} ja existien)"
                return True, msg
            else:
                return False, "Tots els dies ja existien"
                
        except Exception as e:
            logger.error(f"Error afegint període: {e}")
            return False, f"Error: {str(e)}"
    
    def eliminar_descans(self, treballador_id: str, data: date) -> Tuple[bool, str]:
        """
        Elimina un descans individual
        
        Returns:
            Tuple (èxit, missatge)
        """
        try:
            success = self.db.delete_descans(treballador_id, data)
            if success:
                return True, f"Descans eliminat: {data.strftime(config.DATE_FORMAT_DISPLAY)}"
            else:
                return False, "Descans no trobat"
        except Exception as e:
            logger.error(f"Error eliminant descans: {e}")
            return False, f"Error: {str(e)}"
    
    def eliminar_periode_descansos(self, treballador_id: str,
                                  data_inici: date, data_fi: date) -> Tuple[bool, str]:
        """
        Elimina un període de descansos
        
        Returns:
            Tuple (èxit, missatge)
        """
        # Validacions
        if data_inici > data_fi:
            return False, "La data d'inici ha de ser anterior a la data fi"
        
        try:
            dies_eliminats = self.db.delete_periode_descansos(
                treballador_id, data_inici, data_fi
            )
            
            if dies_eliminats > 0:
                return True, f"Període eliminat: {dies_eliminats} dies"
            else:
                return False, "No s'han trobat descansos en aquest període"
                
        except Exception as e:
            logger.error(f"Error eliminant període: {e}")
            return False, f"Error: {str(e)}"
    
    # ========================================================================
    # GESTIÓ DE BAIXES
    # ========================================================================
    
    def gestionar_baixa_llarga(self, treballador_id: str,
                              data_inici: date, data_fi: date,
                              motiu: str = None) -> Tuple[bool, str]:
        """
        Gestiona una baixa llarga (origen='baixa')
        
        Returns:
            Tuple (èxit, missatge)
        """
        return self.afegir_periode_descansos(
            treballador_id, data_inici, data_fi,
            origen='baixa', motiu=motiu
        )
    
    def alertar_baixes_pendents(self) -> List[Dict]:
        """
        Detecta baixes llargues que encara estan actives
        
        Returns:
            Llista de baixes pendents amb informació del treballador
        """
        avui = date.today()
        
        try:
            # Obtenir descansos de tipus 'baixa' que afecten avui o futures dates
            query = """
                SELECT 
                    d.treballador_id,
                    t.treballador,
                    t.plaza,
                    MIN(d.data) as data_inici,
                    MAX(d.data) as data_fi,
                    d.motiu,
                    COUNT(*) as dies_totals
                FROM descansos_dies d
                LEFT JOIN treballadors t ON d.treballador_id = t.id
                WHERE d.origen = 'baixa' AND d.data >= ?
                GROUP BY d.treballador_id, d.motiu
                ORDER BY data_inici
            """
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (avui.strftime(config.DATE_FORMAT),))
                rows = cursor.fetchall()
                
                baixes = []
                for row in rows:
                    baixes.append({
                        'treballador_id': row['treballador_id'],
                        'treballador': row['treballador'],
                        'plaza': row['plaza'],
                        'data_inici': datetime.strptime(row['data_inici'], config.DATE_FORMAT).date(),
                        'data_fi': datetime.strptime(row['data_fi'], config.DATE_FORMAT).date(),
                        'motiu': row['motiu'],
                        'dies_totals': row['dies_totals']
                    })
                
                logger.info(f"Baixes pendents detectades: {len(baixes)}")
                return baixes
                
        except Exception as e:
            logger.error(f"Error alertant baixes: {e}")
            return []
    
    # ========================================================================
    # ESTADÍSTIQUES
    # ========================================================================
    
    def get_estadistiques_descansos(self, any: int = None) -> Dict:
        """
        Obté estadístiques globals de descansos per any
        
        Returns:
            Diccionari amb estadístiques
        """
        if any is None:
            any = datetime.now().year
        
        try:
            # Total descansos per treballador
            query = """
                SELECT 
                    d.treballador_id,
                    t.treballador,
                    COUNT(*) as total_descansos,
                    SUM(CASE WHEN d.origen = 'base' THEN 1 ELSE 0 END) as base,
                    SUM(CASE WHEN d.origen = 'temporal' THEN 1 ELSE 0 END) as temporal,
                    SUM(CASE WHEN d.origen = 'baixa' THEN 1 ELSE 0 END) as baixa,
                    SUM(CASE WHEN d.origen = 'manual' THEN 1 ELSE 0 END) as manual
                FROM descansos_dies d
                LEFT JOIN treballadors t ON d.treballador_id = t.id
                WHERE strftime('%Y', d.data) = ?
                GROUP BY d.treballador_id
                ORDER BY total_descansos DESC
            """
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (str(any),))
                rows = cursor.fetchall()
                
                estadistiques = {
                    'any': any,
                    'total_treballadors': len(rows),
                    'descansos_per_treballador': [dict(row) for row in rows],
                    'total_descansos': sum(row['total_descansos'] for row in rows)
                }
                
                return estadistiques
                
        except Exception as e:
            logger.error(f"Error calculant estadístiques: {e}")
            return {'any': any, 'error': str(e)}
    
    def get_treballadors_disponibles(self, data: date) -> List[Dict]:
        """
        Obté treballadors disponibles en una data específica
        
        Args:
            data: Data a consultar
            
        Returns:
            Llista de treballadors disponibles
        """
        try:
            query = """
                SELECT t.*
                FROM treballadors t
                WHERE t.id NOT IN (
                    SELECT treballador_id 
                    FROM descansos_dies 
                    WHERE data = ?
                )
                ORDER BY t.treballador
            """
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (data.strftime(config.DATE_FORMAT),))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error obtenint disponibles: {e}")
            return []
    
    # ========================================================================
    # VALIDACIONS
    # ========================================================================
    
    def validar_descansos_any(self, treballador_id: str, any: int) -> Dict:
        """
        Valida els descansos d'un treballador per any
        
        Returns:
            Diccionari amb resultats de validació
        """
        descansos = self.veure_descansos(treballador_id, any)
        
        total = len(descansos)
        per_origen = {}
        
        for d in descansos:
            origen = d.get('origen', 'desconegut')
            per_origen[origen] = per_origen.get(origen, 0) + 1
        
        validacio = {
            'treballador_id': treballador_id,
            'any': any,
            'total_descansos': total,
            'per_origen': per_origen,
            'es_valid': total <= config.MAX_DESCANSOS_ANY,
            'max_permesos': config.MAX_DESCANSOS_ANY
        }
        
        if not validacio['es_valid']:
            validacio['alerta'] = f"Supera el màxim de {config.MAX_DESCANSOS_ANY} dies"
        
        return validacio

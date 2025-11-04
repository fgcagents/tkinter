"""
Gestió centralitzada de la base de dades SQLite
Proporciona context managers i operacions CRUD segures
"""
import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Optional, Any
from datetime import datetime, date
import logging
import config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gestor centralitzat de connexions i operacions amb SQLite"""
    
    def __init__(self, db_path: str = None):
        """
        Inicialitza el gestor de base de dades
        
        Args:
            db_path: Ruta a la base de dades. Si no s'especifica, usa config.DB_PATH
        """
        self.db_path = db_path or str(config.DB_PATH)
        logger.info(f"DatabaseManager inicialitzat amb BD: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """
        Context manager per gestionar connexions de manera segura
        
        Usage:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(...)
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Permet accés per nom de columna
            logger.debug("Connexió establerta")
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Error de base de dades: {e}")
            raise
        finally:
            if conn:
                conn.close()
                logger.debug("Connexió tancada")
    
    def execute_query(self, query: str, params: tuple = None) -> List[sqlite3.Row]:
        """
        Executa una consulta SELECT i retorna resultats
        
        Args:
            query: Consulta SQL
            params: Paràmetres de la consulta
            
        Returns:
            Llista de files (sqlite3.Row)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        Executa una consulta INSERT/UPDATE/DELETE
        
        Args:
            query: Consulta SQL
            params: Paràmetres de la consulta
            
        Returns:
            Nombre de files afectades
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.rowcount
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        Executa múltiples operacions en batch
        
        Args:
            query: Consulta SQL
            params_list: Llista de tuples amb paràmetres
            
        Returns:
            Nombre total de files afectades
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    # ========================================================================
    # OPERACIONS CRUD - TREBALLADORS
    # ========================================================================
    
    def get_treballadors(self, filters: Dict[str, Any] = None) -> List[Dict]:
        """
        Obté tots els treballadors amb filtres opcionals
        
        Args:
            filters: Diccionari amb filtres (ex: {'grup': 'T', 'zona': 'A'})
            
        Returns:
            Llista de diccionaris amb dades de treballadors
        """
        query = "SELECT * FROM treballadors"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY treballador"
        
        rows = self.execute_query(query, tuple(params) if params else None)
        return [dict(row) for row in rows]
    
    def get_treballador_by_id(self, treballador_id: str) -> Optional[Dict]:
        """Obté un treballador per ID"""
        query = "SELECT * FROM treballadors WHERE id = ?"
        rows = self.execute_query(query, (treballador_id,))
        return dict(rows[0]) if rows else None
    
    def buscar_treballadors(self, terme: str) -> List[Dict]:
        """
        Busca treballadors per nom, ID o plaça
        
        Args:
            terme: Text a buscar
            
        Returns:
            Llista de treballadors que coincideixen
        """
        query = """
            SELECT id, treballador, plaza, rotacio, zona, grup
            FROM treballadors
            WHERE id LIKE ? OR treballador LIKE ? OR plaza LIKE ?
            ORDER BY treballador
        """
        params = (f'%{terme}%', f'%{terme}%', f'%{terme}%')
        rows = self.execute_query(query, params)
        return [dict(row) for row in rows]
    
    def add_treballador(self, data: Dict) -> bool:
        """
        Afegeix un nou treballador
        
        Args:
            data: Diccionari amb dades del treballador
            
        Returns:
            True si s'ha afegit correctament
        """
        query = """
            INSERT INTO treballadors 
            (id, treballador, plaza, rotacio, zona, grup, linia, habilitacions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data.get('id'),
            data.get('treballador'),
            data.get('plaza'),
            data.get('rotacio'),
            data.get('zona'),
            data.get('grup'),
            data.get('linia'),
            data.get('habilitacions')
        )
        try:
            self.execute_update(query, params)
            logger.info(f"Treballador afegit: {data.get('id')}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Treballador duplicat: {data.get('id')}")
            return False
    
    def update_treballador(self, treballador_id: str, data: Dict) -> bool:
        """
        Actualitza un treballador existent
        
        Args:
            treballador_id: ID del treballador
            data: Diccionari amb camps a actualitzar
            
        Returns:
            True si s'ha actualitzat correctament
        """
        # Construïm la query dinàmicament segons els camps proporcionats
        fields = []
        params = []
        for key, value in data.items():
            if key != 'id':  # No actualitzem l'ID
                fields.append(f"{key} = ?")
                params.append(value)
        
        if not fields:
            return False
        
        params.append(treballador_id)
        query = f"UPDATE treballadors SET {', '.join(fields)} WHERE id = ?"
        
        rows_affected = self.execute_update(query, tuple(params))
        logger.info(f"Treballador actualitzat: {treballador_id}")
        return rows_affected > 0
    
    def delete_treballador(self, treballador_id: str) -> bool:
        """
        Elimina un treballador
        
        Args:
            treballador_id: ID del treballador
            
        Returns:
            True si s'ha eliminat correctament
        """
        query = "DELETE FROM treballadors WHERE id = ?"
        rows_affected = self.execute_update(query, (treballador_id,))
        logger.info(f"Treballador eliminat: {treballador_id}")
        return rows_affected > 0
    
    # ========================================================================
    # OPERACIONS CRUD - DESCANSOS
    # ========================================================================
    
    def get_descansos(self, treballador_id: str = None, 
                      data_inici: date = None, 
                      data_fi: date = None,
                      any: int = None) -> List[Dict]:
        """
        Obté descansos amb filtres opcionals
        
        Args:
            treballador_id: Filtrar per treballador
            data_inici: Data d'inici del període
            data_fi: Data fi del període
            any: Filtrar per any específic
            
        Returns:
            Llista de descansos
        """
        query = """
            SELECT d.*, t.treballador, t.plaza
            FROM descansos_dies d
            LEFT JOIN treballadors t ON d.treballador_id = t.id
            WHERE 1=1
        """
        params = []
        
        if treballador_id:
            query += " AND d.treballador_id = ?"
            params.append(treballador_id)
        
        if data_inici:
            query += " AND d.data >= ?"
            params.append(data_inici.strftime(config.DATE_FORMAT))
        
        if data_fi:
            query += " AND d.data <= ?"
            params.append(data_fi.strftime(config.DATE_FORMAT))
        
        if any:
            query += " AND strftime('%Y', d.data) = ?"
            params.append(str(any))
        
        query += " ORDER BY d.data DESC"
        
        rows = self.execute_query(query, tuple(params) if params else None)
        return [dict(row) for row in rows]
    
    def add_descans(self, treballador_id: str, data: date, 
                    origen: str = 'manual', motiu: str = None) -> bool:
        """
        Afegeix un descans
        
        Args:
            treballador_id: ID del treballador
            data: Data del descans
            origen: Origen del descans (manual, temporal, baixa, base)
            motiu: Motiu del descans
            
        Returns:
            True si s'ha afegit correctament
        """
        query = """
            INSERT INTO descansos_dies (treballador_id, data, origen, motiu)
            VALUES (?, ?, ?, ?)
        """
        params = (treballador_id, data.strftime(config.DATE_FORMAT), origen, motiu)
        try:
            self.execute_update(query, params)
            logger.info(f"Descans afegit: {treballador_id} - {data}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Descans ja existent: {treballador_id} - {data}")
            return False
    
    def delete_descans(self, treballador_id: str, data: date) -> bool:
        """
        Elimina un descans
        
        Args:
            treballador_id: ID del treballador
            data: Data del descans
            
        Returns:
            True si s'ha eliminat correctament
        """
        query = "DELETE FROM descansos_dies WHERE treballador_id = ? AND data = ?"
        params = (treballador_id, data.strftime(config.DATE_FORMAT))
        rows_affected = self.execute_update(query, params)
        logger.info(f"Descans eliminat: {treballador_id} - {data}")
        return rows_affected > 0
    
    def add_periode_descansos(self, treballador_id: str, data_inici: date,
                             data_fi: date, origen: str = 'temporal',
                             motiu: str = None) -> int:
        """
        Afegeix un període de descansos
        
        Args:
            treballador_id: ID del treballador
            data_inici: Data d'inici
            data_fi: Data fi
            origen: Origen (temporal, baixa, etc.)
            motiu: Motiu
            
        Returns:
            Nombre de dies afegits
        """
        from datetime import timedelta
        
        data_actual = data_inici
        dies_afegits = 0
        
        while data_actual <= data_fi:
            if self.add_descans(treballador_id, data_actual, origen, motiu):
                dies_afegits += 1
            data_actual += timedelta(days=1)
        
        logger.info(f"Període afegit: {treballador_id} - {dies_afegits} dies")
        return dies_afegits
    
    def delete_periode_descansos(self, treballador_id: str, 
                                 data_inici: date, data_fi: date) -> int:
        """
        Elimina un període de descansos
        
        Returns:
            Nombre de dies eliminats
        """
        query = """
            DELETE FROM descansos_dies 
            WHERE treballador_id = ? AND data BETWEEN ? AND ?
        """
        params = (
            treballador_id,
            data_inici.strftime(config.DATE_FORMAT),
            data_fi.strftime(config.DATE_FORMAT)
        )
        rows_affected = self.execute_update(query, params)
        logger.info(f"Període eliminat: {treballador_id} - {rows_affected} dies")
        return rows_affected
    
    # ========================================================================
    # OPERACIONS - SERVEIS
    # ========================================================================
    
    def get_serveis(self) -> List[Dict]:
        """Obté tots els serveis"""
        query = "SELECT * FROM serveis ORDER BY servei"
        rows = self.execute_query(query)
        return [dict(row) for row in rows]
    
    # ========================================================================
    # OPERACIONS - ASSIGNACIONS
    # ========================================================================
    
    def get_assignacions(self, data_inici: date = None, 
                        data_fi: date = None) -> List[Dict]:
        """
        Obté assignacions amb filtres opcionals
        
        Args:
            data_inici: Data d'inici
            data_fi: Data fi
            
        Returns:
            Llista d'assignacions
        """
        query = """
            SELECT a.*, t.treballador, t.plaza
            FROM assig_grup_T a
            LEFT JOIN treballadors t ON a.treballador_id = t.id
            WHERE 1=1
        """
        params = []
        
        if data_inici:
            query += " AND a.data >= ?"
            params.append(data_inici.strftime(config.DATE_FORMAT))
        
        if data_fi:
            query += " AND a.data <= ?"
            params.append(data_fi.strftime(config.DATE_FORMAT))
        
        query += " ORDER BY a.data, a.servei"
        
        rows = self.execute_query(query, tuple(params) if params else None)
        return [dict(row) for row in rows]
    
    def clear_assignacions(self) -> int:
        """Neteja la taula d'assignacions"""
        query = "DELETE FROM assig_grup_T"
        rows_affected = self.execute_update(query)
        logger.info(f"Taula assig_grup_T netejada: {rows_affected} registres")
        return rows_affected
    
    # ========================================================================
    # UTILITATS
    # ========================================================================
    
    def test_connection(self) -> bool:
        """
        Prova la connexió a la base de dades
        
        Returns:
            True si la connexió és vàlida
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Error en test de connexió: {e}")
            return False
    
    def get_table_info(self, table_name: str) -> List[Dict]:
        """Obté informació de l'esquema d'una taula"""
        query = f"PRAGMA table_info({table_name})"
        rows = self.execute_query(query)
        return [dict(row) for row in rows]

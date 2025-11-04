"""
Controller per analitzar disponibilitat de serveis
Lògica exacta de dispo_serveis_sqlite_v6.py
"""
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from models.database import DatabaseManager
import config

logger = logging.getLogger(__name__)


class DisponibilitatController:
    """Gestiona l'anàlisi de disponibilitat de serveis"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        """Inicialitza el controller"""
        self.db = db_manager or DatabaseManager()
        logger.info("DisponibilitatController inicialitzat")
    
    # ========================================================================
    # CÀRREGA DE DADES
    # ========================================================================
    
    def carregar_treballadors_i_descansos(self) -> Dict[str, Dict]:
        """
        Carrega tots els treballadors amb els seus descansos
        
        Returns:
            Diccionari amb treballadors indexats per plaza
        """
        try:
            treballadors = self.db.get_treballadors()
            treballadors_dict = {}
            
            for t in treballadors:
                plaza = t['plaza']
                treballadors_dict[plaza] = {
                    'id': t['id'],
                    'nom': t['treballador'],
                    'plaza': plaza,
                    'rotacio': t.get('rotacio'),
                    'zona': t.get('zona'),
                    'grup': t.get('grup'),
                    'descansos': set()  # Set de dates
                }
            
            # Carregar descansos
            descansos = self.db.get_descansos()
            for d in descansos:
                treballador_id = d['treballador_id']
                data_str = d['data']
                data_obj = datetime.strptime(data_str, config.DATE_FORMAT).date()
                
                # Trobar plaza del treballador
                for plaza, info in treballadors_dict.items():
                    if info['id'] == treballador_id:
                        info['descansos'].add(data_obj)
                        break
            
            logger.info(f"Carregats {len(treballadors_dict)} treballadors amb descansos")
            return treballadors_dict
            
        except Exception as e:
            logger.error(f"Error carregant treballadors i descansos: {e}")
            return {}
    
    def carregar_serveis(self) -> List[Dict]:
        """
        Carrega els serveis amb opcio_1 i opcio_2
        
        Returns:
            Llista de serveis
        """
        try:
            query = "SELECT * FROM serveis"
            rows = self.db.execute_query(query)
            
            serveis_list = []
            for row in rows:
                row_dict = dict(row)
                
                servei_dict = {
                    'servei': row_dict['servei'],
                    'opció_1': row_dict.get('opcio_1'),  # Amb guió baix!
                    'opció_2': row_dict.get('opcio_2')   # Amb guió baix!
                }
                
                # Afegir columnes opcionals amb compatibilitat
                # Preferim 'rotacio', fallback 'torn'
                if 'rotacio' in row_dict and row_dict['rotacio']:
                    servei_dict['rotacio'] = row_dict['rotacio']
                elif 'torn' in row_dict:
                    servei_dict['rotacio'] = row_dict['torn']
                else:
                    servei_dict['rotacio'] = None
                
                servei_dict['formacio'] = row_dict.get('formacio')
                servei_dict['linia'] = row_dict.get('linia')
                servei_dict['zona'] = row_dict.get('zona')
                
                serveis_list.append(servei_dict)
            
            logger.info(f"Carregats {len(serveis_list)} serveis")
            return serveis_list
            
        except Exception as e:
            logger.error(f"Error carregant serveis: {e}")
            return []
    
    # ========================================================================
    # ANÀLISI DE DISPONIBILITAT (LÒGICA ORIGINAL EXACTA)
    # ========================================================================
    
    def generar_dates_interval(self, data_inici: date, data_fi: date) -> List[date]:
        """Genera totes les dates de l'interval"""
        dates = []
        data_actual = data_inici
        while data_actual <= data_fi:
            dates.append(data_actual)
            data_actual += timedelta(days=1)
        return dates
    
    def treballador_disponible_per_dia(self, treballador_info: Dict, data: date) -> bool:
        """Comprova si un treballador està disponible un dia específic"""
        return data not in treballador_info['descansos']
    
    def analitzar_disponibilitat(self, data_inici: date, data_fi: date,
                                progress_callback=None) -> Dict:
        """
        Analitza la disponibilitat de serveis en un interval
        LÒGICA EXACTA del script original
        
        Args:
            data_inici: Data d'inici
            data_fi: Data fi
            progress_callback: Funció per notificar progrés (opcional)
            
        Returns:
            Diccionari amb resultats de l'anàlisi i assignacions per guardar
        """
        logger.info(f"Analitzant disponibilitat: {data_inici} - {data_fi}")
        
        # Validacions
        if data_inici > data_fi:
            return {'error': 'Data inici posterior a data fi'}
        
        dies_totals = (data_fi - data_inici).days + 1
        if dies_totals > 180:
            return {'error': 'El període no pot superar 180 dies'}
        
        # Carregar dades
        treballadors = self.carregar_treballadors_i_descansos()
        serveis = self.carregar_serveis()
        
        if not treballadors or not serveis:
            return {'error': 'No s\'han pogut carregar les dades'}
        
        logger.info(f"Treballadors carregats: {len(treballadors)}")
        logger.info(f"Serveis carregats: {len(serveis)}")
        
        # Generar dates
        dates = self.generar_dates_interval(data_inici, data_fi)
        
        # Diccionari per guardar assignacions per dia
        assignacions_per_dia = {data: {'coberts': [], 'descoberts': []} for data in dates}
        treballadors_ocupats_per_dia = {data: set() for data in dates}
        
        # Processar cada dia
        for idx, data_actual in enumerate(dates):
            if progress_callback:
                progress = int((idx + 1) / len(dates) * 100)
                progress_callback(progress)
            
            serveis_coberts_avui = []
            serveis_descoberts_avui = []
            
            # Processar cada servei
            for servei in serveis:
                treballador_trobat = None
                plaza_trobada = None
                motiu_no_cobert = "No trobat"
                prioritat = None
                
                # Buscar per opció_1 (PRIMERA PRIORITAT)
                if servei['opció_1'] in treballadors:
                    treballador_info = treballadors[servei['opció_1']]
                    if (self.treballador_disponible_per_dia(treballador_info, data_actual) and
                        treballador_info['nom'] not in treballadors_ocupats_per_dia[data_actual]):
                        treballador_trobat = treballador_info['nom']
                        plaza_trobada = servei['opció_1']
                        prioritat = 'opció_1'
                        motiu_no_cobert = None
                
                # Si no troba, buscar per opció_2 (SEGONA PRIORITAT)
                if not treballador_trobat and servei['opció_2'] in treballadors:
                    treballador_info = treballadors[servei['opció_2']]
                    if (self.treballador_disponible_per_dia(treballador_info, data_actual) and
                        treballador_info['nom'] not in treballadors_ocupats_per_dia[data_actual]):
                        treballador_trobat = treballador_info['nom']
                        plaza_trobada = servei['opció_2']
                        prioritat = 'opció_2'
                        motiu_no_cobert = None
                
                if treballador_trobat:
                    # Servei COBERT
                    servei_assignat = servei.copy()
                    servei_assignat['treballador'] = treballador_trobat
                    servei_assignat['treballador_id'] = treballadors[plaza_trobada]['id']
                    servei_assignat['plaza_trobada'] = plaza_trobada
                    servei_assignat['prioritat'] = prioritat
                    servei_assignat['data'] = data_actual.strftime(config.DATE_FORMAT)
                    servei_assignat['grup'] = treballadors[plaza_trobada]['grup']
                    
                    serveis_coberts_avui.append(servei_assignat)
                    treballadors_ocupats_per_dia[data_actual].add(treballador_trobat)
                else:
                    # Servei DESCOBERT - Determinar motiu específic
                    if servei['opció_1'] in treballadors:
                        treballador_info = treballadors[servei['opció_1']]
                        if not self.treballador_disponible_per_dia(treballador_info, data_actual):
                            motiu_no_cobert = "Té descans"
                        elif treballador_info['nom'] in treballadors_ocupats_per_dia[data_actual]:
                            motiu_no_cobert = "Treballador ocupat"
                    elif servei['opció_2'] in treballadors:
                        treballador_info = treballadors[servei['opció_2']]
                        if not self.treballador_disponible_per_dia(treballador_info, data_actual):
                            motiu_no_cobert = "Té descans"
                        elif treballador_info['nom'] in treballadors_ocupats_per_dia[data_actual]:
                            motiu_no_cobert = "Treballador ocupat"
                    
                    servei_no_cobert = servei.copy()
                    servei_no_cobert['motiu_no_cobert'] = motiu_no_cobert
                    servei_no_cobert['data'] = data_actual.strftime(config.DATE_FORMAT)
                    
                    serveis_descoberts_avui.append(servei_no_cobert)
            
            assignacions_per_dia[data_actual]['coberts'] = serveis_coberts_avui
            assignacions_per_dia[data_actual]['descoberts'] = serveis_descoberts_avui
        
        # Calcular resum
        resum_coberts = []
        resum_descoberts = []
        
        for data_actual in dates:
            resum_coberts.extend(assignacions_per_dia[data_actual]['coberts'])
            resum_descoberts.extend(assignacions_per_dia[data_actual]['descoberts'])
        
        total_serveis = len(resum_coberts) + len(resum_descoberts)
        total_coberts = len(resum_coberts)
        total_descoberts = len(resum_descoberts)
        
        percentatge_cobertura = (total_coberts / total_serveis * 100) if total_serveis > 0 else 0
        
        resum = {
            'data_inici': data_inici,
            'data_fi': data_fi,
            'dies_analitzats': len(dates),
            'total_serveis': total_serveis,
            'total_coberts': total_coberts,
            'total_descoberts': total_descoberts,
            'percentatge_cobertura': round(percentatge_cobertura, 2)
        }
        
        logger.info(f"Anàlisi completada: {percentatge_cobertura:.2f}% cobertura")
        logger.info(f"Coberts: {total_coberts}, Descoberts: {total_descoberts}")
        
        # Preparar resultats per visualització
        resultats_display = []
        for data_actual in dates:
            dia_setmana = data_actual.strftime('%A')
            
            for servei in assignacions_per_dia[data_actual]['coberts']:
                resultats_display.append({
                    'data': data_actual,
                    'dia_setmana': dia_setmana,
                    'servei': servei['servei'],
                    'zona': servei.get('zona', ''),
                    'linia': servei.get('linia', ''),
                    'disponibles': 1,
                    'estat': 'Cobert',
                    'treballador': servei.get('treballador', '')
                })
            
            for servei in assignacions_per_dia[data_actual]['descoberts']:
                resultats_display.append({
                    'data': data_actual,
                    'dia_setmana': dia_setmana,
                    'servei': servei['servei'],
                    'zona': servei.get('zona', ''),
                    'linia': servei.get('linia', ''),
                    'disponibles': 0,
                    'estat': 'Descobert',
                    'motiu': servei.get('motiu_no_cobert', '')
                })
        
        return {
            'resum': resum,
            'resultats': resultats_display,
            'assignacions_per_dia': assignacions_per_dia
        }
    
    # ========================================================================
    # GUARDAR RESULTATS A LA BASE DE DADES (LÒGICA ORIGINAL)
    # ========================================================================
    
    def netejar_taules(self) -> Tuple[int, int]:
        """
        Neteja COMPLETAMENT les taules assig_grup_A i cobertura
        
        Returns:
            Tuple (registres_assig, registres_cobertura) eliminats
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Esborrar assig_grup_A
                cursor.execute("DELETE FROM assig_grup_A")
                registres_assig = cursor.rowcount
                
                # Esborrar cobertura
                cursor.execute("DELETE FROM cobertura")
                registres_cobertura = cursor.rowcount
                
                conn.commit()
                
                logger.info(f"Taules netejades: {registres_assig} (assig_grup_A), "
                          f"{registres_cobertura} (cobertura)")
                
                return registres_assig, registres_cobertura
                
        except Exception as e:
            logger.error(f"Error netejant taules: {e}")
            raise
    
    def guardar_assignacions_db(self, assignacions_per_dia: Dict) -> Tuple[bool, str]:
        """
        Guarda les assignacions a la base de dades
        LÒGICA EXACTA del script original
        
        Args:
            assignacions_per_dia: Diccionari amb assignacions per cada dia
            
        Returns:
            Tuple (èxit, missatge)
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                total_coberts = 0
                total_descoberts = 0
                
                for data_actual, assignacions in assignacions_per_dia.items():
                    data_str = data_actual.strftime(config.DATE_FORMAT)
                    
                    # A. Serveis COBERTS → Taula assig_grup_A
                    for servei in assignacions['coberts']:
                        timestamp_apunt = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                        
                        cursor.execute("""
                            INSERT INTO assig_grup_A 
                            (servei, treballador_id, data, prioritat, estat, grup, 
                             rotacio, formacio, linia, zona, data_apunt)
                            VALUES (?, ?, ?, ?, 'cobert', ?, ?, ?, ?, ?, ?)
                        """, (
                            servei['servei'],
                            servei['treballador_id'],
                            data_str,
                            servei['prioritat'],
                            servei.get('grup'),
                            servei.get('rotacio'),
                            servei.get('formacio'),
                            servei.get('linia'),
                            servei.get('zona'),
                            timestamp_apunt
                        ))
                        total_coberts += 1
                    
                    # B. Serveis DESCOBERTS → Taula cobertura
                    for servei in assignacions['descoberts']:
                        cursor.execute("""
                            INSERT INTO cobertura 
                            (servei, data, motiu_no_cobert, rotacio, formacio, linia, zona)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            servei['servei'],
                            data_str,
                            servei.get('motiu_no_cobert'),
                            servei.get('rotacio'),
                            servei.get('formacio'),
                            servei.get('linia'),
                            servei.get('zona')
                        ))
                        total_descoberts += 1
                
                conn.commit()
                
                missatge = (f"✅ Assignacions guardades correctament!\n\n"
                          f"• Taula assig_grup_A: {total_coberts} serveis coberts\n"
                          f"• Taula cobertura: {total_descoberts} serveis descoberts")
                
                logger.info(f"Assignacions guardades: {total_coberts} coberts, "
                          f"{total_descoberts} descoberts")
                
                return True, missatge
                
        except Exception as e:
            logger.error(f"Error guardant assignacions: {e}")
            return False, f"Error guardant a la base de dades:\n{str(e)}"
    
    # ========================================================================
    # EXPORTACIÓ
    # ========================================================================
    
    def guardar_a_csv(self, resultats: List[Dict], fitxer: str) -> Tuple[bool, str]:
        """
        Guarda els resultats en un fitxer CSV
        
        Args:
            resultats: Llista de resultats a guardar
            fitxer: Nom del fitxer (sense extensió)
            
        Returns:
            Tuple (èxit, missatge)
        """
        import csv
        import os
        
        try:
            os.makedirs(config.EXPORT_DIR, exist_ok=True)
            
            if not fitxer.endswith('.csv'):
                fitxer += '.csv'
            
            ruta_completa = config.EXPORT_DIR / fitxer
            
            with open(ruta_completa, 'w', newline='', encoding=config.CSV_ENCODING) as f:
                if not resultats:
                    return False, "No hi ha resultats per guardar"
                
                fieldnames = ['data', 'dia_setmana', 'servei', 'zona', 'linia', 
                            'disponibles', 'estat']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                for r in resultats:
                    writer.writerow({
                        'data': r['data'].strftime(config.DATE_FORMAT),
                        'dia_setmana': r['dia_setmana'],
                        'servei': r['servei'],
                        'zona': r['zona'],
                        'linia': r['linia'],
                        'disponibles': r['disponibles'],
                        'estat': r['estat']
                    })
            
            logger.info(f"Resultats guardats a {ruta_completa}")
            return True, f"Fitxer guardat: {ruta_completa}"
            
        except Exception as e:
            logger.error(f"Error guardant CSV: {e}")
            return False, f"Error: {str(e)}"

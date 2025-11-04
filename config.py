"""
Configuració global de l'aplicació
Defineix constants, rutes i paràmetres compartits
"""
import os
from pathlib import Path

# ============================================================================
# RUTES DE BASE DE DADES
# ============================================================================
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / 'treballadors.db'

# Ruta alternativa si vols especificar una ubicació diferent
# DB_PATH = 'C:/ruta/personalitzada/treballadors.db'

# ============================================================================
# PARÀMETRES DE L'ALGORISME GENÈTIC
# ============================================================================
AG_MIDA_POBLACIO = 50
AG_GENERACIONS = 150
AG_PROB_MUTACIO = 0.1

# ============================================================================
# PARÀMETRES DE TREBALLADORS
# ============================================================================
MAX_HORES_ANUALS = 1605.0
MAX_HORES_AMPLIABLES = 1755.0
MAX_DIES_CONSECUTIUS = 9

# ============================================================================
# CONFIGURACIÓ DE LA INTERFÍCIE
# ============================================================================
WINDOW_TITLE = "Gestor de Treballadors - Sistema d'Assignacions"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_MIN_WIDTH = 900
WINDOW_MIN_HEIGHT = 600

# ============================================================================
# COLORS I TEMA
# ============================================================================
COLORS = {
    'primary': '#2E86AB',      # Blau principal
    'secondary': '#A23B72',    # Magenta
    'success': '#06A77D',      # Verd
    'warning': '#F18F01',      # Taronja
    'danger': '#C73E1D',       # Vermell
    'info': '#6C757D',         # Gris
    'light': '#F8F9FA',        # Gris clar
    'dark': '#212529',         # Gris fosc
    'background': '#FFFFFF',   # Blanc
    'text': '#212529',         # Text fosc
}

# ============================================================================
# FORMATS DE DATA
# ============================================================================
DATE_FORMAT = '%Y-%m-%d'
DATE_FORMAT_DISPLAY = '%d/%m/%Y'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# ============================================================================
# CONFIGURACIÓ DE LOGGING
# ============================================================================
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = BASE_DIR / 'logs' / 'app.log'
LOG_MAX_SIZE = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT = 3

# ============================================================================
# MISSATGES DE L'APLICACIÓ
# ============================================================================
MESSAGES = {
    'db_not_found': f"❌ No s'ha trobat la base de dades: {DB_PATH}",
    'db_connection_error': "❌ Error de connexió a la base de dades",
    'operation_success': "✅ Operació realitzada correctament",
    'operation_cancelled': "❌ Operació cancel·lada",
    'confirm_delete': "Estàs segur que vols eliminar aquest registre?",
    'confirm_save': "Vols guardar els canvis?",
}

# ============================================================================
# VALIDACIÓ
# ============================================================================
MAX_DESCANSOS_ANY = 120  # Màxim dies de descans per any
MIN_DESCANS_HORES = 12   # Hores mínimes entre torns

# ============================================================================
# EXPORTACIÓ
# ============================================================================
EXPORT_DIR = BASE_DIR / 'exports'
CSV_ENCODING = 'utf-8-sig'

# Crear directoris necessaris si no existeixen
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

"""
Mòdul core - Algorisme Genètic i Estructures de Dades
Conté la lògica principal de l'algorisme d'assignacions
"""

# Imports de data_structures
from .data_structures import (
    Assignacio,
    Treballador,
    Torn,
    NecessitatCobertura,
    DiaCalendari,
    ServeiTorn,
    EstadistiquesGlobals
)

# Imports de data_loader
from .data_loader import DataLoader

# Imports de genetic_algorithm
from .genetic_algorithm import AlgorismeGenetic

# Imports de constraints
from .constraints import (
    RestriccionManager,
    restriccio_grup_T,
    restriccio_sense_descans,
    restriccio_formacio_requerida,
    restriccio_linia_correcta,
    restriccio_hores_anuals,
    restriccio_dies_consecutius,
    restriccio_equitat_canvis_zona,
    restriccio_equitat_canvis_torn,
    restriccio_cobertura_completa,
    restriccio_distribucio_equilibrada,
    restriccio_sense_solapaments_rigida,
    restriccio_descans_minim_12h_rigida,
    restriccio_divendres_cap_setmana_rigida,
    restriccio_unica_assignacio_per_dia_rigida
)

# Exportem tot per facilitar imports
__all__ = [
    # Data Structures
    'Assignacio',
    'Treballador',
    'Torn',
    'NecessitatCobertura',
    'DiaCalendari',
    'ServeiTorn',
    'EstadistiquesGlobals',
    
    # Data Loader
    'DataLoader',
    
    # Genetic Algorithm
    'AlgorismeGenetic',
    
    # Constraints Manager
    'RestriccionManager',
    
    # Restriccions individuals
    'restriccio_grup_T',
    'restriccio_sense_descans',
    'restriccio_formacio_requerida',
    'restriccio_linia_correcta',
    'restriccio_hores_anuals',
    'restriccio_dies_consecutius',
    'restriccio_equitat_canvis_zona',
    'restriccio_equitat_canvis_torn',
    'restriccio_cobertura_completa',
    'restriccio_distribucio_equilibrada',
    'restriccio_sense_solapaments_rigida',
    'restriccio_descans_minim_12h_rigida',
    'restriccio_divendres_cap_setmana_rigida',
    'restriccio_unica_assignacio_per_dia_rigida'
]

# Informació del mòdul
__version__ = '1.0.0'
__author__ = 'Sistema de Gestió de Treballadors'

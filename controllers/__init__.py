"""
Mòdul de controllers
Gestiona la lògica de negoci entre models i vistes
"""
from .descansos_controller import DescansosController
from .disponibilitat_controller import DisponibilitatController
from .genetic_controller import GeneticController

__all__ = ['DescansosController', 'DisponibilitatController', 'GeneticController']

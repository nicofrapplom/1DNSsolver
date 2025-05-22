"""
Nome file: solver/createFields.py
"""

import numpy as np

def initialize_pressure(num_nodes: int, p_i_IO: float, p_i_IE: float) -> np.ndarray:
    """
    Inizializza la pressione nei nodi tramite interpolazione lineare tra ingresso e uscita.
    """
    return np.linspace(p_i_IO, p_i_IE, num_nodes)

def initialize_temperature(num_nodes: int, T_i_IE: float) -> np.ndarray:
    """
    Inizializza la temperatura nei nodi con un valore uniforme iniziale.
    """
    return np.full(num_nodes, T_i_IE)

def initialize_velocity(num_branches: int) -> np.ndarray:
    """
    Inizializza la velocità nei rami con zeri (condizione di quiete).
    """
    return np.zeros(num_branches)
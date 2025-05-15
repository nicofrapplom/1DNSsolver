# -*- coding: utf-8 -*-
"""
Definizioni delle classi Modello: BaseStretch, Stretch, Tube, Branch.
Queste classi sono progettate per essere coerenti con l'output di `to_grafo`
e con la classe `Tunnel` precedentemente definita.

@author: d.zaffino (adattato da Gemini)
"""

from typing import Dict, List, Optional, Tuple
from models.tube import Tubes
from models.segment import Segment

# Valori di default globali per temperatura e pressione se non specificati altrimenti
DEFAULT_TEMPERATURE = 293.15  # Kelvin
DEFAULT_PRESSURE = 101325.0  # Pascal


class Branch:
    """
    Rappresenta una branch (galleria, pozzo, etc.) del tunnel.
    """

    def __init__(self, name: str, branch_data_processed: Dict, boundary_data: Dict):
        """
        Args:
            name (str): Nome della branch.
            branch_data_processed (Dict): Dati della branch elaborati da to_grafo.
                                          Contiene coordinate assolute e riferimenti.
            boundary_data (Dict): Dati delle boundary del tunnel, per derivare temp/press di default.
        """
        self.name: str = name
        self.branch_type: Optional[str] = branch_data_processed.get("branch_type")
        self.length: Optional[float] = branch_data_processed.get("length")

        # start_point è [(absolute_start_x, ref_name_start)]
        self.start_point: Optional[List[Tuple[float, str]]] = branch_data_processed.get("start_point")
        # end_point è [(local_offset_on_target, ref_name_end)]
        self.end_point: Optional[List[Tuple[float, str]]] = branch_data_processed.get("end_point")
        self.absolute_start_x: Optional[float] = branch_data_processed.get("absolute_start_x")
        self.absolute_end_x: Optional[float] = branch_data_processed.get("absolute_end_x")
        self.y_coordinate: Optional[float] = branch_data_processed.get("y_coordinate")

        # Determina temperatura e pressione di default per i tubi/stretches in questa branch
        default_temp = DEFAULT_TEMPERATURE
        default_press = DEFAULT_PRESSURE
        if self.start_point and self.start_point[0][1] in boundary_data:
            start_boundary_name = self.start_point[0][1]
            default_temp = boundary_data[start_boundary_name].get("temp", DEFAULT_TEMPERATURE)
            default_press = boundary_data[start_boundary_name].get("pressione", DEFAULT_PRESSURE)


        self.segments = Segment.create_segments(branch_data_processed,self.absolute_end_x, self.name)
        self.tubes = Tubes.create_Stretch(self.segments, self.name)

    def __repr__(self) -> str:
        return (f"Branch(name='{self.name}', type='{self.branch_type}', len={self.length}, "
                f"abs_x=[{self.absolute_start_x}-{self.absolute_end_x}], "
                f"num_tubes={len(self.tubes)})")
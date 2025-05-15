# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 14:04:54 2025

@author: d.zaffino (adattato da Gemini)

Classe Tunnel adattata per coerenza con le classi modello e load_tunnel.
"""

from typing import Dict,  Optional
from models.branch import Branch
from models.stretch import Stretch
class Geometry:
    """Classe che rappresenta un Tunnel."""

    def __init__(self, tunnel_data: Dict, branches_data: Dict):

        self.name: str = tunnel_data["name"]
        self.boundary: Dict = tunnel_data["Boundary"]
        self.branches: Dict[str, 'Branch'] = {}  # Utilizza il forward reference per Branch se definito dopo
        for name, branch_specific_data in branches_data.items():
            # Si assume che la classe Branch sia definita e importata, e il suo costruttore sia:
            # Branch(name: str, branch_data_processed: Dict, boundary_data: Dict)
            self.branches[name] = Branch(name, branch_specific_data, self.boundary)

        self.update_all_main_component_references()

    def __repr__(self) -> str:
        return f"Tunnel(name='{self.name}', branches={list(self.branches.keys())})"

    def update_all_main_component_references(self):
        """Aggiorna i riferimenti previous e next solo per il tubo 'Main' di tutte le branch."""
        for branch in self.branches.values():
            if "Main" in branch.components:
                main_component = branch.components["Main"]
                if main_component:
                    # Aggiorniamo solo il primo e l'ultimo stretch del tubo 'Main'
                    main_component[0].previous = self.find_previous_stretch(branch, branch.start_point[0][1],
                                                                                 branch.start_point[0][0])
                    main_component[-1].next = self.find_next_stretch(branch, branch.end_point[0][1],
                                                                          branch.end_point[0][0])

    def find_previous_stretch(self, branch, target_branch_or_boundary: str, target_x: float) -> Optional[Stretch]:
        """Trova lo Stretch precedente per il tubo 'Main' in base alla Branch o Boundary di destinazione."""
        if target_branch_or_boundary in self.boundary:  # Gestione Boundary
            # Crea un oggetto Stretch con informazioni di Boundary
            return Stretch(
                name=target_branch_or_boundary,
                start_x=target_x,
                end_x=target_x,
                # temperature=self.boundary[target_branch_or_boundary]["temp"],
                # pressure=self.boundary[target_branch_or_boundary]["pressione"],
                branch="Boundary"
            )
        else:  # Gestione Branch
            target_branch = self.branches[target_branch_or_boundary]
            if target_branch:
                main_stretches = target_branch.tubes.get("Main", [])
                for stretch in reversed(main_stretches):  # Solo gli stretch del tubo "Main"
                    if stretch.end_x == target_x:  # Confronta end_x per trovare il precedente
                        return stretch
        return None

    def find_next_stretch(self, branch, target_branch_or_boundary: str, target_x: float) -> Optional[Stretch]:
        """Trova lo Stretch successivo per il tubo 'Main' in base alla Branch o Boundary di destinazione."""
        if target_branch_or_boundary in self.boundary:  # Gestione Boundary
            # Crea un oggetto Stretch con informazioni di Boundary
            return Stretch(
                name=target_branch_or_boundary,
                start_x=target_x,
                end_x=target_x,
                # temperature=self.boundary[target_branch_or_boundary]["temp"],
                # pressure=self.boundary[target_branch_or_boundary]["pressione"],
                branch="Boundary"
            )
        else:  # Gestione Branch
            target_branch = self.branches[target_branch_or_boundary]
            if target_branch:
                main_stretches = target_branch.tubes.get("Main", [])
                for stretch in main_stretches:  # Solo gli stretch del tubo "Main"
                    if stretch.start_x == target_x:  # Confronta start_x per trovare il successivo
                        return stretch
        return None
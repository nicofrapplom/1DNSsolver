# -*- coding: utf-8 -*-
"""
incidence_matrix.py
"""

import numpy as np

class IncidenceMatrix:
    def __init__(self, nodes, segments):
        self.nodes = sorted(nodes, key=lambda n: n.id)
        self.segments = sorted(segments, key=lambda s: s.id)
        self.matrix = self.build_matrix()

    def build_matrix(self):
        nn = len(self.nodes)
        nb = len(self.segments)
        A = np.zeros((nn, nb))

        # Mappa nodo globale → indice
        node_index_map = {(n.branch, n.id): idx for idx, n in enumerate(self.nodes)}

        for j, seg in enumerate(self.segments):
            i_start = node_index_map[(seg.start_node.branch, seg.start_node.id)]
            i_end   = node_index_map[(seg.end_node.branch, seg.end_node.id)]
            A[i_start, j] = 1
            A[i_end, j] = -1

        return A

    def __repr__(self):
        return f"Incidence Matrix {self.matrix.shape[0]}x{self.matrix.shape[1]}"

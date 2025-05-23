# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 14:04:54 2025

@author: d.zaffino, n.frapolli
"""

# from input_data.test_setups.Galleria_Breganzona.input_geometry import geometry_data

import os
import importlib
from processing.geometry_loader import load_geometry, import_geometry_data

def main():
    try:
        print("\nLoading the geometry from input files...\n")
        geometry = load_geometry(geometry_data)

        test_case = find_default_test_case()
        print(f"[INFO] Caso di test rilevato automaticamente: {test_case}")
        geometry, A = load_geometry(test_case)

        nodes = geometry.get_nodes()
        segments = geometry.get_segments()

        print(f"[INFO] Plottaggio rete con {len(nodes)} nodi e {len(segments)} segmenti...")

        plot_3d_ordered(nodes, segments)
        plot_xz_ordered(nodes, segments)
        plot_xy_ordered(nodes, segments)

    except Exception as e:
        print(f"[FALLITO] Errore durante il caricamento o il plottaggio: {e}")

if __name__ == "__main__":
    main()

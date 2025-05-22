"""processing/plot_geometry.py"""
import os
import importlib
from processing.geometry_loader import load_geometry, import_geometry_data
from models.channel_visualization import (
    plot_3d_ordered,
    plot_xz_ordered,
    plot_xy_ordered
)

def find_default_test_case():
    input_dir = os.path.join(os.path.dirname(__file__), "..", "input_data")
    input_dir = os.path.abspath(input_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            try:
                import_geometry_data(module_name)
                return module_name
            except Exception:
                continue
    raise RuntimeError("Nessun file valido trovato in 'input_data/' con geometry_data definito.")

def main():
    try:
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

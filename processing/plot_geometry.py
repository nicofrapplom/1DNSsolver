import matplotlib.pyplot as plt
from processing.geometry_loader import load_geometry
from models.channel_visualization import plot_3d_ordered, plot_xz_ordered

def main():
    test_case = "input_geometry"  # Nome del file input_data/input_geometry.py

    try:
        geometry, A = load_geometry(test_case)

        nodes = geometry.get_nodes()
        segments = geometry.get_segments()

        print(f"[INFO] Plottaggio rete con {len(nodes)} nodi e {len(segments)} segmenti...")

        plot_3d_ordered(nodes, segments)
        plot_xz_ordered(nodes, segments)

    except Exception as e:
        print(f"[FALLITO] Errore durante il caricamento o il plottaggio: {e}")

if __name__ == "__main__":
    main()

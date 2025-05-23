# -*- coding: utf-8 -*-
"""
main.py
"""

from input_data.test_setups.Galleria_Breganzona.input_geometry import geometry_data
from processing.data_loader import load_geometry

# from models.branch import Branch
# from tests.utils import count_totals, print_node_connections
# from models.network_geometry import NetworkGeometry
# from models.incidence_matrix import IncidenceMatrix
#
# from channel_visualization import plot_3d, plot_xz
# from channel_visualization import plot_3d_ordered, plot_xz_ordered
#
# import matplotlib.pyplot as plt
# plt.close('all')



def main():

    print("\nLoading the geometry from input files...\n")
    geometry = load_geometry(geometry_data)



if __name__ == "__main__":
    main()
#


# branches = {}
#
# # Build all branches, resolving start_point or alignment if needed
# for name, data in tunnel_data["branches"].items():
#     b = Branch(name, data)
#     if "start_point" in data or "alignment" in data:
#         b.resolve_start_point(branches)
#     b.build_geometry()
#     branches[name] = b
#
# # Visualizzazioni
# # plot_3d(branches)
# # plot_xz(branches)
#
# # Stampa per branch
# from utils import report_branch_summary
# report_branch_summary(branches)
#
#
# print_node_connections(branches)
#
# # Deduplicazione globale
# all_nodes = []
# all_segments = []
# for branch in branches.values():
#     all_nodes.extend(branch.nodes)
#     all_segments.extend(branch.segments)
#
#
#
#
# # Costruzione topologia con spezzamento
# geometry = NetworkGeometry(branches)
# geometry.split_segments_on_shared_nodes()
# geometry.check_segment_intersections(tol=1e-6)
# geometry.deduplicate_nodes()
# geometry.assign_ids_by_branch_sequence()
#
#
#
#
# all_nodes = geometry.get_nodes()
# all_segments = geometry.get_segments()
#
# print("\nTotale rete deduplicata:")
# print(f"Nodi totali (dopo assegnazione)   : {len(all_nodes)}")
# print(f"Segmenti effettivi                : {len(all_segments)}")
#
#
# # Incidence matrix
# A = IncidenceMatrix(geometry.get_nodes(), geometry.get_segments())
#
# print(f"\n {A}")
# print(A.matrix)
#
# plot_3d_ordered(geometry.get_nodes(), geometry.get_segments())
# plot_xz_ordered(geometry.get_nodes(), geometry.get_segments())
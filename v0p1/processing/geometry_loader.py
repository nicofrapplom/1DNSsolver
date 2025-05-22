"""
models/load_geometry.py
"""

from models.branch import Branch
from models.network_geometry import NetworkGeometry
from models.incidence_matrix import IncidenceMatrix
import importlib


def import_geometry_data(test_case_name):
    try:
        module_path = f"input_data.{test_case_name}"
        geometry_module = importlib.import_module(module_path)
        return geometry_module.geometry_data
    except ModuleNotFoundError:
        raise ImportError(f"Modulo di input '{test_case_name}' non trovato.")
    except AttributeError:
        raise ImportError(f"Il modulo '{test_case_name}' non contiene 'geometry_data'.")

def load_geometry(test_case_name):
    print(f"[INFO] Caricamento del caso di test '{test_case_name}'...")
    data = import_geometry_data(test_case_name)
    branch_defs = data["branches"]

    todo = {name: Branch(name, bdata) for name, bdata in branch_defs.items()}
    built = {}
    built_names = set()
    max_attempts = len(todo) * 5
    attempts = 0

    while todo and attempts < max_attempts:
        names = list(todo.keys())  # ordine dinamico
        for name in names:
            branch = todo[name]
            deps_ok = True

            # Check dipendenze topologiche
            if "start_point" in branch.data and "from_branch" in branch.data["start_point"]:
                if branch.data["start_point"]["from_branch"] not in built_names:
                    deps_ok = False
            if "end_point" in branch.data and "to_branch" in branch.data["end_point"]:
                if branch.data["end_point"]["to_branch"] not in built_names:
                    deps_ok = False
            if "alignment" in branch.data and "through_branch" in branch.data["alignment"]:
                if branch.data["alignment"]["through_branch"] not in built_names:
                    deps_ok = False

            if not deps_ok:
                continue

            # Prova a costruire tutto
            try:
                branch.resolve_start_point(built)
                branch.build_geometry(built)
                print(f"[OK] Branch '{name}' costruito con successo.")

                built[name] = branch
                built_names.add(name)
                del todo[name]
            except Exception as e:
                print(f"[AVVISO] Branch '{name}' non ancora costruibile: {e}")
                # lo riproveremo al prossimo giro

        attempts += 1

    if todo:
        raise RuntimeError(f"[ERRORE] Alcuni branch non sono stati costruiti (loop?): {list(todo.keys())}")

    # Costruzione rete e topologia
    geometry = NetworkGeometry(built)
    geometry.split_segments_on_shared_nodes()
    geometry.check_segment_intersections(tol=1e-6)
    geometry.deduplicate_nodes()
    geometry.assign_ids_by_branch_sequence()

    all_nodes = geometry.get_nodes()
    all_segments = geometry.get_segments()
    A = IncidenceMatrix(all_nodes, all_segments)

    print(f"\n[INFO] Matrice di incidenza (shape {A.matrix.shape}):")
    print(A.matrix)

    print(f"[INFO] Geometria caricata con successo.")
    print(f"[INFO] Nodi totali: {len(all_nodes)}, Segmenti totali: {len(all_segments)}")
    print("\n[INFO] Elenco completo dei nodi (ID, branch, coordinate):")
    for node in all_nodes:
        print(f"  Node {node.id:>2} | Branch: {node.branch:>8} | (x={node.x:.2f}, y={node.y:.2f}, z={node.z:.2f})")

    return geometry, A

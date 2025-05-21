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

    # Costruisci oggetti Branch
    branches = {name: Branch(name, bdata) for name, bdata in branch_defs.items()}

    # Risolvi dipendenze topologiche
    def visit(name, visited, sorted_names):
        if name not in visited:
            visited.add(name)
            deps = set()
            d = branch_defs[name]
            if "start_point" in d and "from_branch" in d["start_point"]:
                deps.add(d["start_point"]["from_branch"])
            if "end_point" in d and "to_branch" in d["end_point"]:
                deps.add(d["end_point"]["to_branch"])
            if "alignment" in d and "through_branch" in d["alignment"]:
                deps.add(d["alignment"]["through_branch"])
            for dep in deps:
                visit(dep, visited, sorted_names)
            sorted_names.append(name)

    visited = set()
    sorted_names = []
    for name in branch_defs:
        visit(name, visited, sorted_names)

    # Costruzione completa dei branch
    for name in sorted_names:
        b = branches[name]
        b.resolve_start_point(branches)
        b.resolve_end_point(branches)
        b.build_geometry()

    geometry = NetworkGeometry(branches)
    geometry.split_segments_on_shared_nodes()
    geometry.check_segment_intersections(tol=1e-6)
    geometry.deduplicate_nodes()
    geometry.assign_ids_by_branch_sequence()

    all_nodes = geometry.get_nodes()
    all_segments = geometry.get_segments()
    A = IncidenceMatrix(all_nodes, all_segments)
    print(f"\n {A}")
    print(A.matrix)

    print(f"[INFO] Geometria caricata con successo.")
    print(f"[INFO] Nodi totali: {len(all_nodes)}, Segmenti totali: {len(all_segments)}")
    return geometry, A

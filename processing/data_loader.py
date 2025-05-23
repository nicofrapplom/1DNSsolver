"""
models/load_geometry.py
"""

from geometry.branch import Branch
from geometry.network_geometry import NetworkGeometry
# from models.incidence_matrix import IncidenceMatrix
# import importlib


def load_geometry(geometry_data):

    try:
        # Process branches from input into usable ones
        processed_branches = process_branches(geometry_data)
        # Build the network and the related topology fomr the processed branches
        geometry = NetworkGeometry.from_processed_branches(processed_branches)
        return geometry

    except KeyError as e:
        print(f"Error: Missing key in input data: {e}")
        # Consider to remake the exception and make it more specific
        raise
    except ValueError as e:
        print(f"Error validating geometry data: {e}")
        # Consider to remake the exception and make it more specific
        raise
    except Exception as e:
        print(f"Generic error loading geometry data: {e}")
        # Consider to remake the exception and make it more specific
        raise
        # return None # O handle the error as appropriate for the application


def process_branches(geometry_data):

    branch_defs = geometry_data["branches"]

    todo = {name: Branch(name, bdata) for name, bdata in branch_defs.items()}
    built = {}
    built_names = set()
    max_attempts = len(todo) * 5
    attempts = 0

    while todo and attempts < max_attempts:
        names = list(todo.keys())  # dynamic order
        for name in names:
            branch = todo[name]
            deps_ok = True

            # Check topologic dependencies
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

            # Try to build the network
            try:
                branch.resolve_start_point(built)
                branch.build_geometry(built)
                print(f"[OK] Branch '{name}' successfully built.")

                built[name] = branch
                built_names.add(name)
                del todo[name]
            except Exception as e:
                # otherwise try to rebuild the network in the next round
                print(f"[Warning] Branch '{name}' cannot be built yet: {e}")


        attempts += 1

    if todo:
        raise RuntimeError(f"[ERROR] Some branches have not been built (loop?): {list(todo.keys())}")

    return built

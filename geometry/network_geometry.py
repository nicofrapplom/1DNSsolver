"""
models/network_geometry.py
"""
from geometry.nodes import Node
from geometry.segments import Segment
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class NetworkGeometry:
    def __init__(self):
        self.branches = []
        self.all_nodes = []
        self.all_segments = []

    @classmethod
    def from_processed_branches(cls, branches):
        instance = cls()
        instance.branches = branches
        instance.collect_elements()
        instance.split_segments_on_shared_nodes()
        instance.check_segment_intersections(tol=1e-6)
        instance.deduplicate_nodes()
        instance.assign_ids_by_branch_sequence()

        # all_nodes = geometry.get_nodes()
        # all_segments = geometry.get_segments()
        # A = IncidenceMatrix(all_nodes, all_segments)

        # print(f"\n[INFO] Matrice di incidenza (shape {A.matrix.shape}):")
        # print(A.matrix)
        #
        print(f"[INFO] Geometria caricata con successo.")
        # print(f"[INFO] Nodi totali: {len(all_nodes)}, Segmenti totali: {len(all_segments)}")
        # print("\n[INFO] Elenco completo dei nodi (ID, branch, coordinate):")
        # for node in all_nodes:
        #     print(f"  Node {node.id:>2} | Branch: {node.branch:>8} | (x={node.x:.2f}, y={node.y:.2f}, z={node.z:.2f})")
        #
        # return geometry, A
        return instance


    def collect_elements(self):
        for b in self.branches.values():
            self.all_nodes.extend(b.nodes)
            self.all_segments.extend(b.segments)

    def key(self, node, tol=1e-6):
        return (round(node.x / tol), round(node.y / tol), round(node.z / tol))

    def split_segments_on_shared_nodes(self, tol=1e-6):
        print("\n Topological analysis: check shared nodes internal to the segment")
        updated_segments = []
        coord_map = {}
        for node in self.all_nodes:
            k = self.key(node, tol)
            coord_map.setdefault(k, []).append(node)

        for seg in self.all_segments:
            segment_vector = [
                seg.end_node.x - seg.start_node.x,
                seg.end_node.y - seg.start_node.y,
                seg.end_node.z - seg.start_node.z
            ]
            segment_length = seg.length

            internal_nodes = []
            for k, nodes in coord_map.items():
                for node in nodes:
                    if node not in (seg.start_node, seg.end_node):
                        vec = [node.x - seg.start_node.x,
                               node.y - seg.start_node.y,
                               node.z - seg.start_node.z]
                        proj = sum(vec[i] * segment_vector[i] for i in range(3)) / segment_length
                        if 0.0 < proj < segment_length:
                            dist = math.sqrt(
                                sum((vec[i] - proj * segment_vector[i] / segment_length) ** 2 for i in range(3)))
                            if dist < tol and proj / segment_length > 1e-3 and proj / segment_length < 1 - 1e-3:
                                internal_nodes.append((proj, node))

                                print(
                                    f" Found shared node at ({node.x:.2f}, {node.y:.2f}, {node.z:.2f}) → divided {seg.branch} between N{seg.start_node.id} and N{seg.end_node.id}")

            if not internal_nodes:
                updated_segments.append(seg)
            else:
                # Reorder the internal nodes based on the position along the segment (proj)
                internal_nodes.sort(key=lambda tup: tup[0])
                points = [seg.start_node] + [n for _, n in internal_nodes] + [seg.end_node]

                for i in range(len(points) - 1):
                    updated_segments.append(Segment(
                        branch_name=seg.branch,
                        segment_id=-1,
                        start_node=points[i],
                        end_node=points[i + 1],
                        delta=seg.delta,
                        alpha=seg.alpha,
                        areas=seg.areas,
                        perimeters=seg.perimeters,
                        comp_present=seg.comp_present
                    ))

        self.all_segments = updated_segments
        print(f" Updated segments: {len(self.all_segments)}")

    def check_segment_intersections(self, tol=1.0):
        print("\n Verify gometric intersection between segments:")
        segment_id_counter = len(self.all_segments)
        for i, seg1 in enumerate(self.all_segments[:]):
            for j, seg2 in enumerate(self.all_segments[:]):
                if j <= i:
                    continue
                if seg1.branch == seg2.branch:
                    continue
                print(f"→ Verify {seg1.branch}-S{seg1.id} ↔ {seg2.branch}-S{seg2.id}")
                if self.segments_intersect(seg1, seg2, tol):
                    print(f" Intersection: {seg1.branch}-S{seg1.id} ↔ {seg2.branch}-S{seg2.id}")

                    p1 = np.array(seg1.start_node.coords())
                    p2 = np.array(seg1.end_node.coords())
                    q1 = np.array(seg2.start_node.coords())
                    q2 = np.array(seg2.end_node.coords())
                    u = p2 - p1
                    v = q2 - q1
                    w0 = p1 - q1

                    a = np.dot(u, u)
                    b = np.dot(u, v)
                    c = np.dot(v, v)
                    d = np.dot(u, w0)
                    e = np.dot(v, w0)
                    denom = a * c - b * b
                    s = (b * e - c * d) / denom
                    t = (a * e - b * d) / denom

                    point1 = p1 + s * u
                    point2 = q1 + t * v
                    midpoint = 0.5 * (point1 + point2)

                    tol_node = 1e-3
                    existing = None
                    for node in self.all_nodes:
                        if (abs(node.x - midpoint[0]) < tol_node and
                                abs(node.y - midpoint[1]) < tol_node and
                                abs(node.z - midpoint[2]) < tol_node):
                            existing = node
                            break

                    if existing:
                        new_node = existing
                        print(
                            f" Shared node already existing at ({new_node.x:.2f}, {new_node.y:.2f}, {new_node.z:.2f}) → reused")
                    else:
                        new_node = Node("Shared", -1, *midpoint)
                        self.all_nodes.append(new_node)
                        print(f" Inserted node in ({new_node.x:.2f}, {new_node.y:.2f}, {new_node.z:.2f})")

                    if seg1 in self.all_segments:
                        self.all_segments.remove(seg1)
                    if seg2 in self.all_segments:
                        self.all_segments.remove(seg2)

                    self.all_segments.append(
                        Segment(seg1.branch, segment_id_counter, seg1.start_node, new_node, seg1.delta, seg1.alpha,
                                seg1.areas, seg1.perimeters, seg1.tubi_presenti))
                    segment_id_counter += 1
                    self.all_segments.append(
                        Segment(seg1.branch, segment_id_counter, new_node, seg1.end_node, seg1.delta, seg1.alpha,
                                seg1.areas, seg1.perimeters, seg1.tubi_presenti))
                    segment_id_counter += 1
                    self.all_segments.append(
                        Segment(seg2.branch, segment_id_counter, seg2.start_node, new_node, seg2.delta, seg2.alpha,
                                seg2.areas, seg2.perimeters, seg2.tubi_presenti))
                    segment_id_counter += 1
                    self.all_segments.append(
                        Segment(seg2.branch, segment_id_counter, new_node, seg2.end_node, seg2.delta, seg2.alpha,
                                seg2.areas, seg2.perimeters, seg2.tubi_presenti))
                    segment_id_counter += 1

    def segments_intersect(self, seg1, seg2, tol):
        p1 = np.array(seg1.start_node.coords())
        p2 = np.array(seg1.end_node.coords())
        q1 = np.array(seg2.start_node.coords())
        q2 = np.array(seg2.end_node.coords())
        u = p2 - p1
        v = q2 - q1
        w0 = p1 - q1
        a = np.dot(u, u)
        b = np.dot(u, v)
        c = np.dot(v, v)
        d = np.dot(u, w0)
        e = np.dot(v, w0)
        denom = a * c - b * b
        if denom == 0:
            return False
        s = (b * e - c * d) / denom
        t = (a * e - b * d) / denom
        point1 = p1 + s * u
        point2 = q1 + t * v
        dist = np.linalg.norm(point1 - point2)
        print(f"   → s={s:.2f}, t={t:.2f}, dist={dist:.4f}")
        return (0.01 <= s <= 0.99) and (0.01 <= t <= 0.99) and (dist < tol)

    def deduplicate_nodes(self, tol=1e-2):
        unique_nodes = {}
        coord_to_node = {}
        global_id = 0
        duplicates = []

        def key(node):
            return (round(node.x / tol), round(node.y / tol), round(node.z / tol))

        for node in self.all_nodes:
            k = key(node)
            if k not in coord_to_node:
                node.id = global_id
                coord_to_node[k] = node
                unique_nodes[k] = node
                global_id += 1
            else:
                existing = coord_to_node[k]
                duplicates.append((node, existing))
                node.id = existing.id

        # Update segments
        for seg in self.all_segments:
            seg.start_node = coord_to_node[key(seg.start_node)]
            seg.end_node = coord_to_node[key(seg.end_node)]

        if duplicates:
            print("\nShared nodes (deduplicated):")
            for dup, original in duplicates:
                print(f"  Node {dup.id} ({dup.branch}) is shared with Node {original.id} ({original.branch})")

        # aggiorna lista nodi unici
        self.all_nodes = list(unique_nodes.values())

    def assign_ids_by_branch_sequence(self):
        print("\nAssign ID segments and nodes FOLLOWING the built sequence + divisions")

        self.segment_id_counter = 0
        self.node_id_counter = 0
        node_id_map = {}  # Nodo → ID
        ordered_nodes = []
        ordered_segments = []

        for branch_name in sorted(self.branches.keys()):
            # Prendi tutti i segmenti del branch (compresi quelli spezzati)
            branch_segments = [s for s in self.all_segments if s.branch == branch_name]

            # Ordina i segmenti per progressiva cumulativa (x0)
            branch_segments.sort(key=lambda s: min(s.start_node.x, s.end_node.x))

            for seg in branch_segments:
                # ID nodi
                for node in [seg.start_node, seg.end_node]:
                    if id(node) not in node_id_map:
                        node.id = self.node_id_counter
                        node_id_map[id(node)] = self.node_id_counter
                        ordered_nodes.append(node)
                        self.node_id_counter += 1
                    else:
                        node.id = node_id_map[id(node)]

                # ID segment
                seg.id = self.segment_id_counter
                ordered_segments.append(seg)
                self.segment_id_counter += 1

        self.all_segments = ordered_segments
        self.all_nodes = ordered_nodes

    # def get_segments(self):
    #     return self.all_segments
    #
    # def get_nodes(self):
    #     return list({id(n): n for n in self.all_nodes}.values())

    def plot(self, *views):
        """
        Esegue il plotting della geometria secondo le viste specificate.
        Argomenti possibili: '3d', 'xz', 'xy'
        """
        for view in views:
            view = view.lower()
            if view == '3d':
                self.plot_3d_ordered()
            elif view == 'xz':
                self.plot_xz_ordered()
            elif view == 'xy':
                self.plot_xy_ordered()
            else:
                print(f"[AVVISO] Vista '{view}' non riconosciuta. Opzioni valide: '3d', 'xz', 'xy'.")

    def plot_xy_ordered(self):
        fig, ax = plt.subplots(figsize=(12, 5), constrained_layout=True)

        for node in self.all_nodes:
            ax.scatter(node.x, node.y, color='blue', s=40)
            ax.text(node.x, node.y + 0.5, f'i{node.id}', fontsize=8, color='blue')

        for seg in self.all_segments:
            x0, y0, _ = seg.start_node.coords()
            x1, y1, _ = seg.end_node.coords()
            ax.plot([x0, x1], [y0, y1], color='black')
            xm = (x0 + x1) / 2
            ym = (y0 + y1) / 2
            ax.text(xm, ym, f'j{seg.id}', fontsize=8, color='darkred')

        ax.set_xlabel("X [m]")
        ax.set_ylabel("Y [m]")
        ax.set_title("Rete ordinata - Vista X-Y - Nodi (i) e Segmenti (j)")
        ax.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_xz_ordered(self):
        fig, ax = plt.subplots(figsize=(12, 5))

        for node in self.all_nodes:
            ax.scatter(node.x, node.z, color='blue', s=40)
            ax.text(node.x, node.z + 0.5, f'i{node.id}', fontsize=8, color='blue')

        for seg in self.all_segments:
            x0, _, z0 = seg.start_node.coords()
            x1, _, z1 = seg.end_node.coords()
            ax.plot([x0, x1], [z0, z1], color='black')
            xm = (x0 + x1) / 2
            zm = (z0 + z1) / 2
            ax.text(xm, zm, f'j{seg.id}', fontsize=8, color='darkred')

        ax.set_xlabel("X [m]")
        ax.set_ylabel("Z [m]")
        ax.set_title("Rete ordinata - Vista X-Z - Nodi (i) e Segmenti (j)")
        ax.grid(True)
        plt.tight_layout()
        plt.show()


    def plot_3d_ordered(self):
        fig = plt.figure(figsize=(12, 7))  # niente constrained_layout per 3D
        ax = fig.add_subplot(111, projection='3d')

        for node in self.all_nodes:
            ax.scatter(node.x, node.y, node.z, color='blue', s=40)
            ax.text(node.x, node.y, node.z + 0.5, f'i{node.id}', fontsize=8, color='blue')

        for seg in self.all_segments:
            x0, y0, z0 = seg.start_node.coords()
            x1, y1, z1 = seg.end_node.coords()
            ax.plot([x0, x1], [y0, y1], [z0, z1], color='black')
            xm = (x0 + x1) / 2
            ym = (y0 + y1) / 2
            zm = (z0 + z1) / 2
            ax.text(xm, ym, zm, f'j{seg.id}', fontsize=8, color='darkred')

        ax.set_xlabel("X [m]")
        ax.set_ylabel("Y [m]")
        ax.set_zlabel("Z [m]")
        ax.set_title("Rete ordinata - Vista 3D - Nodi (i) e Segmenti (j)")
        plt.tight_layout()
        plt.show()

# def plot_3d(branches):
#     fig = plt.figure(figsize=(12, 7))
#     ax = fig.add_subplot(111, projection='3d')
#
#     for branch in branches.values():
#         for node in branch.nodes:
#             ax.scatter(node.x, node.y, node.z, color='blue', s=40)
#             ax.text(node.x, node.y, node.z + 0.5, f'i{node.id}', fontsize=8, color='blue')
#
#         for seg in branch.segments:
#             x0, y0, z0 = seg.start_node.coords()
#             x1, y1, z1 = seg.end_node.coords()
#             ax.plot([x0, x1], [y0, y1], [z0, z1], color='black')
#             xm = (x0 + x1) / 2
#             ym = (y0 + y1) / 2
#             zm = (z0 + z1) / 2
#             ax.text(xm, ym, zm, f'j{seg.id}', fontsize=8, color='darkred')
#
#     ax.set_xlabel("X [m]")
#     ax.set_ylabel("Y [m]")
#     ax.set_zlabel("Z [m]")
#     ax.set_title("Tunnel Network - Nodi (i) e Segmenti (j)")
#     plt.tight_layout()
#
#     plt.show()
#
#
# def plot_xz(branches):
#     fig, ax = plt.subplots(constrained_layout=True)
#
#     for branch in branches.values():
#         for node in branch.nodes:
#             ax.scatter(node.x, node.z, color='blue', s=40)
#             ax.text(node.x, node.z + 0.5, f'i{node.id}', fontsize=8, color='blue')
#
#         for seg in branch.segments:
#             x0, _, z0 = seg.start_node.coords()
#             x1, _, z1 = seg.end_node.coords()
#             ax.plot([x0, x1], [z0, z1], color='black')
#             xm = (x0 + x1) / 2
#             zm = (z0 + z1) / 2
#             ax.text(xm, zm, f'j{seg.id}', fontsize=8, color='darkred')
#
#     ax.set_xlabel("X [m]")
#     ax.set_ylabel("Z [m]")
#     ax.set_title("Proiezione X-Z del Tunnel - Nodi (i) e Segmenti (j)")
#     ax.grid(True)
#     plt.show()

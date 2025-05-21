"""
models/network_geometry.py
"""
from models.nodes import Node
from models.segments import Segment
import math
import numpy as np
from scipy.spatial import cKDTree
from collections import defaultdict, deque


class NetworkGeometry:
    def __init__(self, branches):
        self.branches = branches
        self.all_nodes = []
        self.all_segments = []
        self.collect_elements()

    def collect_elements(self):
        for b in self.branches.values():
            self.all_nodes.extend(b.nodes)
            self.all_segments.extend(b.segments)

    def key(self, node, tol=1e-6):
        return (round(node.x / tol), round(node.y / tol), round(node.z / tol))

    def split_segments_on_shared_nodes(self, tol=1e-6):
        print("\n Analisi topologica: controllo nodi condivisi interni ai segmenti")
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
                                    f" Nodo condiviso rilevato a ({node.x:.2f}, {node.y:.2f}, {node.z:.2f}) → spezzato {seg.branch} tra N{seg.start_node.id} e N{seg.end_node.id}")

            if not internal_nodes:
                updated_segments.append(seg)
            else:
                # Ordina i nodi interni secondo la posizione lungo il segmento (proj)
                internal_nodes.sort(key=lambda tup: tup[0])
                points = [seg.start_node] + [n for _, n in internal_nodes] + [seg.end_node]

                for i in range(len(points) - 1):
                    updated_segments.append(Segment(
                        branch_name=seg.branch,
                        segment_id=-1,
                        start_node=points[i],
                        end_node=points[i + 1],
                        alpha=seg.alpha,
                        delta=seg.delta,
                        areas=seg.areas,
                        perimeters=seg.perimeters,
                        tubi_presenti=seg.tubi_presenti
                    ))

        self.all_segments = updated_segments
        print(f" Segmenti aggiornati: {len(self.all_segments)}")

    def check_segment_intersections(self, tol=1.0):
        print("\n Verifica intersezioni geometriche tra segmenti")
        segment_id_counter = len(self.all_segments)
        for i, seg1 in enumerate(self.all_segments[:]):
            for j, seg2 in enumerate(self.all_segments[:]):
                if j <= i:
                    continue
                if seg1.branch == seg2.branch:
                    continue
                print(f"→ Verifica {seg1.branch}-S{seg1.id} ↔ {seg2.branch}-S{seg2.id}")
                if self.segments_intersect(seg1, seg2, tol):
                    print(f" Intersezione: {seg1.branch}-S{seg1.id} ↔ {seg2.branch}-S{seg2.id}")

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
                            f" Nodo condiviso già esistente in ({new_node.x:.2f}, {new_node.y:.2f}, {new_node.z:.2f}) → riutilizzato")
                    else:
                        new_node = Node("Shared", -1, *midpoint)
                        self.all_nodes.append(new_node)
                        print(f" Nodo inserito in ({new_node.x:.2f}, {new_node.y:.2f}, {new_node.z:.2f})")

                    if seg1 in self.all_segments:
                        self.all_segments.remove(seg1)
                    if seg2 in self.all_segments:
                        self.all_segments.remove(seg2)

                    self.all_segments.append(
                        Segment(seg1.branch, segment_id_counter, seg1.start_node, new_node, seg1.alpha, seg1.delta,
                                seg1.areas, seg1.perimeters, seg1.tubi_presenti))
                    segment_id_counter += 1
                    self.all_segments.append(
                        Segment(seg1.branch, segment_id_counter, new_node, seg1.end_node, seg1.alpha, seg1.delta,
                                seg1.areas, seg1.perimeters, seg1.tubi_presenti))
                    segment_id_counter += 1
                    self.all_segments.append(
                        Segment(seg2.branch, segment_id_counter, seg2.start_node, new_node, seg2.alpha, seg2.delta,
                                seg2.areas, seg2.perimeters, seg2.tubi_presenti))
                    segment_id_counter += 1
                    self.all_segments.append(
                        Segment(seg2.branch, segment_id_counter, new_node, seg2.end_node, seg2.alpha, seg2.delta,
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

        # aggiorna segmenti
        for seg in self.all_segments:
            seg.start_node = coord_to_node[key(seg.start_node)]
            seg.end_node = coord_to_node[key(seg.end_node)]

        if duplicates:
            print("\nNodi condivisi (deduplicati):")
            for dup, original in duplicates:
                print(f"  Nodo {dup.id} ({dup.branch}) è condiviso con Nodo {original.id} ({original.branch})")

        # aggiorna lista nodi unici
        self.all_nodes = list(unique_nodes.values())

    def assign_ids_by_branch_sequence(self):
        print("\nAssegnazione ID segmenti e nodi SEGUENDO la sequenza costruita + spezzamenti")

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

                # ID segmento
                seg.id = self.segment_id_counter
                ordered_segments.append(seg)
                self.segment_id_counter += 1

        self.all_segments = ordered_segments
        self.all_nodes = ordered_nodes

    def get_segments(self):
        return self.all_segments

    def get_nodes(self):
        return list({id(n): n for n in self.all_nodes}.values())

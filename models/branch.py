"""
build_branch.py
"""
from models.nodes import Node
from models.segments import Segment


class Branch:
    def __init__(self, name: str, data: dict):
        self.name = name
        self.data = data
        self.nodes = []
        self.segments = []
        self.shared_start_node = None  # nodo condiviso opzionale

    def get_value_at(self, x, lst, default=0.0):
        val = default
        for xi, v in lst:
            if x >= xi:
                val = v
            else:
                break
        return val

    def get_tube_property_at(self, x, tube_data):
        return self.get_value_at(x, tube_data.get("Area", []), 0.0), \
            self.get_value_at(x, tube_data.get("Perimeter", []), 0.0)

    def resolve_start_point(self, geometry_map: dict):

        if "start_point" in self.data and "absolute" in self.data["start_point"]:
            return self._resolve_absolute_point()
        elif "start_point" in self.data and "from_branch" in self.data["start_point"]:
            return self._resolve_relative_point(geometry_map)
        elif "alignment" in self.data:
            return self._resolve_aligned_point(geometry_map)
        else:
            raise ValueError("Start point non riconosciuto")

    def _resolve_absolute_point(self):
        pass

    def _resolve_relative_point(self, geometry_map):
        ref_branch = self.data["start_point"]["from_branch"]
        s_ref = self.data["start_point"]["at_length"]
        if ref_branch not in geometry_map:
            raise ValueError(f"Branch '{ref_branch}' non trovato nella geometry_map")
        branch = geometry_map[ref_branch]
        cum_length = 0.0
        for seg in branch.segments:
            l = seg.length
            if cum_length + l >= s_ref:
                t = (s_ref - cum_length) / l
                x = seg.start_node.x + t * (seg.end_node.x - seg.start_node.x)
                y = seg.start_node.y + t * (seg.end_node.y - seg.start_node.y)
                z = seg.start_node.z + t * (seg.end_node.z - seg.start_node.z)
                self.data["start_point"] = {"absolute": (x, y, z)}
                # Cerca nodo condiviso
                tol = 1e-6
                for node in branch.nodes:
                    if abs(node.x - x) < tol and abs(node.y - y) < tol and abs(node.z - z) < tol:
                        self.shared_start_node = node
                        break
                return
            cum_length += l
        self.data["start_point"] = {"absolute": branch.nodes[-1].coords()}
        self.shared_start_node = branch.nodes[-1]

    def _resolve_aligned_point(self, geometry_map):
        if "alignment" in self.data:
            align = self.data["alignment"]
            target_branch = align["through_branch"]
            if target_branch not in geometry_map:
                raise ValueError(f"Branch '{target_branch}' non trovato per alignment")
            b_target = geometry_map[target_branch]

            # punto di riferimento su branch target
            if align.get("at") == "end":
                x_ref, y_ref, z_ref = b_target.nodes[-1].coords()
            elif align.get("at") == "start":
                x_ref, y_ref, z_ref = b_target.nodes[0].coords()
            elif align.get("at") == "length":
                s_target = align["value"]
                cum_length = 0.0
                for seg in b_target.segments:
                    l = seg.length
                    if cum_length + l >= s_target:
                        t = (s_target - cum_length) / l
                        x_ref = seg.start_node.x + t * (seg.end_node.x - seg.start_node.x)
                        y_ref = seg.start_node.y + t * (seg.end_node.y - seg.start_node.y)
                        z_ref = seg.start_node.z + t * (seg.end_node.z - seg.start_node.z)
                        break
                    cum_length += l
            else:
                raise NotImplementedError("Solo 'at': 'end' è supportato per ora")

            s_local = align["position_along"]  # distanza dal nodo di partenza

            alpha = self.get_value_at(0.0, self.data.get("alpha", [(0.0, 0.0)]))
            delta = self.get_value_at(0.0, self.data.get("delta", [(0.0, 0.0)]))

            if abs(alpha) > 89.9 and abs(delta) < 0.1:
                dx = 0.0
                dy = 0.0
                dz = -s_local
            else:
                norm = (1 + (alpha / 100) ** 2 + (delta / 100) ** 2) ** 0.5
                dx = -(s_local / norm)
                dy = dx * (delta / 100)
                dz = dx * (alpha / 100)

            x0 = x_ref + dx
            y0 = y_ref + dy
            z0 = z_ref + dz
            self.data["start_point"] = {"absolute": (x0, y0, z0)}

        # # caso 1: start_point assoluto
        # if "start_point" in self.data and "absolute" in self.data["start_point"]:
        #     return
        # # caso 2: start_point relativo
        # if "start_point" in self.data and "from_branch" in self.data["start_point"]:
        #     ref_branch = self.data["start_point"]["from_branch"]
        #     s_ref = self.data["start_point"]["at_length"]
        #     if ref_branch not in geometry_map:
        #         raise ValueError(f"Branch '{ref_branch}' non trovato nella geometry_map")
        #     branch = geometry_map[ref_branch]
        #     cum_length = 0.0
        #     for seg in branch.segments:
        #         l = seg.length
        #         if cum_length + l >= s_ref:
        #             t = (s_ref - cum_length) / l
        #             x = seg.start_node.x + t * (seg.end_node.x - seg.start_node.x)
        #             y = seg.start_node.y + t * (seg.end_node.y - seg.start_node.y)
        #             z = seg.start_node.z + t * (seg.end_node.z - seg.start_node.z)
        #             self.data["start_point"] = {"absolute": (x, y, z)}
        #             # Cerca nodo condiviso
        #             tol = 1e-6
        #             for node in branch.nodes:
        #                 if abs(node.x - x) < tol and abs(node.y - y) < tol and abs(node.z - z) < tol:
        #                     self.shared_start_node = node
        #                     break
        #             return
        #         cum_length += l
        #     self.data["start_point"] = {"absolute": branch.nodes[-1].coords()}
        #     self.shared_start_node = branch.nodes[-1]

        # # caso 3: alignment geometrico
        # if "alignment" in self.data:
        #     align = self.data["alignment"]
        #     target_branch = align["through_branch"]
        #     if target_branch not in geometry_map:
        #         raise ValueError(f"Branch '{target_branch}' non trovato per alignment")
        #     b_target = geometry_map[target_branch]

        #     # punto di riferimento su branch target
        #     if align.get("at") == "end":
        #         x_ref, y_ref, z_ref = b_target.nodes[-1].coords()
        #     elif align.get("at") == "start":
        #         x_ref, y_ref, z_ref = b_target.nodes[0].coords()
        #     elif align.get("at") == "length":
        #         s_target = align["value"]
        #         cum_length = 0.0
        #         for seg in b_target.segments:
        #             l = seg.length
        #             if cum_length + l >= s_target:
        #                 t = (s_target - cum_length) / l
        #                 x_ref = seg.start_node.x + t * (seg.end_node.x - seg.start_node.x)
        #                 y_ref = seg.start_node.y + t * (seg.end_node.y - seg.start_node.y)
        #                 z_ref = seg.start_node.z + t * (seg.end_node.z - seg.start_node.z)
        #                 break
        #             cum_length += l
        #     else:
        #         raise NotImplementedError("Solo 'at': 'end' è supportato per ora")

        #     s_local = align["position_along"]  # distanza dal nodo di partenza

        #     alpha = self.get_value_at(0.0, self.data.get("alpha", [(0.0, 0.0)]))
        #     delta = self.get_value_at(0.0, self.data.get("delta", [(0.0, 0.0)]))

        #     if abs(alpha) > 89.9 and abs(delta) < 0.1:
        #         dx = 0.0
        #         dy = 0.0
        #         dz = -s_local
        #     else:
        #         norm = (1 + (alpha / 100) ** 2 + (delta / 100) ** 2) ** 0.5
        #         dx = -(s_local / norm)
        #         dy = dx * (delta / 100)
        #         dz = dx * (alpha / 100)

        #     x0 = x_ref + dx
        #     y0 = y_ref + dy
        #     z0 = z_ref + dz
        #     self.data["start_point"] = {"absolute": (x0, y0, z0)}

    def build_geometry(self):
        x_breaks = set()
        for tube in self.data["Tubes"].values():
            x_breaks.update(x for x, _ in tube.get("Area", []))
            x_breaks.update(x for x, _ in tube.get("Perimeter", []))
        x_breaks.update(x for x, _ in self.data.get("alpha", []))
        x_breaks.update(x for x, _ in self.data.get("delta", []))
        x_breaks.add(self.data["length"])
        x_breaks = sorted(x_breaks)

        start_point = self.data["start_point"]["absolute"]
        alpha_list = self.data.get("alpha", [(0.0, 0.0)])
        delta_list = self.data.get("delta", [(0.0, 0.0)])

        x, y, z = start_point
        if self.shared_start_node is not None:
            self.nodes.append(self.shared_start_node)
            node_id_offset = 1  # iniziamo da 1 perché il nodo iniziale è condiviso
        else:
            self.nodes.append(Node(self.name, 0, x, y, z))
            node_id_offset = 1
        for i in range(node_id_offset, len(x_breaks)):
            x0 = x_breaks[i - 1]
            x1 = x_breaks[i]
            dx = x1 - x0

            alpha = self.get_value_at(x0, alpha_list)
            delta = self.get_value_at(x0, delta_list)

            if abs(alpha) > 89.9 and abs(delta) < 0.1:
                dx3d = 0.0
                dy3d = 0.0
                dz3d = dx
            else:
                norm = (1 + (alpha / 100) ** 2 + (delta / 100) ** 2) ** 0.5
                dx3d = dx / norm
                dy3d = dx3d * (delta / 100)
                dz3d = dx3d * (alpha / 100)

            x += dx3d
            y += dy3d
            z += dz3d

            node = Node(self.name, i, x, y, z)
            self.nodes.append(node)

            areas, perimeters, tubi = {}, {}, {}
            for name, tube in self.data["Tubes"].items():
                area, perim = self.get_tube_property_at(x0, tube)
                areas[name] = area
                perimeters[name] = perim
                tubi[name] = area > 0.0

            segment = Segment(
                branch_name=self.name,
                segment_id=i - 1,
                start_node=self.nodes[i - 1],
                end_node=node,
                alpha=alpha,
                delta=delta,
                areas=areas,
                perimeters=perimeters,
                tubi_presenti=tubi
            )
            self.segments.append(segment)

    def __repr__(self):
        return f"Branch {self.name} | {len(self.nodes)} nodi, {len(self.segments)} segmenti"

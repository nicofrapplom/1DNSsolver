"""
models/branch.py
"""
from models.nodes import Node
from models.segments import Segment

class Branch:
    def __init__(self, name: str, data: dict):
        self.name = name
        self.data = data
        self.nodes = []
        self.segments = []
        self.shared_start_node = None  # nodo condiviso
        self.shared_end_node = None  # nodo condiviso  (end)

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
            return self.resolve_absolute_point()
        elif "start_point" in self.data and "from_branch" in self.data["start_point"]:
            return self.resolve_relative_point(geometry_map)
        elif "alignment" in self.data:
            return self.resolve_aligned_point(geometry_map)
        else:
            raise ValueError("Start point non riconosciuto")

    def resolve_end_point(self, geometry_map: dict):
        if "end_point" in self.data and "absolute" in self.data["end_point"]:
            return self.resolve_absolute_end_point()
        elif "end_point" in self.data and "to_branch" in self.data["end_point"]:
            return self.resolve_relative_end_point(geometry_map)
        else:
            pass  # end_point opzionale


    def resolve_absolute_point(self):
        pass

    def resolve_relative_point(self, geometry_map):
        ref_branch = self.data["start_point"]["from_branch"]
        s_ref = self.data["start_point"]["at_length"]
        if ref_branch not in geometry_map:
            raise ValueError(f"Branch '{ref_branch}' non trovato nella geometry_map")
        branch = geometry_map[ref_branch]

        tol = 1e-3
        branch_length = sum(seg.length for seg in branch.segments)

        if abs(s_ref) < tol:
            node = branch.nodes[0]
            self.shared_start_node = node
            self.data["start_point"] = {"absolute": node.coords()}
            return

        if abs(s_ref - branch_length) < tol:
            node = branch.nodes[-1]
            self.shared_start_node = node
            self.data["start_point"] = {"absolute": node.coords()}
            return

        # Interpolazione interna
        cum_length = 0.0
        for seg in branch.segments:
            l = seg.length
            if cum_length + l >= s_ref:
                t = (s_ref - cum_length) / l
                x = seg.start_node.x + t * (seg.end_node.x - seg.start_node.x)
                y = seg.start_node.y + t * (seg.end_node.y - seg.start_node.y)
                z = seg.start_node.z + t * (seg.end_node.z - seg.start_node.z)

                for node in branch.nodes:
                    if abs(node.x - x) < tol and abs(node.y - y) < tol and abs(node.z - z) < tol:
                        self.shared_start_node = node
                        self.data["start_point"] = {"absolute": node.coords()}
                        return

                self.data["start_point"] = {"absolute": (x, y, z)}
                return
            cum_length += l

        # Fallback
        node = branch.nodes[-1]
        self.shared_start_node = node
        self.data["start_point"] = {"absolute": node.coords()}

    def resolve_aligned_point(self, geometry_map):
        if "alignment" in self.data:
            align = self.data["alignment"]
            target_branch = align["through_branch"]
            if target_branch not in geometry_map:
                raise ValueError(f"Branch '{target_branch}' non trovato per alignment")
            b_target = geometry_map[target_branch]

            at = align.get("at")

            # punto di riferimento su branch target
            if at == "end":
                x_ref, y_ref, z_ref = b_target.nodes[-1].coords()
            elif at == "start":
                x_ref, y_ref, z_ref = b_target.nodes[0].coords()
            elif at == "length":
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
                    print(
                        f"[AVVISO] value={s_target} supera la lunghezza del branch '{target_branch}'. Uso ultimo nodo.")
                    x_ref, y_ref, z_ref = b_target.nodes[-1].coords()
            else:
                raise ValueError(f"Valore 'at' non riconosciuto in alignment: '{at}'")

            # calcolo punto iniziale del branch corrente
            s_local = align["position_along"]  # distanza lungo il nuovo branch

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

    def resolve_relative_end_point(self, geometry_map):
        ref_branch = self.data["end_point"]["to_branch"]
        s_ref = self.data["end_point"]["at_length"]
        if ref_branch not in geometry_map:
            raise ValueError(f"Branch '{ref_branch}' non trovato nella geometry_map")
        branch = geometry_map[ref_branch]
        if True:
            print(f"[DEBUG-FORZATO] Simulazione ramo start_point → uso nodo {branch.nodes[0]}")
            node = branch.nodes[0]
            self.shared_end_node = node
            self.data["end_point"] = {"absolute": node.coords()}
            return

        tol = max(1e-6, 0.001 * branch_length)

        branch_length = sum(seg.length for seg in branch.segments)


        # Caso limite: inizio
        if abs(s_ref) < tol:
            node = branch.nodes[0]
            self.shared_end_node = node
            self.data["end_point"] = {"absolute": node.coords()}
            return

        # Caso limite: fine
        if abs(s_ref - branch_length) < tol:
            node = branch.nodes[-1]
            self.shared_end_node = node
            self.data["end_point"] = {"absolute": node.coords()}
            print(f"[DEBUG] Nodo finale riconosciuto per end_point → i{node.id} ({node.branch})")
            return

        # Interpolazione interna
        cum_length = 0.0
        for seg in branch.segments:
            l = seg.length
            if cum_length + l >= s_ref:
                t = (s_ref - cum_length) / l
                x = seg.start_node.x + t * (seg.end_node.x - seg.start_node.x)
                y = seg.start_node.y + t * (seg.end_node.y - seg.start_node.y)
                z = seg.start_node.z + t * (seg.end_node.z - seg.start_node.z)

                for node in branch.nodes:
                    if abs(node.x - x) < tol and abs(node.y - y) < tol and abs(node.z - z) < tol:
                        self.shared_end_node = node
                        self.data["end_point"] = {"absolute": node.coords()}
                        return

                self.data["end_point"] = {"absolute": (x, y, z)}
                return
            cum_length += l

        # Fallback
        node = branch.nodes[-1]
        self.shared_end_node = node
        self.data["end_point"] = {"absolute": node.coords()}

    def build_geometry(self):
        # Determina la lunghezza e i profili se non già definiti
        if "start_point" in self.data and "absolute" in self.data["start_point"] and \
                "end_point" in self.data and "absolute" in self.data["end_point"]:

            x0, y0, z0 = self.data["start_point"]["absolute"]
            x1, y1, z1 = self.data["end_point"]["absolute"]

            dx = x1 - x0
            dy = y1 - y0
            dz = z1 - z0

            L = (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5
            self.data["length"] = self.data.get("length", L)

            if "alpha" not in self.data:
                self.data["alpha"] = [(0.0, 100.0 * dz / L if L > 0 else 0.0)]
            if "delta" not in self.data:
                self.data["delta"] = [(0.0, 100.0 * dy / L if L > 0 else 0.0)]

        # Coordinate iniziali
        x, y, z = self.data["start_point"]["absolute"]
        length = self.data["length"]

        # Breakpoints lungo il ramo
        x_breaks = set()
        for tube in self.data["Tubes"].values():
            x_breaks.update(x for x, _ in tube.get("Area", []))
            x_breaks.update(x for x, _ in tube.get("Perimeter", []))
        x_breaks.update(x for x, _ in self.data.get("alpha", []))
        x_breaks.update(x for x, _ in self.data.get("delta", []))
        x_breaks.add(length)
        x_breaks = sorted(x_breaks)

        alpha_list = self.data.get("alpha", [(0.0, 0.0)])
        delta_list = self.data.get("delta", [(0.0, 0.0)])

        # Nodo iniziale
        if self.shared_start_node:
            self.nodes.append(self.shared_start_node)
        else:
            self.nodes.append(Node(self.name, 0, x, y, z))

        for i in range(1, len(x_breaks)):
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

            if i == len(x_breaks) - 1 and self.shared_end_node:
                node = self.shared_end_node
            else:
                node = Node(self.name, len(self.nodes), x, y, z)

            self.nodes.append(node)

            areas, perimeters, tubi = {}, {}, {}
            for name, tube in self.data["Tubes"].items():
                area, perim = self.get_tube_property_at(x0, tube)
                areas[name] = area
                perimeters[name] = perim
                tubi[name] = area > 0.0

            segment = Segment(
                branch_name=self.name,
                segment_id=len(self.segments),
                start_node=self.nodes[-2],
                end_node=self.nodes[-1],
                alpha=alpha,
                delta=delta,
                areas=areas,
                perimeters=perimeters,
                tubi_presenti=tubi
            )
            self.segments.append(segment)

    def __repr__(self):
        return f"Branch {self.name} | {len(self.nodes)} nodi, {len(self.segments)} segmenti"

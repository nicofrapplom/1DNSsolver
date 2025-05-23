"""
models/branch.py
"""
from geometry.nodes import Node
from geometry.segments import Segment
import numpy as np


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

    def get_component_property_at(self, x, component_data):
        return self.get_value_at(x, component_data.get("Area", []), 0.0), \
            self.get_value_at(x, component_data.get("Perimeter", []), 0.0)

    def resolve_start_point(self, geometry_map: dict):
        if "start_point" in self.data:
            if "absolute" in self.data["start_point"]:
                return self.resolve_absolute_point()
            elif "from_branch" in self.data["start_point"]:
                return self.resolve_point_along_branch(geometry_map, field_name="start_point", key="from_branch")
            else:
                raise ValueError(f"start_point malformato in branch '{self.name}'")
        elif "alignment" in self.data:
            return self.resolve_aligned_point(geometry_map)
        else:
            raise ValueError(f"Start point non riconosciuto nel branch '{self.name}'")

    def resolve_end_point(self, geometry_map: dict):
        if "end_point" in self.data and "absolute" in self.data["end_point"]:
            return  # Già risolto
        elif "end_point" in self.data and "to_branch" in self.data["end_point"]:
            return self.resolve_point_along_branch(geometry_map, field_name="end_point", key="to_branch")


    def resolve_absolute_point(self):
        pass

    def resolve_point_along_branch(self, geometry_map: dict, field_name: str, key: str):
        """
        Risolve un punto assoluto lungo un altro ramo, usando 'at_length'.
        field_name: 'start_point' o 'end_point'
        key: 'from_branch' (per start) o 'to_branch' (per end)
        """
        ref = self.data[field_name][key]
        s_ref = self.data[field_name]["at_length"]

        if ref not in geometry_map:
            raise ValueError(f"Branch '{ref}' non trovato nella geometry_map")

        branch = geometry_map[ref]

        # CONTROLLO CRITICO
        if not branch.segments:
            raise RuntimeError(
                f"[ATTESA] Branch '{self.name}' non può risolvere '{field_name}' "
                f"perché il branch di riferimento '{ref}' non è stato ancora costruito."
            )

        branch = geometry_map[ref]
        tol = 1e-6
        branch_length = sum(seg.length for seg in branch.segments)

        # Inizio o fine
        if abs(s_ref) < tol:
            node = branch.nodes[0]
            if field_name == "start_point":
                self.shared_start_node = node
            else:
                self.shared_end_node = node
            self.data[field_name] = {"absolute": node.coords()}
            return

        if abs(s_ref - branch_length) < tol:
            node = branch.nodes[-1]
            if field_name == "start_point":
                self.shared_start_node = node
            else:
                self.shared_end_node = node
            self.data[field_name] = {"absolute": node.coords()}
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
                        if field_name == "start_point":
                            self.shared_start_node = node
                        else:
                            self.shared_end_node = node
                        self.data[field_name] = {"absolute": node.coords()}
                        return

                # nodo non trovato → crea nuovo nodo e spezza il segmento corrispondente
                new_node = Node(ref, -1, x, y, z)
                branch.nodes.append(new_node)  # aggiunto temporaneamente
                branch.nodes.sort(key=lambda n: n.x)  # o basato su progressiva lungo il branch

                # individua il segmento da spezzare
                seg_to_split = seg
                branch.segments.remove(seg_to_split)

                # crea due nuovi segmenti con lo stesso α, δ e proprietà
                seg1 = Segment(ref, -1, seg.start_node, new_node, seg.delta, seg.alpha,
                               seg.areas, seg.perimeters, seg.tubi_presenti)
                seg2 = Segment(ref, -1, new_node, seg.end_node, seg.delta, seg.alpha,
                               seg.areas, seg.perimeters, seg.tubi_presenti)

                branch.segments.extend([seg1, seg2])

                print(
                    f"[AUTO] Nodo creato e segmento spezzato a {s_ref:.2f} m in '{ref}' → new point = ({x:.2f}, {y:.2f}, {z:.2f})")

                if field_name == "start_point":
                    self.shared_start_node = new_node
                else:
                    self.shared_end_node = new_node
                self.data[field_name] = {"absolute": new_node.coords()}
                return

                return
            cum_length += l
            if cum_length >= branch_length and s_ref > branch_length:
                raise ValueError(
                    f"[ERRORE] Punto '{s_ref}' fuori dal ramo '{ref}' (lunghezza {branch_length:.2f})"
                )
        raise ValueError(
            f"[ERRORE] Non è stato trovato alcun segmento su cui interpolare '{field_name}' @ {s_ref} m lungo il branch '{ref}'. "
            f"Segmenti totali: {len(branch.segments)}, lunghezza totale: {branch_length:.2f} m. "
            f"Verifica che 'delta' e 'alpha' permettano una discretizzazione corretta del branch."
        )

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

            delta = self.get_value_at(0.0, self.data.get("delta", [(0.0, 0.0)]))
            alpha = self.get_value_at(0.0, self.data.get("alpha", [(0.0, 0.0)]))

            vx = 1.0
            vy = alpha / 100.0
            vz = delta / 100.0

            # Gestione infiniti
            if not all(map(np.isfinite, [vy, vz])):
                if np.isinf(vz) and np.isfinite(vy):
                    vx, vy, vz = 0.0, vy, 1.0
                elif np.isinf(vy) and np.isfinite(vz):
                    vx, vy, vz = 0.0, 1.0, vz
                elif np.isinf(vy) and np.isinf(vz):
                    vx, vy, vz = 0.0, 1.0, 1.0

            norm = (vx ** 2 + vy ** 2 + vz ** 2) ** 0.5

            dx = -s_local * vx / norm
            dy = -s_local * vy / norm
            dz = -s_local * vz / norm

            x0 = x_ref + dx
            y0 = y_ref + dy
            z0 = z_ref + dz
            self.data["start_point"] = {"absolute": (x0, y0, z0)}

    def build_geometry(self, geometry_map=None):
        # [1] Risolvi end_point se ancora relativo
        if geometry_map and "end_point" in self.data and "absolute" not in self.data["end_point"]:
            self.resolve_end_point(geometry_map)

        # [2] Risolvi start_point se ancora relativo (optional fallback)
        if geometry_map and "start_point" in self.data and "absolute" not in self.data["start_point"]:
            self.resolve_start_point(geometry_map)

        if "start_point" in self.data and "absolute" in self.data["start_point"]:
            if "length" not in self.data:
                if "end_point" in self.data and "absolute" in self.data["end_point"]:
                    # calcola la lunghezza se mancante
                    x0, y0, z0 = self.data["start_point"]["absolute"]
                    x1, y1, z1 = self.data["end_point"]["absolute"]
                    dx = x1 - x0
                    dy = y1 - y0
                    dz = z1 - z0
                    L = (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5
                    self.data["length"] = L
                else:
                    raise ValueError(
                        f"[ERRORE] Branch '{self.name}' ha start_point ma manca 'length' o end_point per calcolarla")

            L = self.data["length"]

            if "delta" not in self.data:
                self.data["delta"] = [(0.0, 100.0 * dz / L if L > 0 else 0.0)]
            if "alpha" not in self.data:
                self.data["alpha"] = [(0.0, 100.0 * dy / L if L > 0 else 0.0)]

        else:
            raise ValueError(f"[ERRORE] Branch '{self.name}' → impossibile costruire: manca start_point assoluto.")

        # Costruzione lista x_breaks
        x_breaks = set()
        for component in self.data["Components"].values():
            x_breaks.update(x for x, _ in component.get("Area", []))
            x_breaks.update(x for x, _ in component.get("Perimeter", []))
        x_breaks.update(x for x, _ in self.data.get("delta", []))
        x_breaks.update(x for x, _ in self.data.get("alpha", []))
        x_breaks.add(self.data["length"])
        x_breaks = sorted(x_breaks)

        delta_list = self.data.get("delta", [(0.0, 0.0)])
        deltalist = self.data.get("alpha", [(0.0, 0.0)])
        x, y, z = self.data["start_point"]["absolute"]

        # Nodo iniziale
        if self.shared_start_node:
            self.nodes.append(self.shared_start_node)
        else:
            self.nodes.append(Node(self.name, -1, x, y, z))

        for i in range(1, len(x_breaks)):
            x0 = x_breaks[i - 1]
            x1 = x_breaks[i]
            dx = x1 - x0

            delta = self.get_value_at(x0, delta_list)
            alpha = self.get_value_at(x0, deltalist)

            vx = 1.0
            vy = alpha / 100.0
            vz = delta / 100.0

            # Gestione infinities
            if not all(map(np.isfinite, [vy, vz])):
                if np.isinf(vz) and np.isfinite(vy):
                    vx, vy, vz = 0.0, vy, 1.0
                elif np.isinf(vy) and np.isfinite(vz):
                    vx, vy, vz = 0.0, 1.0, vz
                elif np.isinf(vy) and np.isinf(vz):
                    vx, vy, vz = 0.0, 1.0, 1.0

            norm = (vx ** 2 + vy ** 2 + vz ** 2) ** 0.5
            dx3d = dx * vx / norm
            dy3d = dx * vy / norm
            dz3d = dx * vz / norm

            x += dx3d
            y += dy3d
            z += dz3d

            if i == len(x_breaks) - 1 and self.shared_end_node:
                node = self.shared_end_node
            else:
                node = Node(self.name, -1, x, y, z)
            self.nodes.append(node)

            areas, perimeters, tubi = {}, {}, {}
            for name, component in self.data["Components"].items():
                area, perim = self.get_component_property_at(x0, component)
                areas[name] = area
                perimeters[name] = perim
                tubi[name] = area > 0.0

            segment = Segment(
                branch_name=self.name,
                segment_id=-1,
                start_node=self.nodes[-2],
                end_node=self.nodes[-1],
                delta=delta,
                alpha=alpha,
                areas=areas,
                perimeters=perimeters,
                tubi_presenti=tubi
            )
            self.segments.append(segment)

    def __repr__(self):
        return f"Branch {self.name} | {len(self.nodes)} nodi, {len(self.segments)} segmenti"

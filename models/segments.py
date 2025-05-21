"""
Segments.py
"""
class Segment:
    def __init__(self, branch_name, segment_id, start_node, end_node,
                 alpha, delta, areas, perimeters, tubi_presenti):
        self.branch = branch_name
        self.id = segment_id  # identificativo j
        self.start_node = start_node
        self.end_node = end_node
        self.length = ((end_node.x - start_node.x) ** 2 +
                       (end_node.y - start_node.y) ** 2 +
                       (end_node.z - start_node.z) ** 2) ** 0.5
        self.alpha = alpha
        self.delta = delta
        self.areas = areas  # dict: {"Main": area, "Welk": area, ...}
        self.perimeters = perimeters  # dict: {"Main": P, "Welk": P, ...}
        self.tubi_presenti = tubi_presenti  # dict: {"Main": True, ...}

    def __repr__(self):
        tubi = [k for k, v in self.tubi_presenti.items() if v]
        return (f"Segment {self.id} (Branch: {self.branch}) from Node {self.start_node.id} to Node {self.end_node.id} | "
                f"Length: {self.length:.2f} m | α={self.alpha}%, δ={self.delta}% | Tubi: {', '.join(tubi)}")

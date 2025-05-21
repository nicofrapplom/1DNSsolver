"""
Nodes.py
"""
class Node:
    def __init__(self, branch_name: str, node_id: int, x: float, y: float, z: float):
        self.branch = branch_name
        self.id = node_id  # identificativo i
        self.x = x
        self.y = y
        self.z = z

    def coords(self):
        return (self.x, self.y, self.z)

    def __repr__(self):
        return f"Node {self.id} (Branch: {self.branch}) at ({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"

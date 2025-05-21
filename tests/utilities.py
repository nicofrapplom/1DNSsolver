# -*- coding: utf-8 -*-
"""
utils.py
"""

from collections import defaultdict


def count_totals(branches):
    all_nodes = []
    all_segments = []
    for branch in branches.values():
        all_nodes.extend(branch.nodes)
        all_segments.extend(branch.segments)

    print("\n Totale rete:")
    print(f" Nodi effettivi creati   : {len(all_nodes)}")
    print(f" Segmenti effettivi      : {len(all_segments)}")

    for name, branch in branches.items():
        print(f"{name}: {len(branch.nodes)} nodi, {len(branch.segments)} segmenti")


def print_node_connections(branches):
    print("\n Lista dei nodi e segmenti collegati:")
    for branch in branches.values():
        incoming = defaultdict(list)
        outgoing = defaultdict(list)

        for seg in branch.segments:
            outgoing[seg.start_node.id].append(seg.id)
            incoming[seg.end_node.id].append(seg.id)

        for node in branch.nodes:
            print(f"Node {node.id} (Branch: {branch.name}) at ({node.x:.2f}, {node.y:.2f}, {node.z:.2f})")
            print(f"  → Segmenti in ingresso : {incoming[node.id]}")
            print(f"  → Segmenti in uscita   : {outgoing[node.id]}")


def report_branch_summary(branches):
    for name, b in branches.items():
        print(b)
        for s in b.segments:
            print(s)
    print_node_connections(branches)


def deduplicate_nodes(all_nodes, all_segments, tol=1e-6):
    """Elimina nodi con coordinate duplicate e aggiorna i segmenti."""
    unique_nodes = {}
    coord_to_node = {}
    global_id = 0
    duplicates = []

    def key(node):
        return (round(node.x / tol), round(node.y / tol), round(node.z / tol))

    for node in all_nodes:
        k = key(node)
        if k not in coord_to_node:
            # assegna nuovo ID globale
            node.id = global_id
            coord_to_node[k] = node
            unique_nodes[k] = node
            global_id += 1
        else:
            # punta al nodo già esistente
            existing = coord_to_node[k]
            duplicates.append((node, existing))
            node.id = existing.id

    # aggiorna segmenti a usare i nodi univoci
    for seg in all_segments:
        seg.start_node = coord_to_node[key(seg.start_node)]
        seg.end_node = coord_to_node[key(seg.end_node)]

    if duplicates:
        print("\nNodi condivisi (deduplicati):")
        for dup, original in duplicates:
            print(f"  Nodo {dup.id} ({dup.branch}) è condiviso con Nodo {original.id} ({original.branch})")

    return list(unique_nodes.values())





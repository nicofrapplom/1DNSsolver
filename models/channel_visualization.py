# -*- coding: utf-8 -*-
"""
models/channel_visualization.py
"""



import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot_3d(branches):
    fig = plt.figure(figsize=(12, 7))
    ax = fig.add_subplot(111, projection='3d')

    for branch in branches.values():
        for node in branch.nodes:
            ax.scatter(node.x, node.y, node.z, color='blue', s=40)
            ax.text(node.x, node.y, node.z + 0.5, f'i{node.id}', fontsize=8, color='blue')

        for seg in branch.segments:
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
    ax.set_title("Tunnel Network - Nodi (i) e Segmenti (j)")
    plt.tight_layout()
    plt.show()


def plot_xz(branches):
    fig, ax = plt.subplots(figsize=(12, 5))

    for branch in branches.values():
        for node in branch.nodes:
            ax.scatter(node.x, node.z, color='blue', s=40)
            ax.text(node.x, node.z + 0.5, f'i{node.id}', fontsize=8, color='blue')

        for seg in branch.segments:
            x0, _, z0 = seg.start_node.coords()
            x1, _, z1 = seg.end_node.coords()
            ax.plot([x0, x1], [z0, z1], color='black')
            xm = (x0 + x1) / 2
            zm = (z0 + z1) / 2
            ax.text(xm, zm, f'j{seg.id}', fontsize=8, color='darkred')

    ax.set_xlabel("X [m]")
    ax.set_ylabel("Z [m]")
    ax.set_title("Proiezione X-Z del Tunnel - Nodi (i) e Segmenti (j)")
    ax.grid(True)
    plt.tight_layout()
    plt.show()

def plot_3d_ordered(nodes, segments):
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(12, 7))
    ax = fig.add_subplot(111, projection='3d')

    for node in nodes:
        ax.scatter(node.x, node.y, node.z, color='blue', s=40)
        ax.text(node.x, node.y, node.z + 0.5, f'i{node.id}', fontsize=8, color='blue')

    for seg in segments:
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

def plot_xz_ordered(nodes, segments):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(12, 5))

    for node in nodes:
        ax.scatter(node.x, node.z, color='blue', s=40)
        ax.text(node.x, node.z + 0.5, f'i{node.id}', fontsize=8, color='blue')

    for seg in segments:
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

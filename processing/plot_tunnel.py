import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from models.stretch import Stretch  # Importa BaseStretch

def plot_connection(tunnel):
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors

    plt.figure(figsize=(15, 8))
    ax = plt.gca()
    branch_colors = ['blue', 'green', 'purple', 'orange', 'red', 'brown', 'pink', 'gray', 'cyan', 'magenta']

    for branch_index, (branch_name, branch) in enumerate(tunnel.branches.items()):
        branch_color = branch_colors[branch_index % len(branch_colors)]

        for segment_name, segment in branch.segments.items():
            ax.axvline(x=segment.start_x, color='gray', linestyle='--', linewidth=1)
            ax.axvline(x=segment.end_x, color='gray', linestyle='--', linewidth=1)

        if "Main" in branch.tubes:
            main_stretches = branch.tubes["Main"]
            if main_stretches:
                primo_stretch = main_stretches[0]
                ultimo_stretch = main_stretches[-1]

                ax.plot([primo_stretch.start_x, ultimo_stretch.end_x], [branch.y_coordinate, branch.y_coordinate],
                        color=branch_color, linewidth=3, label=f"Branch: {branch_name}")

                if primo_stretch.previous:
                    if primo_stretch.previous.name in tunnel.boundary:
                        ax.plot(primo_stretch.start_x, branch.y_coordinate, 'o', color=branch_color, markersize=20)
                        ax.text(primo_stretch.start_x, branch.y_coordinate, primo_stretch.previous.name,
                                fontsize=15, color="white", ha='center', va='center')
                    else:
                        ax.plot([primo_stretch.start_x, primo_stretch.start_x, primo_stretch.previous.end_x,primo_stretch.previous.end_x],
                                [branch.y_coordinate, branch.y_coordinate - 0.2, branch.y_coordinate - 0.2,primo_stretch.previous.y_coordinate],
                                linestyle='--', color=branch_color)
                        # ax.plot([primo_stretch.previous.end_x, primo_stretch.start_x],
                        #         [primo_stretch.previous.y_coordinate, branch.y_coordinate], linestyle='--',
                        #         color=branch_color)


                if ultimo_stretch.next:
                    if ultimo_stretch.next.name in tunnel.boundary:
                        ax.plot(ultimo_stretch.end_x, branch.y_coordinate, 'o', color=branch_color, markersize=20)
                        ax.text(ultimo_stretch.end_x, branch.y_coordinate, ultimo_stretch.next.name,
                                fontsize=15, color="white", ha='center', va='center')
                    else:
                        ax.plot([ultimo_stretch.end_x, ultimo_stretch.end_x, ultimo_stretch.next.start_x,ultimo_stretch.next.start_x],
                                [branch.y_coordinate, branch.y_coordinate - 0.2, branch.y_coordinate - 0.2,ultimo_stretch.next.y_coordinate],
                                linestyle='--', color=branch_color)


    ax.set_xlabel("X Coordinate (Absolute)")
    ax.set_ylabel("Y Coordinate")
    ax.set_title("Tunnel Structure (Connections)")
    ax.legend()
    plt.grid(True)
    plt.show(block=False)




def plot_tunnel(tunnel):
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors

    plt.figure(figsize=(15, 8))
    ax = plt.gca()
    branch_colors = ['blue', 'green', 'purple', 'orange', 'red', 'brown', 'pink', 'gray', 'cyan', 'magenta']

    for branch_index, (branch_name, branch) in enumerate(tunnel.branches.items()):
        branch_color = branch_colors[branch_index % len(branch_colors)]

        ax.plot([branch.start_point[0][0], branch.start_point[0][0] + branch.length],
                [branch.y_coordinate, branch.y_coordinate], color=branch_color,
                label=f"Branch: {branch_name}", linewidth=1)

        for segment_name, segment in branch.segments.items():
            ax.axvline(x=segment.start_x, color='gray', linestyle='--')
            ax.axvline(x=segment.end_x, color='gray', linestyle='--')

        tube_offset = 0.2
        for tube_index, (tube_name, stretches) in enumerate(branch.tubes.items()):
            if not stretches:
                continue

            tube_color = mcolors.to_rgba(branch_color, alpha=1 - (tube_index * 0.2))

            start_x = stretches[0].start_x
            end_x = stretches[-1].end_x

            ax.plot([start_x, end_x],
                    [branch.y_coordinate + tube_offset, branch.y_coordinate + tube_offset],
                    color=tube_color, linewidth=1, linestyle='-', label=f"Tube: {tube_name}")

            for stretch in stretches:
                ax.plot([stretch.start_x, stretch.end_x],
                        [branch.y_coordinate + tube_offset, branch.y_coordinate + tube_offset],
                        marker='|', markersize=8, color=tube_color, linestyle='')

            tube_offset += 0.2

    ax.set_xlabel("X Coordinate (Absolute)")
    ax.set_ylabel("Y Coordinate")
    ax.set_title("Tunnel Structure (Absolute Coordinates)")
    ax.legend()
    plt.grid(True)
    plt.show()

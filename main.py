# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 14:04:54 2025

@author: d.zaffino
"""

from processing.data_loader import load_tunnel
from processing.plot_tunnel import plot_connection,plot_tunnel # Importa la funzione plot_tunnel
from input_data.Tunnel import tunnel_data

def main():
    """Esegue il caricamento e stampa la struttura del tunnel."""
    print("\nCaricamento del tunnel dai file di input...\n")

    tunnel = load_tunnel(tunnel_data)

    if tunnel is None:
        print("\nErrore durante il caricamento del tunnel. Impossibile continuare.")
        return None

    print("\nStruttura del tunnel creata con successo:\n")
    print(tunnel)

    # for branch_name, branch_object in tunnel.branches.items():
    #     print("    ", branch_object)
    #     for section_name, section_object in branch_object.sectors.items():
    #         print("      ", section_object)
    #     for tube_name, tube_object in branch_object.tubes.items():
    #         print("      ", tube_object)

    if tunnel:
        plot_connection(tunnel)  # Chiama la funzione plot_tunnel
        plot_tunnel(tunnel)  # Chiama la funzione plot_tunnel

    return tunnel

if __name__ == "__main__":
    tunnel_object = main()

    if tunnel_object is not None:
        print("\nAnalisi dell'oggetto Tunnel:")
        print(f"Nome del tunnel: {tunnel_object.name}")
        print(f"Numero di branch: {len(tunnel_object.branches)}")

        if tunnel_object.branches:
            first_branch_name = list(tunnel_object.branches.keys())[0]
            first_branch = tunnel_object.branches[first_branch_name]
            print(f"\nAnalisi della prima branch: {first_branch.name}")


# -*- coding: utf-8 -*-
"""
File di input combinato
Creato il: Tue Mar 18 16:00:00 2025
@author: d.zaffino

Script modificato per compatibilità con la nuova struttura tunnel_data e ottimizzato.
"""
from collections import deque
from models.tunnel import Tunnel # Si assume che la classe Tunnel sia definita qui
import copy # Per deepcopy

def load_tunnel(tunnel_data_input):
    """Carica i dati dagli input e crea l'oggetto Tunnel con la struttura gerarchica."""
    try:
        # Calcola le coordinate assolute e relative delle Branches
        branches_data_with_coordinates = to_grafo(tunnel_data_input)

        return Tunnel(
            tunnel_data=tunnel_data_input,
            branches_data=branches_data_with_coordinates,
        )
    except KeyError as e:
        print(f"Errore: Chiave mancante nei dati di input: {e}")
        # Considerare di rilanciare l'eccezione o gestirla in modo più specifico
        raise
    except ValueError as e:
        print(f"Errore di validazione dei dati del tunnel: {e}")
        # Considerare di rilanciare l'eccezione o gestirla in modo più specifico
        raise
    except Exception as e:
        print(f"Errore generico durante il caricamento del tunnel: {e}")
        # Considerare di rilanciare l'eccezione o gestirla in modo più specifico
        raise
        # return None # O gestire l'errore come appropriato per l'applicazione

def to_grafo(tunnel_data_input):
    """
    Calcola le coordinate assolute delle Branches e aggiorna i dati dei rami
    (start_point, Tubes, alpha, delta, TGM) per riflettere queste coordinate assolute.
    Conserva anche una snapshot dei dati originali di ciascuna branch.
    """
    branches_data_dict = tunnel_data_input.get("branches", {})
    boundary_data = tunnel_data_input.get("Boundary", {})

    if not branches_data_dict:
        # Non è un errore fatale di per sé, potrebbe essere un tunnel vuoto.
        # Restituire un dizionario vuoto o gestire come appropriato.
        print("Avviso: Nessun dato 'branches' trovato in tunnel_data.")
        return {}

    # Non è strettamente necessario avere Boundary se le coordinate sono tutte relative
    # o se la prima branch ha uno start_point[0] esplicito.
    # Tuttavia, la logica corrente si basa su Boundary per trovare la/le prime branch.
    if not boundary_data:
        print("Avviso: Nessun dato 'Boundary' trovato in tunnel_data. Il calcolo potrebbe fallire se le branch si riferiscono a Boundary.")
        # start_boundary = None # Non usato direttamente se il loop sotto non trova nulla

    branches_with_coordinates = {}

    max_num_tubes_in_branch = 0
    if branches_data_dict.values():
        max_num_tubes_in_branch = max(
            (len(b.get("Tubes", {})) for b in branches_data_dict.values()),
            default=0
        )

    queue = deque()
    # processed_branches_init = set() # Non più necessario con il check successivo

    # Inizializza la coda con le Branch di partenza (quelle che si collegano a una Boundary)
    for branch_name, branch_data in branches_data_dict.items():
        start_point_info_list = branch_data.get("start_point", [])
        if not start_point_info_list: # Controllo per start_point mancante o vuoto
            print(f"Avviso: La branch '{branch_name}' non ha 'start_point' definito o è vuoto. Sarà ignorata nella fase di inizializzazione.")
            continue

        start_point_info = start_point_info_list[0]
        start_offset, ref_name = start_point_info

        if ref_name in boundary_data:
            if branch_name not in branches_with_coordinates:
                branches_with_coordinates[branch_name] = {
                    **copy.deepcopy(branch_data), # Inizia con una copia profonda dei dati originali della branch
                    "absolute_start_x": start_offset, # L'offset da una boundary è già "assoluto" rispetto a quella boundary
                                                      # Se si assume che la "prima" boundary sia a 0, allora questo è l'offset.
                                                      # Per convenzione, la prima branch collegata a una boundary INIZIA a x=0 del sistema globale.
                                                      # Quindi, se start_offset è 0.0 per la prima branch, va bene.
                                                      # Se si vuole che tutte le branch collegate a *qualsiasi* boundary inizino a 0 relativo a quella boundary,
                                                      # e poi si calcola la loro posizione globale, la logica qui potrebbe cambiare.
                                                      # Per ora, si assume che start_offset per la prima branch rispetto a una boundary sia la sua posizione assoluta.
                                                      # Per coerenza, se si collega a "IN" con offset 0, absolute_start_x = 0.
                    "absolute_end_x": start_offset + branch_data.get("length", 0.0),
                    "y_coordinate": 0.0  # Placeholder, verrà calcolata dopo
                }
                queue.append(branch_name)
                # processed_branches_init.add(branch_name) # Non più necessario

    #$1 Se nessuna branch parte da una boundary definita, è un errore.
    if not queue:
        raise ValueError("Nessuna branch di partenza trovata. Almeno una branch deve avere uno start_point che si riferisce a una Boundary definita.")

    # Elabora le Branches in ordine di collegamento (BFS)
    visited_for_bfs = set(b[0] for b in queue) # Inizializza con le branch già in coda

    processed_during_bfs = set() # Tiene traccia delle branch aggiunte alla coda e processate

    while queue:
        current_branch_name = queue.popleft()
        processed_during_bfs.add(current_branch_name)
        current_branch_props = branches_with_coordinates[current_branch_name]

        for next_branch_name, next_branch_data_original in branches_data_dict.items():
            if next_branch_name in branches_with_coordinates: # Già elaborata o in coda per l'elaborazione iniziale
                continue

            start_point_list_next = next_branch_data_original.get("start_point", [])
            if not start_point_list_next:
                continue

            start_offset_next, ref_name_for_start_next = start_point_list_next[0]

            if ref_name_for_start_next == current_branch_name:
                absolute_x_start_next = current_branch_props["absolute_start_x"] + start_offset_next

                branches_with_coordinates[next_branch_name] = {
                    **copy.deepcopy(next_branch_data_original), # Copia profonda dei dati originali
                    "absolute_start_x": absolute_x_start_next,
                    "absolute_end_x": absolute_x_start_next + next_branch_data_original.get("length", 0.0),
                    "y_coordinate": 0.0
                }
                if next_branch_name not in visited_for_bfs: # Evita di aggiungere più volte alla coda
                    queue.append(next_branch_name)
                    visited_for_bfs.add(next_branch_name)


    #$2 Controlla che tutte le branch siano state collegate e processate
    all_input_branch_names = set(branches_data_dict.keys())
    processed_branch_names = set(branches_with_coordinates.keys())

    unconnected_branches = all_input_branch_names - processed_branch_names
    if unconnected_branches:
        raise ValueError(f"Le seguenti branch non sono state processate o non sono connesse alla struttura principale del tunnel: {', '.join(unconnected_branches)}")

    #$3 Rimossa la sezione di aggiornamento opzionale di end_point.

    # Aggiorna le coordinate relative (start_point, Tubes, alpha, delta, TGM)
    # alle coordinate assolute e conserva una snapshot dell'originale.
    for branch_name, branch_data_processed in branches_with_coordinates.items():

        if branch_name in branches_data_dict:
             branch_data_processed["original_branch_data_snapshot"] = copy.deepcopy(branches_data_dict[branch_name])
        current_abs_start_x = branch_data_processed.get("absolute_start_x", 0.0)
        start_point_to_transform = branch_data_processed.get("start_point")
        if start_point_to_transform and isinstance(start_point_to_transform, list) and start_point_to_transform:
            branch_data_processed["start_point"] = [(current_abs_start_x, start_point_to_transform[0][1])]

        # Aggiorna coordinate per Tubes
        tubes_to_transform = branch_data_processed.get("Tubes")
        if tubes_to_transform: # Tubes è un dizionario
            new_tubes_data = {}
            for tube_name, tube_properties in tubes_to_transform.items():
                new_perimeter_list = []
                if "Perimeter" in tube_properties:
                    for p_tuple in tube_properties.get("Perimeter", []):
                        if isinstance(p_tuple, (list, tuple)) and len(p_tuple) == 2:
                            new_perimeter_list.append((current_abs_start_x + p_tuple[0], p_tuple[1]))
                        else:
                            new_perimeter_list.append(p_tuple) # Mantieni se formato non atteso

                new_area_list = []
                if "Area" in tube_properties:
                    for a_tuple in tube_properties.get("Area", []):
                        if isinstance(a_tuple, (list, tuple)) and len(a_tuple) == 2:
                            new_area_list.append((current_abs_start_x + a_tuple[0], a_tuple[1]))
                        else:
                            new_area_list.append(a_tuple) # Mantieni se formato non atteso

                new_tubes_data[tube_name] = {"Perimeter": new_perimeter_list, "Area": new_area_list}
            branch_data_processed["Tubes"] = new_tubes_data

        # Aggiorna coordinate per alpha, delta, TGM
        for key in ["alpha", "delta", "TGM"]:
            list_to_transform = branch_data_processed.get(key)
            if list_to_transform and isinstance(list_to_transform, list):
                updated_list = []
                for item_tuple in list_to_transform:
                    if isinstance(item_tuple, (list, tuple)) and len(item_tuple) == 2:
                         updated_list.append((current_abs_start_x + item_tuple[0], item_tuple[1]))
                    else:
                        updated_list.append(item_tuple)
                branch_data_processed[key] = updated_list

    # Ricostruisci il dizionario mantenendo l'ordine originale delle branches dall'input
    ordered_branches_final = {
        name: branches_with_coordinates[name]
        for name in branches_data_dict
        if name in branches_with_coordinates
    }

    # Calcola le coordinate Y
    y_offset_per_branch_level = 0.5 * (max_num_tubes_in_branch+1) if max_num_tubes_in_branch > 0 else 1.0

    current_y = 0.0
    # Assegna y_coordinate basandosi sull'ordine di input originale
    for branch_name in branches_data_dict.keys():
        if branch_name in ordered_branches_final:
            ordered_branches_final[branch_name]["y_coordinate"] = current_y
            current_y += y_offset_per_branch_level


    # Assegna y_coordinate a ciascun tube all'interno della rispettiva branch
    for branch_data in ordered_branches_final.values():
        base_y = branch_data["y_coordinate"]
        tubes = branch_data["Tubes"]  # Assumiamo che esista e sia un dizionario

        for idx, tube_name in enumerate(tubes):
            tubes[tube_name]["y_coordinate"] = base_y + 0.5 * idx

    return ordered_branches_final
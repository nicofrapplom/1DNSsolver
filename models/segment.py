from models.stretch import Stretch
from typing import List, Tuple, Dict, Optional
import typing

if typing.TYPE_CHECKING:
    from models.branch import Branch

class Segment:
    """Classe che rappresenta un singolo settore della Branch."""

    def __init__(
        self,
        start_x: float,
        end_x: float,
        branch_name:str,
        y_coordinate:float
    ):
        self.start_x = start_x
        self.end_x = end_x
        self.branch_name=branch_name
        self.y_coordinate=y_coordinate


    def __repr__(self):
        return f"Sector(start_x={self.start_x}, end_x={self.end_x})"

    @classmethod
    def create_segments(cls, Branch_data:Dict, x_end: float, Branch:str) -> Dict[str, 'Segment']:
        """Crea i segmenti della Branch, con proprietà per alpha, delta, TGM e dati dei tubi."""
        alpha = Branch_data.get("alpha", [])
        delta = Branch_data.get("delta", [])
        TGM = Branch_data.get("TGM", [])
        tubes_data = Branch_data.get("Tubes", {})

        # Raccogli tutte le tuple di Area e Perimeter da tutti i tubi
        areas_i = []
        perimeters_i = []

        for tubo in tubes_data:
            if "Area" in tubes_data[tubo]:
                areas_i.extend(tubes_data[tubo]["Area"])
            if "Perimeter" in tubes_data[tubo]:
                perimeters_i.extend(tubes_data[tubo]["Perimeter"])

        areas = unique_tuples(areas_i)
        perimeters = unique_tuples(perimeters_i)

        # Estraiamo i valori unici di x da tutte le liste
        all_x = set([x for x, _ in areas] +
                    [x for x, _ in perimeters] +
                    [x for x, _ in alpha] +
                    [x for x, _ in delta] +
                    [x for x, _ in TGM])
        all_x.add(x_end)
        unique_x = sorted(all_x)

        # Ordina una volta sola le liste (così get_last_value funziona correttamente)
        areas.sort(key=lambda x: x[0])
        perimeters.sort(key=lambda x: x[0])
        alpha.sort(key=lambda x: x[0])
        delta.sort(key=lambda x: x[0])
        TGM.sort(key=lambda x: x[0])

        segments = {}

        # Per ogni intervallo (x0, x1), crea un Segment
        for i in range(len(unique_x) - 1):
            start_x = unique_x[i]
            end_x = unique_x[i + 1]

            segment = cls(start_x=start_x, end_x=end_x, branch_name=Branch,y_coordinate=Branch_data["Tubes"]["Main"]["y_coordinate"])

            # Assegna le proprietà alpha, delta, TGM
            segment.alpha = get_last_value(alpha, start_x)
            segment.delta = get_last_value(delta, start_x)
            segment.TGM = get_last_value(TGM, start_x)

            # Costruisci il dizionario dei tubi per questo segmento
            segment.tubes = {}

            for tubo_name, tubo_data in tubes_data.items():
                area_val = get_last_value(tubo_data.get("Area", []), start_x)
                perimeter_val = get_last_value(tubo_data.get("Perimeter", []), start_x)
                y_coordinate = tubo_data["y_coordinate"]

                segment.tubes[tubo_name] = {
                    "Area": area_val,
                    "Perimeter": perimeter_val,
                    "y_coordinate":y_coordinate
                }

            # Salva il segmento nel dizionario con nome Segment-1, Segment-2, ...
            segments[f"Segment-{i + 1}"] = segment

        return segments

def get_last_value(data: List[Tuple[float, float]] or List[Tuple[float, str]], x: float) -> Optional[float] or Optional[str]:
    """Restituisce l'ultimo valore valido associato a x (se esiste)."""
    for xi, value in reversed(data):
        if xi <= x:
            return value
    return None
def unique_tuples(data):
    seen = set()
    result = []
    for item in data:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
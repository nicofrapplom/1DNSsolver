
from typing import List, Dict, Optional

DEFAULT_TEMPERATURE = 293.15
DEFAULT_PRESSURE = 101325.0


class Stretch:
    def __init__(self,
                 name: str,
                 start_x: float,
                 end_x: float,
                 area: Optional[float] = None,
                 perimeter: Optional[float] = None,
                 alpha: Optional[float] = None,
                 delta: Optional[float] = None,
                 TGM: Optional[float] = None,
                 y_coordinate: Optional[float] = None,
                 tube: Optional[str] = None,
                 temperature: Optional[float] = None,
                 pressure: Optional[float] = None,
                 branch: Optional[str] = None):
        self.name = name
        self.start_x = start_x
        self.end_x = end_x
        self.area = area
        self.perimeter = perimeter
        self.alpha = alpha
        self.delta = delta
        self.TGM = TGM
        self.y_coordinate = y_coordinate
        self.tube = tube
        self.temperature = temperature if temperature is not None else DEFAULT_TEMPERATURE
        self.pressure = pressure if pressure is not None else DEFAULT_PRESSURE
        self.branch = branch

        self.previous: Optional['Stretch'] = None
        self.next: Optional['Stretch'] = None

    def __repr__(self):
        return (f"Stretch(name={self.name}, x=[{self.start_x}-{self.end_x}], "
                f"A={self.area}, P={self.perimeter}, α={self.alpha}, δ={self.delta}, TGM={self.TGM}, "
                f"T={self.temperature:.2f}K, P={self.pressure:.0f}Pa, "
                f"sector={self.sector}, tube={self.tube})")

def divide_stretches(stretches: List['Stretch'], min_length: float, max_length: float) -> List['Stretch']:
    """Divide gli Stretch in parti con lunghezza minima e massima specificate e assegna i riferimenti precedente e successivo."""
    new_stretches = []
    for stretch in stretches:
        length = stretch.end_x - stretch.start_x
        if length > max_length:
            start_x = stretch.start_x
            while start_x < stretch.end_x:
                end_x = min(start_x + max_length, stretch.end_x)
                if end_x - start_x >= min_length:
                    new_stretch = Stretch(
                        name=stretch.name,
                        area=stretch.area,
                        perimeter=stretch.perimeter,
                        start_x=start_x,
                        end_x=end_x,
                        alpha=stretch.alpha,
                        delta=stretch.delta,
                        TGM=stretch.TGM,
                        y_coordinate=stretch.y_coordinate,
                        tube=stretch.tube,  # Assegna lo stesso tubo
                        temperature=stretch.temperature,
                        pressure=stretch.pressure,
                        branch=stretch.branch  # Aggiunto
                    )
                    new_stretches.append(new_stretch)
                    start_x = end_x
                else:
                    break
        else:
            new_stretches.append(stretch)

    # Assegna i riferimenti precedente e successivo
    for i in range(len(new_stretches)):
        if i > 0:
            new_stretches[i].previous = new_stretches[i - 1]
        if i < len(new_stretches) - 1:
            new_stretches[i].next = new_stretches[i + 1]

    return new_stretches
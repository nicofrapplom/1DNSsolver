

from typing import List,  Dict, Optional
from models.stretch import Stretch,divide_stretches

class Tubes:
    def __init__(self):
        self.tubes: Dict[str, List[Stretch]] = {}
    #
    # Serve anche dare un nome allo strech ( tipo Branch_name-Tube_name-S1 etc)


    @classmethod
    def create_Stretch(cls, segments: Dict[str, 'Segment'], branch: Optional[str] = None) -> 'Tubes':
        tubes_obj = cls()

        tube_stretch_counter = {}

        for seg_key in sorted(segments.keys(), key=lambda k: segments[k].start_x):
            segment = segments[seg_key]
            start_x = segment.start_x
            end_x = segment.end_x

            for tube_name, props in segment.tubes.items():
                if tube_name not in tube_stretch_counter:
                    tube_stretch_counter[tube_name] = 1
                else:
                    tube_stretch_counter[tube_name] += 1

                stretch_name = f"{branch}-{tube_name}-S{tube_stretch_counter[tube_name]}"

                stretch = Stretch(
                    name=stretch_name,
                    start_x=start_x,
                    end_x=end_x,
                    area=props.get("Area"),
                    perimeter=props.get("Perimeter"),
                    alpha=segment.alpha,
                    delta=segment.delta,
                    TGM=segment.TGM,
                    y_coordinate=props["y_coordinate"],
                    tube=tube_name,
                    temperature=segment.TGM,
                    pressure=segment.delta,
                    branch=branch
                )

                if tube_name not in tubes_obj.tubes:
                    tubes_obj.tubes[tube_name] = []

                if tubes_obj.tubes[tube_name]:
                    prev = tubes_obj.tubes[tube_name][-1]
                    stretch.previous = prev
                    prev.next = stretch

                tubes_obj.tubes[tube_name].append(stretch)
        for tube_name in tubes_obj.tubes:
            tubes_obj.tubes[tube_name] = divide_stretches(tubes_obj.tubes[tube_name], 10, 25)

        return tubes_obj.tubes

    def get(self, tube_name: str) -> Optional[List[Stretch]]:
        return self.tubes.get(tube_name)
    def __repr__(self):
        out = "Tubes:\n"
        for tube, stretches in self.tubes.items():
            out += f"  {tube}:\n"
            for s in stretches:
                out += f"    {s}\n"
        return out

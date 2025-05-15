

from typing import List,  Dict, Optional
from models.stretch import Stretch,divide_stretches

class Components:
    def __init__(self):
        self.components: Dict[str, List[Stretch]] = {}
    #
    # Serve anche dare un nome allo strech ( tipo Branch_name-Tube_name-S1 etc)


    @classmethod
    def create_Stretch(cls, segments: Dict[str, 'Segment'], branch: Optional[str] = None) -> 'Components':
        components_obj = cls()

        component_stretch_counter = {}

        for seg_key in sorted(segments.keys(), key=lambda k: segments[k].start_x):
            segment = segments[seg_key]
            start_x = segment.start_x
            end_x = segment.end_x

            for component_name, props in segment.components.items():
                if component_name not in component_stretch_counter:
                    component_stretch_counter[component_name] = 1
                else:
                    component_stretch_counter[component_name] += 1

                stretch_name = f"{branch}-{component_name}-S{component_stretch_counter[component_name]}"

                stretch = Stretch(
                    name=stretch_name,
                    start_x=start_x,
                    end_x=end_x,
                    area=props.get("Area"),
                    perimeter=props.get("Perimeter"),
                    alpha=segment.alpha,
                    delta=segment.delta,
                    # TGM=segment.TGM,
                    y_coordinate=props["y_coordinate"],
                    component=component_name,
                    # temperature=segment.TGM,
                    # pressure=segment.delta,
                    branch=branch
                )

                if component_name not in components_obj.components:
                    components_obj.components[component_name] = []

                if components_obj.components[component_name]:
                    prev = components_obj.components[component_name][-1]
                    stretch.previous = prev
                    prev.next = stretch

                components_obj.components[component_name].append(stretch)
        for component_name in components_obj.components:
            components_obj.components[component_name] = divide_stretches(components_obj.components[component_name], 10, 25)

        return components_obj.components

    def get(self, component_name: str) -> Optional[List[Stretch]]:
        return self.components.get(component_name)
    def __repr__(self):
        out = "Components:\n"
        for component, stretches in self.components.items():
            out += f"  {component}:\n"
            for s in stretches:
                out += f"    {s}\n"
        return out

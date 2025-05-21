# -*- coding: utf-8 -*-
"""
input_data/input_geometry.py
"""
geometry_data = {
    "branches": {
        "Branch_1": {
            "length": 1000.0,
            "start_point": {"absolute": (0.0, 0.0, 0.0)},
            "alpha": [(0.0, 2.0)],
            "delta": [(0.0, 0.0)],
            "Tubes": {
                "Main": {"Perimeter": [(0, 200)], "Area": [(0, 200), (250.0, 100)]},
                "Welk": {"Perimeter": [(0, 200)], "Area": [(0, 200)]},
                "Areazione": {"Perimeter": [(0, 200)], "Area": [(0, 200)]}
            },
            # "TGM": [(0.0, 300.2), (500.0, 1000.4)]
        },
        "Branch_2": {
            "length": 50.0,
            "start_point": {"from_branch": "Branch_1", "at_length": 250.0},
            "alpha": [(0.0, 100)],
            "delta": [(0.0, 0.0)],
            "Tubes": {
                "Main": {"Perimeter": [(0.0, 300)], "Area": [(0.0, 300)]}
            },
            # "TGM": [(0.0, 0.0)]
        },
        "Branch_3": {
            "length": 300.0,
            "alignment": {"through_branch": "Branch_2",  # Branch a cui si collega
                          "at": "length",  # specifica che è una posizione interna
                          "value": 5.0,  # distanza lungo il branch target

                          # "at": "end", # posizione del Branch a cui si collega
                          "position_along": 100.0},  # quanti metri dalla partenza di Branch_3
            "alpha": [(0.0, 2.0)],
            "delta": [(0.0, 0.0)],
            "Tubes": {
                "Main": {"Perimeter": [(0, 200)], "Area": [(0, 200)]},
                "Welk": {"Perimeter": [(0, 200)], "Area": [(0, 200)]},
                "Areazione": {"Perimeter": [(0, 200)], "Area": [(0, 200)]}
            },
            # "TGM": [(0.0, 200.0), (100.0, 150.0)]
        },
        "Branch_4": {
            "start_point": {
                "from_branch": "Branch_1",
                "at_length": 0.0
            },
            "end_point": {
                "to_branch": "Branch_3",
                "at_length": 0.0
            },
            "Tubes": {
                "Main": {"Perimeter": [(0, 200)], "Area": [(0, 200)]},

            },
            # "TGM": [(0.0, 200.0), (100.0, 150.0)]
        },
    }
}


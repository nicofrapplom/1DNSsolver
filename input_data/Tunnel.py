# -*- coding: utf-8 -*-
"""
File di input combinato
Creato il: Tue Mar 18 16:00:00 2025
@author: d.zaffino
"""

tunnel_data = {
    "name": "Tunnel_A",
    "Boundary": {
        "IN": {"temp": 293.15, "pressione": 101325},
        "IE": {"temp": 293.15, "pressione": 101000},
        "IS": {"temp": 294.15, "pressione": 101000}
    },
    "branches": {
        "Branch_1": {
            "branch_type": "Gallery",
            "length": 2000.0,
            "start_point": [(0.0, "IN")],
            "end_point": [(2000.0, "IS")],
            "alpha": [(0.0, -1.0)],
            "delta": [(0.0, 0.0)],
            "Tubes": {
                "Main": {"Perimeter": [(0, 200),(300, 200)], "Area": [(0, 200)]},
                "Welk": {"Perimeter": [(0, 200)], "Area": [(0, 200),(250, 200)]},
                "Areazione": {"Perimeter": [(0, 200)], "Area": [(0, 200),(400, 200)]}
            },
            "TGM": [(0.0, 300.2), (500.0, 1000.4)]
        },
        "Branch_2": {
            "branch_type": "Gallery",
            "length": 1800.0,
            "start_point": [(500.0, "Branch_1")],
            "end_point": [(1800.0, "IE")],
            "alpha": [(0.0, -1.0)],
            "delta": [(0.0, 0.0)],
            "Tubes": {
                "Main": {"Perimeter": [(0, 1000),(350, 1000)], "Area": [(0, 1000)]},
                "Welk": {"Perimeter": [(0, 1000)], "Area": [(0, 1000),(550, 1000)]},
                "Area_3": {"Perimeter": [(0, 1000)], "Area": [(0, 1000)]}
            },
            "TGM": [(0.0, 300.2), (500.0, 1000.4)]
        },
        "Branch_3": {
            "branch_type": "Gallery",
            "length": 500.0,
            "start_point": [(1500.0, "Branch_2")],
            "end_point": [(1800.0, "Branch_1")],
            "alpha": [(0.0, -1.0)],
            "delta": [(0.0, 0.0)],
            "Tubes": {
                "Main": {"Perimeter": [(0, 300)], "Area": [(0, 300)]},
                "Welk": {"Perimeter": [(0, 300)], "Area": [(0, 300)]}
            },
            "TGM": [(0.0, 300.2), (75.0, 1000.4)]
        },
        "Branch_4": {
            "branch_type": "Gallery",
            "length": 1800.0,
            "start_point": [(1000.0, "Branch_1")],
            "end_point": [(1500.0, "Branch_1")],
            "alpha": [(0.0, -1.0)],
            "delta": [(0.0, 0.0)],
            "Tubes": {
                "Main": {"Perimeter": [(0, 1800)], "Area": [(0, 1800)]}
        },
            "TGM": [(0.0, 300.2), (1100.0, 1000.4)]
        }
    }
}

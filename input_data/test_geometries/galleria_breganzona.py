# -*- coding: utf-8 -*-
"""
File di input combinato
Creato il: Tue Mar 18 16:00:00 2025
@author: d.zaffino
"""

geometry_data = {
    "name": "Galleria_Breganzona",
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
        }
    }
}

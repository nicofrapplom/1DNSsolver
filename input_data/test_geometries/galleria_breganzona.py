# -*- coding: utf-8 -*-
"""
File di input combinato
Creato il: Tue Mar 18 16:00:00 2025
@author: d.zaffino
"""

geometry_data = {
    "name": "Galleria_Breganzona",
    "Boundary": {
        "IO": {},
        "IE": {}
    },
    "branches": {
        "Branch_1": {
            "branch_type": "Gallery",
            "length": 2000.0,
            "start_point": [(0.0, "IO")],
            "end_point": [(2000.0, "IE")],
            "alpha": [(0.0, 0.0)],
            "delta": [(0.0, 0.0)],
            "Components": {
                "Main": {"Perimeter": [(0, 40.0)], "Area": [(0, 80.0)]}
            }
        }
    }
}

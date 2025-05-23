# Nome file: input_general.py
# File di input generali

boundaries_conditions = {
    "name": "Tunnel_A",

    "Boundary": {
        "IO": {"temp": 293.15, "pressione": 101325}, # Dobbiamo poterlo dare anche come rampa temporale, o attraverso un file direttamente nell'input
        "IE": {"temp": 293.15, "pressione": 101000} # Per alcuni nodi la boundary è velocità (o volume flow)
    },

    "Wall_Temperature": {
        "Branch_1": {
            "temp_profile": [(0, 293.15), (500, 300.0), (2000, 293.15)]
        },
        "Branch_2": {
            "temp_profile": [(0, 290.0), (1000, 305.0)]
        }
    },

    "Mountain_Heating": {
        "Branch_1": {
            "Q_profile": [(0, 200), (1000, 300), (2000, 200)]  # W/m
        }
    },

    "Fire": {
        "Branch_1": {
            "location": 1000,        # m
            "start_time": 120,       # s
            "Q_curve": [(0, 0), (10, 1e6), (300, 0)]  # W/m³ numeri oppure predefined functions
        }
    }
}

mesh = {
    "dx": 10.0
}

simulation_settings = {
    "dt": 1.0,
    "t_end": 600.0
}
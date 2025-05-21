# processing/parameters.py

import json

class SimulationParameters:
    """
    Contiene i parametri della simulazione:
    - condizioni al contorno (pressione, temperatura, parete)
    - parametri numerici (dt, t_end, n_steps)
    - parametri tecnici del solver (tol, max_iter, ecc.)
    - profili distribuiti (temperatura parete per branch)
    """

    def __init__(self, boundaries_conditions: dict, simulation_settings: dict):
        """
        boundaries_conditions: dizionario con chiavi:
            - 'Boundary': contiene 'IO', 'IE' → dizionari con 'temp' e 'pressione'
            - 'Wall_Temperature': profili per branch → {'Branch_1': {'temp_profile': [...]}}

        simulation_settings: dict con:
            - 'dt': passo temporale [s]
            - 't_end': durata totale della simulazione [s]
        """

        # === Estrazione condizioni al contorno ===
        boundary = boundaries_conditions.get("Boundary", {})
        self.p_i_IO = boundary.get("IO", {}).get("pressione", 101325.0)
        self.p_i_IE = boundary.get("IE", {}).get("pressione", 101000.0)
        self.T_i_IO = boundary.get("IO", {}).get("temp", 293.15)
        self.T_i_IE = boundary.get("IE", {}).get("temp", 293.15)

        # === Profili distribuiti ===
        self.wall_temperature_profiles = boundaries_conditions.get("Wall_Temperature", {})

        # === Parametri numerici ===
        self.dt = simulation_settings.get("dt", 1.0)
        self.t_end = simulation_settings.get("t_end", 600.0)
        self.n_steps = int(self.t_end / self.dt)

        # === Parametri solver (interni, non modificabili da input) ===
        self.max_iter = 150
        self.tol = 1e-5
        self.alpha_u = 1.0
        self.alpha_p = 1.0

        # === Debug ===
        print(f"[PARAMETERS] dt = {self.dt}, t_end = {self.t_end}, steps = {self.n_steps}")
        print(f"[PARAMETERS] p_i_IO = {self.p_i_IO}, p_i_IE = {self.p_i_IE}")
        print(f"[PARAMETERS] T_i_IO = {self.T_i_IO}, T_i_IE = {self.T_i_IE}")
        print(f"[PARAMETERS] Wall_Temperature profiles: {list(self.wall_temperature_profiles.keys())}")

    def as_dict(self) -> dict:
        """Restituisce i parametri principali come dizionario."""
        return {
            "dt": self.dt,
            "t_end": self.t_end,
            "n_steps": self.n_steps,
            "p_i_IO": self.p_i_IO,
            "p_i_IE": self.p_i_IE,
            "T_i_IO": self.T_i_IO,
            "T_i_IE": self.T_i_IE,
            "wall_temperature_profiles": self.wall_temperature_profiles,
            "max_iter": self.max_iter,
            "tol": self.tol,
            "alpha_u": self.alpha_u,
            "alpha_p": self.alpha_p
        }

    def save_to_file(self, filepath: str):
        """Salva i parametri in un file JSON per tracciabilità o post-processing."""
        with open(filepath, "w") as f:
            json.dump(self.as_dict(), f, indent=2)

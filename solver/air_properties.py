"""
Nome file: solver/air_properties.py
"""

import numpy as np

class AirProperties:
    def __init__(self):
        # Costanti fisiche dell'aria
        self.g = 9.81               # m/s²
        self.R = 287.05             # J/(kg·K)
        self.c_p = 1005.0           # J/(kg·K)
        self.mu = 1.8e-5            # Pa·s
        self.lambda_air = 0.026     # W/(m·K)
        self.Pr = 0.71

    def calc_rho_i(self, T_nodes, p_nodes):
        return p_nodes / (self.R * T_nodes)

    def calc_rho_j(self, rho_i, u_j):
        rho_j = np.zeros_like(u_j)
        for j in range(len(u_j)):
            rho_j[j] = rho_i[j] if u_j[j] >= 0 else rho_i[j + 1]
        return rho_j

    def compute_Reynolds(self, rho_j, u_j, D):
        return rho_j * np.abs(u_j) * D / self.mu

    def compute_Nusselt(self, Re, heating=True):
        if Re > 4000:
            n = 0.4 if heating else 0.3
            return 0.023 * Re**0.8 * self.Pr**n
        else:
            G = Re * self.Pr
            Nu = 3.66 + (0.065 * G) / (1 + 0.04 * G**(2/3))
            return max(Nu, 3.66)

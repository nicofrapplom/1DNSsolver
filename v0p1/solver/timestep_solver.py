"""
Nome file: solver/timestep_solver.py
"""

from solver.momentum import build_Y, build_t, solve_momentum
from solver.pressure import pressure_correction, velocity_correction
from solver.update import update_fields
from solver.energy import solve_energy_equation  # opzionale

class TimestepSolver:
    """
    Classe che gestisce le iterazioni interne di un singolo timestep.
    """

    def __init__(self, mesh, parameters, air_properties):
        self.mesh = mesh
        self.params = parameters
        self.air = air_properties

    def run_iter(self, p_i, u_j, T_i, step):
        """
        Esegue l'iterazione implicita per un singolo timestep.
        Restituisce p_i_new, u_j_new, T_i_new, n_iter
        """
        dt = self.params.dt
        max_iter = self.params.max_iter
        tol = self.params.tol
        alpha_u = self.params.alpha_u
        alpha_p = self.params.alpha_p

        u_j_prev = u_j.copy()
        T_i_prev = T_i.copy()

        rho_i = self.air.calc_rho_i(T_i, p_i)
        rho_j = self.air.calc_rho_j(rho_i, u_j_prev)
        rho_i_prev = rho_i.copy()

        for it in range(max_iter):
            Y, Y_inv = build_Y(self.mesh, u_j, rho_j, self.params)
            t_vec = build_t(self.mesh, u_j_prev, rho_j, rho_i, self.params)

            u_star = solve_momentum(self.mesh.A_T, p_i, Y_inv, t_vec)
            p_corr = pressure_correction(self.mesh.A, u_star, Y_inv, rho_j, rho_i, rho_i_prev, self.params)
            u_corr = velocity_correction(self.mesh.A_T, p_corr, Y_inv)

            p_i_new, u_j_new = update_fields(p_i, u_star, p_corr, u_corr, alpha_p, alpha_u, self.params)

            if self.params.enable_energy:
                T_i_new = solve_energy_equation(rho_i, rho_j, T_i, T_i_prev, u_j_new, self.mesh, self.params)
            else:
                T_i_new = T_i.copy()

            err_p = np.linalg.norm(p_corr[1:-1])
            err_u = np.linalg.norm(u_corr)
            err_T = np.linalg.norm(T_i_new - T_i)

            if err_p < tol and err_u < tol and err_T < tol:
                break

            p_i, u_j, T_i = p_i_new, u_j_new, T_i_new

        return p_i_new, u_j_new, T_i_new, it + 1

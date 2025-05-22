# solver/UEqn.py

import numpy as np

def build_Y(mesh, u_j, rho_j, f, beta, D, dt):
    """
    Costruisce la matrice diagonale Y per l'equazione della quantità di moto.
    Y = termine transitorio + perdite (attrito + perdite locali)
    """
    trans = rho_j * mesh.L_j / dt
    frict = 0.5 * (f * mesh.L_j / D + beta) * rho_j * np.abs(u_j)

    Y_diag = trans + frict
    Y = np.diag(Y_diag)
    Y_inv = np.diag(1.0 / Y_diag)

    return Y, Y_inv

def build_t(mesh, u_j_prev, rho_j, rho_i, g, slope_percent, dt):
    """
    Costruisce il termine noto t nella forma:
    t = -transitorio - piston + chimney
    """
    # Transitorio (dipendente dalla velocità al passo precedente)
    t_trans = -rho_j * mesh.L_j / dt * u_j_prev

    # Chimney effect: dp_ch = -slope * delta(rho) * g * dx
    drho = rho_i[1:] - rho_i[:-1]  # dimensione: num_branches
    slope = slope_percent / 100.0
    dp_chimney = -slope * (drho / 2.0) * g * mesh.L_j

    # Piston effect placeholder (da aggiungere se necessario)


    t_vec = t_trans + dp_chimney
    return t_vec

def solve_momentum(A_T, p_i, Y_inv, t):
    """
    Risolve per u*:
    u* = Y_inv (A^T p - t)
    """
    rhs = A_T @ p_i - t
    u_star = Y_inv @ rhs
    return u_star

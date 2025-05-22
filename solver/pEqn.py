# solver/pEqn.py

import numpy as np

def pressure_correction(A, u_star, Y_inv, rho_j, rho_i, rho_i_prev, mesh, params):
    """
    Calcola la correzione di pressione p'.
    Risolve il sistema K p' = -r, con:
      - K = A M Y⁻¹ Aᵀ
      - r = A (M u*) + b_trans
    """
    S = mesh.area_j
    M = np.diag(rho_j * S)  # matrice massa M = diag(rho * S)

    r1 = A @ (M @ u_star)  # residuo base

    # Termine b transitorio esplicito: coeff * (rho_i - rho_i_prev)
    coeff = np.abs(A) @ (mesh.L_j / (2 * params.dt))
    b_trans = coeff * (rho_i - rho_i_prev)

    r = r1 + b_trans

    # Applicazione BC: nodi interni (escludo 0 e -1)
    r_int = r[1:-1]
    A_int = A[1:-1, :]

    # Matrice sistema K
    K = A_int @ M @ Y_inv @ A_int.T

    # Risoluzione del sistema
    p_corr_int = np.linalg.solve(K, -r_int)

    # Ricostruzione il vettore completo con p'_0 = p'_N = 0
    p_corr = np.zeros(mesh.num_nodes)
    p_corr[1:-1] = p_corr_int

    return p_corr

def velocity_correction(A_T, p_corr, Y_inv):
    """
    Calcola la correzione di velocità u' = Y⁻¹ Aᵀ p'
    """
    return Y_inv @ A_T @ p_corr

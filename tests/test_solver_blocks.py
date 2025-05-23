import sys
import os
import numpy as np

# Setup path di progetto
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Import locali coerenti col tuo progetto
from processing.data_loader import load_geometry
from input_data.test_geometries.galleria_breganzona import geometry_data
from input_data.test_setups.Test_Neva.input_general import boundaries_conditions, simulation_settings
from solver.parameters import SimulationParameters
from models.fvmesh import Mesh1D
from solver.UEqn import build_Y, build_t, solve_momentum
from solver.pEqn import pressure_correction, velocity_correction
from solver.air_properties import AirProperties
from solver.initial_conditions import (
    initialize_pressure,
    initialize_temperature,
    initialize_velocity
)

# === Caricamento geometria e mesh
geometry = load_geometry(geometry_data)
first_branch = list(geometry.branches.values())[0]
stretches = first_branch.components["Main"]
mesh = Mesh1D(stretches)

# === Parametri e proprietà
params = SimulationParameters(boundaries_conditions, simulation_settings)
air = AirProperties()
f = 0.015
D = 1.0
beta = np.zeros(mesh.num_branches)
beta[0] = 1.0
beta[-1] = 0.6
slope_percent = 2.0

# === Condizioni iniziali
p_i = initialize_pressure(mesh.num_nodes, params.p_i_IO, params.p_i_IE)
T_i = initialize_temperature(mesh.num_nodes, params.T_i_IE)
u_j = initialize_velocity(mesh.num_branches)

# === Densità e sistema
rho_i = air.calc_rho_i(T_i, p_i)
rho_j = air.calc_rho_j(rho_i, u_j)

Y, Y_inv = build_Y(mesh, u_j, rho_j, f, beta, D, params.dt)
t_vec = build_t(mesh, u_j, rho_j, rho_i, air.g, slope_percent, params.dt)
u_star = solve_momentum(mesh.A_T, p_i, Y_inv, t_vec)

p_corr = pressure_correction(mesh.A, u_star, Y_inv, rho_j, rho_i, rho_i, mesh, params)
u_corr = velocity_correction(mesh.A_T, p_corr, Y_inv)

# === Output verifica
print("Y =\n", Y)
print("t =\n", t_vec)
print("u* =", u_star)
print("p' =", p_corr)
print("u' =", u_corr)

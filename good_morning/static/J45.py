from good_morning.fittings.J_versus_voltage import fit_J, J_to_voltage, fit_delta_B_vs_J
from core_tools.utility.variable_mgr.var_mgr import variable_mgr
import numpy as np

from core_tools.data.SQL.connect import set_up_local_storage
set_up_local_storage("xld_user", "XLDspin001", "vandersypen_data", "6dot", "XLD", "6D2S - SQ21-1-2-10-DEV-1")

gates  = ('vB0','vP1', 'vB1','vP2', 'vB2','vP3', 'vB3','vP4', 'vB4','vP5', 'vB5','vP6')
voltages_gates = (-0,0, -0,0, -0,0, -70,variable_mgr().symm45_P4, variable_mgr().cphase45_B4,variable_mgr().symm45_P5, -70,0)
# voltages_gates = (0,0,0,0, 0,0, -80,0, 200,0, -100,0)

J_off = 0.022917827490600135
J_max = 4306.648735663147
alpha = 3.7242883106110556

def return_scalled_barier(voltage):
	args = [variable_mgr().J_V_off45, variable_mgr().J_max45, variable_mgr().J_alpha45]
	def barrier(J):
		return voltage*J_to_voltage(J, *args)
	return barrier

def gen_J_to_voltage():
	barriers = []
	for gate, voltage in zip(gates, voltages_gates):
		barriers += [return_scalled_barier(voltage)]
	return barriers

def barrier_perc_to_voltage(percentage):
	voltages = list()
	for V in voltages_gates:
		voltages.append(percentage*V)

	return tuple(voltages)
	
def return_delta_B_J_relation():
	coeff= []
	for i in range(6):
		coeff += [getattr(variable_mgr(),f'iSWAP_45_J_f_res_coeff_{i}')]

	return np.poly1d(coeff)

J_rel = np.array([0e6, 0.2e6, 0.3e6, 0.5e6 ,1e6 ,2e6 ,3e6 ,4e6 ,5e6 ,6e6 ,7e6, 8e6])
delta_B = np.array([82.32e6, 79.96e6, 79.66e6, 79.23e6 , 78.77e6, 78.13e6, 77.7e6, 77.5e6, 77.26e6, 77.11e6, 76.97e6, 76.86e6])


if __name__ == '__main__':
	import numpy as np
	barrier_percentage = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
	J_effective = np.array([10e3, 20e3, 28e3, 40e3, 110e3, 0.18e6, 0.42e6, 0.96e6,  1.84e6, 4.3e6, 8.74e6 ])
	
	poly = fit_delta_B_vs_J(J_rel, delta_B, True)

	J_off, J_max, alpha = fit_J(barrier_percentage, J_effective, True)
	print(J_off, J_max, alpha)
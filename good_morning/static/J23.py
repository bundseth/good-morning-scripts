from good_morning.fittings.J_versus_voltage import fit_J, J_to_voltage, fit_delta_B_vs_J
from core_tools.utility.variable_mgr.var_mgr import variable_mgr
import numpy as np

gates  = ('vB0','vP1', 'vB1','vP2', 'vB2','vP3', 'vB3','vP4', 'vB4','vP5', 'vB5','vP6')
voltages_gates = (-80,0, -80,variable_mgr().symm23_P2, variable_mgr().B2_23,variable_mgr().symm23_P3, -80,0, -80,0, -80,0)

J_off = -0.0023569391439328497
J_max =280095.87977114564
alpha = 2.157771283116629

J_rel = np.array([0e6 ,1e6 ,2e6 ,3e6 ,4e6 ,5e6 ,6e6 ,7e6, 8e6 ,9e6 ,10e6])
delta_B = np.array([61.81e6 , 58.25e6, 55.76e6, 54.6e6, 53.8e6, 53.4e6, 53.27e6, 53.19e6, 53.3e6, 53.5e6, 53.8e6])

def _return_scalled_barier_(voltage):
	def barrier(J):
		return voltage*J_to_voltage(J, variable_mgr().J_V_off23, variable_mgr().J_max23, variable_mgr().J_alpha23)
	return barrier

def gen_J_to_voltage():
	barriers = []
	for gate, voltage in zip(gates, voltages_gates):
		barriers += [_return_scalled_barier_(voltage)]
	return barriers

def return_delta_B_J_relation():
	return fit_delta_B_vs_J(J_rel*2, delta_B, False)

if __name__ == '__main__':
	import numpy as np
	import matplotlib.pyplot as plt

	barrier_percentage = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
	J_effective = np.array([200e3, 350e3, 525e3, 1.28e6, 1.45e6, 1.77e6, 3.7e6, 5.4e6, 9.0e6, 14.1e6, 20.4e6])
	
	J_rel = [0e6 ,1e6 ,2e6 ,3e6 ,4e6 ,5e6 ,6e6 ,7e6, 8e6 ,9e6 ,10e6]
	delta_B = [61.81e6 , 58.25e6, 55.76e6, 54.6e6, 53.8e6, 53.4e6, 53.27e6, 53.19e6, 53.3e6, 53.5e6, 53.8e6]
	# plt.plot(J_rel, delta_B)
	# plt.show()
	poly = fit_delta_B_vs_J(J_rel, delta_B, True)
	print(poly(5e6))
	# J_off, J_max, alpha = fit_J(barrier_percentage, J_effective, True)
	# print(J_off, J_max, alpha)

	# a =J_to_voltage([200e3, 350e3, 525e3, 1.28e6, 1.45e6, 1.77e6, 3.7e6, 5.4e6, 9.0e6, 14.1e6, 20.4e6], J_off, J_max, alpha)
	# print(a)
from core_tools.data.SQL.connect import set_up_local_storage
set_up_local_storage("xld_user", "XLDspin001", "vandersypen_data", "6dot", "XLD", "6D2S - SQ21-1-2-10-DEV-1")

from good_morning.fittings.J_versus_voltage import fit_J, J_to_voltage, voltage_to_J
from core_tools.utility.variable_mgr.var_mgr import variable_mgr

gates  = ('vB0','vP1', 'vB1','vP2', 'vB2','vP3', 'vB3','vP4', 'vB4','vP5', 'vB5','vP6')
voltages_gates = (-50,variable_mgr().symm12_P1, variable_mgr().cphase12_B1,variable_mgr().symm12_P2, -80,0, -0,0, -0,0, -0,0)
# voltages_gates = (-40,0,50,0, -40,0,0,0,0,0,0,0) 

J_off = 0.019 
J_max = 46213.051 
alpha = 2.479

def _return_scalled_barier_(voltage):
	def barrier(J):
		return voltage*J_to_voltage(J, variable_mgr().J_V_off12, variable_mgr().J_max12, variable_mgr().J_alpha12)
	return barrier

def gen_J_to_voltage():
	barriers = []
	for gate, voltage in zip(gates, voltages_gates):
		barriers += [_return_scalled_barier_(voltage)]
	return barriers

def barrier_perc_to_voltage(percentage):
	voltages = list()
	for V in voltages_gates:
		voltages.append(percentage*V)

	return tuple(voltages)

if __name__ == '__main__':
	import numpy as np
	import matplotlib.pyplot as plt

	barrier_percentage = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
	J_effective = np.array([6.60e+04, 9.10e+04, 1.81e+05, 3.60e+05, 6.25e+05, 1.00e+06, 1.60e+06, 2.40e+06, 4.80e+06, 7.10e+06])
	
	# J_off, J_max, alpha = fit_J(barrier_percentage, J_effective)
	# print(J_off, J_max, alpha)
	# _return_scalled_barier_(1)

	plt.plot(barrier_percentage, J_effective)
	plt.plot(barrier_percentage,voltage_to_J(barrier_percentage, variable_mgr().J_V_off12, variable_mgr().J_max12, variable_mgr().J_alpha12))
	plt.show()
	# a =J_to_voltage([0, 6.60e+04, 9.10e+04, 1.81e+05, 3.60e+05, 6.25e+05, 1.00e+06, 1.60e+06, 2.40e+06, 4.80e+06, 7.10e+06], J_off, J_max, alpha)
	# print(a)


	generators = gen_J_to_voltage()

	on = list()
	J_wanted = 5e6

	for gen in generators:
		on.append(gen(J_wanted))

	print(on)
from good_morning.fittings.J_versus_voltage import fit_J, J_to_voltage
from core_tools.utility.variable_mgr.var_mgr import variable_mgr



gates  = ('vB0','vP1', 'vB1','vP2', 'vB2','vP3', 'vB3','vP4', 'vB4','vP5', 'vB5','vP6')
voltages_gates = (-40,0, -40,0, -40,0, -40,0, -140,variable_mgr().symm56_P5, variable_mgr().cphase56_B5,variable_mgr().symm56_P6) 
# voltages_gates = (-120,0,0,0, -80,0, -70,0, -70,0, -70,0)

J_off = 0.0264355989289498
J_max = 39003.52887708517
alpha = 2.2928821036820044

def return_scalled_barier(voltage):
	def barrier(J):
		return voltage*J_to_voltage(J, variable_mgr().J_V_off56, variable_mgr().J_max56, variable_mgr().J_alpha56)
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
	

if __name__ == '__main__':
	import numpy as np
	barrier_percentage = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
	J_effective = np.array([30e3, 50e3, 83e3, 150e3, 270e3, 0.38e6, 0.67e6, 1.08e6, 1.74e6, 2.82e6, 4.27e6 ])
	
	J_off, J_max, alpha = fit_J(barrier_percentage, J_effective, True)
	print(J_off, J_max, alpha)

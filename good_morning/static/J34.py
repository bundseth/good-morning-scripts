from good_morning.fittings.J_versus_voltage import fit_J, J_to_voltage
from core_tools.utility.variable_mgr.var_mgr import variable_mgr

from core_tools.data.SQL.connect import set_up_local_storage
set_up_local_storage("xld_user", "XLDspin001", "vandersypen_data", "6dot", "XLD", "6D2S - SQ21-1-2-10-DEV-1")
gates  = ('vB0','vP1', 'vB1','vP2', 'vB2','vP3', 'vB3','vP4', 'vB4','vP5', 'vB5','vP6')
voltages_gates = (0,0, 0,0, -50,variable_mgr().symm34_P3, variable_mgr().cphase34_B3,variable_mgr().symm34_P4, -50,0, -0,0)
# voltages_gates = (-120,0,0,0, -80,0, -70,0, -70,0, -70,0)
 
J_off = -0.02003706650354627 
J_max = 91207.33465174529
alpha = 2.408349090428599 
  
 
def return_scalled_barier(voltage):
	def barrier(J):
		return voltage*J_to_voltage(J, variable_mgr().J_V_off34, variable_mgr().J_max34, variable_mgr().J_alpha34)
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

if __name__ == '__main__':
	import numpy as np
	barrier_percentage = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
	J_effective = np.array([50e3, 80e3, 150e3, 280e3, 500e3,  0.84e6, 1.46e6, 2.45e6,  3.98e6, 6.37e6, 10.185e6 ])
	
	J_off, J_max, alpha = fit_J(barrier_percentage, J_effective, True)
	print(J_off, J_max, alpha)
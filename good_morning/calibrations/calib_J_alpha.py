from good_morning.fittings.J_versus_voltage import fit_J, J_to_voltage, voltage_to_J
from good_morning.calibrations.ultility import get_target, readout_convertor
from good_morning.fittings.fit_rabi_osc import fit_ramsey

from core_tools.sweeps.pulse_lib_wrappers.PSB_exp import run_qubit_exp
from core_tools.utility.variable_mgr.var_mgr import variable_mgr
from core_tools.sweeps.sweeps import scan_generic, do0D, do1D
from core_tools.job_mgnt.job_mgmt import job_wrapper

from pulse_templates.coherent_control.two_qubit_gates.cphase import cphase_basic

from dev_V2.six_qubit_QC_v2.system import six_dot_sample
import pulse_lib.segments.utility.looping as lp

import qcodes as qc
import numpy as np

import good_morning.static.J12 as J12
import good_morning.static.J23 as J23
import good_morning.static.J34 as J34
import good_morning.static.J45 as J45
import good_morning.static.J56 as J56

@job_wrapper
def calib_J_alpha(target, plot=False):
	'''
	calibrates a single qubit phase for a target qubit

	Args:
		target (int) : qubit pair to target
	'''
	var_mgr = variable_mgr()
	s = six_dot_sample(qc.Station.default.pulse)

	target = str(int(target))
	s.init(target[0], target[1])

	s.add(s.wait(100))
	s.add(s.pre_pulse)
	s.add(s.wait(100))

	N_J = 5

	J_target = globals()[f'J{target}']
	barrier = lp.linspace(0.8, 1, N_J, axis = 1,name=f'vB{target[0]}', unit='mV')
	gate_time = lp.linspace(0,getattr(var_mgr, f'cphase_time_{target}')*10, 80, axis=0, name='time', unit='ns')

	s.add(s[f'q{target[0]}'].X90)
	s.add_func(cphase_basic, J_target.gates, tuple([0]*len(J_target.gates)), J_target.barrier_perc_to_voltage(barrier), t_gate= gate_time/2, t_ramp=10)
	s.add(s[f'q{target[0]}'].X180)
	s.add(s[f'q{target[1]}'].X180)
	s.add_func(cphase_basic, J_target.gates, tuple([0]*len(J_target.gates)), J_target.barrier_perc_to_voltage(barrier), t_gate= gate_time/2, t_ramp=10)
	s.add(s[f'q{target[0]}'].X90)

	s.add(s.wait(100))

	s.read(target[0],target[1])

	sequence, minstr, name = run_qubit_exp(f'J_V cal :: {target}', s.sequencer)
	ds = scan_generic(sequence, minstr, name=name).run()


	time = ds(readout_convertor(f'read{target[0]}')).y()*1e-9
	probabilities = ds(readout_convertor(f'read{target[0]}')).z()
	
	J_meas=[]
	for i in range(N_J):
		time_fit = time[5:]
		probabilities_fit = probabilities[i][5:]
		J_meas += [2/(fit_ramsey(time_fit, probabilities_fit, plot=plot)*2)*1e9]

	barrier_percentage = np.asarray([0] + list(np.linspace(0.8, 1,5)))
	J_V_off, J_max, alpha = fit_J(barrier_percentage, np.array([10e3] + J_meas), plot=plot)

	if not hasattr(var_mgr,f'J_V_off{target}'):
		var_mgr.add_variable(f'CPhase{target}',f'J_V_off{target}', 'mV',0.1,0)
	if not hasattr(var_mgr,f'J_max{target}'):
		var_mgr.add_variable(f'CPhase{target}',f'J_max{target}', 'mV',0.1,0)
	if not hasattr(var_mgr,f'J_alpha{target}'):
		var_mgr.add_variable(f'CPhase{target}',f'J_alpha{target}', 'mV',0.1,0)		
	setattr(var_mgr,f'J_V_off{target}', round(J_V_off,6))
	setattr(var_mgr,f'J_max{target}', round(J_max,5))
	setattr(var_mgr,f'J_alpha{target}', round(alpha,5))

	print(f'calibrated J_{target} with a J_max of {np.array(J_meas)[-1]}')

if __name__ == '__main__':
	from core_tools.data.SQL.connect import set_up_local_storage
	set_up_local_storage("xld_user", "XLDspin001", "vandersypen_data", "6dot", "XLD", "6D2S - SQ21-1-2-10-DEV-1")

	import matplotlib.pyplot as plt
	from core_tools.data.ds.data_set import load_by_uuid
	ds = load_by_uuid(1646647112053974076)

	var_mgr = variable_mgr()
	target= '12'

	gates = globals()[f'J{target}'].gates
	N_J = 5


	time = ds(readout_convertor(f'read{target[0]}')).y()*1e-9
	probabilities = ds(readout_convertor(f'read{target[0]}')).z()

	J_meas=[]
	for i in range(N_J):
		time_fit = time[2:]
		probabilities_fit = probabilities[i][2:]
		J_meas += [2/(fit_ramsey(time_fit, probabilities_fit, plot=False)*2)*1e9]

	barrier_percentage = np.asarray([0] + list(np.linspace(0.8, 1,5)))

	J_V_off, J_max, alpha = fit_J(barrier_percentage, np.array([10e3] + J_meas), plot=True)

	if not hasattr(var_mgr,f'J_V_off{target}'):
		var_mgr.add_variable(f'CPhase{target}',f'J_V_off{target}', 'mV',0.1,0)
	if not hasattr(var_mgr,f'J_max{target}'):
		var_mgr.add_variable(f'CPhase{target}',f'J_max{target}', 'mV',0.1,0)
	if not hasattr(var_mgr,f'J_alpha{target}'):
		var_mgr.add_variable(f'CPhase{target}',f'J_alpha{target}', 'mV',0.1,0)	
	print(J_V_off, J_max, alpha)	
	setattr(var_mgr,f'J_V_off{target}', J_V_off)
	setattr(var_mgr,f'J_max{target}', J_max)
	setattr(var_mgr,f'J_alpha{target}', alpha)
	print(round(J_V_off,6), round(J_max,5), round(alpha,5))
	print(f'calibrated J_{target} with a J_max of {np.array(J_meas)[-1]}')
	import matplotlib.pyplot as plt
	voltage= np.linspace(0,1)
	plt.plot(voltage, round(J_max,5)*np.exp(2*round(alpha,5)*(voltage+ round(J_V_off,6))))

	plt.plot(voltage, J_max*np.exp(2*alpha*(voltage+ J_V_off)))
	plt.show()
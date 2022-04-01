from good_morning.fittings.J_versus_voltage import fit_J, J_to_voltage, voltage_to_J
from good_morning.calibrations.ultility import get_target, readout_convertor
from good_morning.fittings.fit_rabi_osc import fit_ramsey

from core_tools.sweeps.pulse_lib_wrappers.PSB_exp import run_qubit_exp
from core_tools.utility.variable_mgr.var_mgr import variable_mgr
from core_tools.sweeps.sweeps import scan_generic, do0D, do1D
from core_tools.job_mgnt.job_mgmt import job_wrapper

import pulse_lib.segments.utility.looping as lp

from pulse_templates.coherent_control.two_qubit_gates.cphase import cphase_basic
from dev_V2.six_qubit_QC.system import six_dot_sample

import qcodes as qc
import numpy as np

import good_morning.static.J12 as J12
import good_morning.static.J23 as J23
import good_morning.static.J34 as J34
import good_morning.static.J45 as J45
import good_morning.static.J56 as J56

@job_wrapper
def calib_J_V_off(target, plot=False):
	'''
	calibrates a single qubit phase for a target qubit

	Args:
		target (int) : qubit pair to target
	'''
	var_mgr = variable_mgr()
	s = six_dot_sample(qc.Station.default.pulse)

	target = str(int(target))
	s.init(target[0], target[1])

	s.wait(100).add(s.manip)
	s.pre_pulse.add(s.manip)
	s.wait(100).add(s.manip)

	gates = globals()[f'J{target}'].gates
	voltages =globals()[f'J{target}'].voltages_gates
	gate_time = lp.linspace(0,getattr(var_mgr, f'time_{target}')*8, 100, axis=0, name='time', unit='ns')
	
	getattr(s,f'q{target[0]}').X90.add(s.manip)
	cphase_basic(s.manip, gates, tuple([0]*len(gates)), voltages, t_gate= gate_time/2, t_ramp=100)
	getattr(s,f'q{target[0]}').X180.add(s.manip)
	getattr(s,f'q{target[1]}').X180.add(s.manip)
	cphase_basic(s.manip, gates, tuple([0]*len(gates)), voltages, t_gate= gate_time/2, t_ramp=100)
	getattr(s,f'q{target[0]}').X90.add(s.manip)

	s.wait(100).add(s.manip)

	s.read(target[0], target[1])

	sequence, minstr, name = run_qubit_exp(f'J_V_off cal :: {target}', s.segments(), s.measurement_manager)
	ds = scan_generic(sequence, minstr, name=name).run()

	time = ds(readout_convertor(f'read{target[0]}')).x()*1e-9
	probabilities = ds(readout_convertor(f'read{target[0]}')).y()
	time = time[5:]
	probabilities = probabilities[5:]
	Pi_time = fit_ramsey(time, probabilities, plot=plot)
	J_max = 1/(Pi_time*2)*1e9
	
	J_max_voltage = J_to_voltage(J_max, 0, globals()[f'J{target}'].J_max, globals()[f'J{target}'].alpha)
	J_off = J_max_voltage - 1

	if not hasattr(var_mgr,f'J_V_off{target}'):
		var_mgr.add_variable(f'cphase{target}',f'J_V_off{target}', 'mV',0.1,0)

	old_phase = getattr(var_mgr,f'J_V_off{target}')
	setattr(var_mgr,f'J_V_off{target}', round(J_off,3))

	return J_off

from good_morning.calibrations.ultility import get_target, readout_convertor
from good_morning.fittings.phase_oscillations import fit_phase

from core_tools.sweeps.pulse_lib_wrappers.PSB_exp import run_qubit_exp
from core_tools.utility.variable_mgr.var_mgr import variable_mgr
from core_tools.sweeps.sweeps import scan_generic, do0D, do1D
from core_tools.job_mgnt.job_mgmt import job_wrapper

from pulse_templates.coherent_control.single_qubit_gates.phase_offsets_charac import phase_offset_charac
from dev_V2.six_qubit_QC_v2.system import six_dot_sample

import qcodes as qc
import numpy as np

@job_wrapper
def phase_calib(target, *gates, plot=False):
	'''
	calibrates a single qubit phase for a target qubit

	Args:
		target (int) : qubit number to target (1-6)
		gates (str) : name of the gate to call (e.g, q2.X or q12.cphase ).
			The net result of this sequency shuold be identity
	'''
	s = six_dot_sample(qc.Station.default.pulse)
	var_mgr = variable_mgr()

	s.add(s.pre_pulse)

	s.init(target)
	s.add(s.wait(1000))

	gate_set = getattr(s, f'q{target}')

	target_gates = []
	for gate in gates:
		target_gates += [get_target(s,gate)]
	s.add_func(phase_offset_charac, gate_set, target_gates, npoints=50)

	s.add(s.wait(1000))

	s.read(target)

	gate = gates[0]
	sequence, minstr, name = run_qubit_exp(f'phase_cal_q{target}, target gate : {gate}', s.sequencer)
	ds = scan_generic(sequence, minstr, name=name).run()

	input_phases = ds(readout_convertor(f'read{target}')).x()
	amplitude = ds(readout_convertor(f'read{target}')).y()

	# get rid of the first part due to heating
	input_phases = input_phases[20:]
	amplitude = amplitude[20:]

	phase, std_error = fit_phase(input_phases, amplitude, plot=plot)
	phase = phase/len(target_gates)

	if not hasattr(var_mgr, f'PHASE_q{target}_{gate.replace(".", "_")}'):
		var_mgr.add_variable(f'Qubit {target}',f'PHASE_q{target}_{gate.replace(".", "_")}','rad',0.1,0)

	old_phase = getattr(var_mgr, f'PHASE_q{target}_{gate.replace(".", "_")}')	
	setattr(var_mgr, f'PHASE_q{target}_{gate.replace(".", "_")}', round(phase,3))

	print(f'calibrated phase for qubit {target}, '+
		f'for gate {gate}. \n Old phase : {round(old_phase,2)} \n New Phase : {round(phase,2)} [{round(std_error[0],2)} : {round(std_error[1],2)}]\n')

	return phase
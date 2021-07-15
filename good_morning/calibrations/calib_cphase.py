from good_morning.calibrations.ultility import get_target, readout_convertor
from good_morning.fittings.phase_oscillations import fit_phase as fit_phase_osc
from good_morning.fittings.shaped_cphase import fit_phase

from core_tools.sweeps.pulse_lib_wrappers.PSB_exp import run_qubit_exp
from core_tools.utility.variable_mgr.var_mgr import variable_mgr
from core_tools.job_mgnt.job_mgmt import job_wrapper
from core_tools.sweeps.sweeps import scan_generic

from dev_V2.six_qubit_QC_v2.system import six_dot_sample
import pulse_lib.segments.utility.looping as lp

import qcodes as qc
import numpy as np

@job_wrapper
def cphase_ZZ_calib(target, even=False, plot=False):
	'''
	Args:
		qubit_pair (str) : pair of qubits to calibrate cphase for.
	'''
	s = six_dot_sample(qc.Station.default.pulse)

	s.add(s.pre_pulse)

	target = str(int(target))
	s.init(target[0], target[1])

	sweep = lp.linspace(-0.2*np.pi,3*np.pi, 100, 'angle', 'rad', 0)

	s.add(s[f'q{target[0]}'].X90)
	s.add(s[f'q{target}'].cphase, cphase_angle=sweep, phase_corrections={})
	s.add(s[f'q{target[0]}'].X180)
	s.add(s[f'q{target[1]}'].X180)
	s.add(s[f'q{target}'].cphase, cphase_angle=sweep, phase_corrections={})
	s.add(s[f'q{target[0]}'].X90)

	s.add(s.wait(100))

	s.read(target[0], target[1])

	sequence, minstr, name = run_qubit_exp(f'cphase cal :: {target}', s.sequencer)
	ds = scan_generic(sequence, minstr, name=name).run()


	target_ds = target[0]
	input_phases = ds(readout_convertor(f'read{target_ds}')).x()
	amplitude = ds(readout_convertor(f'read{target_ds}')).y()

	# get rid of the first part due to heating
	input_phases = input_phases[10:]
	amplitude = amplitude[10:]

	J_time = fit_phase(input_phases, amplitude, even, plot=plot)
	print('phase =', J_time)
	var_mgr = variable_mgr()	
	if not hasattr(var_mgr,f'J_pi_{target}'):
		var_mgr.add_variable(f'CPhase{target}',f'J_pi_{target}','rad',0.1,0)

	old_phase = getattr(var_mgr,f'J_pi_{target}')
	setattr(var_mgr,f'J_pi_{target}', round(J_time,3))

@job_wrapper
def cphase_ZI_IZ_cal(pair, target, expected_outcome = 0, plot=False):
	'''
	calibrate single qubit phases.

	args:
		pair   : pair of qubit to calibrate
		target : qubit to target with the cnot
		expected_outcome : expected outcome when performing a CNOT on this qubit
	'''

	s = six_dot_sample(qc.Station.default.pulse)
	s.add(s.pre_pulse)

	pair = str(int(pair))
	s.init(pair[0], pair[1])

	s.add(s[f'q{target}'].X90, phase_corrections={})
	s.add(s[f'q{pair}'].cphase, phase_corrections={})
	s.add(s[f'q{target}'].X90, phase = lp.linspace(-np.pi,4*np.pi, 100, 'angle', 'rad', 0))

	s.add(s.wait(1000))

	s.read(pair[0], pair[1])

	sequence, minstr, name = run_qubit_exp(f'cphase single qubit phase cal :: q{target}', s.sequencer)
	ds = scan_generic(sequence, minstr, name=name).run()

	input_phases = ds(readout_convertor(f'read{target}')).x()
	amplitude = ds(readout_convertor(f'read{target}')).y()

	# get rid of the first part due to heating
	input_phases = input_phases[15:]
	amplitude = amplitude[15:]

	phase, std_error = fit_phase_osc(input_phases, amplitude, plot=plot)
	phase = -phase
	if expected_outcome == 0:
		phase += np.pi
	var_mgr = variable_mgr()

	if not hasattr(var_mgr, f'PHASE_q{target}_q{pair}_cphase'):
		var_mgr.add_variable(f'Qubit {target}',f'PHASE_q{target}_q{pair}_cphase','rad',0.1,0)

	old_phase = getattr(var_mgr, f'PHASE_q{target}_q{pair}_cphase')
	setattr(var_mgr, f'PHASE_q{target}_q{pair}_cphase', round(phase,3))

	print('setting ' + f'PHASE_q{target}_q{pair}_cphase to {phase}')

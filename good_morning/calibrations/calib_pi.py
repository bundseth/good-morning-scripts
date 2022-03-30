from good_morning.calibrations.ultility import get_target, readout_convertor
from good_morning.fittings.fit_rabi_osc import fit_ramsey

from core_tools.sweeps.pulse_lib_wrappers.PSB_exp import run_qubit_exp
from core_tools.sweeps.sweeps import scan_generic, do0D, do1D
from core_tools.utility.variable_mgr.var_mgr import variable_mgr
from core_tools.job_mgnt.job_mgmt import job_wrapper

from pulse_lib.segments.utility.looping import linspace
from dev_V2.six_qubit_QC_v2.system import six_dot_sample

import qcodes as qc
import numpy as np

@job_wrapper
def Pi_calib(target, plot=False):
	'''
	calibrates a single qubit phase for a target qubit

	Args:
		target (int) : qubit number to target (1-6)
		ancillary (list) : qubit that need to be initialized to make this work
	'''
	s = six_dot_sample(qc.Station.default.pulse)
	var_mgr = variable_mgr()

	s.init(target)
	s.add(s.pre_pulse)

	s.add(s.wait(10000))

	gate_set = getattr(s, f'q{target}')
	old_pi = getattr(var_mgr, f'pi_q{target}')
	s.add(gate_set.X180, t_pulse = linspace(1,old_pi*4, 60, 'time', 'ns', 0)/2)
	s.add(s.wait(50e3))
	s.read(target)

	sequence, minstr, name = run_qubit_exp(f'Pi_cal_q{target}', s.sequencer)
	ds = scan_generic(sequence, minstr, name=name).run()

	time = ds(readout_convertor(f'read{target}')).x()*1e-9
	probabilities = ds(readout_convertor(f'read{target}')).y()
	time = time[5:]
	probabilities = probabilities[5:]
	Pi_time = fit_ramsey(time, probabilities, plot=plot)
	var_mgr = variable_mgr()

	Pi_time = round(Pi_time/10)*10-2
	old_Pi = getattr(var_mgr, f'pi_q{target}')
	setattr(var_mgr, f'pi_q{target}', round(Pi_time,6))

	print(f'calibrated resonance for qubit {target}, '+
		f'Old resonance : {round(old_Pi,6)} \n New resonance : {round(Pi_time,6)} \n')

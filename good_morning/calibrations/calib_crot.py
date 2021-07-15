from good_morning.calibrations.ultility import get_target, readout_convertor
from good_morning.fittings.fit_resonance import fit_resonance
from good_morning.fittings.fit_rabi_osc import fit_ramsey

from core_tools.sweeps.pulse_lib_wrappers.PSB_exp import run_qubit_exp
from core_tools.utility.variable_mgr.var_mgr import variable_mgr
from core_tools.sweeps.sweeps import scan_generic, do0D, do1D
from core_tools.job_mgnt.job_mgmt import job_wrapper

from pulse_templates.coherent_control.single_qubit_gates.single_qubit_gates import single_qubit_gate_spec
from pulse_lib.segments.utility.looping import linspace

from dev_V2.six_qubit_QC_v2.system import six_dot_sample
from pulse_templates.utility.plotting import plot_seg

import qcodes as qc
import numpy as np

import good_morning.static.J12 as J12
import good_morning.static.J23 as J23
import good_morning.static.J34 as J34
import good_morning.static.J45 as J45
import good_morning.static.J56 as J56


def CROT_cali_meas(pair, target, ancilla, old_freq, time, flip):
	s = six_dot_sample(qc.Station.default.pulse)
	s.add(s.pre_pulse)

	var_mgr = variable_mgr()

	pair = str(int(pair))
	s.init(pair[0], pair[1])

	s.add(s.wait(100))

	gate_set = getattr(s, f'q{pair}')
	target_gate_set = getattr(s, f'q{pair[target-1]}')
	ancilla_gate_set = getattr(s, f'q{pair[ancilla-1]}')

	if flip:
		s.add(ancilla_gate_set.X180)

	scan_range = single_qubit_gate_spec(f'qubit{target}_MW', 
                                    linspace(old_freq*1e9-30e6, old_freq*1e9+30e6,50, axis= 0, name='freq', unit='Hz'),
                                    time, getattr(var_mgr, f'CROT{pair}_MW_power'), padding=20)

	s.add(getattr(gate_set, f'CROT{target}{ancilla}') , gate_spec = scan_range)

	s.add(s.wait(100))
	s.read(pair[target-1])

	sequence, minstr, name = run_qubit_exp(f'crot-z_crot_cal_q{pair}_target{pair[target-1]}', s.sequencer)

	return sequence, minstr, name

@job_wrapper
def CROT_calib(pair, target, ancilla, plot=False):
	'''
	calibrates a single qubit phase for a target qubit

	Args:
		target (int) : qubit number to target (1-6)
		ancillary (list) : qubit that need to be initialized to make this work
	'''
	var_mgr = variable_mgr()
	pair = str(int(pair))

	old_crot = getattr(var_mgr, f'crot{pair[target-1]}{pair[ancilla-1]}')
	old_z_crot = getattr(var_mgr, f'z_crot{pair[target-1]}{pair[ancilla-1]}')
	crot_time = getattr(var_mgr, f'pi_crot{pair[target-1]}')
	z_crot_time = getattr(var_mgr, f'pi_z_crot{pair[target-1]}')

	gate_time= min(crot_time,z_crot_time)	

	sequence, minstr, name = CROT_cali_meas(pair, target, ancilla, old_crot, gate_time, 1)
	ds_one = scan_generic(sequence, minstr, name=name).run()
	sequence, minstr, name = CROT_cali_meas(pair, target, ancilla, old_z_crot, gate_time, 0)
	ds_two = scan_generic(sequence, minstr, name=name).run()

	frequency_one = ds_one(readout_convertor(f'read{pair[target-1]}')).x()
	probabilities_one = ds_one(readout_convertor(f'read{pair[target-1]}')).y()
	fit_freq_one = fit_resonance(frequency_one[5:], probabilities_one[5:], plot=plot)
	
	frequency_two = ds_two(readout_convertor(f'read{pair[target-1]}')).x()
	probabilities_two = ds_two(readout_convertor(f'read{pair[target-1]}')).y()
	fit_freq_two = fit_resonance(frequency_two[5:], probabilities_two[5:], plot=plot)

	z_crot_res = min(fit_freq_one, fit_freq_two)
	crot_res = max(fit_freq_one, fit_freq_two)

	old_z_crot = getattr(var_mgr, f'z_crot{pair[target-1]}{pair[ancilla-1]}')
	setattr(var_mgr, f'z_crot{pair[target-1]}{pair[ancilla-1]}', round(z_crot_res*1e-9,6))
	old_crot = getattr(var_mgr, f'crot{pair[target-1]}{pair[ancilla-1]}')
	setattr(var_mgr, f'crot{pair[target-1]}{pair[ancilla-1]}', round(crot_res*1e-9,6))
	print(f'calibrated z_crot_res for qubit pair {pair}, target {pair[target-1]} '+
		f'Old z_crot_res : {round(old_z_crot,6)} \n New z_crot_res : {round(z_crot_res*1e-9,6)} \n')
	print(f'calibrated crot_res for qubit pair {pair}, target {pair[target-1]} '+
		f'Old crot_res : {round(old_crot,6)} \n New z_crot_res : {round(crot_res*1e-9,6)} \n')



def crot_calib_seq(target, CROT_target_gate, gate_spec, additional_instruction=None):
	s = six_dot_sample(qc.Station.default.pulse)

	s.add(s.pre_pulse)

	s.init(target[0], target[1])
	s.add(s.wait(100))

	if additional_instruction is not None:
		s.add(get_target(s, additional_instruction))

	s.add(s.wait(500))
	s.add(get_target(s, CROT_target_gate), gate_spec = gate_spec)

	s.add(s.wait(100))
	s.read(target[0], target[1])

	sequence, minstr, name = run_qubit_exp(f'crot_{CROT_target_gate}_calibration', s.sequencer)
	return scan_generic(sequence, minstr, name=name).run()

@job_wrapper
def crot_calib_freq(pair):
	'''
	calibrate CROT frequencies
	'''
	# generate variables if they don't exist.
	var_mgr = variable_mgr()
	pair = str(int(pair))

	if not hasattr(var_mgr, f'CROT{pair}_J_target'):
		var_mgr.add_variable(f'CROT{pair}', f'CROT{pair}_J_target','MHz',0.1,5)

	for i in ['12', '12_z', '21', '21_z']:

		target = pair[0] if '12' in i else pair[1]
		not_target = pair[1] if '12' in i else pair[0]
		
		if not hasattr(var_mgr, f'CROT{pair}_{i}_MW_power'):
			power = getattr(var_mgr, f'q{target}_MW_power')
			var_mgr.add_variable(f'CROT{pair}',f'CROT{pair}_{i}_MW_power','mV',0.1,power)
		if not hasattr(var_mgr, f'CROT{pair}_{i}_freq'):
			freq = getattr(var_mgr, f'frequency_q{target}') 
			var_mgr.add_variable(f'CROT{pair}',f'CROT{pair}_{i}_freq','GHz',0.1,freq)
		if not hasattr(var_mgr, f'CROT{pair}_{i}_pi_time'):
			time = getattr(var_mgr, f'pi_q{target}')
			var_mgr.add_variable(f'CROT{pair}', f'CROT{pair}_{i}_pi_time','ns',0.1,time)

		additional_instr = None
		if 'z' in i:
			additional_instr = f'q{not_target}.X180'

		old_freq = getattr(var_mgr, f'CROT{pair}_{i}_freq')
		gate_spec = single_qubit_gate_spec(f'qubit{target}_MW', linspace(old_freq*1e9-10e6, old_freq*1e9+10e6, 75, axis= 0, name='freq', unit='Hz'),
                                        getattr(var_mgr, f'CROT{pair}_{i}_pi_time'), getattr(var_mgr, f'CROT{pair}_{i}_MW_power'), padding=10)

		ds = crot_calib_seq(pair, f'q{pair}.CROT_{i}', gate_spec, additional_instr)

		frequency = ds(readout_convertor(f'read{target}')).x()
		probabilities = ds(readout_convertor(f'read{target}')).y()
		freq = fit_resonance(frequency[5:], probabilities[5:], plot=True)

		setattr(var_mgr, f'CROT{pair}_{i}_freq', round(freq*1e-9,4))

		print(f'Updating frequency for CROT{pair} from \n\t{old_freq} GHz to \n\t{round(freq*1e-9,4)} GHz')

@job_wrapper
def crot_calib_time(pair):
	'''
	calibrate CROT frequencies
	'''
	# generate variables if they don't exist.
	var_mgr = variable_mgr()
	pair = str(int(pair))

	for i in ['12', '12_z', '21', '21_z']:

		target = pair[0] if '12' in i else pair[1]
		not_target = pair[1] if '12' in i else pair[0]

		additional_instr = None
		if 'z' in i:
			additional_instr = f'q{not_target}.X180'

		old_time = getattr(var_mgr, f'CROT{pair}_{i}_pi_time')
		gate_spec = single_qubit_gate_spec(f'qubit{target}_MW', getattr(var_mgr, f'CROT{pair}_{i}_freq')*1e9,
                                linspace(0,old_time*4, 50, axis= 0, name='time', unit='ns'), getattr(var_mgr, f'CROT{pair}_{i}_MW_power'), padding=10)

		ds = crot_calib_seq(pair, f'q{pair}.CROT_{i}', gate_spec, additional_instr)

		time = ds(readout_convertor(f'read{target}')).x()
		probabilities = ds(readout_convertor(f'read{target}')).y()
		pi_time = fit_ramsey(time[5:]*1e-9, probabilities[5:], plot=True)

		setattr(var_mgr, f'CROT{pair}_{i}_pi_time', round(pi_time))

		print(f'Updating time for CROT{pair} from \n\t{old_time} ns to \n\t{round(pi_time)} ns')
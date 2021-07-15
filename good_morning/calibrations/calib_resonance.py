from good_morning.calibrations.ultility import get_target, readout_convertor
from good_morning.fittings.fit_resonance import fit_resonance

from core_tools.sweeps.pulse_lib_wrappers.PSB_exp import run_qubit_exp
from core_tools.utility.variable_mgr.var_mgr import variable_mgr
from core_tools.job_mgnt.job_mgmt import job_wrapper
from core_tools.sweeps.sweeps import scan_generic

from dev_V2.six_qubit_QC_v2.system import six_dot_sample
from pulse_lib.segments.utility.looping import linspace

import qcodes as qc
import numpy as np


from lmfit import Parameters, minimize
from lmfit.printfuncs import report_fit

import numpy as np
import matplotlib.pyplot as plt

def get_freq_estimate(x,y):
	return x[np.argmax(y)]

def get_vis_and_offset(x,y):
	vis = np.max(y)-np.min(y)
	off = (np.max(y)+np.min(y))/2
	return vis, off

def f_res_residual(pars, x, data=None):
	f_res =pars['f_res']
	sigma =pars['rabi_freq']
	angle =pars['angle']
	vis = pars['vis']
	off = pars['off']

	sigma_bar = np.sqrt(sigma**2 + (x-f_res)**2)
	model = (sigma**2)/(sigma_bar**2)*(0.5-0.5*np.cos(0.5*sigma_bar*angle)) * vis + off
	if data is None:
		return model

	return model-data

def fit_f_res(x,y):
	fit_params = Parameters()
    
	x = x*1e-9
	freq = get_freq_estimate(x, y)
	vis, off = get_vis_and_offset(x, y)

	fit_params.add('f_res', value=freq, min=0)
	fit_params.add('rabi_freq', value=4e6*1e-9)
	fit_params.add('angle', value=np.pi)
	fit_params.add('off', value=off)
	fit_params.add('vis', value=vis, max = 1)

	out = minimize(f_res_residual, fit_params, args=(x,), kws={'data': y})
	fit = f_res_residual(out.params, x)
	print(out.params)

	return fit


@job_wrapper
def res_calib(target, plot=False):
	'''
	calibrates a single qubit phase for a target qubit

	Args:
		target (int) : qubit number to target (1-6)
		ancillary (list) : qubit that need to be initialized to make this work
	'''
	s = six_dot_sample(qc.Station.default.pulse)
	var_mgr = variable_mgr()


	if not hasattr(var_mgr, f'frequency_q{target}'):
		var_mgr.add_variable(f'Qubit {target}', f'frequency_q{target}', 'GHz',11.000, 0.1)
		var_mgr.add_variable(f'Qubit {target}', f'pi_q{target}', 'ns',200, 1)
		var_mgr.add_variable(f'Qubit {target}', f'q{target}_MW_power', 'mV',600, 1)

	s.add(s.pre_pulse)
	s.add(s.wait(100))	
	s.init(target)
	# s.init(target)

	s.add(s.wait(1000))

	gate_set = getattr(s, f'q{target}')
	old_freq = getattr(var_mgr, f'frequency_q{target}')
	s.add(gate_set.X180, f_qubit = linspace(old_freq*1e9-20e6, old_freq*1e9+20e6, 50, axis= 0, name='freq', unit='Hz'))
	s.add(s.wait(1000))
	s.read(target)

	sequence, minstr, name = run_qubit_exp(f'frequency_cal_q{target}', s.sequencer)
	ds = scan_generic(sequence, minstr, name=name).run()

	frequency = ds(readout_convertor(f'read{target}')).x()
	probabilities = ds(readout_convertor(f'read{target}')).y()
	resonance = fit_resonance(frequency, probabilities, plot=plot)
	var_mgr = variable_mgr()

	old_res = getattr(var_mgr, f'frequency_q{target}')
	setattr(var_mgr, f'frequency_q{target}', round(resonance*1e-9,6))

	print(f'calibrated resonance for qubit {target}, '+
		f'Old resonance : {round(old_res,6)} \n New resonance : {round(resonance*1e-9,6)} \n')

if __name__ == '__main__':
	main()
import matplotlib.pyplot as plt
import numpy as np

import lmfit


def res_function(pars, x, data=None):
	amp = pars['amp']
	offset = pars['offset']
	phase = pars['phase']

	model = 0.5*np.cos(x + phase)*amp + offset

	if data is None:
		return model
	return model-data

def fit_phase(phases,amplitudes, plot=False):
	'''
	fit phases:
	Args:
		phases (np.ndarray) : array of phase (note that only one full period is expected)
		amplitudes (np.ndarray) : array with amplitude for the phase
	Returns 
		phase (double) : measured phase on the fitting
		ci (tuple) : 95% confidence interval
	'''
	fit_result, confidence_interval = fit_phase_raw(phases, amplitudes)

	if plot==True:
		plt.figure()
		plt.plot(phases, amplitudes, label='original data')
		plt.plot(phases, res_function(fit_result.params, phases), label='fitted data')
		plt.xlabel('phase (rad)')
		plt.ylabel(('spin probability (%)'))
		plt.legend()
		plt.show()

	min_value = confidence_interval['phase'][2][1]-confidence_interval['phase'][3][1]
	max_value = confidence_interval['phase'][5][1]-confidence_interval['phase'][3][1]

	phase = np.angle(np.exp(1j*fit_result.params['phase'].value))
	if phase < 0 : 
		phase += 2*np.pi

	return phase, (min_value, max_value)

def fit_phase_raw(phases,amplitudes):
	'''
	fit phases:
	Args:
		phases (np.ndarray) : array of phase
		amplitudes (np.ndarray) : array with amplitude for the phase
	'''
	# estimators for fit
	min_val = np.min(amplitudes)
	max_val = np.max(amplitudes)
	phase_est = np.average(np.angle(amplitudes + 1j*np.roll(amplitudes, int(len(amplitudes/4)))))-np.pi/2

	fit_params = lmfit.Parameters()
	fit_params.add('amp', value=max_val-min_val, min = 0.1, max=1.1)
	fit_params.add('offset', value=(max_val+ min_val)/2, min=0, max=1)
	fit_params.add('phase', value=phase_est, min=-2*np.pi, max=2*np.pi)


	mini = lmfit.Minimizer(res_function, fit_params, fcn_args=(phases,), fcn_kws={'data': amplitudes})
	intermedediate_result = mini.minimize(method='Nelder')
	result = mini.minimize(method='leastsq', params=intermedediate_result.params)

	confidence_intervals = lmfit.conf_interval(mini, result, verbose=False)

	return result, confidence_intervals


def test():
	phase = -0.1
	x = np.linspace(0,np.pi*2)
	y = np.cos(x + phase)/2 + 0.5 + np.random.random(x.shape)*0.1


	print(phase)
	phase, ci = fit_phase(x, y, True)
	print(phase)
	print(ci)
if __name__ == '__main__':
	from core_tools.data.SQL.connect import set_up_local_storage
	set_up_local_storage("xld_user", "XLDspin001", "vandersypen_data", "6dot", "XLD", "6D2S - SQ21-XX-X-XX-X")

	from core_tools.data.ds.data_set import load_by_id
	ds = load_by_id(20916)
	data = ds('read56')

	x = data.x()[15:]
	y = data.y()[15:]

	p, ci = fit_phase(x, y, False)
	print(p-2*np.pi)
import matplotlib.pyplot as plt
import numpy as np

import lmfit


def res_function(pars, x, data=None):
	amp = pars['amp']
	offset = pars['offset']
	phase = pars['phase']
	freq_offset = pars['freq_offset']

	model = 0.5*np.cos(freq_offset*(x - phase))*amp + offset

	if data is None:
		return model
	return np.nan_to_num(model-data)

def fit_phase_raw(phases,amplitudes, even):
	'''
	fit phases:
	Args:
		phases (np.ndarray) : array of phase
		amplitudes (np.ndarray) : array with amplitude for the phase
	'''
	# estimators for fit
	min_val = np.min(np.nan_to_num(amplitudes))
	max_val = np.max(np.nan_to_num(amplitudes))
	
	phase_est = np.pi
	if even == True : 
		phase_est = 0

	fit_params = lmfit.Parameters()
	fit_params.add('amp', value=max_val-min_val, min = 0.1, max=1.1)
	fit_params.add('offset', value=(max_val+ min_val)/2, min=0, max=1)
	fit_params.add('phase', value=phase_est, min=-2*np.pi, max=2*np.pi)
	fit_params.add('freq_offset', value=1.0, min=0.5, max=2)

	mini = lmfit.Minimizer(res_function, fit_params, fcn_args=(phases,), fcn_kws={'data': amplitudes})
	intermedediate_result = mini.minimize(method='Nelder')
	result = mini.minimize(method='leastsq', params=intermedediate_result.params)

	confidence_intervals = lmfit.conf_interval(mini, result, verbose=False)

	return result, confidence_intervals

def fit_phase(phases,amplitudes, even=True, plot=False):
	'''
	fit phases:
	Args:
		phases (np.ndarray) : array of phase (note that only one full period is expected)
		amplitudes (np.ndarray) : array with amplitude for the phase
	Returns 
		phase (double) : measured phase on the fitting
		ci (tuple) : 95% confidence interval
	'''
	if not even : 
		amplitudes = -1*amplitudes + 1

	fit_result, confidence_interval = fit_phase_raw(phases, amplitudes, even)

	phase = fit_result.params['phase'].value
	freq = fit_result.params['freq_offset'].value


	pt = (2*np.pi)/freq/2
	idx = np.where((phases > pt-2) & (phases < pt + 2))[0]
	detailed_fit  =  np.poly1d(np.polyfit(phases[idx], np.nan_to_num(amplitudes[idx]), 7))

	pi_time = phases[idx][np.argmax(detailed_fit(phases[idx]))]

	if plot==True:
		plt.figure()
		plt.plot(phases, amplitudes, '-', label='original data')
		plt.plot(phases, res_function(fit_result.params, phases), label='fitted data')
		plt.plot(phases[idx], detailed_fit(phases[idx]))
		plt.xlabel('phase (rad)')
		plt.ylabel(('spin probability (%)'))
		plt.legend()
		plt.show()


	return pi_time


def test():
	phase = -0.1
	x = np.linspace(0,np.pi*2)
	y = np.cos(x + phase)/2 + 0.5 + np.random.random(x.shape)*0.1


	print(phase)
	phase, ci = fit_phase(x, y, True)
	print(phase)
	print(ci)
if __name__ == '__main__':
    from core_tools.data.SQL.connect import SQL_conn_info_local, set_up_remote_storage, sample_info, set_up_local_storage
    from core_tools.data.ds.data_set import load_by_id

    # set_up_remote_storage('131.180.205.81', 5432, 'xld_measurement_pc', 'XLDspin001', 'spin_data', "6dot", "XLD", "6D3S - SQ20-20-5-18-4")
    set_up_local_storage("xld_user", "XLDspin001", "vandersypen_data", "6dot", "XLD", "6D2S - SQ21-XX-X-XX-X")

    # ds = load_by_id(16949)
    # data = ds('read5')
    # fit_phase(data.x(), data.y(), False, True)

    # ds = load_by_id(16947)
    # data = ds('read1')
    # fit_phase(data.x(), data.y(), False, True)

    # ds = load_by_id(16948)
    # data = ds('read2')
    # fit_phase(data.x(), data.y(), True, True)

    # ds = load_by_id(16950)
    # data = ds('read4')
    # fit_phase(data.x(), data.y(), True, True)

    # ds = load_by_id(16949)
    # data = ds('read5')
    # fit_phase(data.x(), data.y(), False, True)

    # ds = load_by_id(17046)
    # data = ds('read4')
    # fit_phase(data.x(), data.y(), True, True)

    ds = load_by_id(20622)
    data = ds('read5')
    a = fit_phase(data.x(), data.y(), True, True)
    print(a)


    # plt.show()
import matplotlib.pyplot as plt
import numpy as np

import lmfit


def res_function(pars, x, data=None):
	amp = pars['amp'].value
	offset = pars['offset'].value
	freq = pars['freq'].value
	phase = pars['phase'].value
	T2 = pars['T2'].value

	model = 0.5*np.sin(x*2*np.pi*freq + phase)*amp*np.exp(-(x/T2)**2) + offset

	if data is None:
		return model
		
	return np.nan_to_num(model-data)

def get_freq_and_phase_estimate(time, amp):
	data = np.zeros([amp.size*10])
	data[:amp.size] = amp - np.average(amp)

	freq = np.fft.fftfreq(data.shape[-1], d=time[1]-time[0])
	amp = np.fft.fft(data)

	idx = np.argmax(np.abs(amp))
	rabi_freq = freq[idx]
	phase = np.angle(amp[idx])
	return rabi_freq, phase

def fit_ramsey_raw(time,amplitudes):
	'''
	fit ramsey::
	Args:
		time (np.ndarray) : time..
		amplitudes (np.ndarray) : array with amplitude
	'''
	# estimators for fit
	min_val = np.min(np.nan_to_num(amplitudes))
	max_val = np.max(np.nan_to_num(amplitudes))
	freq_est, phase_est = get_freq_and_phase_estimate(time, np.nan_to_num(amplitudes))  
	fit_params = lmfit.Parameters()
	fit_params.add('amp', value=max_val-min_val, min = 0, max=1)
	fit_params.add('offset', value=(max_val+ min_val)/2, min=0, max=1)
	fit_params.add('phase', value=phase_est, min=-2*np.pi, max=2*np.pi)
	fit_params.add('freq', value=abs(freq_est), min=10e3, max=50e6)
	fit_params.add('T2', value=5e-6, min=0)


	mini = lmfit.Minimizer(res_function, fit_params, fcn_args=(time,), fcn_kws={'data': amplitudes})
	intermedediate_result = mini.minimize(method='Nelder')
	result = mini.minimize(method='leastsq', params=intermedediate_result.params)

	confidence_intervals = None# lmfit.conf_interval(mini, result, verbose=False)
	
	return result, confidence_intervals

def fit_ramsey(time,amplitudes, plot=False):
	'''
	fit ramsey:
	Args:
		time (np.ndarray) : time
		amplitudes (np.ndarray) : spin prob
	'''
	fit_result, confidence_interval = fit_ramsey_raw(time, amplitudes)

	print(f'rabi freq = {round(fit_result.params["freq"].value*1e-6, 4)} MHz')
	if plot==True:
		plt.figure()
		plt.plot(time, amplitudes, label='original data')
		plt.plot(time, res_function(fit_result.params, time), label='fitted data')
		plt.xlabel('time (ns)')
		plt.ylabel(('spin probability (%)'))
		plt.legend()
		plt.show()
	# min_value = confidence_interval['phase'][2][1]-confidence_interval['phase'][3][1]
	# max_value = confidence_interval['phase'][5][1]-confidence_interval['phase'][3][1]
	return 1/fit_result.params['freq'].value/2*1e9


def test():
	rabi_freq = 10e6
	phase = 0.5
	T2 = 500e-9
	
	t = np.linspace(0,500e-9, 500)
	amp = 0.5*np.cos(2*np.pi*rabi_freq*t + phase)*np.exp(-(t/0.5e-6)**2) + 0.5+ np.random.random(t.shape)*0.1
	
	fit_ramsey(t, amp, plot=True)

if __name__ == '__main__':
	from core_tools.data.SQL.connect import set_up_local_storage
	set_up_local_storage("xld_user", "XLDspin001", "vandersypen_data", "6dot", "XLD", "6D2S - SQ21-XX-X-XX-X")

	from core_tools.data.ds.data_set import load_by_uuid
	ds = load_by_uuid(1630329900257898284)
	data = ds('read5')
	# print(data)
	# x = data.y()[5:]*1e-9
	# y = data.z()[4][5:]

	x = data.x()*1e-9
	y = data.y()
	f = fit_ramsey(x, y, True)
	print(2/f)
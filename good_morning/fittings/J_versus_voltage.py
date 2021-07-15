import matplotlib.pyplot as plt
import numpy as np

import lmfit

def J_to_voltage(J, J_off, J_max, alpha):
	J = np.asarray(J) + 1
	voltages = (np.log(J/J_max) -J_off)/alpha/2

	if isinstance(J, np.ndarray):
		voltages[voltages < 0] = 0
	return voltages
	
def voltage_to_J(voltage, J_off, J_max, alpha):
	return J_max*np.exp(2*alpha*(voltage+ J_off))

def res_function(pars, x, data=None):
	J_off = pars['J_off']
	J_max = pars['J_max']
	alpha = pars['alpha']

	model = voltage_to_J(x, J_off, J_max, alpha)

	if data is None:
		return model

	return model-data

def fit_J_raw(barrier_voltages,J_array):
	'''
	fit phases:
	Args:
		barrier_voltages (np.ndarray) : value of the barrier (normalzied to 1)
		J_array (np.ndarray) : array with amplitude of J vor the barrier_voltages
	'''
	# estimators for fit
	J_off = 0
	J_max = J_array[-1]/2.7
	alpha = 1/barrier_voltages[-1]/2

	fit_params = lmfit.Parameters()
	fit_params.add('J_off', value=J_off)
	fit_params.add('J_max', value=J_max)
	fit_params.add('alpha', value=alpha)


	mini = lmfit.Minimizer(res_function, fit_params, fcn_args=(barrier_voltages,), fcn_kws={'data': J_array})
	intermedediate_result = mini.minimize(method='Nelder')
	result = mini.minimize(method='leastsq', params=intermedediate_result.params)

	confidence_intervals = lmfit.conf_interval(mini, result, verbose=False)
	
	return result, confidence_intervals


def fit_J(barrier_voltages,J_array, plot=False):
	fit_result, confidence_interval = fit_J_raw(barrier_voltages, J_array)

	if plot==True:
		plt.figure()

		plt.plot(barrier_voltages, J_array/1e6,'ro', label='original data')
		plt.plot(barrier_voltages, res_function(fit_result.params, barrier_voltages)/1e6, label='fitted data')
		
		plt.xlabel('Barrier gate (%)')
		plt.ylabel('J (MHz)')
		plt.legend()
		plt.show()

	return fit_result.params['J_off'].value ,fit_result.params['J_max'].value , fit_result.params['alpha'].value 


def fit_delta_B_vs_J_raw(J, delta_B):
	return np.poly1d(np.polyfit(J, delta_B, 5))

def fit_delta_B_vs_J(J, delta_B, plot=False):
	J = np.asarray(J)
	delta_B = np.asarray(delta_B)
	fit_func = fit_delta_B_vs_J_raw(J, delta_B)

	if plot==True:
		plt.figure()

		plt.plot(J/1e6, delta_B/1e6,'ro', label='original data')
		plt.plot(J/1e6, fit_func(J)/1e6, label='fitted data')
		
		plt.xlabel('J (MHz)')
		plt.ylabel('delta_B (MHz)')
		plt.legend()
		plt.show()

	return fit_func
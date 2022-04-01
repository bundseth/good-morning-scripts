import matplotlib.pyplot as plt
import numpy as np

from lmfit import Parameters, minimize
import lmfit

def gauss_peak_function(pars, x, data=None):
	amp = pars['amp'].value
	off = pars['off'].value
	f_res = pars['f_res'].value
	linewidth = pars['linewidth'].value

	model = off + amp*np.exp(-((x-f_res)**2)/(2*linewidth**2))

	if data is None:
		return model
	return np.nan_to_num(model-data)   

def fit_resonance_raw(frequency,probability, linewidth):
	fit_params = lmfit.Parameters()

	prob_real = np.nan_to_num(probability)
	fit_params.add('amp', value=2*round(((np.max(prob_real)+np.min(prob_real))/2-np.mean(prob_real)),1), max=1, min=-1)
	fit_params.add('off', value=np.average(prob_real), max=1.0, min=0.0)
	if (np.max(prob_real)+np.min(prob_real))/2-np.average(prob_real)>0:
		fit_params.add('f_res', value=frequency[np.argmax(prob_real)], vary = False)
	else:
		fit_params.add('f_res', value=frequency[np.argmax(prob_real)], vary = False)

	fit_params.add('linewidth', value=linewidth)

	mini = lmfit.Minimizer(gauss_peak_function, fit_params, fcn_args=(frequency,), fcn_kws={'data': probability}, max_nfev=5000)
	intermedediate_result = mini.minimize(method='Nelder', max_nfev=5000)
	intermedediate_result.params['f_res'].vary = True
	result = mini.minimize(method='leastsq', params=intermedediate_result.params)

	confidence_intervals = None# lmfit.conf_interval(mini, result, verbose=False)
	
	return result, confidence_intervals

def fit_resonance(frequency,probability, rabi_freq=5e6, angle=np.pi,linewidth = 1e6, plot=False, method = 'exact', optimize_angle=True):
	'''
	fit resonance:
	Args:
		frequency (np.ndarray) : GHz
		probability (np.ndarray) : spin prob
	'''
	if method == 'gaussian': 
		fit_result, confidence_interval = fit_resonance_raw(frequency, probability, linewidth)
	elif method == 'exact':
		fit_result, _ = fit_f_res(frequency, probability, rabi_freq, angle, optimize_angle)
	else:
		raise ValueError('invalid method')

	if plot==True:
		plt.figure()
		
		if method == 'gaussian':
			plt.plot(frequency, probability, label='original data')
			plt.plot(frequency, gauss_peak_function(fit_result.params, frequency), label='fitted data')
		else:
			plt.plot(frequency, probability, label='original data')
			plt.plot(frequency,  f_res_residual(fit_result.params, frequency), label='fitted data')
		plt.xlabel('frequency (GHz)')
		plt.ylabel(('spin probability (%)'))
		plt.legend()
		plt.show()


	return fit_result.params['f_res'].value

def get_freq_estimate(x,y):
	return x[np.argmax(y)]

def get_vis_and_offset(x,y):
	vis = np.max(y)-np.min(y)
	off = (np.max(y)+np.min(y))/2
	return vis, off

def f_res_residual(pars, x, data=None):
	f_res =pars['f_res']
	sigma =pars['rabi_freq']
	angle =2/sigma*pars['angle']
	vis = pars['vis']
	off = pars['off']

	sigma_bar = np.sqrt(sigma**2 + (x-f_res)**2)
	model = (sigma**2)/(sigma_bar**2)*(0.5-0.5*np.cos(0.5*sigma_bar*angle)) * vis + off -.5
	if data is None:
		return model

	return np.nan_to_num(model-data)

def fit_f_res(x,y, rabi_freq = 5e6, rotation_angle=np.pi, optimize_angle=True):
	fit_params = Parameters()
    
	x = x
	freq = get_freq_estimate(x, np.nan_to_num(y))
	vis, off = get_vis_and_offset(x, np.nan_to_num(y))

	fit_params.add('f_res', value=freq, min=False)
	fit_params.add('rabi_freq', value=rabi_freq, min=0)
	fit_params.add('angle', value=rotation_angle, vary=True)
	fit_params.add('off', value=off, min=0, max=1)
	fit_params.add('vis', value=vis, min=0, max = 1)

	mini = lmfit.Minimizer(f_res_residual, fit_params, fcn_args=(x,), fcn_kws={'data': y}, max_nfev=5000)
	intermedediate_result = mini.minimize(method='Nelder', max_nfev=5000)
	intermedediate_result.params['f_res'].vary = True
	out = mini.minimize(method='leastsq', params=intermedediate_result.params)

	return out, None

if __name__ == '__main__':
	from core_tools.data.SQL.connect import set_up_local_storage
	set_up_local_storage("xld_user", "XLDspin001", "vandersypen_data", "6dot", "XLD", "6D2S - SQ21-XX-X-XX-X")

	from core_tools.data.ds.data_set import load_by_uuid
	ds = load_by_uuid(1630656904060898284)
	data = ds('read1')
	print(data)
	x = data.x()
	y = data.y()

	fit_resonance(x, y, rabi_freq=4.5e6, angle=np.pi,plot=True, optimize_angle=False)

	# ds = load_by_uuid(1626428250013898284)
	# data = ds('read56')
	# x = data.x()
	# y = data.y()
	# res = fit_resonance(x, y, plot=True, linewidth=10, method='gaussian')
	# print(res)
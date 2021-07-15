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
	return (model - data)    

def fit_resonance_raw(frequency,probability, linewidth):
	fit_params = lmfit.Parameters()

	fit_params.add('amp', value=2*round(((np.max(probability)+np.min(probability))/2-np.mean(probability)),1), max=1, min=-1)
	fit_params.add('off', value=np.average(probability), max=1.0, min=0.0)
	if (np.max(probability)+np.min(probability))/2-np.average(probability)>0:
		fit_params.add('f_res', value=frequency[np.argmax(probability)], vary = False)
	else:
		fit_params.add('f_res', value=frequency[np.argmin(probability)], vary = False)

	fit_params.add('linewidth', value=linewidth)

	mini = lmfit.Minimizer(gauss_peak_function, fit_params, fcn_args=(frequency,), fcn_kws={'data': probability}, max_nfev=5000)
	intermedediate_result = mini.minimize(method='Nelder', max_nfev=5000)
	intermedediate_result.params['f_res'].vary = True
	result = mini.minimize(method='leastsq', params=intermedediate_result.params)

	confidence_intervals = None# lmfit.conf_interval(mini, result, verbose=False)
	
	return result, confidence_intervals

def fit_resonance(frequency,probability, linewidth = 1e6, plot=False, method = 'exact'):
	'''
	fit resonance:
	Args:
		frequency (np.ndarray) : GHz
		probability (np.ndarray) : spin prob
	'''
	if method == 'gaussian': 
		fit_result, confidence_interval = fit_resonance_raw(frequency, probability, linewidth)
	elif method == 'exact':
		fit_result, _ = fit_f_res(frequency, probability)
	else:
		raise ValueError('invalid method')

	print(f'res freq = {round(fit_result.params["f_res"].value*1e-9, 6)} GHz')
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
    
	x = x
	freq = get_freq_estimate(x, y)
	vis, off = get_vis_and_offset(x, y)

	fit_params.add('f_res', value=freq, min=0)
	fit_params.add('rabi_freq', value=5e6)
	fit_params.add('angle', value=1/5e6*np.pi)
	fit_params.add('off', value=off)
	fit_params.add('vis', value=vis, max = 1)

	out = minimize(f_res_residual, fit_params, args=(x,), kws={'data': y})

	return out, None

if __name__ == '__main__':
	from core_tools.data.SQL.connect import set_up_local_storage
	set_up_local_storage("xld_user", "XLDspin001", "vandersypen_data", "6dot", "XLD", "6D2S - SQ21-XX-X-XX-X")

	from core_tools.data.ds.data_set import load_by_uuid
	ds = load_by_uuid(1626248432577898284)
	data = ds('read1')
	print(data)
	x = data.x()
	y = data.y()

	fit_resonance(x, y, plot=True)
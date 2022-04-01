import matplotlib.pyplot as plt
import numpy as np
from skimage import measure
import scipy as sp
from lmfit import Parameters, minimize
import pulse_lib.segments.utility.looping as lp

def linear_fit(pars, x, data=None):
    a = pars['a'].value
    b = pars['b'].value

    model = b + a*x
    if data is None:
        return model

    return (model - data)

def fit_symmetry(x,y,probability, plot=False):
	data_on = sp.ndimage.filters.gaussian_filter(probability, [1,1], mode='constant')
	contours = measure.find_contours(data_on[3:-3,3:-3], 0.4)  
	Biggest = contours[np.argmax(contour.size for contour in contours)]
	y_mean=abs(Biggest[1][0]+Biggest[-1][0])/2
	x_mean=abs(Biggest[1][1]+Biggest[-1][1])/2
	y_max=Biggest.flatten('F')[:int(Biggest.flatten('F').size/2)].max()
	x_max=Biggest.flatten('F')[int(Biggest.flatten('F').size/2)+1:].max()

	fit_params = Parameters()
	fit_params.add('a', value=1)
	fit_params.add('b', value=0)
	out = minimize(linear_fit, fit_params, args=(np.array([x_mean,x_max]),), kws={'data': np.array([y_mean,y_max])})
	fit = linear_fit(out.params, len(x)/2)
	print(y[int(len(x)/2)])
	print(x[int(fit)]) 
	if plot:
		fig, ax = plt.subplots()
		ax.imshow(data_on, cmap=plt.cm.gray)
		# for contour in contours:
		#     ax.plot(contour[:, 1], contour[:, 0], linewidth=2)
		ax.plot(Biggest[:, 1], Biggest[:, 0], linewidth=2)   
		ax.axis('image')
		ax.set_xticks([])
		ax.set_yticks([])
		xx=lp.linspace(0,len(x)-1,len(x))
		yy=linear_fit(out.params,xx)
		ax.plot(xx,yy)
		plt.show()
	return y[int(len(x)/2)], x[int(fit)]
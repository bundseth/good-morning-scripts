from lmfit import Minimizer, Parameters, report_fit

import matplotlib.pyplot as plt
import numpy as np

def error_model_allXY(visibility, offset, rotation_error, detuning_error):
    '''
    Function that models the first order error behavior of an allXY experiment

    Args:
        data (np.ndarray)  : standard allXY sequence (spin down = 0, spin up = 1)
        visibility (float) : visibility of the qubit [0,1]
        offset (float)     : offset of the visibility [-0.5,0.5]
        rotation_error (float) : under/over-rotation of the qubit in rad
        detuning_error (float) : detuning error of the qubit, normalized by the pi time.
    '''
    # convert spin probability to Z projection
    data_ideal = np.zeros([21])
    data_ideal[:5] = 1
    data_ideal[-4:] = -1
    
    # power errors :
    rotation_error_syndrome = np.asarray([0] + [-8*rotation_error**2]*2 + [-4*rotation_error**2]*2 +
                            [-rotation_error]*2 +  [rotation_error**2]*2 +  [rotation_error]*4 +  [rotation_error*3]*4 +
                            [2*rotation_error**2]*4)

    detuning_error = np.asarray([0] + [-(np.pi**2)*detuning_error**4/32]*2 + [- detuning_error**2]*2 +
                            [(1-np.pi/2)*detuning_error**2]*2 + [-2*detuning_error]  + [2*detuning_error]  + 
                            [-detuning_error]  + [detuning_error] + [-detuning_error]  + [detuning_error] + [3*np.pi*detuning_error**2/8]*4 +
                            [0.5*detuning_error**2]*2  + [2*detuning_error**2]*2)

    data_ideal += rotation_error_syndrome
    data_ideal += detuning_error
    data_ideal = (data_ideal*-1 +1)/2
    data_ideal = data_ideal*visibility + offset

    return data_ideal

def fit_func_allXY(pars, data):
    data_model = error_model_allXY(pars['visibility'], pars['offset'], pars['rotation_error'], pars['detuning_error'])
    return data - data_model

def fit_allXY(data, time_pi_pulse, plot=False):
    pfit = Parameters()

    offset = np.average(data)
    visibility = np.max(data)-np.min(data)

    pfit.add(name='visibility', value=visibility, min = 0, max=1, vary=False)
    pfit.add(name='offset', value=offset, min=0, max=0.5)
    pfit.add(name='rotation_error', value=0.01, min=-np.pi/10, max=np.pi/10) #20deg error max
    pfit.add(name='detuning_error', value=0.01)

    mini = Minimizer(fit_func_allXY, pfit, fcn_args=(data,))
    intermedediate_result = mini.minimize(method='Nelder')
    result = mini.minimize(method='leastsq', params=intermedediate_result.params)

    best_fit = data + result.residual

    if plot==True:
        plt.figure()
        plt.plot(data, 'bo')
        plt.plot(best_fit, 'r--', label='best fit')
        plt.xlabel('nth gate')
        plt.ylabel('spin prob (%)')
        plt.legend(loc='best')
        plt.show()
    
    # approximate errors.
    print(f'Change pi time by {round(-result.params["rotation_error"].value/np.pi*100,2)} %')
    print(f'Off resonant by {round(result.params["detuning_error"].value/time_pi_pulse*1e-6, 3)} MHz')

    return -result.params["rotation_error"].value/np.pi, result.params["detuning_error"].value/time_pi_pulse/2

if __name__ == '__main__':
    import numpy as np
    from core_tools.data.SQL.connect import set_up_local_storage
    set_up_local_storage("xld_user", "XLDspin001", "vandersypen_data", "6dot", "XLD", "6D2S - SQ21-XX-X-XX-X")

    from core_tools.data.ds.data_set import load_by_id
    ds = load_by_id(32369)
    data = np.average(np.reshape(ds('read1').y(), (2, 21))[1:], axis= 0)

    a,b = fit_allXY(data, 300e-9, True)
    print(a, b)
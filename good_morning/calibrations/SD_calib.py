from core_tools.sweeps.pulse_lib_wrappers.PSB_exp import run_qubit_exp
from core_tools.utility.variable_mgr.var_mgr import variable_mgr
from core_tools.sweeps.sweeps import scan_generic
from core_tools.job_mgnt.job_mgmt import job_wrapper

from dev_V2.six_qubit_QC_v2.system import six_dot_sample
from dev_V2.six_qubit_QC_v2.VAR import variables

import pulse_lib.segments.utility.looping as lp
import qcodes as qc
import numpy as np
import matplotlib.pyplot as plt


@job_wrapper
def SD1_calibration(verbose = False, plot=False):
    gates, _311113, ST_anti_12, ST_anti_12_tc_high, ST_anti_56, ST_anti_56_tc_high, vSD1_threshold, vSD2_threshold = variables()
    
    anticrossing = list(ST_anti_12)
    anticrossing[1] = lp.linspace(anticrossing[1] -3,anticrossing[1] + 3, 2, axis=1, name='vP1', unit='mV') 
    anticrossing[12] = lp.linspace(anticrossing[12] - 3,anticrossing[12] + 3, 80, axis=0, name='vSD1', unit='mV')
    anticrossing =tuple(anticrossing)
    s = six_dot_sample(qc.Station.default.pulse)
    s.add(s.read12, anti_crossing = anticrossing)
    s.n_rep = 500

    sequence, minstr, name = run_qubit_exp(f'SD1_calibration', s.sequencer)

    ds = scan_generic(sequence, minstr, name=name).run()
    subset = ds.m1_1.average(2)
    data = subset()
    y = subset.y()

    idx = np.argmax(data[0] - data[1])
    SD1_winner = y[idx]
    threshold = np.average(data[:,idx])
    
    var_mgr = variable_mgr()
    var_mgr.PSB12_SD1 = SD1_winner 
    var_mgr.threshold_SD1 = threshold 
    
    if plot == True:
        plt.plot(y, data[0])
        plt.plot(y, data[1])
        plt.scatter(SD1_winner, threshold)
        plt.xlabel('SD volatage (mV)')
        plt.ylabel('Reflected signal (mV)')
        plt.show()

    print(f'\n\n--SD1 calib complete--\n\n\tSetting SD1_P to : {SD1_winner},\n\tSetting threshold set to {threshold}')

    return None

@job_wrapper
def SD2_calibration(verbose = False, plot=False):
    gates, _311113, ST_anti_12, ST_anti_12_tc_high, ST_anti_56, ST_anti_56_tc_high, vSD1_threshold, vSD2_threshold = variables()
   
    anticrossing = list(ST_anti_56)
    anticrossing[11] = lp.linspace(anticrossing[11] - 5,anticrossing[11] + 5, 2, axis=1, name='vP6', unit='mV') 
    anticrossing[13] = lp.linspace(anticrossing[13] - 3,anticrossing[13] + 3, 80, axis=0, name='vSD2', unit='mV')
    anticrossing =tuple(anticrossing)

    s = six_dot_sample(qc.Station.default.pulse)
    s.add(s.read56, anti_crossing = anticrossing)
    s.n_rep = 500
    sequence, minstr, name = run_qubit_exp(f'SD2_calibration', s.sequencer)

    ds = scan_generic(sequence, minstr, name=name).run()
    
    averaged_data_set = ds.m1_1.average(2)
    y = averaged_data_set.y()
    data = averaged_data_set.z()
        
    idx = np.argmax(data[1] - data[0])
    SD2_winner = y[idx]
    threshold = np.average(data[:,idx])

    var_mgr = variable_mgr()
    var_mgr.PSB56_SD2 = SD2_winner 
    var_mgr.threshold_SD2 = threshold 
    
    if plot == True:
        plt.plot(y, data[0])
        plt.plot(y, data[1])
        plt.scatter(SD2_winner, threshold)
        plt.xlabel('SD volatage (mV)')
        plt.ylabel('Reflected signal (mV)')
        plt.show()
    print(f'\n\n--SD2 calib complete--\n\n\tSetting SD2_P to : {SD2_winner},\n\tSetting threshold set to {threshold}')
    
    return None

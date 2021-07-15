from core_tools.sweeps.pulse_lib_wrappers.PSB_exp import run_qubit_exp
from core_tools.utility.variable_mgr.var_mgr import variable_mgr
from core_tools.job_mgnt.job_mgmt import job_wrapper
from core_tools.sweeps.sweeps import scan_generic

from dev_V2.six_qubit_QC_v2.system import six_dot_sample
from dev_V2.six_qubit_QC_v2.VAR import variables

import pulse_lib.segments.utility.looping as lp

import matplotlib.pyplot as plt
import qcodes as qc
import scipy as sp
import numpy as np

import multiprocessing
import pyqtgraph as pg

def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, [0]*N))

    return (cumsum[N:] - cumsum[0:-N])/N

def plot_stuff(x_, y_no_MW_, y_wi_MW_, diff_, voltage_read_, pair_):
            plt.figure()
            plt.plot(x_, y_no_MW_, label = 'spin down init')
            plt.plot(x_, y_wi_MW_, label = 'spin up init')
            plt.plot(x_, diff_, label = 'DIFF')
            plt.scatter([voltage_read_],[0.5], label ='selected point')
            plt.xlabel(f'vP{str(pair_)[0]} (mV)')
            plt.ylabel('Spin prob (%)')
            plt.legend()
            plt.show()

def _run_PSB_12_exp(sweep_range, MW_pulse=False):
    var_mgr = variable_mgr()
    gates, _311113, ST_anti_12, ST_anti_12_tc_high, ST_anti_56, ST_anti_56_tc_high, vSD1_threshold, vSD2_threshold = variables()
    
    anticrossing = list(ST_anti_12)
    anticrossing[1] = lp.linspace(anticrossing[1] - sweep_range/2,anticrossing[1] + sweep_range/2, 50, axis=0, name='vP1', unit='mV') 
    anticrossing =tuple(anticrossing)

    s = six_dot_sample(qc.Station.default.pulse)
    s.n_rep = 500
    
    s.add(s.init12, anti_crossing = anticrossing)
    if MW_pulse == True:
        # seg = s.get_seg()
        # seg.qubit1_MW.add_chirp(0, 50e3, var_mgr.frequency_q1*1e9-5e6, var_mgr.frequency_q1*1e9+5e6, 300)
        # seg.reset_time()
        s.add(s.q2.X180)
    s.add(s.read12, anti_crossing = anticrossing)
    
    sequence, minstr, name = run_qubit_exp(f'PSB12_calibration_FAST_MW={MW_pulse}', s.sequencer)

    return scan_generic(sequence, minstr, name=name).run()

def _run_PSB_56_exp(sweep_range, MW_pulse=False):
    var_mgr = variable_mgr()
    gates, _311113, ST_anti_12, ST_anti_12_tc_high, ST_anti_56, ST_anti_56_tc_high, vSD1_threshold, vSD2_threshold = variables()
    
    anticrossing = list(ST_anti_56)
    anticrossing[9] = lp.linspace(anticrossing[9] -  sweep_range/2,anticrossing[9] +  sweep_range/2, 50, axis=0, name='vP5', unit='mV')
    anticrossing =tuple(anticrossing)

    s = six_dot_sample(qc.Station.default.pulse)
    s.n_rep = 500
    
    s.add(s.init56, anti_crossing = anticrossing)
    if MW_pulse == True:
        # seg = s.get_seg()
        # seg.qubit6_MW.add_chirp(0, 20e3, var_mgr.frequency_q6*1e9-5e6, var_mgr.frequency_q6*1e9+5e6, 300)
        # seg.reset_time()
        s.add(s.q5.X180)
    s.add(s.read56, anti_crossing = anticrossing)
    
    sequence, minstr, name = run_qubit_exp(f'PSB56_calibration_FAST_MW={MW_pulse}', s.sequencer)

    return scan_generic(sequence, minstr, name=name).run()

@job_wrapper
def PSB_calibration(pair= 12, sweep_range=2, plot=False):
    if pair == 12:
        ds_no_MW = _run_PSB_12_exp(sweep_range, False)
        ds_wi_MW = _run_PSB_12_exp(sweep_range, True)
    else:
        ds_no_MW = _run_PSB_56_exp(sweep_range, False)
        ds_wi_MW = _run_PSB_56_exp(sweep_range, True)
    
    print(ds_no_MW)
    x = ds_no_MW(f'read{int(pair)}').x()
    y_no_MW = ds_no_MW(f'read{int(pair)}').y()
    y_no_MW[np.isnan(y_no_MW)] = 0
    y_wi_MW = ds_wi_MW(f'read{int(pair)}').y()
    y_wi_MW[np.isnan(y_wi_MW)] = 0    
    y_sel = ds_wi_MW(f'init{int(pair)} selected').y()

    idx_invalid = np.where(y_sel < 200)[0]
    y_no_MW[idx_invalid] = 0
    y_wi_MW[idx_invalid] = 0

    diff = np.abs(running_mean(y_wi_MW-y_no_MW, 3))
    
    voltage_read = x[np.argmax(diff)]
    var_mgr = variable_mgr()
    setattr(var_mgr, f"PSB{int(pair)}_P{str(pair)[0]}", round(voltage_read, 2))

    print(f'\nSetting readout point\n\tpoint : {voltage_read}mV\n')
    if plot == True:
        plot_stuff(x, y_no_MW, y_wi_MW, diff, voltage_read, pair)
        # p = multiprocessing.Process(target=plot_stuff, args=(x, y_no_MW, y_wi_MW, diff, voltage_read, pair))
        # p.start()
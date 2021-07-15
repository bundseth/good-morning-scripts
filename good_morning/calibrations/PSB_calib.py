from good_morning.calibrations.ultility import get_target, readout_convertor

from core_tools.utility.variable_mgr.var_mgr import variable_mgr
from core_tools.sweeps.pulse_lib_wrappers.PSB_exp import run_qubit_exp
from core_tools.sweeps.sweeps import scan_generic
from core_tools.job_mgnt.job_mgmt import job_wrapper

from dev_V2.six_qubit_QC_v2.system import six_dot_sample
from dev_V2.Elzerman_2_qubits_clean.TRIG import mk_TRIG
from dev_V2.six_qubit_QC_v2.VAR import variables

import pulse_lib.segments.utility.looping as lp
import matplotlib.pyplot as plt

import qcodes as qc
import scipy as sp
import numpy as np

@job_wrapper
def PSB12_calibration(sweep_range=0.5, plot=False):
    gates, _311113, ST_anti_12, ST_anti_12_tc_high, ST_anti_56, ST_anti_56_tc_high, vSD1_threshold, vSD2_threshold = variables()
    
    anticrossing = list(ST_anti_12)
    anticrossing[1] = lp.linspace(anticrossing[1] - sweep_range/2,anticrossing[1] + sweep_range/2, 20, axis=0, name='vP1', unit='mV') 
    anticrossing[3] = lp.linspace(anticrossing[3] - sweep_range/2,anticrossing[3] + sweep_range/2, 20, axis=1, name='vP2', unit='mV') 
    anticrossing =tuple(anticrossing)

    var_mgr = variable_mgr()

    s = six_dot_sample(qc.Station.default.pulse)
    
    s.add(s.init12, anti_crossing = anticrossing)
    s.add(s.q2.X180)
    s.add(s.read12, anti_crossing = anticrossing)
    
    s.n_rep = 500
    sequence, minstr, name = run_qubit_exp(f'PSB12_calibration_SLOW', s.sequencer)

    qc.Station.default.MW_source.on()    
    ds_on = scan_generic(sequence, minstr, name=name).run()
    
    # qc.Station.default.MW_source.off()
    # ds_off = scan_generic(sequence, minstr, name=name).run()

    # x = ds_on('read12').x()
    # y = ds_on('read12').y()

    # contrast = np.where(ds_on('read12')()>0.9,0,ds_on('read12')()) -  np.where(ds_off('read12')()>0.9,0,ds_off('read12')())
    # contrast = sp.ndimage.filters.gaussian_filter(contrast, [2,2], mode='constant')
    # if plot:
    #     plt.imshow(contrast)
        
    # var_mgr.PSB_12_P2 = round(x[np.where(contrast == contrast.max())[0][0]], 2)
    # var_mgr.PSB_12_P1 = round(y[np.where(contrast == contrast.max())[1][0]], 2)

    # print(f"Selected point\n\tvP1 :: {var_mgr.PSB_12_P1}\n\tvP2 :: {var_mgr.PSB_12_P2}")

    # qc.Station.default.MW_source.on()        

@job_wrapper
def PSB56_calibration(sweep_range=0.5, plot=False):
    gates, _311113, ST_anti_12, ST_anti_12_tc_high, ST_anti_56, ST_anti_56_tc_high, vSD1_threshold, vSD2_threshold = variables()
    
    anticrossing = list(ST_anti_56)
    anticrossing[9] = lp.linspace(anticrossing[9] -  sweep_range/2,anticrossing[9] +  sweep_range/2, 20, axis=1, name='vP5', unit='mV') 
    anticrossing[11] = lp.linspace(anticrossing[11] -  sweep_range/2,anticrossing[11] +  sweep_range/2, 20, axis=0, name='vP6', unit='mV')
    anticrossing =tuple(anticrossing)

    var_mgr = variable_mgr()

    s = six_dot_sample(qc.Station.default.pulse)
    
    s.add(s.init56, anti_crossing = anticrossing)
    s.add(s.q5.X180)
    s.add(s.read56, anti_crossing = anticrossing)
    
    s.n_rep = 500
    sequence, minstr, name = run_qubit_exp(f'PSB12_calibration_SLOW', s.sequencer)

    qc.Station.default.MW_source.on()    
    ds_on = scan_generic(sequence, minstr, name=name).run()
    # qc.Station.default.MW_source.off()    
    # ds_off = scan_generic(sequence, minstr, name=name).run()

    # x = ds_on('read56').x()
    # y = ds_on('read56').y()    
    # contrast = np.where(ds_on('read56')()>0.9,0,ds_on('read56')()) -  np.where(ds_off('read56')()>0.9,0,ds_off('read56')())
    # contrast = sp.ndimage.filters.gaussian_filter(contrast, [2,2], mode='constant')
    # if plot:
    #     plt.imshow(contrast)

    # var_mgr.PSB_56_P5 = round(x[np.where(contrast == contrast.max())[0][0]],2)
    # var_mgr.PSB_56_P6 = round(y[np.where(contrast == contrast.max())[1][0]],2)
    # print(f"Selected point\n\tvP5 :: {var_mgr.PSB_56_P5}\n\tvP6 :: {var_mgr.PSB_56_P6}")

    # qc.Station.default.MW_source.on()
from good_morning.calibrations.ultility import get_target, readout_convertor
from good_morning.fittings.fit_resonance import fit_resonance

from core_tools.sweeps.pulse_lib_wrappers.PSB_exp import run_qubit_exp
from core_tools.sweeps.sweeps import scan_generic, do0D, do1D
from core_tools.utility.variable_mgr.var_mgr import variable_mgr
from core_tools.job_mgnt.job_mgmt import job_wrapper

import pulse_lib.segments.utility.looping as lp
from dev_V2.six_qubit_QC_v2.system import six_dot_sample

import qcodes as qc
import numpy as np

@job_wrapper
def cal_power_hires(target, plot=False):

    s = six_dot_sample(qc.Station.default.pulse)

    var_mgr = variable_mgr()

    
    s.add(s.wait(100))  
    s.init(target)

    qubit = getattr(s, f'q{target}')
    power = getattr(var_mgr, f'q{target}_MW_power')
    start, stop  = (power-30, power+30)
    s.add(s.wait(10e3))
    s.add(s.pre_pulse)
    s.add(qubit.X180, phase_corrections = {}, MW_power =  lp.linspace(start,stop, 50, name = 'Power', unit='mV', axis=0))
    s.add(qubit.X180, phase_corrections = {}, MW_power =  lp.linspace(start,stop, 50, name = 'Power', unit='mV', axis=0))
    s.add(qubit.X180, phase_corrections = {}, MW_power =  lp.linspace(start,stop, 50, name = 'Power', unit='mV', axis=0))
    s.add(qubit.X180, phase_corrections = {}, MW_power =  lp.linspace(start,stop, 50, name = 'Power', unit='mV', axis=0))
    s.add(qubit.X180, phase_corrections = {}, MW_power =  lp.linspace(start,stop, 50, name = 'Power', unit='mV', axis=0))
    s.add(qubit.X180, phase_corrections = {}, MW_power =  lp.linspace(start,stop, 50, name = 'Power', unit='mV', axis=0))
    s.add(qubit.X180, phase_corrections = {}, MW_power =  lp.linspace(start,stop, 50, name = 'Power', unit='mV', axis=0))
    s.add(qubit.X180, phase_corrections = {}, MW_power =  lp.linspace(start,stop, 50, name = 'Power', unit='mV', axis=0))
    s.add(qubit.X180, phase_corrections = {}, MW_power =  lp.linspace(start,stop, 50, name = 'Power', unit='mV', axis=0))
    s.add(s.wait(100e3))

    s.read(target)

    sequence, minstr, name = run_qubit_exp(f'qubit{target} power calib', s.sequencer)
    ds = scan_generic(sequence, minstr, name=name).run()

    MW_power = ds(readout_convertor(f'read{target}')).x()
    probabilities = ds(readout_convertor(f'read{target}')).y()

    power_new = fit_resonance(MW_power, probabilities,linewidth=10, method='gaussian', plot=plot)
    print(f'setting power to :: {round(power,1)} \t (old value, {round(power_new,1)}')
    setattr(var_mgr, f'q{target}_MW_power', round(power_new,1))

@job_wrapper
def cal_freq_hires(target, plot=False):

    s = six_dot_sample(qc.Station.default.pulse)

    var_mgr = variable_mgr()

    s.init(target)

    qubit = getattr(s, f'q{target}')
    old_freq = getattr(var_mgr, f'frequency_q{target}')
    rabi_freq =  0.5e9/getattr(var_mgr, f'pi_q{target}')
    s.add(s.pre_pulse)
    s.add(qubit.X180, phase_corrections = {}, f_qubit = lp.linspace(old_freq*1e9-rabi_freq, old_freq*1e9+rabi_freq, 50, axis= 0, name='freq', unit='Hz'))
    s.add(qubit.X180, phase_corrections = {}, f_qubit = lp.linspace(old_freq*1e9-rabi_freq, old_freq*1e9+rabi_freq, 50, axis= 0, name='freq', unit='Hz'))
    s.add(qubit.X180, phase_corrections = {}, f_qubit = lp.linspace(old_freq*1e9-rabi_freq, old_freq*1e9+rabi_freq, 50, axis= 0, name='freq', unit='Hz'))
    s.add(qubit.X180, phase_corrections = {}, f_qubit = lp.linspace(old_freq*1e9-rabi_freq, old_freq*1e9+rabi_freq, 50, axis= 0, name='freq', unit='Hz'))
    s.add(qubit.X180, phase_corrections = {}, f_qubit = lp.linspace(old_freq*1e9-rabi_freq, old_freq*1e9+rabi_freq, 50, axis= 0, name='freq', unit='Hz'))
    s.add(qubit.X180, phase_corrections = {}, f_qubit = lp.linspace(old_freq*1e9-rabi_freq, old_freq*1e9+rabi_freq, 50, axis= 0, name='freq', unit='Hz'))
    s.add(qubit.X180, phase_corrections = {}, f_qubit = lp.linspace(old_freq*1e9-rabi_freq, old_freq*1e9+rabi_freq, 50, axis= 0, name='freq', unit='Hz'))
    s.add(qubit.X180, phase_corrections = {}, f_qubit = lp.linspace(old_freq*1e9-rabi_freq, old_freq*1e9+rabi_freq, 50, axis= 0, name='freq', unit='Hz'))
    s.add(qubit.X180, phase_corrections = {}, f_qubit = lp.linspace(old_freq*1e9-rabi_freq, old_freq*1e9+rabi_freq, 50, axis= 0, name='freq', unit='Hz'))
    s.add(s.wait(100e3))

    s.read(target)

    sequence, minstr, name = run_qubit_exp(f'qubit{target} freq calib', s.sequencer)
    ds = scan_generic(sequence, minstr, name=name).run()

    freq = ds(readout_convertor(f'read{target}')).x()
    probabilities = ds(readout_convertor(f'read{target}')).y()

    res = fit_resonance(freq, probabilities,  rabi_freq=rabi_freq, angle=9*np.pi, plot=plot)*1e-9
    print(f'setting power to :: {round(res,5)} \t (old value, {round(old_freq,5)}')
    setattr(var_mgr, f'frequency_q{target}', round(res,5))
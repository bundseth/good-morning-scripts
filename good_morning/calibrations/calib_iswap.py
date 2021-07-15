from pulse_templates.coherent_control.two_qubit_gates.iswap import iswap, iswap_cal

from core_tools.utility.variable_mgr.var_mgr import variable_mgr
from core_tools.sweeps.pulse_lib_wrappers.PSB_exp import run_qubit_exp
from core_tools.sweeps.sweeps import scan_generic, do0D, do1D
from core_tools.job_mgnt.job_mgmt import job_wrapper

from good_morning.calibrations.ultility import get_target, readout_convertor
from good_morning.fittings.J_versus_voltage import fit_J, J_to_voltage, fit_delta_B_vs_J
from good_morning.fittings.fit_resonance import fit_resonance

import pulse_lib.segments.utility.looping as lp
from dev_V2.six_qubit_QC_v2.system import six_dot_sample

import good_morning.static.J12 as J12
import good_morning.static.J23 as J23
import good_morning.static.J34 as J34
import good_morning.static.J45 as J45
import good_morning.static.J56 as J56

import qcodes as qc
import numpy as np

from good_morning.fittings.shaped_cphase import fit_phase

@job_wrapper
def iswap_f_res_calib(target, even = False, plot=False):
    target = str(int(target))
    var_mngr = variable_mgr()

    s = six_dot_sample(qc.Station.default.pulse)
    s.add(s.pre_pulse)
    s.init(target[0], target[1])

    if even == True:
        s.add(s[f'q{target[0]}'].X180)
    
    J_max = getattr(var_mngr, f'J_max_{target}')*1e6
    delta_B = getattr(var_mngr, f'frequency_q{target[1]}')*1e9 - getattr(var_mngr, f'frequency_q{target[0]}')*1e9

    s.add_func(iswap_cal,
        gates = globals()[f'J{target}'].gates,
        J_value = lp.linspace(1e6, J_max, 5, 'J', 'Hz', 0),
        J_excitation = lp.linspace(1e6, J_max, 5, 'J', 'Hz', 0),
        f_excitation = lp.linspace(delta_B-8e6, delta_B+8e6, 50, 'freq', 'Hz', 1),
        angle = np.pi,
        J_to_voltage_relation = globals()[f'J{target}'].gen_J_to_voltage(),
        padding = 20)

    s.read(target[0], target[1])

    sequence, minstr, name = run_qubit_exp(f'iswap frequency cal high_range :: {target}', s.sequencer)
    ds1 = scan_generic(sequence, minstr, name=name).run()

    s = six_dot_sample(qc.Station.default.pulse)
    s.add(s.pre_pulse)
    s.init(target[0], target[1])

    sweep = lp.linspace(-0.2*np.pi,3*np.pi, 100, 'angle', 'rad', 0)

    if even == True:
        s.add(s[f'q{target[0]}'].X180)
    
    J_max = getattr(var_mngr, f'J_max_{target}')*1e6
    delta_B = getattr(var_mngr, f'frequency_q{target[1]}')*1e9 - getattr(var_mngr, f'frequency_q{target[0]}')*1e9
    s.add_func(iswap_cal,
        gates = globals()[f'J{target}'].gates,
        J_value = lp.linspace(0.2e6, 0.9e6, 4, 'J', 'Hz', 0),
        J_excitation = lp.linspace(0.2e6, 0.9e6, 4, 'J', 'Hz', 0),
        f_excitation = lp.linspace(delta_B-3e6, delta_B+3e6, 50, 'freq', 'Hz', 1),
        angle = np.pi,
        J_to_voltage_relation = globals()[f'J{target}'].gen_J_to_voltage(),
        padding = 20)

    s.read(target[0], target[1])

    sequence, minstr, name = run_qubit_exp(f'iswap frequency cal low_range :: {target}', s.sequencer)
    ds2 = scan_generic(sequence, minstr, name=name).run()

    # fitting
    J_values_1 = ds1(readout_convertor(f'read{target[1]}')).x()
    f_res_1 = ds1(readout_convertor(f'read{target[1]}')).y()
    measurement_1 = ds1(readout_convertor(f'read{target[1]}')).z()

    J_values_2 = ds2(readout_convertor(f'read{target[1]}')).x()
    f_res_2 = ds2(readout_convertor(f'read{target[1]}')).y()
    measurement_2 = ds2(readout_convertor(f'read{target[1]}')).z()

    var_mngr = variable_mgr()

    resonance = list()
    J_vals = list()

    for i in range(len(measurement_2)):
        res = fit_resonance(f_res_2, measurement_2[i], J_values_2[i]/2)
        resonance.append(res)
        J_vals.append(J_values_2[i])

    for i in range(len(measurement_1)):
        res = fit_resonance(f_res_1, measurement_1[i], J_values_1[i]/2)
        resonance.append(res)
        J_vals.append(J_values_1[i])


    coeff = fit_delta_B_vs_J(J_vals, resonance, False)


    for i in range(6):
        if not hasattr(var_mngr,f'iSWAP_{target}_J_f_res_coeff_{i}'):
          var_mngr.add_variable(f'iSWAP_{target}',f'iSWAP_{target}_J_f_res_coeff_{i}','a.u.',0.1,0)

        old_phase = getattr(var_mngr,f'iSWAP_{target}_J_f_res_coeff_{i}')
        setattr(var_mngr,f'iSWAP_{target}_J_f_res_coeff_{i}', coeff.c[i])

@job_wrapper
def iswap_rotation_angle(target, even = False, plot=False):
    target = str(int(target))
    var_mngr = variable_mgr()

    s = six_dot_sample(qc.Station.default.pulse)

    s.pre_pulse.add(s.manip2)
    s.init(target[0], target[1])

    if even == True:
        getattr(s,f'q{target[0]}').X180.add(s.manip)
    
    J_max = getattr(var_mngr, f'J_max_{target}')*1e6
    delta_B = getattr(var_mngr, f'frequency_q{target[1]}')*1e9 - getattr(var_mngr, f'frequency_q{target[0]}')*1e9

    iswap(s.manip, globals()[f'J{target}'].gates,
        lp.linspace(0,np.pi*2, 40, 'angle', 'rad', 0), 0, J_max, delta_B,
        globals()[f'J{target}'].gen_J_to_voltage(), globals()[f'J{target}'].return_delta_B_J_relation())
    s.read(target[0], target[1])

    sequence, minstr, name = run_qubit_exp(f'iswap angle calibration:: {target}', s.segments(), s.measurement_manager)
    
    ds = scan_generic(sequence, minstr, name=name).run()

    target_ds = target[0]
    input_phases = ds(readout_convertor(f'read{target_ds}')).x()
    amplitude = ds(readout_convertor(f'read{target_ds}')).y()
    # get rid of the first part due to heating
    input_phases = input_phases[10:]
    amplitude = amplitude[10:]

    J_time = fit_phase(input_phases, amplitude, True, plot=plot)
    print(J_time)

    var_mgr = variable_mgr()    
    if not hasattr(var_mgr,f'iSWAP_{target}_J_angle'):
        var_mgr.add_variable(f'iSWAP_{target}',f'iSWAP_{target}_J_angle','rad',0.1,0)

    old_phase = getattr(var_mgr,f'iSWAP_{target}_J_angle')
    setattr(var_mgr,f'iSWAP_{target}_J_angle', round(J_time,3))

if __name__ == '__main__':
    from core_tools.data.SQL.connect import set_up_local_storage
    from core_tools.data.ds.data_set import load_by_id
    
    set_up_local_storage("xld_user", "XLDspin001", "vandersypen_data", "6dot", "XLD", "6D2S - SQ21-XX-X-XX-X")
    
    import matplotlib.pyplot as plt

    ds1 = load_by_id(20612)
    ds2 = load_by_id(20613)

    J_values_1 = ds1('read5').x()
    f_res_1 = ds1('read5').y()
    measurement_1 = ds1('read5').z()

    J_values_2 = ds2('read5').x()
    f_res_2 = ds2('read5').y()
    measurement_2 = ds2('read5').z()

    var_mngr = variable_mgr()
    target = '45'

    resonance = list()
    J_vals = list()

    for i in range(len(measurement_2)):
        plt.plot(f_res_2, measurement_2[i])
        res = fit_resonance(f_res_2, measurement_2[i], J_values_2[i]/2, False)

        resonance.append(res)
        J_vals.append(J_values_2[i])

    for i in range(len(measurement_1)):
        plt.plot(f_res_1, measurement_1[i])
        res = fit_resonance(f_res_1, measurement_1[i], J_values_1[i]/2, False)

        resonance.append(res)
        J_vals.append(J_values_1[i])

    coeff = fit_delta_B_vs_J(J_vals, resonance, False)

    for i in range(6):
        if not hasattr(var_mngr,f'iSWAP_{target}_J_f_res_coeff_{i}'):
          var_mngr.add_variable(f'iSWAP_{target}',f'iSWAP_{target}_J_f_res_coeff_{i}','a.u.',0.1,0)

        old_phase = getattr(var_mngr,f'iSWAP_{target}_J_f_res_coeff_{i}')
        setattr(var_mngr,f'iSWAP_{target}_J_f_res_coeff_{i}', coeff.c[i])

    relation = np.poly1d(coeff)
    plt.figure()
    plt.plot([0] + J_vals, J45.return_delta_B_J_relation()([0] + list(J_vals)))
    plt.plot(J_vals, resonance)
    plt.show()
from good_morning.fittings.J_versus_voltage import fit_J, J_to_voltage, voltage_to_J
from good_morning.calibrations.ultility import get_target, readout_convertor
from good_morning.fittings.fit_rabi_osc import fit_ramsey

from core_tools.sweeps.pulse_lib_wrappers.PSB_exp import run_qubit_exp
from core_tools.utility.variable_mgr.var_mgr import variable_mgr
from core_tools.sweeps.sweeps import scan_generic, do0D, do1D
from core_tools.job_mgnt.job_mgmt import job_wrapper
from pulse_templates.coherent_control.two_qubit_gates.standard_set import two_qubit_std_set, two_qubit_gate_generic

from pulse_templates.coherent_control.two_qubit_gates.cphase import cphase_basic

from dev_V2.six_qubit_QC_v2.system import six_dot_sample
import pulse_lib.segments.utility.looping as lp

import qcodes as qc
import numpy as np

import good_morning.static.J12 as J12
import good_morning.static.J23 as J23
import good_morning.static.J34 as J34
import good_morning.static.J45 as J45
import good_morning.static.J56 as J56

@job_wrapper
def calib_symm_point(target, pulse_range=6, even=False, plot=False):
	'''
	Args:
		qubit_pair (str) : pair of qubits to calibrate cphase for.
	'''
	s = six_dot_sample(qc.Station.default.pulse)
	var_mgr = variable_mgr()

	t_cphase = getattr(var_mgr, f'cphase_time_{target}')
	target = str(int(target))

	gates = list(globals()[f'J{target}'].gates)
	voltages_gates = list(globals()[f'J{target}'].voltages_gates)

	voltages_gates[gates.index('vP' + target[0])] = lp.linspace(-pulse_range + voltages_gates[gates.index('vP' + target[0])],
																		pulse_range + voltages_gates[gates.index('vP' + target[0])],
																		25, axis=0, name=f'vP{target[0]}', unit='mV')
	voltages_gates[gates.index('vP' + target[1])] = lp.linspace(-pulse_range + voltages_gates[gates.index('vP' + target[1])],
																		pulse_range + voltages_gates[gates.index('vP' + target[1])],
																		25, axis=1, name=f'vP{target[1]}', unit='mV')

	s.init(target[0], target[1])
	s.add(s.wait(100))
	s.add(s.pre_pulse)
	s.add(s.wait(100))

	s.add(s[f'q{target[0]}'].X90)
	s.add_func(cphase_basic, tuple(gates), tuple([0]*len(gates)), tuple(voltages_gates), t_gate= t_cphase/2, t_ramp=10)
	s.add(s[f'q{target[0]}'].X180)
	s.add(s[f'q{target[1]}'].X180)
	s.add_func(cphase_basic, tuple(gates), tuple([0]*len(gates)), tuple(voltages_gates), t_gate= t_cphase/2, t_ramp=10)
	s.add(s[f'q{target[0]}'].X90)

	s.add(s.wait(100))

	s.read(target[0])

	sequence, minstr, name = run_qubit_exp(f'symm cal :: {target}', s.sequencer)
	ds = scan_generic(sequence, minstr, name=name).run()

	# x_axis = ds(readout_convertor(f'read{target[0]}')).x()
	# y_axis = ds(readout_convertor(f'read{target[0]}')).y()
	# probabilities = ds(readout_convertor(f'read{target[0]}')).z()
	# fit_symmetry(x_axis,y_axis,probabilities, plot)
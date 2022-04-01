from pulse_templates.coherent_control.single_qubit_gates.single_qubit_gates import single_qubit_gate_spec
from pulse_templates.coherent_control.single_qubit_gates.standard_set import single_qubit_std_set

from pulse_templates.coherent_control.two_qubit_gates.standard_set import two_qubit_std_set, two_qubit_gate_generic
from pulse_templates.coherent_control.two_qubit_gates.cphase import cphase_basic, cphase
from pulse_templates.coherent_control.two_qubit_gates.iswap import iswap, iswap_cal
from pulse_templates.coherent_control.two_qubit_gates.CROT import CROT_basic, CROT

from pulse_templates.oper.operators import wait

from pulse_templates.psb_pulses.readout_standard_set import readout_spec, readout_std_set
from pulse_templates.psb_pulses.readout_pulses import PSB_read
from pulse_templates.psb_pulses.readout_template import ReadoutTemplate

from pulse_templates.measurement.measurement import measurement, MeasurementSet
from pulse_templates.coherent_control.wait import wait_std_set

from pulse_templates.utility.sequence_template import SequenceTemplate
from pulse_templates.utility.plotting import plot_seg

from pulse_lib.sequence_builder import sequence_builder
from pulse_templates.utility.conditional_template import Conditional

from dev_V2.six_qubit_QC_v2.basic_operations import do_READ_12, do_READ_56
from core_tools.utility.variable_mgr.var_mgr import variable_mgr
from dev_V2.six_qubit_QC_v2.VAR import variables

import good_morning.static.J12 as J12
import good_morning.static.J23 as J23
import good_morning.static.J34 as J34
import good_morning.static.J45 as J45
import good_morning.static.J56 as J56

import numpy as np
import qcodes as qc

class MODES:
    FAST = 0
    FULL = 1

from scipy import signal

def blackman_sloped_envelope(delta_t, sample_rate = 1):
    """
    function that has blackman slopes at the start and at the end (first 8 and last 8 ns)

    Args:
        delta_t (double) : time in ns of the pulse.
        sample_rate (double) : sampling rate of the pulse (GS/s).

    Returns:
        evelope (np.ndarray) : array of the evelope.
    """

    n_points = int(delta_t*sample_rate)

    
    envelope = np.ones([n_points], np.double)

    if delta_t < 20:
        envelope = signal.get_window('hann', n_points*10)[::10]
    else:
        time_slope = (20 + delta_t)*sample_rate - int(delta_t*sample_rate)
        envelope_left_right = signal.get_window('hann', int(time_slope*10))[::10]

        half_pt_gauss = int(time_slope/2)

        envelope[:half_pt_gauss] = envelope_left_right[:half_pt_gauss]
        envelope[half_pt_gauss:half_pt_gauss+n_points-int(time_slope)] = 1
        envelope[n_points-len(envelope_left_right[half_pt_gauss:]):] = envelope_left_right[half_pt_gauss:]

    return envelope


class six_dot_sample:
    def __init__(self, pulse):
        var_mngr = variable_mgr()
        self.mode = 0
        self._sequencer = sequence_builder(pulse)
        self.n_rep = int(var_mngr.n_rep)

        self.init_done = False
        self.read_done = False

        self.pre_pulse = single_qubit_gate_spec('qubit1_MW', 16.0e9, 10e3, 00, padding= 100)
        self.wait = wait_std_set(gates=('P1',), p_0=(0,))

        self.PSB_calls = [0,0]
        
        try:
            qc.Station.default.dig.set_demodulated_in(1,var_mngr.phase_SD1, False)
            qc.Station.default.dig.set_demodulated_in(3,var_mngr.phase_SD2, False)
        except:
            pass

        for qubit_n in range(1,7):
            self[f'q{qubit_n}'] = single_qubit_std_set()

            phase_corrections = dict()
            for qubit_m in range(1,7):
                phase_corrections[f'qubit{qubit_m}_MW'] = var_mngr[f'PHASE_q{qubit_m}_q{qubit_n}_X']

            pulse.set_qubit_idle_frequency(f'qubit{qubit_n}_MW', var_mngr[f'frequency_q{qubit_n}']*1e9)
            # getattr(pulse,f'qubit{qubit_n}_MW').LO = var_mngr[f'frequency_q{qubit_n}']*1e9

            self[f'q{qubit_n}'].X =  single_qubit_gate_spec(f'qubit{qubit_n}_MW', f_qubit =  var_mngr[f'frequency_q{qubit_n}']*1e9,
                                                t_pulse = var_mngr[f'pi_q{qubit_n}']/2, 
                                                MW_power = var_mngr[f'q{qubit_n}_MW_power'], 
                                                phase_corrections =  phase_corrections,
                                                # AM_mod='blackman',
                                                padding=5)

        for tg in ['12', '23', '34', '45', '56']:
            self[ f'q{tg}'] = two_qubit_std_set(self[f'q{tg[0]}'], self[f'q{tg[1]}'])
            self[ f'q{tg}'].cphase = two_qubit_gate_generic(cphase, {'gates' :  globals()[f'J{tg}'].gates ,
                                                        'cphase_angle' : var_mngr[f'J_pi_{tg}'], 
                                                        'J_max' : var_mngr[f'J_target_{tg}']*1e6, 
                                                        'delta_B' : abs(var_mngr[f'frequency_q{tg[1]}']*1e9 - var_mngr[f'frequency_q{tg[0]}']*1e9),
                                                        'voltage_to_J_relation' : globals()[f'J{tg}'].gen_J_to_voltage(),
                                                        'padding' : 40}, 
                                                        phase_corrections = {f'qubit1_MW' : var_mngr[f'PHASE_q1_q{tg}_cphase'],
                                                                             f'qubit2_MW' : var_mngr[f'PHASE_q2_q{tg}_cphase'],
                                                                             f'qubit3_MW' : var_mngr[f'PHASE_q3_q{tg}_cphase'],
                                                                             f'qubit4_MW' : var_mngr[f'PHASE_q4_q{tg}_cphase'],
                                                                             f'qubit5_MW' : var_mngr[f'PHASE_q5_q{tg}_cphase'],
                                                                             f'qubit6_MW' : var_mngr[f'PHASE_q6_q{tg}_cphase']})
        #     for i in ['12', '12_z', '21', '21_z']:
        #         target = tg[0] if '12' in i else tg[1]

        #         spec_12 = single_qubit_gate_spec(f'qubit{target}_MW', var_mngr[f'CROT{tg}_{i}_freq']*1e9,
        #                                 var_mngr[f'CROT{tg}_{i}_pi_time'], var_mngr[f'CROT{tg}_{i}_MW_power'], padding=30)
        #         self[f'q{tg}'][f'CROT_{i}'] = two_qubit_gate_generic(CROT, {'gates' :  globals()[f'J{tg}'].gates ,
        #                                                 'gate_spec' : spec_12 ,
        #                                                 'J_target' : var_mngr[f'CROT{tg}_J_target']*1e6, 
        #                                                 'delta_B' : var_mngr[f'frequency_q{tg[1]}']*1e9 - var_mngr[f'frequency_q{tg[0]}']*1e9,
        #                                                 'voltage_to_J_relation' : globals()[f'J{tg}'].gen_J_to_voltage(),
        #                                                 'padding' : 10},
        #                                             phase_corrections = {})



        CROT_23 = single_qubit_gate_spec('qubit2_MW', var_mngr.crot23*1e9,
                                    var_mngr.pi_crot2, var_mngr.CROT23_MW_power, padding=10)

        CNOT_via_CROT23 = two_qubit_gate_generic(CROT_basic, {'gates' :  J23.gates, 
                                    'v_exchange_pulse_off' : tuple([0]*len(J23.gates)),
                                    'v_exchange_pulse_on' :  J23.barrier_perc_to_voltage(var_mngr.CROT23_B2),
                                    'gate_spec' : CROT_23,
                                    't_ramp' : 20,
                                    'padding': 10})

        self.q23.CROT12 = CNOT_via_CROT23
        # self.q23.SWAP = two_qubit_gate_generic(iswap_cal, {'gates' : J23.gates, 
        #                             'J_value' : 6e6,
        #                             'J_excitation' : 2e6,
        #                             'f_excitation' : 53.2e6,
        #                             'angle' : np.pi,
        #                             'J_to_voltage_relation' : J23.gen_J_to_voltage()
        #                             })

        CROT_45 = single_qubit_gate_spec('qubit5_MW', 
                                    var_mngr.crot54*1e9,
                                    var_mngr.pi_crot5, var_mngr.CROT45_MW_power, padding=2)

        crot45 = two_qubit_gate_generic(CROT_basic, {'gates' : J45.gates, 
                                    'v_exchange_pulse_off' :  tuple([0]*len(J45.gates)),
                                    'v_exchange_pulse_on' :  J45.barrier_perc_to_voltage(var_mngr.CROT45_B4),
                                    'gate_spec' : CROT_45,
                                    't_ramp' : 20,
                                    'padding': 10})

        self.q45.CROT21 = crot45
        # self.q45.iSWAP  = two_qubit_gate_generic(iswap, {'gates' :  globals()[f'J{45}'].gates ,
        #                                                  'iswap_angle' : var_mngr[f'iSWAP_{45}_J_angle'], 
        #                                                  'phase' : 0, 
        #                                                  'J_max' : var_mngr[f'J_max_{45}']*1e6,  
        #                                                  'delta_B' : var_mngr[ f'frequency_q{str(45)[1]}']*1e9 - var_mngr[ f'frequency_q{str(45)[0]}']*1e9,
        #                                                  'J_to_voltage_relation' : globals()[f'J{45}'].gen_J_to_voltage(),
        #                                                  'f_res_to_J_relation' : globals()[f'J{45}'].return_delta_B_J_relation(),
        #                                                 'padding' : 20}, 
        #                                                 phase_corrections = {})

        measure_12 = measurement(channel='SD1_IQ', t_measure=10e3, threshold=var_mngr.threshold_SD1)
        measure_56 = measurement(channel='SD2_IQ', t_measure=15e3, threshold=var_mngr.threshold_SD2)

        self.psb12 = ReadoutTemplate(do_READ_12, measure_12, ramp= 1e2, t_measure = 10e3)
        self.psb56 = ReadoutTemplate(do_READ_56, measure_56, ramp= 2e3, t_measure = 15e3)

        m = MeasurementSet()
        _init12 = m.add('init12', self.psb12, accept=0)
        _init3  = m.add('init3' , self.psb12, accept=0)
        _init56 = m.add('init56', self.psb56, accept=0)
        _init4  = m.add('init4' , self.psb56, accept=0)

        _read12 = m.add('read12', self.psb12)
        _read12_cnot3 = m.add('read12_cnot3', self.psb12) # raw value and result value match
        _read3 = m.add('read3', m['read12'] ^ m['read12_cnot3'])  # no raw value, only result

        _read56 = m.add('read56', self.psb56)
        _read56_cnot4 = m.add('read56_cnot4', self.psb56)
        _read4 = m.add('read4', m['read56'] ^ m['read56_cnot4'])

        self.init12 = _init12
        self.init56 = _init56

        self.init1 = m.add('init1', self.psb12, accept=0)
        self.init2 = m.add('init2', self.psb12, accept=0)
        self.init5 = m.add('init5', self.psb56, accept=0)
        self.init6 = m.add('init6', self.psb56, accept=0)

        self.init3 = SequenceTemplate(self.wait(100), self.q23.CROT12, self.wait(100), _init3, self.wait(100), self.q23.CROT12, self.wait(100), _init3, self.wait(100), self.q23.CROT12, self.wait(100), _init3)
        self.init4 = SequenceTemplate(self.wait(100), self.q45.CROT21, self.wait(100), _init4, self.wait(100), self.q45.CROT21, self.wait(100), _init4, self.wait(100), self.q45.CROT21, self.wait(100), _init4)

        self.read12 = _read12
        self.read56 = _read56

        self.read1 = m.add('read1', self.psb12)
        self.read2 = m.add('read2', self.psb12)
        self.read5 = m.add('read5', self.psb56)
        self.read6 = m.add('read6', self.psb56)

        self.read3 = SequenceTemplate(self.wait(100), self.q23.CROT12, self.wait(100), _read12_cnot3, _read3)
        self.read4 = SequenceTemplate(self.wait(100), self.q45.CROT21, self.wait(100), _read56_cnot4, _read4)

        self._init12_FPGA = m.add('_init12_FPGA_M1', self.psb12)
        _fix_12 = Conditional(m['_init12_FPGA_M1'], None, self.q1.X180)
        self.init12_FPGA = SequenceTemplate(self._init12_FPGA, self.wait(1e3), _fix_12,self.wait(1e3), self.init12)

        self._init56_FPGA = m.add('_init56_FPGA_M1', self.psb56)
        _fix_56 = Conditional(m['_init56_FPGA_M1'], None, self.q6.X180)
        self.init56_FPGA = SequenceTemplate(self._init56_FPGA, self.wait(1e3), _fix_56, self.wait(1e3), self.init56)

    @property
    def n_rep(self):
        return self._sequencer.n_rep

    @n_rep.setter
    def n_rep(self, n_rep):
        self._sequencer.n_rep = n_rep

    def generalized_init(self):
        '''
        load all qubits
        '''
        if self.init_done == False:
            self.add(self.init12)
            self.add(self.init3)
            self.add(self.init3)
            self.add(self.init56)
            self.add(self.init4)
            
            self.PSB_calls[0] += 3
            self.PSB_calls[1] += 2
            self.init_done = True

    def generalized_read(self):
        if self.read_done == False:
            self.add(self.read12)
            self.add(self.read3)
            self.add(self.read56)
            self.add(self.read4)
            self.PSB_calls[0] += 2
            self.PSB_calls[1] += 2
            self.read_done = True

    def init(self,*qubits):
        '''
        auto-init qubits

        Args:
            *qubits (int) : unpacked list of numbers of the qubits to initialize (e.g. init 1,3,5,6)
        '''
        if self.mode == MODES.FAST:
            qubits = np.asarray(qubits, dtype=int)
            qubits[qubits == 12] = 0
            qubits[qubits == 4] = 100

            qubits = np.sort(qubits)
            qubits[qubits == 0] = 12
            qubits[qubits == 100] = 4

            for q in qubits:
                if q == 3: 
                    if not any(q in [1,2,12] for q in qubits): self.add(self.init12)
                    self.PSB_calls[0] += 1
                if q == 4: 
                    if not any(q in [5,6,56] for q in qubits): self.add(self.init56)
                    self.PSB_calls[1] += 1
                self.add(getattr(self, f'init{q}'))
                if q<=3 or q == 12:
                    self.PSB_calls[0] += 1
                else:
                    self.PSB_calls[1] += 1
        else:
            self.generalized_init()
        
    def read(self,*qubits):
        '''
        auto_read_qubits
        '''
        if self.mode == MODES.FAST:
            qubits = np.asarray(qubits, dtype=int)
            qubits[qubits == 12] = 0
            qubits[qubits == 4] = 100
            qubits = np.sort(qubits)
            qubits[qubits == 0] = 12
            qubits[qubits == 100] = 4

            for q in qubits:
                if q == 3: 
                    if not any(q in [12] for q in qubits): self.add(self.read12)
                    self.PSB_calls[0] += 1
                if q == 4: 
                    if not any(q in [56] for q in qubits): self.add(self.read56)
                    self.PSB_calls[1] += 1
                self.add(getattr(self, f'read{q}'))

                if q<=3 or q == 12:
                    self.PSB_calls[0] += 1
                else:
                    self.PSB_calls[1] += 1
        else:
            self.generalized_read()

    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        setattr(self, name, value)

    @property
    def sequencer(self):
        gates, _311113, ST_anti_12, ST_anti_12_tc_high, ST_anti_56, ST_anti_56_tc_high, vSD1_threshold, vSD2_threshold  = variables()
        scaler = .8
        ST_anti_12 = tuple(np.asarray(ST_anti_12)*scaler*-1)
        ST_anti_56 = tuple(np.asarray(ST_anti_56)*scaler*-1)
        print(self.PSB_calls)
        for i in range(self.PSB_calls[0]):
            self.add_func(do_READ_12, meas=None, ramp = 1e3*1/scaler, t_measure=4e3*1/scaler, anti_crossing=ST_anti_12, debug=True)
        for i in range(self.PSB_calls[1]):
            self.add_func(do_READ_56, meas=None, ramp = 1e3*1/scaler, t_measure=4e3*1/scaler, anti_crossing=ST_anti_56, debug=True)

        return self._sequencer
    
    def add(self, *args, **kwargs):
        self._sequencer.add(*args, **kwargs)

    def add_func(self, func, *args, **kwargs):
        seg = self._sequencer._get_segment()
        func(seg, *args, **kwargs)

    def get_seg(self):
        return self._sequencer._get_segment()


if __name__ == '__main__':
    from core_tools.data.SQL.connect import set_up_local_storage
    set_up_local_storage("xld_user", "XLDspin001", "vandersypen_data", "6dot", "XLD", "6D2S - SQ21-1-2-10-DEV-1")

    from pulse_templates.demo_pulse_lib.virtual_awg import get_demo_lib
    from pulse_lib.configuration.physical_channels import digitizer_channel, digitizer_channel_iq
    from core_tools.drivers.M3102A import DATA_MODE, OPERATION_MODES
    from pulse_lib.segments.utility.measurement_converter import measurement_converter
    import pulse_lib.segments.utility.looping as lp

    pulse = get_demo_lib('six')

    s = six_dot_sample(pulse)
    seg = s.get_seg()
    # s.init12.build(seg)
    # s.init56_FPGA.build(seg)
    s.q1.X90.build(seg)
    # s.read56.build(seg)
    # s.add(s.q6.X180 ,t_pulse = lp.linspace(10,3e3, 80,axis=0))
    # seq.add(s.q6.X90(lp.linspace(-0.5, 2*np.pi,50, axis=1)))
    
    # s.read(45)

    # gates, _311113, ST_anti_12, ST_anti_12_tc_high, ST_anti_56, ST_anti_56_tc_high, vSD1_threshold, vSD2_threshold  = variables()
    # scaler = .8
    # ST_anti_12 = tuple(np.asarray(ST_anti_12)*scaler*-1)
    # ST_anti_56 = tuple(np.asarray(ST_anti_56)*scaler*-1)
    # PSB_calls = [2,0]
    # for i in range(PSB_calls[0]):
    #     do_READ_12(seg, meas=None, ramp = 1e3*1/scaler, t_measure=4e3*1/scaler, anti_crossing=ST_anti_12, debug=True)
    # for i in range(PSB_calls[1]):
    #     do_READ_56(seg, meas=None, ramp = 1e3*1/scaler, t_measure=4e3*1/scaler, anti_crossing=ST_anti_56, debug=True)


    plot_seg(seg)



# pxi_triggers = [
#     SD1.SD_TriggerExternalSources.TRIGGER_PXI6,
#     SD1.SD_TriggerExternalSources.TRIGGER_PXI7,
# ]

# # configure PXI trigger in
# for awg in awgs:
#     with awg._lock:
#         for pxi in pxi_triggers:
#             check_error(awg.awg.FPGATriggerConfig(
#                 pxi,
#                 SD1.SD_FpgaTriggerDirection.IN,
#                 SD1.SD_TriggerPolarity.ACTIVE_LOW,
#                 SD1.SD_SyncModes.SYNC_NONE,
#                 0))

 

# # configure PXI trigger out
# for pxi in pxi_triggers:
#     check_error(dig.SD_AIN.FPGATriggerConfig(
#         pxi,
#         SD1.SD_FpgaTriggerDirection.INOUT,
#         SD1.SD_TriggerPolarity.ACTIVE_LOW,
#         SD1.SD_SyncModes.SYNC_NONE,
#         0))

 
# #### After the experiment: disable PXI output
# for pxi in pxi_triggers:
#     check_error(dig.SD_AIN.FPGATriggerConfig(
#         pxi,
#         SD1.SD_FpgaTriggerDirection.IN,
#         SD1.SD_TriggerPolarity.ACTIVE_LOW,
#         SD1.SD_SyncModes.SYNC_NONE,
#         0))

 
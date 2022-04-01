from pulse_templates.oper.operators import wait, jump, add_stage
from pulse_templates.utility.oper import add_block, add_ramp

import pulse_lib.segments.utility.looping as lp

from dev_V2.six_qubit_QC_v2.VAR import variables

# def PSB_read_multi_12(segment, measurement, gates, t_ramp, t_read, p_0, p_1, p_2, disable_trigger=False):
#     '''
#     pulse able to perform a psb readout

#     Args:
#         segment (segment_container) : segment to which to add this stuff
#         gates (tuple<str>) : plunger gate names
#         t_ramp (double) : time to linearly ramp trought the anticrossing
#         t_read (double) : readout time
#         p_0 (tuple <double>) : starting point
#         p_1 (tuple<double>) : point after the anticrossing, where the readout should happen.
#         disable_trigger (bool) : disable triggerig for digitizer, only for debuggig.
#     '''
#     # pulse towards the window and stay for the measurment time
#     _311113_high_tc = p_0
#     _311113_high_tc(2) = 50
#     # ST_anti_12_tc_high = p_1
#     ST_anti_12_tc_high(2) = 50
#     add_ramp(segment, t_ramp, gates, p_0, p_1)
#     add_block(segment, 40, gates, p_1)
    
#     if disable_trigger != True:
#         measurement.build(segment)
#         segment.M_SD2.add_marker(0, t_read)
#         segment.M_SD1.add_marker(0, t_read)
#     add_block(segment, t_read, gates, p_1)
    
#     add_ramp(segment, 100 , gates, p_1, ST_anti_12_tc_high)
#     add_ramp(segment, 500, gates, ST_anti_12_tc_high, _311113_high_tc)    
#     add_ramp(segment, 500 , gates, _311113_high_tc, p_0)

def PSB_read_multi(segment, measurement, gates, t_ramp, t_read, p_0, p_1, p_2, disable_trigger=False):
    '''
    pulse able to perform a psb readout

    Args:
        segment (segment_container) : segment to which to add this stuff
        gates (tuple<str>) : plunger gate names
        t_ramp (double) : time to linearly ramp trought the anticrossing
        t_read (double) : readout time
        p_0 (tuple <double>) : starting point
        p_1 (tuple<double>) : point after the anticrossing, where the readout should happen.
        disable_trigger (bool) : disable triggerig for digitizer, only for debuggig.
    '''

    # pulse towards the window and stay for the measurment time
    add_ramp(segment,t_ramp, gates, p_0, p_1)
    if disable_trigger != True:
        measurement.build(segment)
        segment.M_SD2.add_marker(0, t_read)
        segment.M_SD1.add_marker(0, t_read)

    add_block(segment, t_read, gates, p_1)
    add_ramp(segment, 100, gates, p_1, p_2)  #added this and it made a difference
    add_ramp(segment, t_ramp, gates, p_2, p_0)  

def PSB_read_multi_2(segment, measurement, gates, t_ramp, t_read, p_0, p_1, p_2, disable_trigger=False):
    '''
    pulse able to perform a psb readout

    Args:
        segment (segment_container) : segment to which to add this stuff
        gates (tuple<str>) : plunger gate names
        t_ramp (double) : time to linearly ramp trought the anticrossing
        t_read (double) : readout time
        p_0 (tuple <double>) : starting point
        p_1 (tuple<double>) : point after the anticrossing, where the readout should happen.
        disable_trigger (bool) : disable triggerig for digitizer, only for debuggig.
    '''

    # pulse towards the window and stay for the measurment time
    add_ramp(segment,t_ramp, gates, p_0, p_2)
    add_ramp(segment, 20, gates, p_2, p_1)
    if disable_trigger != True:
        measurement.build(segment)
        segment.M_SD2.add_marker(0, t_read)
        segment.M_SD1.add_marker(0, t_read)

    add_block(segment, t_read, gates, p_1)
    add_ramp(segment, 20, gates, p_1, p_2)  #added this and it made a difference
    add_ramp(segment, t_ramp, gates, p_2, p_0)  

def do_READ_12(segment, meas, ramp = 2e3, t_measure=2e3, anti_crossing = None,debug=False):
    gates, _311113, ST_anti_12, ST_anti_12_tc_high, ST_anti_56, ST_anti_56_tc_high, vSD1_threshold, vSD2_threshold = variables()

    if anti_crossing is not None:
        ST_anti_12 = anti_crossing

    PSB_read_multi(segment, meas, gates, ramp, t_measure, _311113, ST_anti_12,ST_anti_12_tc_high, disable_trigger=debug)

def do_READ_56(segment, meas, ramp = 2e3, t_measure=2e3, anti_crossing = None,debug=False):
    gates, _311113, ST_anti_12, ST_anti_12_tc_high, ST_anti_56, ST_anti_56_tc_high, vSD1_threshold, vSD2_threshold = variables()
    if anti_crossing is not None:
        ST_anti_56 = anti_crossing
        ST_anti_56_tc_high =  anti_crossing

    PSB_read_multi_2(segment,meas, gates, ramp,  t_measure, _311113, ST_anti_56, ST_anti_56_tc_high, disable_trigger=debug)

if __name__ == '__main__':
    from core_tools.data.SQL.connect import set_up_local_storage
    set_up_local_storage("xld_user", "XLDspin001", "vandersypen_data", "6dot", "XLD", "6D2S - SQ21-XX-X-XX-X")
    gates, _311113, ST_anti_12, ST_anti_12_tc_high, ST_anti_56, ST_anti_56_tc_high, vSD1_threshold, vSD2_threshold = variables()

    print(gates)
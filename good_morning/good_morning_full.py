from core_tools.utility.variable_mgr.var_mgr import variable_mgr
from dev_V2.six_qubit_QC.system import MODES

var_mgr = variable_mgr()

####################
# General settings #
####################

var_mgr.n_rep = 2000 # maybe 5000/10000 for paper data
var_mgr.sample_mode = MODES.FULL #options MODES.FULL / MODES.FAST
plotting_enabled = True

###########
# imports #
###########

from good_morning.calibrations.SD_calib import SD1_calibration, SD2_calibration
from good_morning.calibrations.calib_PSB import PSB_calibration
from good_morning.calibrations.PSB_calib import PSB12_calibration, PSB56_calibration

from good_morning.calibrations.calib_resonance import res_calib
from good_morning.calibrations.calib_phases import phase_calib
from good_morning.calibrations.calib_allXY import allXY

from good_morning.calibrations.calib_crot_pi import CROT_pi_calib
from good_morning.calibrations.calib_crot import CROT_calib, crot_calib_freq, crot_calib_time

from good_morning.calibrations.calib_cphase import cphase_ZZ_calib, cphase_ZI_IZ_cal
from good_morning.calibrations.calib_J_alpha import calib_J_alpha

################
# SD + PSB cal #
################

SD1_calibration()
SD2_calibration()

PSB_calibration(12, 2, plot=plotting_enabled)
PSB_calibration(56, 2, plot=plotting_enabled)

##############
# qubit 1256 #
##############

res_calib(1,plot=plotting_enabled)
res_calib(2,plot=plotting_enabled)
res_calib(5,plot=plotting_enabled)
res_calib(6,plot=plotting_enabled)

allXY(1, plot=plotting_enabled)
allXY(2, plot=plotting_enabled)
allXY(5, plot=plotting_enabled)
allXY(6, plot=plotting_enabled)

############
# qubit 34 #
############
crot_calib_freq(23)
crot_calib_time(23)

CROT_calib(45,2,1,plot=plotting_enabled)

res_calib(3,plot=plotting_enabled)
res_calib(4,plot=plotting_enabled)
allXY(3, plot=plotting_enabled)
allXY(4, plot=plotting_enabled)

############################
# single qubit xtalk calib #
############################

phase_calib(1, 'q2.X', 'q2.mX', plot=plotting_enabled)
phase_calib(1, 'q3.X', 'q3.mX', plot=plotting_enabled)
phase_calib(1, 'q4.X', 'q4.mX', plot=plotting_enabled)
phase_calib(1, 'q5.X', 'q5.mX', plot=plotting_enabled)
phase_calib(1, 'q6.X', 'q6.mX', plot=plotting_enabled)

phase_calib(2, 'q1.X', 'q1.mX', plot=plotting_enabled)
phase_calib(2, 'q3.X', 'q3.mX', plot=plotting_enabled)
phase_calib(2, 'q4.X', 'q4.mX', plot=plotting_enabled)
phase_calib(2, 'q5.X', 'q5.mX', plot=plotting_enabled)
phase_calib(2, 'q6.X', 'q6.mX', plot=plotting_enabled)

phase_calib(3, 'q1.X', 'q1.mX', plot=plotting_enabled)
phase_calib(3, 'q2.X', 'q2.mX', plot=plotting_enabled)
phase_calib(3, 'q4.X', 'q4.mX', plot=plotting_enabled)
phase_calib(3, 'q5.X', 'q5.mX', plot=plotting_enabled)
phase_calib(3, 'q6.X', 'q6.mX', plot=plotting_enabled)

phase_calib(4, 'q1.X', 'q1.mX', plot=plotting_enabled)
phase_calib(4, 'q2.X', 'q2.mX', plot=plotting_enabled)
phase_calib(4, 'q3.X', 'q3.mX', plot=plotting_enabled)
phase_calib(4, 'q5.X', 'q5.mX', plot=plotting_enabled)
phase_calib(4, 'q6.X', 'q6.mX', plot=plotting_enabled)

phase_calib(5, 'q1.X', 'q1.mX', plot=plotting_enabled)
phase_calib(5, 'q2.X', 'q2.mX', plot=plotting_enabled)
phase_calib(5, 'q3.X', 'q3.mX', plot=plotting_enabled)
phase_calib(5, 'q4.X', 'q4.mX', plot=plotting_enabled)
phase_calib(5, 'q6.X', 'q6.mX', plot=plotting_enabled)

phase_calib(6, 'q1.X', 'q1.mX', plot=plotting_enabled)
phase_calib(6, 'q2.X', 'q2.mX', plot=plotting_enabled)
phase_calib(6, 'q3.X', 'q3.mX', plot=plotting_enabled)
phase_calib(6, 'q4.X', 'q4.mX', plot=plotting_enabled)
phase_calib(6, 'q5.X', 'q5.mX', plot=plotting_enabled)

############################
# two qubit ZZ/IZ/ZI calib #
############################

cphase_ZZ_calib(12, False, plot=plotting_enabled) # pi on other qubit flips readout, so False
cphase_ZZ_calib(23, True , plot=plotting_enabled)
cphase_ZZ_calib(34, True , plot=plotting_enabled)
cphase_ZZ_calib(45, True , plot=plotting_enabled)
cphase_ZZ_calib(56, False, plot=plotting_enabled) # pi on other qubit flips readout, so False

cphase_ZI_IZ_cal(12, 1, expected_outcome = 0, plot=plotting_enabled)
cphase_ZI_IZ_cal(12, 2, expected_outcome = 1, plot=plotting_enabled)
cphase_ZI_IZ_cal(23, 2, expected_outcome = 0, plot=plotting_enabled)
cphase_ZI_IZ_cal(23, 3, expected_outcome = 0, plot=plotting_enabled)
cphase_ZI_IZ_cal(34, 3, expected_outcome = 0, plot=plotting_enabled)
cphase_ZI_IZ_cal(34, 4, expected_outcome = 0, plot=plotting_enabled)
cphase_ZI_IZ_cal(45, 4, expected_outcome = 1, plot=plotting_enabled)
cphase_ZI_IZ_cal(45, 5, expected_outcome = 0, plot=plotting_enabled)
cphase_ZI_IZ_cal(56, 5, expected_outcome = 0, plot=plotting_enabled)
cphase_ZI_IZ_cal(56, 6, expected_outcome = 1, plot=plotting_enabled)

#########################
# two qubit xtalk calib #
#########################

phase_calib(3, 'q12.cphase',  plot=plotting_enabled)
phase_calib(4, 'q12.cphase',  plot=plotting_enabled)
phase_calib(5, 'q12.cphase',  plot=plotting_enabled)
phase_calib(6, 'q12.cphase',  plot=plotting_enabled)

phase_calib(1, 'q23.cphase',  plot=plotting_enabled)
phase_calib(4, 'q23.cphase',  plot=plotting_enabled)
phase_calib(5, 'q23.cphase',  plot=plotting_enabled)
phase_calib(6, 'q23.cphase',  plot=plotting_enabled)

phase_calib(1, 'q34.cphase',  plot=plotting_enabled)
phase_calib(2, 'q34.cphase',  plot=plotting_enabled)
phase_calib(5, 'q34.cphase',  plot=plotting_enabled)
phase_calib(6, 'q34.cphase',  plot=plotting_enabled)

phase_calib(1, 'q45.cphase',  plot=plotting_enabled)
phase_calib(2, 'q45.cphase',  plot=plotting_enabled)
phase_calib(3, 'q45.cphase',  plot=plotting_enabled)
phase_calib(6, 'q45.cphase',  plot=plotting_enabled)

phase_calib(1, 'q56.cphase',  plot=plotting_enabled)
phase_calib(2, 'q56.cphase',  plot=plotting_enabled)
phase_calib(3, 'q56.cphase',  plot=plotting_enabled)
phase_calib(4, 'q56.cphase',  plot=plotting_enabled)

############################
# CROT readout outer pairs #
############################

crot_calib_freq(12)
crot_calib_freq(56)

crot_calib_time(12)
crot_calib_time(56)

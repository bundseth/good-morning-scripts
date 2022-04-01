from core_tools.utility.variable_mgr.var_mgr import variable_mgr
import pulse_lib.segments.utility.looping as lp

gates =('vB0', 'vP1', 'vB1', 'vP2','vB2' ,'vP3', 'vB3', 'vP4' ,'vB4' ,'vP5', 'vB5' , 'vP6', 'vSD1_P' , 'vSD2_P' ,'vS2')

def variables():
	var_mngr = variable_mgr()

	vSD1_P_ST_readout =  var_mngr.PSB12_SD1
	vSD1_P_off = 0

	vSD2_P_ST_readout =  var_mngr.PSB56_SD2
	vSD2_P_off = 0

	vSD1_threshold = var_mngr.threshold_SD1
	vSD2_threshold = var_mngr.threshold_SD2

	vP1_anticrossing = var_mngr.PSB12_P1
	vB1_anticrossing = var_mngr.PSB12_B1
	vP2_anticrossing = var_mngr.PSB12_P2

	vP6_anticrossing = var_mngr.PSB56_P6
	vP5_anticrossing = var_mngr.PSB56_P5
	vB5_anticrossing = var_mngr.PSB56_B5

	_311113 = 	   (  0  ,  0   ,   0  ,  0   ,  0   ,  0  ,  0   ,   0   ,  0   ,  0  ,   0   ,   0  ,vSD1_P_off,vSD2_P_off,  0  )	#3131
	ST_anti_12 = (0, vP1_anticrossing, vB1_anticrossing, vP2_anticrossing, 0,0,0,0,0,0,0,0,vSD1_P_ST_readout,0,0)

	# ST_anti_12 = (-80, vP1_anticrossing+0.4+lp.linspace(-1, 1, 25, axis=0, name='vP1', unit='mV'), vB1_anticrossing+100, vP2_anticrossing+lp.linspace(-3, 3, 25, axis=1, name='vP2', unit='mV'), -80,0,0,0,0,0,0,0,vSD1_P_ST_readout,0,0)
	ST_anti_12_tc_high = (-40, vP1_anticrossing, 40, vP2_anticrossing, -40, 0,0,0,0,0,0,0,0,0,0)
	# ST_anti_56 = (0, 0, 0, 0, 0,0,0,0,0,vP5_anticrossing,vB5_anticrossing,vP6_anticrossing,0,vSD2_P_ST_readout,0)
	ST_anti_56 = (0, 0, 0, 0, 0,0,0,0,0,vP5_anticrossing,vB5_anticrossing+20,vP6_anticrossing,0,vSD2_P_ST_readout,0)

	ST_anti_56_tc_high = (0, 0, 0, 0, 0,0,0,0,0,vP5_anticrossing, vB5_anticrossing+40, vP6_anticrossing,0,0)

	return gates, _311113, ST_anti_12, ST_anti_12_tc_high, ST_anti_56, ST_anti_56_tc_high, vSD1_threshold, vSD2_threshold

# ST_anti_56 = (0, 0, 0, 0, 0,0,0,0,-80,vP5_anticrossing,vB5_anticrossing,vP6_anticrossing,0,vSD2_P_ST_readout,0)
# ST_anti_56_tc_high = (0, 0, 0, 0, 0,0,0,0,-100,vP5_anticrossing, 80, vP6_anticrossing+5,0,0)
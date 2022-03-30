from core_tools.utility.variable_mgr.var_mgr import variable_mgr

def get_target(obj, name):
	name = name.split('.')

	for operator in name:
		obj = getattr(obj, operator)
	
	return obj


def readout_convertor(readout_name):
	var_mgr = variable_mgr()
	if var_mgr.sample_mode ==-1:
		if readout_name == 'read1' or readout_name == 'read2' : 
			return 'read12'
		if readout_name == 'read5' or readout_name == 'read6' : 
			return 'read56'
	return readout_name
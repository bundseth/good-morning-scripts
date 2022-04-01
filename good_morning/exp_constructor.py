


class PSB_readout():
	def __init__(self):
		self._mode = 'ZZ'
		# single qubit rotations of the qubit
		self.gate_set_Q1 = None
		self.gate_set_Q2 = None
		# two qubit gate set
		self.gate_set_Q12 = None
		
		# general_info
		self._number_of_readout_calls = 1
		self.pre_select_enable = False

	@property
	def mode(self):
		return self._mode

	@mode.setter
	def mode(self, value):
		if value in ['ZZ', 'ZI', 'ZI']

	@property

class _6dot_exp():
	def __init__(self):


	def configure_exp(self, qubits = [1,2]):
		'''
		configure the readout configuration for the experiment to be run.
		'''
		self.qubits = [1,2]
		self.nrep = 500

		# derived properties ::
		self.n_qubits = 2
		self.phase = [var_mgr.SD1_rf_readout_phase]
		self.channels = [1,2]
		self.thresholds = ...

	def return_manual_experiment(self, readout_time, *sequences):
		run_PSB_exp(exp_name, sequences, 2e3, n_rep, 2, False, phase=var_mgr.RF_readout_phase, channels=[1,2], threshold=[vSD1_threshold, vSD1_threshold])

	def return_exeriment(self, manip_sequence):
		sequence = [self.init_sequence, manip_sequence, self.readout_sequence]
		run_PSB_exp(exp_name, sequence, self.t_read, n_rep, 2, False, phase=var_mgr.RF_readout_phase, channels=[1,2], threshold=[vSD1_threshold, vSD1_threshold])

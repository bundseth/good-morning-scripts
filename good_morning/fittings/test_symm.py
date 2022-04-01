from good_morning.fittings.fit_symmetry import fit_symmetry

if __name__ == '__main__':
	from core_tools.data.SQL.connect import set_up_local_storage
	set_up_local_storage("xld_user", "XLDspin001", "vandersypen_data", "6dot", "XLD", "6D2S - SQ21-XX-X-XX-X")

	from core_tools.data.ds.data_set import load_by_id
	ds = load_by_id(16789)
	x_axis = ds('read1').x()
	y_axis = ds('read1').y()
	probabilities = ds('read1').z()
	fit_symmetry(x_axis,y_axis,probabilities, True)
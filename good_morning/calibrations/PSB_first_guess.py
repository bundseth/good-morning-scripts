# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 14:09:43 2021

@author: V2
"""

#%%
from core_tools.sweeps.sweeps import do0D, do1D, do2D
from qcodes.instrument.specialized_parameters import ElapsedTimeParameter

from core_tools.GUI.keysight_videomaps.data_getter.scan_generator_Keysight import  construct_2D_scan_fast
from core_tools.GUI.keysight_videomaps.data_getter.scan_generator_Keysight import  construct_1D_scan_fast
from core_tools.utility.variable_mgr.var_mgr import variable_mgr
# from good_morning.calibrations.fitting import analysis

from core_tools.utility.combi_paramter import make_combiparameter,v_src_rescaler
from core_tools.data.ds.data_set import load_by_id
#%%
from good_morning.calibrations.ML_model_template import ConvolutionalModel
from good_morning.calibrations.ac_detection import find_anticrossing
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import numpy as np
import os, pathlib
import matplotlib.pyplot as plt

from good_morning.calibrations.guesser import Guesser
from good_morning.calibrations.guess_initial_PSB_point import guess_initial_PSB_point
import tkinter as tk
from tkinter.messagebox import askquestion

#%%
vP5_guess, vP6_guess = -26, -16

# Start: 45622(1638886240282974076)
# Failed: 45624(1638887355379974076), 45634(1638893048593974076), 45635(1638956568269974076)
   
root = tk.Tk()
msg = askquestion("Stop Liveplot", "Did you stop the liveplotting?")
root.destroy()

if msg == "yes":

	param = construct_2D_scan_fast('vP6', 30, 200, 'vP5', 30, 200, 10000, True, pulse, station.dig, 
		                           [3], 100e6, acquisition_delay_ns=0, enabled_markers=['M_SD2'],
		                           pulse_gates={'vP6': vP6_guess, 'vP5': vP5_guess})
	gate = ElapsedTimeParameter('time')
	gate_to_change ='vP5'
	gate_2 = getattr(station.gates, gate_to_change)
	start = gate_2() - 20
	stop = gate_2() + 20
	n_points = 50
	delay = 0.01
	ds = do2D(gate, -1, 1, 20, 0.01, gate_2, start, stop, n_points, delay, param, name = 'zoomed-in', reset_param=True ).run()


#%%
param = construct_2D_scan_fast('vP5', 100, 200, 'vP6', 100, 200,10000, True, pulse, station.dig, 
	                           [3], 100e6, acquisition_delay_ns=0, enabled_markers=['M_SD2'])
gate = ElapsedTimeParameter('time')
ds = do1D(gate, -1, 1, 20, 0, param, name = 'average' ).run()
#%%

#ds = load_by_id(45608)
P51, P61 = guesser.get_first_guess(ds)
P52, P62 = guesser.get_first_guess_filter(ds)

print(P51, P61)
print(P52, P62)

#%%
# P5, P6 = guesser.get_first_guess(ds)
# print(P5, P6)
# a, b = guesser.get_first_guess(ds)
# print(a, b)

# pred = find_anticrossing(np.mean(ds.m1(), axis = 0))

# def _transform_pred(pred, ds):
# 		inx, iny = ds.m1().shape[-2:]
# 		x, y = ds('ch3').k(), ds('ch3').j()
# 		predx, predy = pred

# 		diffx = abs(x[0]-x[-1])
# 		diffy = abs(y[0]-y[-1])

# 		return x[0] + diffx * (predx / inx), y[0] + diffy * (predy / iny)

# P6, P5 = _transform_pred(pred, ds)
# print(P6, P5)
#%%
param = construct_2D_scan_fast('vP6',20, 200, 'vP5', 20, 200,10000, True, pulse, station.dig, 
	                           [3], 100e6, acquisition_delay_ns=0, enabled_markers=['M_SD2'],
	                           pulse_gates={'vP6': P61, 'vP5': P51})
gate = ElapsedTimeParameter('time')
ds = do1D(gate, -1, 1, 20, 0, param, name = 'average' ).run()

#David_P5, David_P6= DAvid analysis(ds)
#var_mgr = variable_mgr()

#setattr(var_mgr, 'PSB56_P5', round(David_P5,6))

#%%
guesser = Guesser(location_anticrossing= "lower right")
guess = guess_initial_PSB_point(guesser, pulse, station)
print(guess)
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 18:40:22 2021

@author: V2
"""
import matplotlib.pyplot as plt
import numpy as np

import multiprocessing
#multiprocessing.freeze_support() # <- may be required on windows

def plot(datax, datay, name):
    x = datax
    y = datay**2
    plt.scatter(x, y, label=name)
    plt.legend()
    plt.show()

def multiP():
    for i in range(2):
        p = multiprocessing.Process(target=plot, args=(i, i, i))
        p.start()


# if __name__ == "__main__": 
#     multiP()
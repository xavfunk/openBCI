#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 16:29:34 2021

@author: xavfun
"""
import numpy as np
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt

data2 = np.loadtxt("testdata.csv", delimiter = ',')
eeg_data = data2[np.array([1, 2, 3, 4, 5, 6, 7, 8])]
#fftdata = np.real(fft(eeg_data, axis = 0))
fftdata = fft(eeg_data, axis = 0)


N = fftdata.shape[1]
T = 1/250
        
xf = fftfreq(N,T)[:N//2]

plt.plot(xf, 2.0/N * np.abs(fftdata[2][0:N//2]))
for i in range(len(eeg_data)):
    plt.plot(eeg_data[i])
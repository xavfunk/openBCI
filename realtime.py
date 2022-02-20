#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 16:17:28 2021

@author: xavfun

enter this in terminal 
python3.8 realtime.py --board-id 0 --serial-port /dev/ttyUSB0
sudo chmod a+rw /dev/ttyUSB0

# see on openBCI GUI how the plot should look like

"""

import argparse
import time
import logging
import random
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowError
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, WindowFunctions, DetrendOperations



class Graph:
    def __init__(self, board_shim):
        self.board_id = board_shim.get_board_id()
        self.board_shim = board_shim
        self.exg_channels = BoardShim.get_exg_channels(self.board_id)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.update_speed_ms = 4*1000
        self.window_size = 4
        self.num_points = self.window_size * self.sampling_rate

        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow(title='BrainFlow Plot',size=(800, 600))

        #self._init_timeseries()
        self._init_bands()

        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(self.update_speed_ms)
        QtGui.QApplication.instance().exec_()

        self.stack = np.zeros((8, 100))


    def _init_timeseries(self):
        self.plots = list()
        self.curves = list()
        for i in range(len(self.exg_channels)):
            p = self.win.addPlot(row=i,col=0)
            p.showAxis('left', False)
            p.setMenuEnabled('left', False)
            p.showAxis('bottom', False)
            p.setMenuEnabled('bottom', False)
            if i == 0:
                p.setTitle('TimeSeries Plot')
            self.plots.append(p)
            curve = p.plot()
            self.curves.append(curve)
            
    def _init_bands(self):
        
        #self.bands = np.zeros((24, 1000))
        N = 1000 #fftdata.shape[1]
        T = 1/self.sampling_rate
        
        xf = fftfreq(N,T)[:N//2]
        
        p = self.win.addPlot()
        self.band = p.plot()

    def update(self):
        data = self.board_shim.get_current_board_data(self.num_points)
        # get channels
        # fft the data
        fftdata = np.real(fft(data, axis = 0))
        print(fftdata.shape)
        #plt.plot(fftdata)
        #print(self.exg_channels)
        
        N = fftdata.shape[1]
        T = 1/self.sampling_rate
        
        xf = fftfreq(N,T)[:N//2]
        
        
        avg_bands = [0, 0, 0, 0, 0]
        for count, channel in enumerate(self.exg_channels):
            # plot timeseries
            DataFilter.detrend(data[channel], DetrendOperations.CONSTANT.value)
            # DataFilter.perform_bandpass(data[channel], 
            #                             self.sampling_rate, 
            #                             51.0, 
            #                             100.0, 
            #                             2,
            #                             FilterTypes.BUTTERWORTH.value, 
            #                             0)
            # DataFilter.perform_bandpass(data[channel], self.sampling_rate, 51.0, 100.0, 2,
            #                             FilterTypes.BUTTERWORTH.value, 0)
            DataFilter.perform_bandstop(data[channel], self.sampling_rate, 50.0, 4.0, 2,
                                        FilterTypes.BUTTERWORTH.value, 0)
            # DataFilter.perform_bandstop(data[channel], self.sampling_rate, 60.0, 4.0, 2,
            #                             FilterTypes.BUTTERWORTH.value, 0)
            #self.curves[count].setData(data[channel].tolist())
            
            #self.curves[count].setData(fftdata[channel].tolist())
        
        
        #self.band.setXRange(xf)
        self.band.setData(fftdata[2])
        #self.band.setData(data[0])
        print(fftdata[2])

        self.app.processEvents()


def main():
    BoardShim.enable_dev_board_logger()
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    # use docs to check which parameters are required for specific board, e.g. for Cyton - set serial port
    parser.add_argument('--timeout', type=int, help='timeout for device discovery or connection', required=False,
                        default=0)
    parser.add_argument('--ip-port', type=int, help='ip port', required=False, default=0)
    parser.add_argument('--ip-protocol', type=int, help='ip protocol, check IpProtocolType enum', required=False,
                        default=0)
    parser.add_argument('--ip-address', type=str, help='ip address', required=False, default='')
    parser.add_argument('--serial-port', type=str, help='serial port', required=False, default='')
    parser.add_argument('--mac-address', type=str, help='mac address', required=False, default='')
    parser.add_argument('--other-info', type=str, help='other info', required=False, default='')
    parser.add_argument('--streamer-params', type=str, help='streamer params', required=False, default='')
    parser.add_argument('--serial-number', type=str, help='serial number', required=False, default='')
    parser.add_argument('--board-id', type=int, help='board id, check docs to get a list of supported boards',
                        required=False, default=BoardIds.SYNTHETIC_BOARD)
    parser.add_argument('--file', type=str, help='file', required=False, default='')
    args = parser.parse_args()

    params = BrainFlowInputParams()
    params.ip_port = args.ip_port
    params.serial_port = args.serial_port
    params.mac_address = args.mac_address
    params.other_info = args.other_info
    params.serial_number = args.serial_number
    params.ip_address = args.ip_address
    params.ip_protocol = args.ip_protocol
    params.timeout = args.timeout
    params.file = args.file

    try:
        board_shim = BoardShim(args.board_id, params)
        board_shim.prepare_session()
        board_shim.start_stream(450000, args.streamer_params)
        g = Graph(board_shim)
    except BaseException as e:
        logging.warning('Exception', exc_info=True)
    finally:
        logging.info('End')
        if board_shim.is_prepared():
            logging.info('Releasing session')
            board_shim.release_session()


if __name__ == '__main__':
    main()

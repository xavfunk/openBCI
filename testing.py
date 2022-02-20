#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 15:04:13 2021

@author: xavfun

run this in terminal before:
sudo chmod a+rw /dev/ttyUSB0

then, run:
python3.8 testing.py --board-id 0 --serial-port /dev/ttyUSB0

board channels as found out with board.get_xy_channels

package_num:0
EXG:        [1, 2, 3, 4, 5, 6, 7, 8]; ['Fp1', 'Fp2', 'C3', 'C4', 'P7', 'P8', 'O1', 'O2']
accel:      [9, 10, 11]
analog:     [19, 20, 21] 
timestamp:  22
other:      [12, 13, 14, 15, 16, 17, 18]
marker:     23

"""

import argparse
import time
import numpy as np
import matplotlib.pyplot as plt
import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, WindowFunctions, DetrendOperations


def main():
    BoardShim.enable_dev_board_logger()

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
                        required=True)
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
    board = BoardShim(args.board_id, params)
    board.prepare_session()
    
    print(board.get_sampling_rate(0))
    sampling_rate = board.get_sampling_rate(0)
    # board.start_stream () # use this for default options
    print("starting stream")
    board.start_stream(10000, args.streamer_params)
    print('sleep')
    time.sleep(15)
    #data = board.get_current_board_data (256) # get latest 256 packages or less, doesnt remove them from internal buffer
    print('get_data')
    data = board.get_board_data()  # get all data and remove it from internal buffer
    print(data.shape)
    print("current board data is: ", board.get_current_board_data(10), board.get_current_board_data(10).shape)
    board.stop_stream()
    board.release_session()

    # preprocessing
    # for count, channel in enumerate(board.get_exg_channels(0)):
    #     #DataFilter.detrend(data[channel], DetrendOperations.CONSTANT.value)
    #     DataFilter.perform_bandpass(data[channel], 
    #                                          sampling_rate, 
    #                                          51.0, 
    #                                          100.0, 
    #                                          2,
    #                                          FilterTypes.BUTTERWORTH.value, 
    #                                          0)
    #     DataFilter.perform_bandpass(data[channel], sampling_rate, 51.0, 100.0, 2,
    #                                          FilterTypes.BUTTERWORTH.value, 0)
    #     DataFilter.perform_bandstop(data[channel], sampling_rate, 50.0, 4.0, 2,
    #                                        FilterTypes.BUTTERWORTH.value, 0)
    #     DataFilter.perform_bandstop(data[channel], sampling_rate, 60.0, 4.0, 2,
    #                                          FilterTypes.BUTTERWORTH.value, 0)

    print(data.shape)
    print(board.get_eeg_channels(0))
    np.savetxt("testdata.csv", data, delimiter = ',')
    
    
if __name__ == "__main__":
    main() #--board-id 0 --serial-port /dev/ttyUSB0
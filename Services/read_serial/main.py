import serial
import os
import time
import queue
import threading
import logging
import numpy as np
from datetime import datetime
from lib import setup_logging

# Setup as environment variable
WRITE_FILE_DURATION=5
ESTIMATED_DURATION=60

class FetchData:

    def __init__(self, logger):
        self.logger = logger
        self.serial = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)
        self.publisher = None
        self.stopped = False
        self.dataqueue = queue.Queue()
        # TODO implement cython arrays to boost the efficiency
        self.datapoints = []
        self.cwd = os.path.dirname(__file__)
        
    def save_data(self):
        self.logger.info("Started saving data thread")
        while True:
            time.sleep(1)
            while not self.dataqueue.empty():
                datapoints = self.dataqueue.get()
                filename = str(self.cwd) + "/" + datetime.now().strftime("%A_%d_%B_%Y_%H_%M_%S") + ".csv"
                np.savetxt(filename, datapoints, newline="\n", fmt='%s')
                self.logger.debug("Saved batched data")

    def read_data(self):
        self.logger.info("Started reading data thread")
        while True:
            start_time = time.time()
            elapsed_time = 0
            while elapsed_time <= WRITE_FILE_DURATION:
                val = self.serial.readline().decode('utf-8').rstrip()
                self.datapoints.append(val)
                elapsed_time = time.time() - start_time
            self.dataqueue.put(self.datapoints)
            self.datapoints = []
            self.logger.debug("Sent batched data to queue")
            if self.stopped:
                return
    
    def run(self):
        self.logger.info("Started reading serial service")
        self.readthread = threading.Thread(target=self.read_data)
        self.savethread = threading.Thread(target=self.save_data)
        self.readthread.setDaemon(True)
        self.savethread.setDaemon(True)
        self.readthread.start()
        self.savethread.start()
        self.readthread.join()
        
    def stop(self):
        self.logger.info("Stopped Service")
        self.stopped = True

def main(logger):
    fetch_data = FetchData(logger = logger)
    fetch_data.run()
    time.sleep(ESTIMATED_DURATION)
    fetch_data.stop()
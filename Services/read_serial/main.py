import serial
import time
import queue
import threading
import logging
import numpy as np
from datetime import datetime

# Values are in seconds
RECORD_DURATION = 5
TOTAL_DURATION = 60

class FetchData:

    def __init__(self):
        # TODO implement cython arrays to boost the efficiency
        self.setup_logging()
        try:
            self.serial = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)
        except Exception as e:
            self.logger.error(e)
            raise e

        self.publisher = None
        self.stopped = False
        self.dataqueue = queue.Queue()
        self.datapoints = []

    def setup_logging(self):
        # TODO add in utils
        self.logger = logging.getLogger('FETCHDATA')
        self.logger.setLevel(logging.INFO)

        fileHandler = logging.FileHandler('readserial.log')
        fileHandler.setLevel(logging.INFO)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.INFO)

        self.logger.addHandler(fileHandler)
        self.logger.addHandler(consoleHandler)

        formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')
        consoleHandler.setFormatter(formatter)
        fileHandler.setFormatter(formatter)
        
    def save_data(self):
        self.logger.info("Started saving data thread")
        while True:
            time.sleep(1)
            while not self.dataqueue.empty():
                datapoints = self.dataqueue.get()
                filename = datetime.now().strftime("%A_%d_%B_%Y_%H_%M_%S") + ".csv"
                np.savetxt(filename, datapoints, newline="\n", fmt='%s')
                self.logger.info("Saved batched data")

    def read_data(self):
        self.logger.info("Started reading data thread")
        while True:
            start_time = time.time()
            elapsed_time = 0
            while elapsed_time <= RECORD_DURATION:
                val = self.serial.readline().decode('utf-8').rstrip()
                self.datapoints.append(val)
                elapsed_time = time.time() - start_time
            self.dataqueue.put(self.datapoints)
            self.datapoints = []
            self.logger.info("Sent batched data to queue")
            if self.stopped:
                return
    
    def run(self):
        self.logger.info("Started reading serial service")
        self.savethread = threading.Thread(target=self.save_data)
        self.readthread = threading.Thread(target=self.read_data)
        self.savethread.setDaemon(True)
        self.readthread.setDaemon(True)
        self.readthread.start()
        self.savethread.start()
        self.readthread.join()
        
    def stop(self):
        self.stopped = True

fetch_data = FetchData()
fetch_data.run()
time.sleep(TOTAL_DURATION)
fetch_data.stop()
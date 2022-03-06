import serial
import os
import time
import queue
import threading
import numpy as np
from datetime import datetime
from lib import setup_logging
from publisher import TestPublisher

# Setup as environment variable
WRITE_FILE_DURATION=60
ESTIMATED_DURATION=86400

class FetchData:

    def __init__(self, logger):
        """"""
        self.logger = logger
        self.serial = serial.Serial(port='/dev/ttyACM0', baudrate=9600)
        self.publisher = TestPublisher(logger = self.logger)
        self.running = True
        self.dataqueue = queue.Queue()
        # TODO implement cython arrays to boost the efficiency
        self.datapoints = []
        self.cwd = os.path.dirname(__file__)

    def save_data(self):
        self.logger.info("Started saving data thread")
        while self.running:
            time.sleep(1)
            while not self.dataqueue.empty():
                datapoints = self.dataqueue.get()
                filename = str(self.cwd) + "/" + datetime.now().strftime("%A_%d_%B_%Y_%H_%M_%S") + ".csv"
                np.savetxt(filename, datapoints, newline="\n", fmt='%s')
                self.logger.debug("Saved batched data")

    def read_data(self):
        self.logger.info("Started reading data thread")
        while self.running:
            start_time = time.time()
            elapsed_time = 0
            while elapsed_time <= WRITE_FILE_DURATION:
                try:    
                    val = self.serial.readline().decode('utf-8').rstrip()
                except UnicodeDecodeError as e:
                    self.logger.error(e)
                    val = 0.0
                except ValueError as e:
                    self.logger.error(e)
                    val = 0.0
                self.datapoints.append(val)
                self.publisher.run(val)
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
        self.running = False
        raise UserWarning("Stopped Service")



def main(logger):
    fetch_data = FetchData(logger=logger)
    fetch_data.run()
    time.sleep(ESTIMATED_DURATION)
    fetch_data.stop()

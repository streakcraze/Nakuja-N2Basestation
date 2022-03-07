import serial
import os
import time
import queue
import json
import threading
import numpy as np
from datetime import datetime
from lib import setup_logging
from publisher import TestPublisher

# Setup as environment variable
WRITE_FILE_DURATION=60
ESTIMATED_DURATION=120

class FetchData:

    def __init__(self, logger):
        """"""
        self.logger = logger
        self.serial = None
        self.find_serial()
        self.publisher = TestPublisher(logger = self.logger)
        self.running = False
        self.dataqueue = queue.Queue()
        # TODO implement cython arrays to boost the efficiency
        self.datapoints = []
        self.cwd = os.path.dirname(__file__)
        self.filename = str(self.cwd) + "/" + datetime.now().strftime("%A_%d_%B_%Y_%H_%M_%S") + ".csv"

    def find_serial(self):
        SERIAL_PORTS = ['/dev/ttyUSB1', '/dev/ttyUSB0', '/dev/ttyACM1', '/dev/ttyACM0']
        for i in SERIAL_PORTS:
            try:
                self.serial = serial.Serial(port=i, baudrate=9600)
            except serial.serialutil.SerialException as e:
                self.logger.error(e)
            else:
                break
    
    def check_logging(self):
        count = 0
        while True:
            try:
                message = json.loads(str(self.publisher.check_message()))
                if str(message['data']['action']) == "Started logging" and str(message['data']['logging status']) == "True":
                    break
            except json.decoder.JSONDecodeError as e:
                if count == 0:
                    self.logger.error("Check logging error: {}".format(e))
                    count = count + 1
            time.sleep(1)
        self.running = True
        return True

    def save_data(self):
        self.logger.info("Started saving data thread")
        while self.running:
            time.sleep(1)
            while not self.dataqueue.empty():
                datapoints = self.dataqueue.get()
                maximum_val = max(datapoints)
                with open(self.filename, "a+") as f:
                    for i in datapoints:
                        f.write("{}\n".format(i))
                self.logger.debug("Saved batched data")
                new_filename = str(self.cwd) + "/" + str(maximum_val) + "_" + datetime.now().strftime("%A_%d_%B_%Y_%H_%M_%S") + ".csv"
                os.rename(self.filename, new_filename)
                self.filename = new_filename
                if not self.running:
                    return

    def read_data(self):
        self.logger.info("Started reading data thread")
        self.serial.reset_input_buffer()
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
                if elapsed_time == 0:
                    self.logger.info("Inserting the first value")
                self.datapoints.append(val)
                self.publisher.run(val)
                elapsed_time = time.time() - start_time
            self.dataqueue.put(self.datapoints)
            self.datapoints = []
            self.logger.debug("Sent batched data to queue")
            if not self.running:
                return

    def run(self):
        self.logger.info("Started reading serial service")
        self.readthread = threading.Thread(target=self.read_data)
        self.savethread = threading.Thread(target=self.save_data)
        self.loggingthread = threading.Thread(target=self.check_logging)
        self.stopthread = threading.Thread(target=self.stop)
        self.readthread.setDaemon(True)
        self.savethread.setDaemon(True)
        self.loggingthread.setDaemon(True)
        self.stopthread.setDaemon(True)
        self.readthread.start()
        self.savethread.start()
        self.loggingthread.start()
        self.stopthread.start()
        self.readthread.join()

    def stop(self):
        count = 0
        while True:
            try:
                message = json.loads(str(self.publisher.check_message()))
                if str(message['data']['action']) == "Stopped logging" and str(message['data']['logging status']) == "False":
                    self.logger.info("Stopped Service")
                    raise UserWarning("Stopped Service")
                    break
            except json.decoder.JSONDecodeError as e:
                if count == 0:
                    self.logger.error("Check logging error: {}".format(e))
                    count = count + 1
            time.sleep(1)
        self.running = False
        self.readthread.join()
        self.savethread.join()
        return True



def main(logger):
    fetch_data = FetchData(logger=logger)
    while True:
        if fetch_data.check_logging() == True:
            break
    fetch_data.run()
    time.sleep(ESTIMATED_DURATION)
    fetch_data.stop()

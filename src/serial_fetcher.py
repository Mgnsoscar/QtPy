from __future__ import annotations
from typing import *
import serial.tools.list_ports

class SerialDevice(serial.Serial):

    def __init__(self, baudrate: int, port: Optional[str] = None, timeout: Optional[int] = None ) -> None:
        """
        Initialize a serial device. Open said device if the port is found and available.
        :param baudrate:
        :param port:
        :param timeout:
        """

        # Init self as a serial.Serial object
        super().__init__(port = port, baudrate = baudrate, timeout = timeout)

        # Try to open the serial device. If no ports have been found, leave it unopened.
        try:

            self.open()

        except:

            pass

    def readSerial(self, sensors: Optional[list[str]] = None, printToConsole: bool = False) -> dict:
        """
        Reads the serial stream and fetches the most recently measured values. The serial format must be "NameOfSensor1:value, NameOfSensor2:value,... "
        :param sensors: If not None, a list with the names of sensor to be read from. Default is None, meaning all values are read.
        :param printToConsole: True if fetched sensor values are to be printed to console. False by default.
        :return: Dictionary of values from the serial stream. Keys are the sensor names. If no sensor data is found, the dictionary is empty.
        """
        # Buffer to store incomplete lines
        buffer = ''

            # Read bytes from the serial port
        data = self.read(self.in_waiting or 1).decode()
        print(data)
            # Concatenate the received bytes to the buffer
        buffer += data
            
            # Split the buffer by newline characters
        lines = buffer.split('\n')
        values = {}
            # Process complete lines
        for line in lines[:-1]:
            if line.startswith("Sensor1:"):
                sensors = line.split(",")
                for sensor in sensors:
                    pair = sensor.split(":")
                    values[pair[0].strip()] = float(pair[1].strip())
                print(values)
                return values
            else:
                return
        # Store the incomplete line back to the buffer
        buffer = lines[-1]
                        
    def newBaudrate(self, newBaudrate: int) -> None:
        """
        Defines a new baudrate
        :param newBaudrate: The new baudrate.
        """

        self.baudrate = newBaudrate

    def newPort(self, newPort: str) -> None:
        """
        Chooses a new port as input.
        :param newPort: Thw name of the new port.
        """
        self.port = newPort
        self.open()

    @staticmethod
    def fetchPorts() -> list[str]|None:
        """
        Retrieve a list with names of available ports.
        :return: List of available port names. None if no ports are available.
        """

        # Fetch available ports
        ports       =   serial.tools.list_ports.comports()
        portsList   =   []

        for port in ports:

            portsList.append( str( port ) )

        return portsList
    
    def portConnected(self) -> bool:
        """Returns true if the device is connected to a port.
        """
        return False if self.port == None else True
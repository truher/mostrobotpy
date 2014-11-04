#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .interfaces import Accelerometer
from .spi import SPI
from .sensorbase import SensorBase

__all__ = ["ADXL345_SPI"]

class ADXL345_SPI(SensorBase):
    kPowerCtlRegister = 0x2D
    kDataFormatRegister = 0x31
    kDataRegister = 0x32
    kGsPerLSB = 0.00390625

    kAddress_Read = 0x80
    kAddress_MultiByte = 0x40

    kPowerCtl_Link = 0x20
    kPowerCtl_AutoSleep = 0x10
    kPowerCtl_Measure = 0x08
    kPowerCtl_Sleep = 0x04

    kDataFormat_SelfTest = 0x80
    kDataFormat_SPI = 0x40
    kDataFormat_IntInvert = 0x20
    kDataFormat_FullRes = 0x08
    kDataFormat_Justify = 0x04

    Range = Accelerometer.Range

    class Axes:
        kX = 0x00
        kY = 0x02
        kZ = 0x04

    def __init__(self, port, range):
        """Constructor. Use this when the device is the first/only device on
        the bus

        :param port: The SPI bus port.
        :param range: The range (+ or -) that the accelerometer will measure.
        """
        self.spi = SPI(port)
        self.spi.setClockRate(500000)
        self.spi.setMSBFirst()
        self.spi.setSampleDataOnFalling()
        self.spi.setClockActiveLow()
        self.spi.setChipSelectActiveHigh()

        # Turn on the measurements
        self.spi.write([self.kPowerCtlRegister, self.kPowerCtl_Measure])

        self.setRange(range)

        hal.HALReport(hal.HALUsageReporting.kResourceType_ADXL345,
                      hal.HALUsageReporting.kADXL345_SPI)

    # Accelerometer interface

    def setRange(self, range):
        """Set the measuring range of the accelerometer.

        :param range: The maximum acceleration, positive or negative, that
        the accelerometer will measure.
        """
        if range == self.k2G:
            value = 0
        elif range == self.k4G:
            value = 1
        elif range == self.k8G:
            value = 2
        elif range == self.k16G:
            value = 3
        else:
            value = 0

        self.spi.write([self.kDataFormatRegister,
                        self.kDataFormat_FullRes | value])

    def getX(self):
        """Get the x axis acceleration

        :returns: The acceleration along the x axis in g-forces
        """
        return self.getAcceleration(self.Axes.kX)

    def getY(self):
        """Get the y axis acceleration

        :returns: The acceleration along the y axis in g-forces
        """
        return self.getAcceleration(self.Axes.kY)

    def getZ(self):
        """Get the z axis acceleration

        :returns: The acceleration along the z axis in g-forces
        """
        return self.getAcceleration(self.Axes.kZ)

    def getAcceleration(self, axis):
        """Get the acceleration of one axis in Gs.

        :param axis: The axis to read from.
        :returns: Acceleration of the ADXL345 in Gs.
        """
        data = [(self.kAddress_Read | self.kAddress_MultiByte |
                 self.kDataRegister) + axis, 0, 0]
        data = self.spi.transaction(data)
        # Sensor is little endian... swap bytes
        rawAccel = (data[2] << 8) | data[1]
        return rawAccel * self.kGsPerLSB

    def getAccelerations(self):
        """Get the acceleration of all axes in Gs.

        :returns: X,Y,Z tuple of acceleration measured on all axes of the
            ADXL345 in Gs.
        """
        # Select the data address.
        data = [0] * 7
        data[0] = (self.kAddress_Read | self.kAddress_MultiByte |
                   self.kDataRegister)
        data = self.spi.transaction(data)

        # Sensor is little endian... swap bytes
        rawData = []
        for i in range(3):
            rawData.append((data[i*2+2] << 8) | data[i*2+1])

        return (rawData[0] * self.kGsPerLSB,
                rawData[1] * self.kGsPerLSB,
                rawData[2] * self.kGsPerLSB)

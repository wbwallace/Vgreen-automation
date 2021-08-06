""" vgreen commands
"""

from vgreenfunctions import crc16

ADDRESS = 0x15  # default address

COMMAND_ACK = 0x20
REPLY_ACK = 0x10

NACK_ERRORS = {
    0x01: "Command not recognized / illegal",
    0x02: "Operand out of allowed range",
    0x03: "Data out of range",
    0x04: "General failure: fault mode",
    0x05: "Incorrect command length",
    0x06: "Command cannot be executed now",
    0x09: "Buffer error (not used)",
    0x0A: "Running parameters incomplete (not used)",
}

SENSOR_FAULT_CODES = {
    0x21: "Software Overcurrent",
    0x22: "DC overvoltage",
    0x23: "DC under voltage",
    0x26: "Hardware overcurrent",
    0x2A: "Startup Failure",
    0x2D: "Processor – Fatal",
    0x2E: "IGBT over temperature",
    0x2F: "Loss of phase",
    0x30: "Low Power",
    0x31: "Processor - Registers",
    0x32: "Processor - Program counter",
    0x33: "Processor - Interrupt/Execution",
    0x34: "Processor - Clock",
    0x35: "Processor - Flash memory",
    0x36: "Ras Fault",
    0x37: "Processor - ADC",
    0x3C: "Keypad Fault",
    0x3D: "LVB Data Flash Fault",
    0x3E: "Comm Loss Fault- LVB & Drive",
    0x3F: "Generic Fault; any other code not listed",
    0x40: "Coherence Fault",
    0x41: "UL Fault",
    0x42: "SVRS Fault Type 1",
    0x43: "SVRS Fault Type 2",
    0x44: "SVRS Fault Type 13",
}

FUNCTION_CODES = {0x41:'Go', 0x42:'Stop', 0x43:'Status',
                  0x44: 'Set Demand', 0x45: 'Read Sensor',
                  0x46: 'Read Identification',
                  0x64: 'Configuration Read/Write', 0x65: 'Store Configuration' }

# If there is a message error the pump replies with the MSB of the function byte set
FUNCTION_CODES.update((code|0x80,'Message Error') for code in FUNCTION_CODES)

class Message:
    def __init__(
        self,
        address=ADDRESS,
        function=None,
        ack=COMMAND_ACK,
        msglength=0,    # bytes
        data=None,  # b'' ???
        datalength=0,
        crc_lo=None,
        crc_hi=None,
    ):
        self.address = address
        self.function = function
        self.ack = ack
        self.msglength = msglength
        self.data = data
        self.data = data
        self.datalength = datalength
        if ack == COMMAND_ACK:
            crc_lo, crc_hi = self.calc_crc16()
        self.crc_lo = crc_lo
        self.crc_hi = crc_hi

    def calc_crc16(self):
        packet = [self.address,self.function,self.ack]
        if data:
            packet.append(data)
        return crc16(packet)

# Simple messages, no data, packet length = 5 bytes
# [ADDRESS][FUNCTION][ACK][CRCLO][CRCHI]
# GO cmd and reply [0x15][0x41][0x20]
GO = Message(function=0x41,ack=0x20,msglength=5)
STOP = Message(function=0x42,ack=0x20,msglength=5)
STATUS = Message(function=0x43,ack=0x20,msglength=5)
STORE_CONFIG = Message(function=0x65,ack=0x20,msglength=5))


class Message:
    def __init__(
        self,
        address=ADDRESS,
        function=None,
        ack=COMMAND_ACK,
        data=None,
        datalength=0,
    ):
        self.address = address
        self.function = function
        self.ack = ack
        self.data = data
        self.datalength = datalength

""" Data structures to encode vgreen commands
"""

from vgreenfunctions import crc16a as crc16
from operator import itemgetter
from collections import namedtuple

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

# {code: ['description', cmd_length, reply_length],...}
FUNCTION_CODES = {0x41:['Go',5,5], 0x42:['Stop',5,5], 0x43:['Status',5,6],
                  0x44: ['Set Demand',8,8], 0x45: ['Read Sensor',7,9],
                  0x46: ['Read Identification',None,None],
                  0x64: ['Configuration Read/Write',None,None], 0x65: ['Store Configuration',None,None]
                   }

# If there is a message error the pump replies with the MSB of the function byte set
FUNCTION_CODES.update((code|0x80,'Message Error') for code in FUNCTION_CODES)

# Message packet structure 
# 
# [Start]                [Address]  [Function] [ACK]    [Data]          [CRC]     [End]
# [3.5+ bytes idle time] [1 byte]   [1 byte]   [1 byte] [0 to 11 bytes] [2 bytes] [3.5+ bytes idle time]
# 
# Start: Minimum of 3.5 bytes times bus idle.
# Address: One byte address of the slave unit.
#          0x15 is the default address for the EPC ECM
#          0 is reserved for broadcast messages, motors will respond with their actual address.
#          Only odd addresses from 0x15 through 0x0F7 (and 0 for broadcast) are valid for this protocol
#          0xF8 through 0xFF are reserved for compatibility with MODBUS.
# Function/Command: One byte function code 0-0x7F.
#                   The Most Significant bit is set in an error reply - see NACK byte
# ACK: 0x20 in command from bus master,
#      0x10 in reply from motor
#      NACK error code - valid command and data block that cannot be processed for some reason
# Data: Zero up to 11 bytes of data depending on the function
# CRC: 2 byte CRC-16 as described in “MODBUS over Serial Line, V1.0, Modbus.org”
#      or see Error! Reference source not found.
# End: Minimum of 3.5 byte times bus idle.
#      In theory, end and start idle times can overlap leaving just
#      one idle time between message packets.
#      In practice, a message sent to the EPC ECM is followed by
#      a minimum of 4ms idle time (for 9600 baud rate) before the response is sent.
#      between 4ms (for 9600 baud rate) and 10ms (Except STORE command - 1 second)
# 
# Each message has a specified length which is dependent on the function
# Commands/Requests and replies can have different lengths.
# 
# The motor only responds to commands with its address
# and validates the message by checking its length and its CRC

# address,function,ack,data,crclo,crchi
msg_parts = itemgetter(0,1,2,slice(2,-2),-2,-1)
msgparts = itemgetter('addr','fn','ack','data','crclo','crchi')
Qmsg = namedtuple('Qmsg',['addr','fn','ack','data','crclo','crchi'])

class Message:
    def __init__(
        self,
        address=ADDRESS,
        function=None,
        ack=COMMAND_ACK,
        msglength=0,    # bytes
        data=None,  # b'' ???
        datalength=0,   # specify length for commands, check length for replies
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
        if self.data:
            packet.append(self.data)
        return crc16(packet)
    

# Simple messages, no data, packet length = 5 bytes
# [ADDRESS][FUNCTION][ACK][CRCLO][CRCHI]
# GO cmd and reply [0x15][0x41][0x20]
GO = Message(function=0x41,ack=0x20,msglength=5)
STOP = Message(function=0x42,ack=0x20,msglength=5)
STATUS = Message(function=0x43,ack=0x20,msglength=5)
STORE_CONFIG = Message(function=0x65,ack=0x20,msglength=5)


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

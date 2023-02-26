import argparse
from enum import Enum
from datetime import datetime
import socket
import struct

class Packet_Type(Enum):
    REQUEST = 'R'
    DATA = 'D'
    END = 'E'

# variables sent as command line arguments, initializing with dummy values
requester_port_number = 12345
sender_port_number = 12344
sequence_number = 0
data_length = 0
rate = 0

def command_line_args_range_checker(input):
    if (not input.isnumeric()):
        print('invalid int value: ', input)
    input = int(input)

    #TODO: uncomment this when ready
    # if input < 2050 or input > 65536:
    #     raise argparse.ArgumentTypeError('input value out of range')
    return input

def parse_command_line():
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--sender_port', help='port on which the sender waits for requests', required=True, type=command_line_args_range_checker, metavar="[2050,65536]")
    parser.add_argument('-g', '--requester_port', help='port on which the requester is waiting', required=True, type=command_line_args_range_checker, metavar="[2050,65536]")
    parser.add_argument('-r', '--rate', help='the number of packets to be sent per second', required=True, type=int)
    parser.add_argument('-q', '--seq_no', help='the initial sequence of the packet exchange', required=True)
    parser.add_argument('-l', '--length', help='length of the payload (in bytes) in the packets', required=True)

    args = parser.parse_args()

    return args

# print packet information before each packet is sent to the requester
def print_packet_information(requester_host_name, sequence_number, data, packet_type):
    if (packet_type == 'D'):
        print('DATA Packet')
    elif (packet_type == 'E'):
        print('END Packet')

    print('send time: ', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
    print('requester addr: ', requester_host_name)
    print('Sequence num: ', sequence_number)
    print('length: ', len(data))
    print('payload: ', data.decode('utf-8'))
    print()

# if file exists, read the file and return the file data
# if file does not exist, return -1
def read_file(file_name):
    try:
        with open(file_name, 'r') as reader:
            data = reader.read()
            return data
    except:
        return -1

def send_packet(data, packet_type, sequence_number, requester_host_name, requester_port_number):
    data = data.encode()

    # assemble udp header
    header = struct.pack('!cII', packet_type.encode('ascii'), sequence_number, len(data))
    packet_with_header = header + data

    sock.sendto(packet_with_header, (requester_host_name, requester_port_number))
    print_packet_information(requester_host_name, sequence_number, data, packet_type)

# parse_command_line_args()
# print('sender port number: ', sender_port_number)
# print('requester port number: ', requester_port_number)

args = parse_command_line()
print(args)

# create socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_host = socket.gethostname()
sock.bind((udp_host, sender_port_number))

# wait for request packet
print('waiting for requester to send the filename it wants to retrieve...')
packet_with_header, sender_address = sock.recvfrom(1024)
header = struct.unpack("!cII", packet_with_header[:9])
file_name = packet_with_header[9:]

print('received filename from requester: ', file_name.decode('utf-8'))

requester_host_name = socket.gethostname()

# read the file data
# TODO: if file does not exist (data == -1), then we send the END packet immediately
data = read_file(file_name)

print('-----------------------------------------------------------------------------')
print("sender's print information:")

# send data packets here
send_packet(data, Packet_Type.DATA.value, sequence_number, requester_host_name, requester_port_number)

# send end packet when done with data packets
sequence_number = 0
length = 0
send_packet('', Packet_Type.END.value, sequence_number, requester_host_name, requester_port_number)

print('-----------------------------------------------------------------------------')
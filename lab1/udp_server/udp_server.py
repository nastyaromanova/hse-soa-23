import os
import json
import socket
import struct
import threading 

from utils.get_env_vars import get_env_vars
from utils.get_method_object import get_method_object

from tester.data import data

env_vars = {
        'group' : '0.0.0.0',
        'port' : 2001,
        'method' : 'native',
        'multicast_group' : '224.0.0.1',
        'multicast_port' : 5000,
        'buffer_size' : 8192
    }

def Testing(method_object) -> str:
    method_object.serialize_and_deserialize(data)

    if method_object.error is None:
        return f'{method_object.name} - {method_object.size} - {method_object.serialize_time:.2f}ms - {method_object.deserialize_time:.2f}ms;\n'
    else:
        return method_object.error

def MessageSender(sock, method_object, address):
    response_data = Testing(method_object)
    sock.sendto(response_data.encode(), address)

def BaseProtocol(method_object, base_group, base_port, buffer_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((base_group, base_port))

    while True:
        _, address = sock.recvfrom(buffer_size)
        MessageSender(sock, method_object, address)

def MulticastProtocol(method_object, multicast_group, multicast_port, buffer_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((multicast_group, multicast_port))

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(multicast_group) + socket.inet_aton('0.0.0.0'))

    while True:
        _, address = sock.recvfrom(buffer_size)
        MessageSender(sock, method_object, address)

if __name__ == "__main__":
    env_vars = get_env_vars()

    method_object = get_method_object(env_vars['method'])
    base_thread = threading.Thread(target=BaseProtocol, args=(method_object, env_vars['group'], env_vars['port'], env_vars['buffer_size']))
    multicast_thread = threading.Thread(target=MulticastProtocol, args=(method_object, env_vars['multicast_group'], env_vars['multicast_port'], env_vars['buffer_size']))
    
    base_thread.start(), multicast_thread.start()

    base_thread.join(), multicast_thread.join()
import asyncio
import os
import json
import socket
import struct

from utils.get_env_vars import get_env_vars

env_vars = {
        'group' : '0.0.0.0',
        'port' : 2000,
        'method' : 'proxy',
        'multicast_group' : '224.0.0.1',
        'multicast_port' : 5000,
        'buffer_size' : 8192
    }

avaliable_methods = {
    'native' : ('native', 2001), 
    'json' : ('json', 2002), 
    'xml' : ('xml', 2003), 
    'protobuf' : ('protobuf', 2004), 
    'avro' : ('avro', 2005), 
    'yaml' : ('yaml', 2006), 
    'msgpack' : ('msgpack', 2007)
}


def MessageSender(sock, message, address, encoded=False):
    if encoded:
        sock.sendto(message, address)
    else:
        sock.sendto(message.encode(), address)

def BaseRequest(env_vars, sock, request, address):
    if isinstance(request['method'], str):
        request['method'] = [request['method']]

    for method in request['method']:
        method = method.lower()

        if method not in avaliable_methods.keys():
            MessageSender(sock, f'Bad request parameter "method" : {method}\n', address)
            continue

        method_address = avaliable_methods[method]

        inner_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        MessageSender(inner_sock, f'get_result', method_address)

        response, _ = inner_sock.recvfrom(env_vars['buffer_size'])
        MessageSender(sock, response, address, True)

def AllRequest(env_vars, sock, request, address):
    inner_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    inner_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))

    MessageSender(inner_sock, f'get_result', (env_vars['multicast_group'], env_vars['multicast_port']))

    for i in range(len(avaliable_methods)):
        response, _ = inner_sock.recvfrom(env_vars['buffer_size'])
        MessageSender(sock, response, address, True)


def MainProtocol(env_vars):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 2000))

    while True:
        json_request, address = sock.recvfrom(env_vars['buffer_size'])
        try:
            request = json.loads(json_request.decode('utf-8'))
        except json.decoder.JSONDecodeError:
            MessageSender(sock, f'Bad request format. It must be JSON\n', address)
        else:
            if 'type' not in request or request['type'] != 'get_result':
                MessageSender(sock, f'Bad request parameter "type"\n', address)
                continue
            
            if isinstance(request['method'], str) and request['method'].lower() == 'all':
                AllRequest(env_vars, sock, request, address)
            else:
                BaseRequest(env_vars, sock, request, address)

if __name__ == '__main__':
    env_vars = get_env_vars()
    MainProtocol(env_vars)
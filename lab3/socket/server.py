import socket
import threading

from interface import DataType, Interface


class Server:
    def __init__(self):
            self.Host = socket.gethostbyname(socket.gethostname())
            while True:
                try:
                    self.Port = int(input('Enter port number to run on: '))

                    self.Sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    self.Sock.settimeout(5)
                    self.Sock.bind((self.Host, self.Port))

                    break
                except:
                    print("Couldn't bind to that port")

            self.Clients = {}
            self.ClientCharId = {}
            threading.Thread(target=self.receive_data).start()

    def receive_data(self):   
        print('Running on host: '+ self.Host)
        print('Running on port: '+ str(self.Port))
        
        while True:
            try:
                data, addr = self.Sock.recvfrom(1025)
                message = Interface(datapacket=data)
                self.handle_message(message, addr)
            except socket.timeout:
                pass

    def handle_message(self, message, addr):
        print("Received {} message from {}".format(message.DataType, addr))
        if message.DataType == DataType.Handshake:
            if self.Clients.get(addr, None) is None:
                try:
                    name = message.data.decode(encoding='utf-8')

                    self.Clients[addr] = name
                    self.ClientCharId[addr] = len(self.Clients)

                    print('{} has connected on {}!'.format(name, addr))
                    ret = Interface(dataType=DataType.Handshake, data='ok'.encode(encoding='utf-8'))
                    self.Sock.sendto(ret.out(), addr)
                except:
                    pass
        elif message.DataType == DataType.Disconnect:
            name = message.data.decode(encoding='utf-8')

            if addr in self.Clients:
                del self.Clients[addr]
                del self.ClientCharId[addr]
                print('{} on {} successfully disconnected'.format(name, addr))
            
            ret = Interface(dataType=DataType.Disconnect, data='ok'.encode(encoding='utf-8'))
            self.Sock.sendto(ret.out(), addr)
        elif message.DataType == DataType.ClientData:
            self.broadcast(addr, message)
        else:
            print("Unknown datatype: {}".format(message.DataType))

    def broadcast(self, sentFrom, data):
        data.head = self.ClientCharId[sentFrom]
        for client in self.Clients:
            if client != sentFrom:
                try:
                    self.Sock.sendto(data.out(), client)
                except:
                    pass


if '___name___' == main:
    server = Server()
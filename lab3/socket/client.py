import os
import sys
import socket
import threading

import pyaudio

from interface import DataType, Interface


class Client:
    def __init__(self):
        self.Sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.Connected = False
        
        self.Username = input('Enter your name: ')
        
        while True:
            try:
                self.TargetHost = input('Enter target host of server: ')
                self.TargetPort = int(input('Enter target port of server: '))
                self.Server = (self.TargetHost, self.TargetPort)
                self.connect_to_server()
                break
            except:
                print("Couldn't connect to server")

        self.AudioFormat = pyaudio.paInt16
        self.ChunkSize = 512
        self.Channels = 1
        self.Rate = 20000

        self.audio = pyaudio.PyAudio()
        self.playing_stream = self.audio.open(
            format=self.AudioFormat, 
            channels=self.Channels, 
            rate=self.Rate, 
            output=True, 
            frames_per_buffer=self.ChunkSize
        )
        self.recording_stream = self.audio.open(
            format=self.AudioFormat, 
            channels=self.Channels, 
            rate=self.Rate, 
            input=True, 
            frames_per_buffer=self.ChunkSize
        )

        receive_thread = threading.Thread(target=self.receive_server_data).start()
        self.send_data_to_server()
        self.terminate()

    def receive_server_data(self):
        while self.connected:
            try:
                data, addr = self.Sock.recvfrom(1025)
                message = Interface(datapacket=data)
                if message.DataType == DataType.ClientData:
                    self.playing_stream.write(message.data)
            except:
                pass

    def connect_to_server(self):
        if self.connected:
            return True

        message = Interface(dataType=DataType.Handshake, data=self.Username.encode(encoding='utf-8'))
        self.Sock.sendto(message.out(), self.Server)

        data, addr = self.Sock.recvfrom(1025)
        datapack = Interface(datapacket=data)

        if addr == self.Server and datapack.DataType == DataType.Handshake and datapack.data.decode('utf-8') == 'ok':
            print('Connected to server successfully!')
            print('Press Control + C to disconnect')
            self.connected = True
        return self.connected

    def send_data_to_server(self):
        while self.connected:
            try:
                data = self.recording_stream.read(512)
                message = Interface(dataType=DataType.ClientData, data=data)
                self.Sock.sendto(message.out(), self.Server)
            except:
                self.disconnect()

    def disconnect(self):
        print("Try to disconnect")
        self.playing_stream.stop_stream()
        self.playing_stream.close()
        self.recording_stream.stop_stream()
        self.recording_stream.close()
        self.audio.terminate()

        message = Interface(dataType=DataType.Disconnect, data=self.Username.encode(encoding='utf-8'))
        self.Sock.sendto(message.out(), self.Server)
        self.connected = False

    @staticmethod
    def terminate():
        print("Succesfuly disconnected")
        os._exit(1)


if '___name___' == main:
    client = Client()
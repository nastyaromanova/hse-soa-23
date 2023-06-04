import os
import grpc
import random
import threading
import logging
import time
import sys, os

from proto import mafia_pb2
from proto import mafia_pb2_grpc
from proto.mafia_pb2 import User, AddUserRequest, BaseUserRequest, StatusCode

import configs.client_config as config

HOST = 'localhost'
PORT = 9000

class MafiaClient():
    def __init__(self):
        self.bot_mode = input('Do you want bot mode (yes/no): ') == 'yes'
        if not self.bot_mode:
            self.name = input('Enter your name: ')
        else: 
            self.name = 'Bot'
        with grpc.insecure_channel(HOST + ':' + str(PORT)) as channel:
            self.client_is_alive = True
            self.stub = mafia_pb2_grpc.MafiaStub(channel)
            self.user_id = self.add_user()
            self.lock = threading.Lock()
            self.messages = [
                mafia_pb2.CommunicationRequest(
                    user_id=self.user_id, data_type=mafia_pb2.CommunicationDataType.Value('HANDSHAKE_MESSAGE')),
            ]
            self.threads = [
                threading.Thread(target=lambda: self.server_communication()),
                threading.Thread(target=lambda: self.client_communication())
            ]
            for thread in self.threads:
                thread.start()
            for thread in self.threads:
                thread.join()

    def add_user(self):
        response = self.stub.add_user(AddUserRequest(name=self.name))
        user_id = response.data['user_id']
        return int(user_id)

    def client_communication(self):
        self.client_in_process = False

        if self.bot_mode:
            self.BotMode()
        else:
            while self.client_is_alive:
                if not self.client_in_process:
                    command = input('> ')
                    self._execute_command(command)
                    self.client_in_process = False

    def server_communication(self):
        def generate_messages():
            if self.messages:
                message = self.messages.pop(0)
                yield message
            else:
                yield mafia_pb2.CommunicationRequest(
                    user_id=self.user_id, data_type=mafia_pb2.CommunicationDataType.Value('EMPTY_MESSAGE'))

        while self.client_is_alive:
            time.sleep(0.8)
            try:
                responses = self.stub.init_communication_channel(generate_messages())
                try:
                    for response in responses:
                        if response.message or response.author:
                            print(f'{response.author}: {response.message}', end='\n> ')
                        else:
                            break
                except:
                    print('Game finished')
                    os._exit(0)
            except:
                print('Game finished')
                os._exit(0)

    def _execute_command(self, command_str):
        command_str = command_str.strip()
        if not command_str:
            return
        command = command_str.split()[0]
        args_str = ' '.join(command_str.split()[1:])

        if command == config.COMMAND_TYPES.get_users:
            response = self.stub.get_users(mafia_pb2.Empty())
            print(response.data['users'])
        elif command == config.COMMAND_TYPES.get_role:
            response = self.stub.get_role(mafia_pb2.BaseUserRequest(user_id=self.user_id))
            print(response.message)
        elif command == config.COMMAND_TYPES.help:
            response = self.stub.help(mafia_pb2.Empty())
            print(response.data['command_list'])
        elif command == config.COMMAND_TYPES.broadcast:
            message = args_str
            self.messages.append(
                mafia_pb2.CommunicationRequest(
                    user_id=self.user_id,
                    message=message,
                    data_type=mafia_pb2.CommunicationDataType.Value('BROADCAST_MESSAGE')))
        elif command == config.COMMAND_TYPES.finish_day:
            response = self.stub.finish_day(mafia_pb2.BaseUserRequest(user_id=self.user_id))
            print(response.message)
        elif command == config.COMMAND_TYPES.decision:
            target_str_id = args_str.strip()
            self.messages.append(
                mafia_pb2.CommunicationRequest(
                    user_id=self.user_id,
                    message=target_str_id,
                    data_type=mafia_pb2.CommunicationDataType.Value('DECISION_MESSAGE')))
            print(f'You decided to kill/check user {target_str_id}')
        elif command == config.COMMAND_TYPES.vote:
            target_str_id = args_str.strip()
            response = self.stub.vote_user(mafia_pb2.VoteUserRequest(user_id=self.user_id, voted_user_id=int(target_str_id)))
            self.messages.append(
                mafia_pb2.CommunicationRequest(
                    user_id=self.user_id,
                    message=target_str_id,
                    data_type=mafia_pb2.CommunicationDataType.Value('VOTE_MESSAGE')))
            print(f'You voted to kill user {target_str_id}')
        elif command == config.COMMAND_TYPES.verify:
            response = self.stub.verify(mafia_pb2.BaseUserRequest(user_id=self.user_id))
            print(response.message)
        elif command == config.COMMAND_TYPES.exit:
            response = self.stub.verify(mafia_pb2.BaseUserRequest(user_id=self.user_id))
            print(response.message)

    def BotMode(self):
        print(f'Start bot mode')
        while self.client_is_alive:
            with self.lock:
                try:
                    response = self.stub.get_valid_actions(mafia_pb2.BaseUserRequest(user_id=self.user_id))
                    valid = response.data['valid_actions'].split('\n')
                except:
                    valid = []

            random.shuffle(valid)

            if len(valid) != 0:
                print(f'Bot action: {valid[0]}')
                if not self.client_in_process:
                    print(f'> {valid[0]}')
                    self._execute_command(valid[0])
                    self.client_in_process = False

if __name__ == '__main__':
    logging.basicConfig()
    try:
        client = MafiaClient()
    except:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
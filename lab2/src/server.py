import grpc
import threading
import time
import random
from concurrent import futures
import logging
import sys, os

from proto import mafia_pb2
from proto import mafia_pb2_grpc

import configs.server_config as config
from configs.client_config import COMMANDS_LIST
from worker import validate_day, validate_night, validate_game_started, validate_game_not_started, validate_is_alive, validate_is_game, lock


class MafiaServicer(mafia_pb2_grpc.MafiaServicer):
    def __init__(self):
        self.Lock = threading.Lock()
        self.Interval = config.INTERVAL.day
        self.Users = {}
        self.Roles = {}
        self.VoteVotes = {}
        self.MafiaVotes = {}
        self.SheriffVotes = {}
        self.UserMessages = {}
        self.FinishDayVotes = {}
        self.ValidActions = {}
        self.IsGameStarted = False
        self.IsGameFinished = False
        self.DayNum = 0
        self.BotMode = False

    def send_message(self, message, author_id=None, to=None):
        if author_id == 'Admin':
            self.UserMessages[to].append(
                    mafia_pb2.CommunicationResponse(message=message, author='Admin'))
        else: 
            self.UserMessages[to].append(
                    mafia_pb2.CommunicationResponse(message=message, author=self.Users[author].name))


    @validate_is_game
    def init_communication_channel(self, request_iterator, context):
        user_id = None
        while True:
            for request in request_iterator:
                user_id = request.user_id
                if request.data_type == mafia_pb2.CommunicationDataType.Value('HANDSHAKE_MESSAGE'):
                    yield self._handle_handshake_message()
                elif request.data_type == mafia_pb2.CommunicationDataType.Value('BROADCAST_MESSAGE'):
                    yield self._handle_broadcast_message(request)
                elif request.data_type == mafia_pb2.CommunicationDataType.Value('DECISION_MESSAGE'):
                    yield self._handle_decision(request)
                elif request.data_type == mafia_pb2.CommunicationDataType.Value('EMPTY_MESSAGE'):
                    pass

            if user_id is not None and self.UserMessages[user_id]:
                message = self.UserMessages[user_id].pop(0)
                yield message
            else:
                yield mafia_pb2.CommunicationResponse()

    def _handle_handshake_message(self):
        return mafia_pb2.CommunicationResponse(message='You successfully joined Mafia game', author='Admin')

    @validate_is_alive
    def _handle_broadcast_message(self, request):
        cur_user_id = request.user_id
        message = request.message
        user_role = self.Roles[cur_user_id]
        filter_role = lambda _: True

        if self.Interval == config.INTERVAL.night:
            if user_role in [config.ROLES.mafia, config.ROLES.sheriff]:
                filter_role = lambda role: role == user_role
            else:
                return mafia_pb2.Response(
                    status=mafia_pb2.StatusCode.FORBIDDEN, message=f'You cannot message during night')
        for user_id in self.Users.keys():
            if cur_user_id != user_id and filter_role(self.Roles[user_id]):
                self.UserMessages[user_id].append(
                    mafia_pb2.CommunicationResponse(message=message, author=self.Users[cur_user_id].name))
        return mafia_pb2.CommunicationResponse()

    @validate_night
    @validate_is_alive
    def _handle_decision(self, request):
        print(f'Decision request from {request.user_id}: DECISION {request.message}')
        cur_user_id = request.user_id
        role = self.Roles[cur_user_id]
        if role in [config.ROLES.mafia, config.ROLES.sheriff]:
            target_user_id = int(request.message.strip())
            if target_user_id not in self.Users:
                return mafia_pb2.CommunicationResponse(message=f'No user with id {target_user_id}', author='Admin')
            elif (role == config.ROLES.mafia and self.MafiaVotes[cur_user_id] is not None) or \
                (role == config.ROLES.sheriff and self.SheriffVotes[cur_user_id] is not None):
                return mafia_pb2.CommunicationResponse(message='You already voted', author='Admin')
            elif self.Roles[target_user_id] == role:
                return mafia_pb2.CommunicationResponse(
                    message=f'User {target_user_id} has the same role with you', author='Admin')
            elif self.Roles[target_user_id] == config.ROLES.ghost:
                return mafia_pb2.CommunicationResponse(message=f'User {target_user_id} is already died', author='Admin')
            else:
                if role == config.ROLES.mafia:
                    votes = self.MafiaVotes
                elif role == config.ROLES.sheriff:
                    votes = self.SheriffVotes
                else:
                    raise ValueError('Invalid role')

                votes[cur_user_id] = target_user_id
                for user_id in self.Users.keys():
                    if user_id != cur_user_id and self.Roles[user_id] == role:
                        message = f'I vote for {target_user_id}'
                        self.UserMessages[user_id].append(
                            mafia_pb2.CommunicationResponse(message=message, author=self.Users[cur_user_id].name))
                return mafia_pb2.CommunicationResponse(message=f'You voted for user {target_user_id}', author='Admin')
        else:
            return mafia_pb2.CommunicationResponse(message='You are not mafia or sheriff', author='Admin')

    @validate_game_not_started
    @validate_is_game
    @lock
    def add_user(self, request, context):
        cur_user_id = len(self.Users)
        name = request.name
        while cur_user_id in self.Users.keys():
            cur_user_id += 1

        for user_id in self.Users.keys():
            message = f'User {name} has just been added'
            self.UserMessages[user_id].append(
                            mafia_pb2.CommunicationResponse(message=message, author='Admin'))
        

        self.Users[cur_user_id] = mafia_pb2.User(user_id=cur_user_id, name=name)
        self.Roles[cur_user_id] = config.ROLES.not_assigned
        self.UserMessages[cur_user_id] = []

        return mafia_pb2.Response(status=mafia_pb2.StatusCode.CREATED, data={'user_id': str(cur_user_id)})

    @validate_game_not_started
    @validate_is_game
    def delete_user(self, request, context):
        user_id = request.user_id
        if user_id in self.Users.keys():
            del self.Users[user_id]
            return mafia_pb2.DeleteUserResponse(status=mafia_pb2.StatusCode.OK)
        else:
            return mafia_pb2.Response(
                status=mafia_pb2.StatusCode.NOT_FOUND, message=f'No user with id {user_id}')

    def _is_alive(self, user_id):
        return self.Roles[user_id] != config.ROLES.ghost

    def get_users(self, request, context):
        users = '\n'.join([
            f'{user.name}, user_id: {user.user_id}, is alive: {self._is_alive(user.user_id)}'
            for user in self.Users.values()
        ])
        return mafia_pb2.Response(status=mafia_pb2.StatusCode.OK, data={'users': users})

    def get_role(self, request, context):
        role = self.Roles[request.user_id]
        return mafia_pb2.Response(status=mafia_pb2.StatusCode.OK, message=f'Your role is {role}')

    def help(self, request, context):
        return mafia_pb2.Response(status=mafia_pb2.StatusCode.OK, data=COMMANDS_LIST)

    def exit(self, request, context):
        self.Roles[request.user_id] = 'ghost'
        return mafia_pb2.Response(status=mafia_pb2.StatusCode.OK, message='You left the game')

    @validate_day
    @validate_game_started
    @validate_is_alive
    def verify(self, request, context):
        user_id = request.user_id
        if self.Roles[user_id] == 'sheriff':
            self._execute_sheriff_verify(user_id)
            return mafia_pb2.Response(status=mafia_pb2.StatusCode.OK, message=f'Result of the last check was published')
        else:
            return mafia_pb2.Response(status=mafia_pb2.StatusCode.FORBIDDEN, message=f'You are not sheriff')

    @lock
    def _assign_roles(self):
        assert len(self.Users) >= config.MIN_USERS_NUM

        shuffled_user_ids = random.sample(self.Users.keys(), len(self.Users))
        mafias_num = config.MAFIA_NUM

        for user_id in shuffled_user_ids[:mafias_num]:
            self.Roles[user_id] = config.ROLES.mafia

        self.Roles[shuffled_user_ids[mafias_num]] = config.ROLES.sheriff

        for user_id in shuffled_user_ids[mafias_num + 1:]:
            self.Roles[user_id] = config.ROLES.innocent

    @validate_day
    @validate_game_started
    @validate_is_alive
    @validate_is_game
    def vote_user(self, request, context):
        if self.DayNum > 1:
            user_id = request.user_id
            voted_user_id = request.voted_user_id
            if self.Roles[voted_user_id] == config.ROLES.ghost:
                return mafia_pb2.Response(
                    status=mafia_pb2.StatusCode.BAD_REQUEST,
                    message=f'User {voted_user_id} is already a ghost')
            elif user_id in self.Users.keys() and voted_user_id in self.Users.keys():
                self.VoteVotes[user_id] = voted_user_id
                return mafia_pb2.Response(status=mafia_pb2.StatusCode.OK, message='OK')
            else:
                return mafia_pb2.Response(status=mafia_pb2.StatusCode.BAD_REQUEST, message='Wrong user ids')
        else:
            return mafia_pb2.Response(
                status=mafia_pb2.StatusCode.BAD_REQUEST, message="You can't vote in the first day")

    def run(self):
        print('Run service')
        while True:
            if not self.IsGameStarted and (len(self.Users) >= config.MIN_USERS_NUM or self.BotMode == True):
                self._start_game()
                
            if self.IsGameStarted:
                if self._is_mafia_win() and not self.IsGameFinished:
                    self.IsGameFinished = True
                    for user_id in self.Users.keys():
                        mafias = [
                            user.name
                            for user in self.Users.values()
                            if self.Roles[user.user_id] == config.ROLES.mafia
                        ]
                        message = f'Mafia {mafias} win!'
                        self.UserMessages[user_id].append(
                            mafia_pb2.CommunicationResponse(message=message, author='Admin'))
                    time.sleep(len(self.Users))
                
                elif self._is_innocent_win() and not self.IsGameFinished:
                    self.IsGameFinished = True
                    for user_id in self.Users.keys():
                        innocentes = [
                            user.name
                            for user in self.Users.values()
                            if self.Roles[user.user_id] == config.ROLES.innocent or self.Roles[user.user_id] == config.ROLES.sheriff
                        ]
                        message = f'Innocentes {innocentes} win!'
                        self.UserMessages[user_id].append(
                            mafia_pb2.CommunicationResponse(message=message, author='Admin'))
                    time.sleep(len(self.Users))

                elif all(self.FinishDayVotes.values()) and self.Interval == config.INTERVAL.day:
                    if self.DayNum != 1:
                        self._kill_voted_user()
                    if not self._is_mafia_win() and not self._is_innocent_win():
                        self._start_night()

                elif all([x is not None for x in self.MafiaVotes.values()]) and all(
                    [x is not None for x in self.SheriffVotes.values()]) and \
                        self.Interval == config.INTERVAL.night:
                    print('Everybody voted, finish night')
                    self._start_day()

    @lock
    def _is_innocent_win(self):
        alive_mafia_count = 0
        for user_id in self.Users.keys():
            if self._is_alive(user_id):
                if self.Roles[user_id] == config.ROLES.mafia:
                    alive_mafia_count += 1
        return alive_mafia_count == 0


    @lock
    def _is_mafia_win(self):
        alive_mafia_count = 0
        alive_others_count = 0
        for user_id in self.Users.keys():
            if self._is_alive(user_id):
                if self.Roles[user_id] == config.ROLES.mafia:
                    alive_mafia_count += 1
                else:
                    alive_others_count += 1
        return alive_mafia_count >= alive_others_count

    def _start_game(self):
        print('Game started')
        self.IsGameStarted = True
        self._assign_roles()
        for user_id in self.Users.keys():
            message = f'Game has just started, your role is {self.Roles[user_id]}.'
            self.UserMessages[user_id].append(
                mafia_pb2.CommunicationResponse(message=message, author='Admin'))
            message = f"If you don't know commands type 'HELP' to see the list of them"
            self.UserMessages[user_id].append(
                mafia_pb2.CommunicationResponse(message=message, author='Admin'))
        self._start_day()
        

    @validate_day
    @validate_game_started
    @validate_is_alive
    @validate_is_game
    @lock
    def finish_day(self, request, context):
        cur_user_id = request.user_id
        print(f'Received VOTE for DAY FINISH from {cur_user_id}')
        if cur_user_id in self.Users.keys():
            self.FinishDayVotes[cur_user_id] = True
            for user_id in self.Users.keys():
                if user_id != cur_user_id:
                    message = f'User {cur_user_id} voted to finish game day'
                    self.UserMessages[user_id].append(
                        mafia_pb2.CommunicationResponse(message=message, author='Admin'))
            return mafia_pb2.Response(status=mafia_pb2.StatusCode.OK, message='Your vote has been counted')
        else:
            return mafia_pb2.Response(status=mafia_pb2.StatusCode.BAD_REQUEST, message='Wrong user id')
        

    @lock
    def _start_day(self):
        print('Started day')
        assert len(self.Users) >= config.MIN_USERS_NUM
        if self.DayNum != 0:
            self._execute_mafia_decision()
            self._execute_sheriff_decision()

        for user_id in self.Users.keys():
            message = f'Day started'
            self.UserMessages[user_id].append(
                mafia_pb2.CommunicationResponse(message=message, author='Admin'))

        self.Interval = config.INTERVAL.day
        self.DayNum += 1
        self.VoteVotes = {
            user_id: None for user_id in self.Users.keys() if self.Roles[user_id] is not config.ROLES.ghost
        }
        self.FinishDayVotes = {
            user_id: False for user_id in self.Users.keys() if self.Roles[user_id] is not config.ROLES.ghost
        }

        for user_id in self.Users.keys():
            self.ValidActions[user_id] = '\n'.join([
                    f'VOTE {vote_user_id}' 
                    for vote_user_id in self.Users.keys()
                    if vote_user_id != user_id and self.Roles[vote_user_id] is not config.ROLES.ghost
                ])
            if self.Roles[user_id] == 'sheriff':
                self.ValidActions[user_id] += '\nVERIFY'
            self.ValidActions[user_id] += '\nFINISH_DAY'

    def _execute_mafia_decision(self):
        mafia_votes = list(self.MafiaVotes.values())
        target_user_id = max(mafia_votes, key=mafia_votes.count)
        self.Roles[target_user_id] = config.ROLES.ghost

        for user_id in self.Users.keys():
            if user_id == target_user_id:
                message = f'Mafia killed you'
            else:
                message = f'Mafia killed user {target_user_id}'
            self.UserMessages[user_id].append(
                mafia_pb2.CommunicationResponse(message=message, author='Admin'))

    def _execute_sheriff_decision(self):
        sheriff_votes = list(self.SheriffVotes.values())
        target_user_id = max(set(sheriff_votes), key=sheriff_votes.count)

        for user_id in self.Users.keys():
            if self.Roles[user_id] == 'sheriff':
                if self.Roles[target_user_id] == config.ROLES.mafia:
                    message = f'You found mafia: user {target_user_id}'
                    self.UserMessages[user_id].append(
                        mafia_pb2.CommunicationResponse(message=message, author='Admin'))
                else:
                    message = f"You did't find mafia at night"            
                    self.UserMessages[user_id].append(
                        mafia_pb2.CommunicationResponse(message=message, author='Admin'))

    def _execute_sheriff_verify(self, sheriff_id):
        sheriff_votes = list(self.SheriffVotes.values())
        target_user_id = max(set(sheriff_votes), key=sheriff_votes.count)

        if self.Roles[target_user_id] == config.ROLES.mafia:
            for user_id in self.Users.keys():
                message = f'Sheriff {self.Users[sheriff_id].name} found mafia: user {target_user_id}'
                self.UserMessages[user_id].append(
                    mafia_pb2.CommunicationResponse(message=message, author='Admin'))
        else:
            message = f"You did't find mafia at the previous night"            
            self.UserMessages[sheriff_id].append(
                mafia_pb2.CommunicationResponse(message=message, author='Admin'))
        

    @lock
    def _start_night(self):
        print('Started night')
        self.MafiaVotes = {user_id: None for user_id in self.Users.keys() if self.Roles[user_id] == config.ROLES.mafia}
        self.SheriffVotes = {
            user_id: None for user_id in self.Users.keys() if self.Roles[user_id] == config.ROLES.sheriff
        }
        self.Interval = config.INTERVAL.night
        self.FinishDayVotes = {user_id: False for user_id in self.Users.keys()}
        for user_id in self.Users.keys():
            message = f'Night started'
            self.UserMessages[user_id].append(
                mafia_pb2.CommunicationResponse(message=message, author='Admin'))
            if self.Roles[user_id] == config.ROLES.mafia:
                message = f'Choose user to kill'
            elif self.Roles[user_id] == config.ROLES.sheriff:
                message = f'Choose user to check if mafia'
            else:
                message = f'You are just sleeping all the night'
            self.UserMessages[user_id].append(
                mafia_pb2.CommunicationResponse(message=message, author='Admin'))
                
        for user_id in self.Users.keys():
            if self.Roles[user_id] == 'sheriff':
                self.ValidActions[user_id] = '\n'.join([
                    f'DECISION {vote_user_id}' 
                    for vote_user_id in self.Users.keys() 
                    if self.Roles[vote_user_id] != 'sheriff' and self.Roles[vote_user_id] is not config.ROLES.ghost
                ])
            elif self.Roles[user_id] == 'mafia':
                self.ValidActions[user_id] = '\n'.join([
                    f'DECISION {vote_user_id}' 
                    for vote_user_id in self.Users.keys() 
                    if self.Roles[vote_user_id] != 'mafia' and self.Roles[vote_user_id] is not config.ROLES.ghost
                ])

    def _kill_voted_user(self):
        votes = list(self.VoteVotes.values())
        target_user_id = max(votes, key=votes.count)
        self.Roles[target_user_id] = config.ROLES.ghost

        for user_id in self.Users.keys():
            if user_id == target_user_id:
                message = 'Majority voted for you, you are a ghost now'
            elif target_user_id is None:
                message = 'Nobody was killed bu vote'
            else:
                message = f'User {target_user_id} was killed by votes'
            self.UserMessages[user_id].append(
                mafia_pb2.CommunicationResponse(message=message, author='Admin'))

    def get_valid_actions(self, response, context):
        valid_actions = self.ValidActions[response.user_id]
        return mafia_pb2.Response(status=mafia_pb2.StatusCode.OK, data={'valid_actions': valid_actions})


def serve(servicer):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mafia_pb2_grpc.add_MafiaServicer_to_server(servicer, server)
    server.add_insecure_port('[::]:9000')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    try:
        servicer = MafiaServicer()
        threads = [threading.Thread(target=lambda: serve(servicer)), threading.Thread(target=lambda: servicer.run())]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    except:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
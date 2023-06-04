from .utils import create_namedtuple_instance

COMMAND_TYPES = create_namedtuple_instance(
    'command_types',
    get_users='GET_USERS',
    get_role='GET_ROLE',
    help='HELP',
    broadcast='BROADCAST',
    finish_day='FINISH_DAY',
    decision='DECISION',
    vote='VOTE',
    verify='VERIFY',
    exit='EXIT')

COMMANDS_LIST = {'command_list' :
                    'GET_USERS - get list of users\n' \
                    'BROADCAST - send message to other users\n' \
                    'FINISH_DAY - vote for the end of the day\n' \
                    "DECISION - send mafias' or sheriffs' decisions\n" \
                    'VOTE - vote whom to kill during the day\n' \
                    "VERIFY – publish sheriff's mafia check\n" \
                    'EXIT – leave the game'}

MIN_USERS_NUM = 4
MAFIA_NUM = 1
from configs.utils import create_namedtuple_instance

ROLES = create_namedtuple_instance(
    'roles', mafia='mafia', sheriff='sheriff', innocent='innocent', ghost='ghost', not_assigned='not_assigned')

INTERVAL = create_namedtuple_instance('interval', day='day', night='night')

MIN_USERS_NUM = 4
MAFIA_NUM = 1
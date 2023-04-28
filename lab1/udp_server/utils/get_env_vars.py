import os

def get_var_by_name(varname):
    value = os.getenv(varname)
    if value is None:
        raise RuntimeError(f'Unknown environment variable {varname}.')
    return value

def get_env_vars():
    port = int(get_var_by_name('PORT'))
    method = get_var_by_name('METHOD')
    multicast_group = get_var_by_name('MULTICAST_GROUP')
    multicast_port = int(get_var_by_name('MULTICAST_PORT'))
    env_vars = {
        'group' : '0.0.0.0',
        'port' : port,
        'method' : method,
        'multicast_group' : multicast_group,
        'multicast_port' : multicast_port,
        'buffer_size' : 8192
    }
    return env_vars
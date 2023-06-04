import collections

def create_namedtuple_instance(name, **kwargs):
    return collections.namedtuple(name, kwargs.keys())(**kwargs)
import sys
import timeit
import ast

class Native:
    def __init__(self):
        self.name = 'Native'

        self.serialize_time = None
        self.deserialize_time = None
        self.size = None

        self.error = None

    def serialize(self, data : dict):
        return str(data)

    def deserialize(self, serialize_data):
        return ast.literal_eval(serialize_data)

    def checker(self, data, deserialize_data):
        if data != deserialize_data:
            self.error = f'Something went wrong during serialize/deserialize in method {self.name}\nInput data is {data}\nOutput data is {deserialize_data}\n'

    def serialize_and_deserialize(self, data : dict, num_iter=1000):
        self.error = None
        self.serialize_time = int(timeit.Timer(lambda: self.serialize(data)).timeit(number=num_iter) * 1_000_000 / num_iter) 
        serialize_data = self.serialize(data)

        self.size = sys.getsizeof(serialize_data)

        self.deserialize_time = int(timeit.Timer(lambda: self.deserialize(serialize_data)).timeit(number=num_iter) * 1_000_000 / num_iter)
        deserialize_data = self.deserialize(serialize_data)

        self.checker(data, deserialize_data)



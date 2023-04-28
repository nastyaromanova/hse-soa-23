import sys
import timeit

import google.protobuf.json_format
from tester.data_pb2 import MyData

class ProtoBuffer:
    def __init__(self):
        self.name = 'ProtoBuffer'

        self.serialize_time = None
        self.deserialize_time = None
        self.size = None

        self.error = None

    def serialize(self, data : dict):
        message = MyData()
        google.protobuf.json_format.ParseDict(data, message)
        return MyData.SerializeToString(message)

    def deserialize(self, serialize_data):
        message = MyData()
        message.ParseFromString(serialize_data)
        return google.protobuf.json_format.MessageToDict(message)

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




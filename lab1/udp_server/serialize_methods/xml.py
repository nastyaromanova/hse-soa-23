import sys
import timeit

import xmltodict
import dicttoxml
import xml.etree.ElementTree as ET

class XML:
    def __init__(self):
        self.name = 'XML'

        self.serialize_time = None
        self.deserialize_time = None
        self.size = None

        self.error = None

    def serialize(self, data : dict):
        return dicttoxml.dicttoxml(data)

    def clear_data(self, data):
        if data['@type'] == 'int':
            return int(data['#text'])
        if data['@type'] == 'float':
            return float(data['#text'])
        if data['@type'] == 'bool':
            if data['#text'] == 'true':
                return True
            return False
        if data['@type'] == 'str':
            return str(data['#text'])
        if data['@type'] == 'list':
            res = list()
            for value in data['item']:
                res.append(self.clear_data(value))
            return res
        if data['@type'] == 'dict':
            res = dict()
            for key, value in data.items():
                if key == '@type':
                    continue
                res[key] = self.clear_data(value)
            return res

    def deserialize(self, serialize_data):
        deserialize_data = xmltodict.parse(serialize_data)['root']
        deserialize_data['@type'] = 'dict'
        return self.clear_data(deserialize_data)


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




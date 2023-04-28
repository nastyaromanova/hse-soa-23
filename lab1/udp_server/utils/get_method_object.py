from serialize_methods.native import Native
from serialize_methods.xml import XML
from serialize_methods.json import JSON
from serialize_methods.protobuffer import ProtoBuffer
from serialize_methods.avro import Avro
from serialize_methods.yaml import YAML
from serialize_methods.msgpack import MsgPack

def get_method_object(method_name):
    if method_name == 'native':
        return Native()
    if method_name == 'xml':
        return XML()
    if method_name == 'json':
        return JSON()
    if method_name == 'protobuffer':
        return ProtoBuffer()
    if method_name == 'avro':
        return Avro()
    if method_name == 'yaml':
        return YAML()
    if method_name == 'msgpack':
        return MsgPack()
    raise RuntimeError(f'Unexpected method name – {method_name}.')

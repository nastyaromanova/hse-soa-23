import enum

class DataType(enum.Enum):
    ClientData = 1
    Handshake = 2
    Disconnect = 3


class Interface:
    CLIENT_DATA_MIN = 0
    CLIENT_DATA_MAX = 50
    HANDSHAKE = 51
    DISCONNECT = 52

    typeToOrd = {DataType.ClientData:CLIENT_DATA_MIN, DataType.Handshake:HANDSHAKE, DataType.Disconnect:DISCONNECT}
    ordToType = {v: k for k, v in typeToOrd.items()}

    def __init__(self, dataType=None, head=None, data=None, datapacket=None):
        if dataType is not None:
            self.head = Interface.typeToOrd[dataType]
        else:
            self.head = datapacket[0] if head is None else head
        self.data = datapacket[1:] if data is None else data
        self.DataType = Interface.getDataType(self.head)

    @staticmethod
    def getDataType(head):
        if head <= Protocol.CLIENT_DATA_MAX and head >= Protocol.CLIENT_DATA_MIN:
            return DataType.ClientData
        try:
            return Interface.ordToType[head]
        except:
            return None

    def out(self):
        bytearr = bytearray(b'')
        bytearr.append(self.head)
        return bytes(bytearr + self.data)
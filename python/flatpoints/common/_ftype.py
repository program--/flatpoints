from enum import Enum

class ftype(Enum):
    UNKNOWN = 0
    INT32 = 1
    INT64 = 2
    UINT32 = 3
    UINT64 = 4
    FLOAT32 = 5
    FLOAT64 = 6
    STRING = 7
    BOOL = 8

    def dump(self, data: list) -> bytes:
        if self.value == 7:
            return b''.join([f'{d}\0'.encode('utf-8') for d in data])
        else:
            if self.value == 1:
                fstr = 'l'
            elif self.value == 2:
                fstr = 'q'
            elif self.value == 3:
                fstr = 'Q'
            elif self.value == 4:
                fstr = 'L'
            elif self.value == 5:
                fstr = 'f'
            elif self.value == 6:
                fstr = 'd'
            elif self.value == 8:
                fstr = '?'
            else:
                raise TypeError(f'Type {self.value} is not dumpable')

            return struct.pack(f'<{len(data)}{fstr}', *data)

def get_ftype(obj: object) -> ftype:
    typeclass = type(obj)
    if typeclass is int:
        if obj < 0:
            return ftype.INT32 if obj.bit_length() < 33 else ftype.INT64
        else:
            return ftype.UINT32 if obj.bit_length() < 33 else ftype.UINT64
    elif typeclass is float:
        # TODO: Discern between float32 and float64
        return ftype.FLOAT64
    elif typeclass is str:
        return ftype.STRING
    elif typeclass is bool:
        return ftype.BOOL
    else:
        return ftype.UNKNOWN
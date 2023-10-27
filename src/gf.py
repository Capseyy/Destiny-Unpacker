import os,struct,binascii


def hex_to_little_endian(hex_string):
    little_endian_hex = bytearray.fromhex(hex_string)[::-1]
    return little_endian_hex
def get_uint16_big(file,offset):
    return int.from_bytes(file[offset:offset+2],"big")

def fill_hex_with_zeros(s, desired_length):
    return ("0"*desired_length + s)[-desired_length:]

def get_float32(file,offset):
    Dat=binascii.hexlify(bytes(file[offset:offset+4])).decode()
    flipped=binascii.hexlify(bytes(hex_to_little_endian(Dat))).decode('utf-8')
    return struct.unpack('!f', bytes.fromhex(flipped))[0]
def get_flipped_bin(h, length):
    if length % 2 != 0:
        print("Flipped bin length is not even.")
        return None
    return h[:length][::-1]


def mkdir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass


def get_uint32(hx, offset):
    return int.from_bytes(hx[offset:offset+4], byteorder='little')
def get_int32(hx, offset):
    return int.from_bytes(hx[offset:offset+4], byteorder='little')




def get_int16(hx, offset):
    return int.from_bytes(hx[offset:offset+2], byteorder='little')

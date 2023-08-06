
import binascii
def stripZeros(txt):
    temp=list(txt)
    count=0
    index=0
    print(temp)
    for char in temp:
        if char == "0":
            index+=1
            
        else:
            break
    return "".join(temp[index:])

def hex_to_little_endian(hex_string):
    little_endian_hex = bytearray.fromhex(hex_string)[::-1]
    return little_endian_hex

t=binascii.hexlify(bytes(hex_to_little_endian("0a01"))).decode()
print(stripZeros(t))


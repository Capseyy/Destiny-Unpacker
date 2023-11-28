import os,sys,binascii,gf,ast


def ReadIndexData(PrimitiveType,is32,IndexOffset,IndexCount,ind):
    IndexData=[]
    if PrimitiveType == 5:
        if is32 == False:
            triCount=0
            ind.seek(IndexOffset*2)
            Start=ind.tell()
            if binascii.hexlify(bytes(ind.read(2))).decode() != "ffff":
                ind.seek(ind.tell()-2)
            while (ind.tell()+4-Start) < (IndexCount*2):
                i1=binascii.hexlify(bytes(ind.read(2))).decode()
                i2=binascii.hexlify(bytes(ind.read(2))).decode()
                i3=binascii.hexlify(bytes(ind.read(2))).decode()
                if i3 == "ffff":
                    triCount=0
                    continue
                if i1 == "":
                    break
                if i2 == "":
                    break
                if i3 == "":
                    break
                i1=ast.literal_eval("0x"+gf.stripZeros(binascii.hexlify(bytes(gf.hex_to_little_endian(i1))).decode('utf-8')))
                i2=ast.literal_eval("0x"+gf.stripZeros(binascii.hexlify(bytes(gf.hex_to_little_endian(i2))).decode('utf-8')))
                i3=ast.literal_eval("0x"+gf.stripZeros(binascii.hexlify(bytes(gf.hex_to_little_endian(i3))).decode('utf-8')))
                if triCount % 2 == 0:
                    IndexData.append([i1,i2,i3])
                else:
                    IndexData.append([i2,i1,i3])
                ind.seek(ind.tell()-4)
                triCount+=1
                if len(IndexData) == IndexCount:
                    break
        else:
            triCount=0
            ind.seek(IndexOffset*4)
            Start=ind.tell()
            while (ind.tell()+8-Start) < (IndexCount*4):
                i1=binascii.hexlify(bytes(ind.read(4))).decode()
                i2=binascii.hexlify(bytes(ind.read(4))).decode()
                i3=binascii.hexlify(bytes(ind.read(4))).decode()
                if i3 == "ffffffff":
                    triCount=0
                    continue
                temp=[i1,i2,i3]
                if "" in temp:
                    break
                i1=ast.literal_eval("0x"+gf.stripZeros(binascii.hexlify(bytes(gf.hex_to_little_endian(i1))).decode('utf-8')))
                i2=ast.literal_eval("0x"+gf.stripZeros(binascii.hexlify(bytes(gf.hex_to_little_endian(i2))).decode('utf-8')))
                i3=ast.literal_eval("0x"+gf.stripZeros(binascii.hexlify(bytes(gf.hex_to_little_endian(i3))).decode('utf-8')))
                if triCount % 2 == 0:
                    IndexData.append([i1,i2,i3])
                else:
                    IndexData.append([i2,i1,i3])
                ind.seek(ind.tell()-8)
                triCount+=1
                if len(IndexData) == IndexCount:
                    break
    else:
        if is32 == False:
            ind.seek(IndexOffset*2)
            for j in range(0,int(IndexCount),3):
                s = binascii.hexlify(bytes(ind.read(6))).decode()
                Inds=[s[i:i+4] for i in range(0, len(s), 4)]
                if len(Inds) < 3:
                    break
                i1=ast.literal_eval("0x"+gf.stripZeros(binascii.hexlify(bytes(gf.hex_to_little_endian(Inds[0]))).decode('utf-8')))
                i2=ast.literal_eval("0x"+gf.stripZeros(binascii.hexlify(bytes(gf.hex_to_little_endian(Inds[1]))).decode('utf-8')))
                i3=ast.literal_eval("0x"+gf.stripZeros(binascii.hexlify(bytes(gf.hex_to_little_endian(Inds[2]))).decode('utf-8')))
                IndexData.append([i1,i2,i3])
        else:
            print(IndexOffset)
            ind.seek(IndexOffset*4)
            for j in range(0,int(IndexCount),3):
                if len(IndexData) >= (int(IndexCount/3)):
                    break
                i1=int.from_bytes(ind.read(4),"little")
                i2=int.from_bytes(ind.read(4),"little")
                i3=int.from_bytes(ind.read(4),"little")
                IndexData.append([i1,i2,i3])
    return IndexData
import os,sys

temp=os.getcwd()
temp=temp.split("\\")
output="/".join(temp[:len(temp)])
sys.path.append(output+"/ThirdParty")
custom_direc=output
import gf
import ExtractSingleEntry
from dataclasses import dataclass, fields, field
import numpy as np
from typing import List

import os
from ctypes import cdll, c_char_p, create_string_buffer
from Crypto.Cipher import AES
import binascii
import io
import fnmatch
import time
from ctypes import *
import bisect, sys, Model

oodlepath = "E:\oo2core_9_win64.dll" #Path to Oodle DLL in Destiny 2/bin/x64.dle DLL in Destiny 2/bin/x64.
def GeneratePackageCache():
    PackageCache=[]
    Packages=os.listdir(path)
    Packages.sort(reverse=True)
    usedIds=[]
    for File in Packages:
        temp=File.split("_")
        try:
            ID=ast.literal_eval("0x"+stripZeros(temp[len(temp)-2]))
        except SyntaxError:
            continue
        if ID not in usedIds:
            PackageCache.append([File,ID])
            usedIds.append(ID)
    #newPackageCache=[]
    #for Entry in newPackageCache:
    #    ID=Entry[0]
    PackageCache.sort(key=lambda x: x[1])
    return PackageCache

def hex_to_little_endian(hex_string):
    little_endian_hex = bytearray.fromhex(hex_string)[::-1]
    return little_endian_hex
def hex_to_big_endian(hex_string):
    return bytearray.fromhex(hex_string)
def GetPkgId(Hash):
    if (Hash & 0x01000000) != 0:
        return ((Hash >> 0xD) & 0x3FF) | 0x400
    else:
        return (Hash >> 0xD) & 0x3FF
def addNode( pScene, nodeName, **kwargs ):
    
    # Obtain a reference to the scene's root node.
    #scaling = kwargs["scaling"]
    location = kwargs["location"]
    newNode = fbx.FbxNode.Create( pScene, nodeName )
    newNode.LclScaling.Set(fbx.FbxDouble3(1, 1, 1))
    newNode.LclTranslation.Set(fbx.FbxDouble3(location[0]*1, location[1]*1, location[2]*1))
    return newNode

def ReadHash64():
    file=open(os.getcwd()+"/h64.txt","r")
    data=file.read()
    Hash64Data=data.split("\n")
    return Hash64Data
            

def Package_ID(Hash):
    ID = (Hash >> 13) & 0xFFF

    if (ID & 0x800) > 0 and (ID & 0x400) > 0:
        return ID & 0xBFF
    elif (ID & 0x400) == 0:
        return (ID & 0x3FF) | 0x400
    elif (ID & 0x200) == 0:
        return ID & 0x1FF
    elif (ID & 0x400) > 0:
        return ID & 0x3FF
    else:
        raise Exception("Unknown package encoding configuration.")
def Entry_ID(Hash):
    return Hash & 0x1FFF
def Hex_String(Num):
    Hex_Digits = "0123456789abcdef"
    return ''.join([
        Hex_Digits[(Num & 0xF000) >> 12],
        Hex_Digits[(Num & 0xF00) >> 8],
        Hex_Digits[(Num & 0xF0) >> 4],
        Hex_Digits[Num & 0xF]
    ])
def stripZeros(txt):
    if txt == "0000":
        return("0")
    elif txt == "00000000":
        return("0")
    elif txt == "00":
        return("0")
    else:
        temp=list(txt)
        count=0
        index=0
        #print(temp)
        for char in temp:
            if char == "0":
                index+=1
                
            else:
                break
        #print("".join(temp[index:]))
        return str("".join(temp[index:]))

def twos_complement(hexstr, bits):
    value = int(hexstr, 16)
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value
def convert(s):
    i = int(s, 16)                   # convert from hex to a Python int
    cp = pointer(c_int(i))           # make this into a c integer
    fp = cast(cp, POINTER(c_float))  # cast the int pointer to a float                                    # dereference the pointer, get the float pointer
    return fp.contents.value   

def binary_search_single(arr, x):
    low = 0
    high = len(arr) - 1
    mid = 0
 
    while low <= high:
 
        mid = (high + low) // 2
        if int(arr[mid]) < x:
            low = mid + 1
 
        # If x is smaller, ignore right half
        elif int(arr[mid]) > x:
            high = mid - 1
 
        # means x is present at mid
        else:
            return mid
    # If we reach here, then the element was not present
    return -1          
def binary_search(arr, x):
    low = 0
    high = len(arr) - 1
    mid = 0
 
    while low <= high:
 
        mid = (high + low) // 2
        if int(arr[mid][1]) < x:
            low = mid + 1
 
        # If x is smaller, ignore right half
        elif int(arr[mid][1]) > x:
            high = mid - 1
 
        # means x is present at mid
        else:
            return mid
    # If we reach here, then the element was not present
    return -1
def GetEntryA(path,PackageCache,Val):
    flipped=binascii.hexlify(bytes(hex_to_little_endian(Val))).decode('utf-8')
    new=int(ast.literal_eval("0x"+flipped))
    pkg=Hex_String(Package_ID(new))
    temp=ast.literal_eval("0x"+stripZeros(pkg))
    Index=binary_search(PackageCache,int(temp))
    Package=PackageCache[Index][0]
    ent=Hex_String(Entry_ID(new))
    EntryA=ExtractSingleEntry.GetEntryA(path,custom_direc,Package,ent)
    return EntryA
def binary_search2(arr, x):
    low = 0
    high = len(arr) - 1
    mid = 0
 
    while low <= high:
 
        mid = (high + low) // 2
        if int(arr[mid][0]) < x:
            low = mid + 1
 
        # If x is smaller, ignore right half
        elif int(arr[mid][0]) > x:
            high = mid - 1
 
        # means x is present at mid
        else:
            return mid
    # If we reach here, then the element was not present
    return -1
def ReadFloat32(Input):
    try:
        num=struct.unpack('!f', bytes.fromhex(binascii.hexlify(bytes(hex_to_little_endian(Input))).decode('utf-8')))[0]
    except struct.error:
        return 0
    else:
        return num
def DumpHash(path,PackageCache,Val):
    flipped=binascii.hexlify(bytes(hex_to_little_endian(Val))).decode('utf-8')
    new=int(ast.literal_eval("0x"+flipped))
    pkg=Hex_String(Package_ID(new))
    temp=ast.literal_eval("0x"+stripZeros(pkg))
    Index=binary_search(PackageCache,int(temp))
    Package=PackageCache[Index][0]
    ent=Hex_String(Entry_ID(new))
    ExtractSingleEntry.unpack_entry_ext(path,custom_direc+"/out",Package,ent)
def Hash64Search(Hash64Data,Input):
    Found=False
    ans=binary_search2(Hash64Data,int(Input))
    if str(ans) != "-1":
        Found=True
    if Found == True:
        return Hash64Data[ans][1]
    else:
        return False
def ParseMaterial(Material,outfile,H64Sort,path,PackageCache,name):
    DumpHash(path,PackageCache,Material)
    Header=binascii.hexlify(bytes(hex_to_little_endian(Material))).decode('utf-8')
    new=ast.literal_eval("0x"+Header)
    pkg = Hex_String(Package_ID(new))
    ent = Hex_String(Entry_ID(new))
    Bank=pkg+"-"+ent+".bin"
    MaterialData=open(custom_direc+"/out/"+Bank,"rb")
    MaterialData.seek(0x2C0)
    Offset=int.from_bytes(MaterialData.read(4),"little")
    MaterialData.seek(MaterialData.tell()-4+Offset)
    MatCount=int.from_bytes(MaterialData.read(4),"little")
    MaterialData.seek(MaterialData.tell()+12)
    PartMats=[]
    for i in range(MatCount):
        MaterialData.seek(MaterialData.tell()+16)
        Mat64=int.from_bytes(MaterialData.read(8),"little")
        Hash=Hash64Search(H64Sort,Mat64)
        if Hash != False:
            new=ast.literal_eval(Hash)
            pkg = Hex_String(Package_ID(new))
            ent = Hex_String(Entry_ID(new))
            Bank=pkg+"-"+ent
            PartMats.append(Bank)
    return PartMats
    


import ast,fbx,struct
from fbx import FbxManager
import FbxCommon
def Get32(path,Header,PackageCache):
    DumpHash(path,PackageCache,Header)
    Header=binascii.hexlify(bytes(hex_to_little_endian(Header))).decode('utf-8')
    new=ast.literal_eval("0x"+Header)
    pkg = Hex_String(Package_ID(new))
    ent = Hex_String(Entry_ID(new))
    Bank=pkg+"-"+ent+".bin"
    IHeader=open(custom_direc+"/out/"+Bank,"rb")
    IHeader.seek(0x1)
    is32=int.from_bytes(IHeader.read(1),"little")
    IHeader.close()
    if is32 == 1:
        return True
    else:
        return False
def GetVerts(path,Header,PackageCache,MeshScale):
    DumpHash(path,PackageCache,Header)
    Buffer=GetEntryA(path,PackageCache,Header)
    Header=binascii.hexlify(bytes(hex_to_little_endian(Header))).decode('utf-8')
    new=ast.literal_eval("0x"+Header)
    pkg = Hex_String(Package_ID(new))
    ent = Hex_String(Entry_ID(new))
    Bank=pkg+"-"+ent+".bin"
    VHeader=open(custom_direc+"/out/"+Bank,"rb")
    VBufferSize=int.from_bytes(VHeader.read(4),"little")
    Stride=int.from_bytes(VHeader.read(2),"little")
    Type=int.from_bytes(VHeader.read(2),"little")
    VHeader.close()
    new=ast.literal_eval(Buffer)
    pkg = Hex_String(Package_ID(new))
    ent = Hex_String(Entry_ID(new))
    Bank=pkg+"-"+ent+".bin"
    DumpHash(path,PackageCache,binascii.hexlify(bytes(hex_to_little_endian(Buffer[2:]))).decode('utf-8'))
    VBuffer=open(custom_direc+"/out/"+Bank,"rb")
    VertCount=0
    Verts=[]
    if Type == 1:
        if Stride == 24:
            for i in range(int(VBufferSize/int(Stride))):
                s = binascii.hexlify(bytes(VBuffer.read(int(Stride)))).decode()
                Data=[s[i:i+4] for i in range(0, len(s), 4)]
                if len(Data) < 3:
                    break
                x= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[0]))).decode('utf-8'),16)/32767)*(MeshScale)
                y= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[1]))).decode('utf-8'),16)/32767)*(MeshScale)
                z= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[2]))).decode('utf-8'),16)/32767)*(MeshScale)
                Verts.append([x,y,z,VertCount])
                VertCount+=1
        elif Stride == 48:
            for i in range(int(VBufferSize/int(Stride))):
                s = binascii.hexlify(bytes(VBuffer.read(int(Stride)))).decode()
                Data=[s[i:i+8] for i in range(0, len(s), 8)]
                #print(Data)
                if len(Data) < 3:
                    break
                x= ReadFloat32(Data[0])*(MeshScale)
                y= ReadFloat32(Data[1])*(MeshScale)
                z= ReadFloat32(Data[2])*(MeshScale)
                Verts.append([x,y,z,VertCount])
                VertCount+=1
        else:
            for i in range(int(VBufferSize/int(Stride))):
                s = binascii.hexlify(bytes(VBuffer.read(int(Stride)))).decode()
                Data=[s[i:i+4] for i in range(0, len(s), 4)]
                if len(Data) < 3:
                    break
                x= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[0]))).decode('utf-8'),16)/32767)*(MeshScale)
                y= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[1]))).decode('utf-8'),16)/32767)*(MeshScale)
                z= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[2]))).decode('utf-8'),16)/32767)*(MeshScale)
                Verts.append([x,y,z,VertCount])
                VertCount+=1
    elif Type == 0:
        if Stride == 24:
            for i in range(int(VBufferSize/int(Stride))):
                s = binascii.hexlify(bytes(VBuffer.read(int(Stride)))).decode()
                Data=[s[i:i+4] for i in range(0, len(s), 4)]
                if len(Data) < 3:
                    break
                x= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[0]))).decode('utf-8'),16)/32767)*(MeshScale)
                y= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[1]))).decode('utf-8'),16)/32767)*(MeshScale)
                z= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[2]))).decode('utf-8'),16)/32767)*(MeshScale)
                Verts.append([x,y,z,VertCount])
                VertCount+=1
        #elif Stride == 48:
        #    for i in range(int(VBufferSize/int(Stride))):
        #        s = binascii.hexlify(bytes(VBuffer.read(int(Stride)))).decode()
        #        Data=[s[i:i+8] for i in range(0, len(s), 8)]
        #        #print(MeshScale)
        #        print(Data)
        #        x= ReadFloat32(Data[0])*(MeshScale)
        #        y= ReadFloat32(Data[1])*(MeshScale)
        #        z= ReadFloat32(Data[2])*(MeshScale)
        #        Verts.append([x,y,z,VertCount])
        #        #print([x,y,z,VertCount])
        #        VertCount+=1f07dbb80
        else:
            for i in range(int(VBufferSize/int(Stride))):
                s = binascii.hexlify(bytes(VBuffer.read(int(Stride)))).decode()
                Data=[s[i:i+4] for i in range(0, len(s), 4)]
                #print(MeshScale)
                if len(Data) < 3:
                    break
                x= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[0]))).decode('utf-8'),16)/32767)*(MeshScale)
                y= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[1]))).decode('utf-8'),16)/32767)*(MeshScale)
                z= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[2]))).decode('utf-8'),16)/32767)*(MeshScale)
                Verts.append([x,y,z,VertCount])
                VertCount+=1
    return Verts
def ReadUV(path,Header,PackageCache,UVXScale,UVXOff,UVYScale,UVYOff):
    DumpHash(path,PackageCache,Header)
    Buffer=GetEntryA(path,PackageCache,Header)
    Header=binascii.hexlify(bytes(hex_to_little_endian(Header))).decode('utf-8')
    new=ast.literal_eval("0x"+Header)
    pkg = Hex_String(Package_ID(new))
    ent = Hex_String(Entry_ID(new))
    Bank=pkg+"-"+ent+".bin"
    VHeader=open(custom_direc+"/out/"+Bank,"rb")
    VBufferSize=int.from_bytes(VHeader.read(4),"little")
    Stride=int.from_bytes(VHeader.read(2),"little")
    VHeader.close()
    new=ast.literal_eval(Buffer)
    pkg = Hex_String(Package_ID(new))
    ent = Hex_String(Entry_ID(new))
    Bank=pkg+"-"+ent+".bin"
    DumpHash(path,PackageCache,binascii.hexlify(bytes(hex_to_little_endian(Buffer[2:]))).decode('utf-8'))
    UVData=[]
    UV=open(custom_direc+"/out/"+Bank,"rb")
    if Stride == 0:
        Stride=1
    for i in range(int(VBufferSize/Stride)):
        Data=binascii.hexlify(bytes(UV.read(Stride))).decode()
        Uvs=[Data[i:i+4] for i in range(0, len(Data), 4)]
        if len(Uvs) < 2:
            break
        U= ((twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Uvs[0]))).decode('utf-8'),16)/32767)* float(UVXScale))+float(UVXOff)
        V= ((twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Uvs[1]))).decode('utf-8'),16)/32767)* float(-UVYScale)) + (1 - float(UVYOff))
        UVData.append([U,V])
    UV.close()
    return UVData
def ExtractEntity(path,PackageCache,Input,H64Sort):
    DumpHash(path,PackageCache,Input)
    Input2=binascii.hexlify(bytes(hex_to_little_endian(Input))).decode('utf-8')
    new=ast.literal_eval("0x"+Input2)
    pkg = Hex_String(Package_ID(new))
    ent = Hex_String(Entry_ID(new))
    Bank=pkg+"-"+ent+".bin"
    file=open(custom_direc+"/out/"+Bank,"rb")
    file.seek(0x08)
    ResourceCount=int.from_bytes(file.read(4),"little")
    file.seek(0x10)
    ResourceOffset=int.from_bytes(file.read(4),"little")
    file.seek(0x10+ResourceOffset+16)
    MeshFiles=[]
    for i in range(ResourceCount):
        EntityResource=binascii.hexlify(bytes(file.read(4))).decode()
        #print(EntityResource)
        file.read(8)
        DumpHash(path,PackageCache,EntityResource)
        new=ast.literal_eval("0x"+binascii.hexlify(bytes(hex_to_little_endian(EntityResource))).decode('utf-8'))
        pkg = Hex_String(Package_ID(new))
        ent = Hex_String(Entry_ID(new))
        Bank=pkg+"-"+ent+".bin"
        Resource=open(custom_direc+"/out/"+Bank,"rb")
        Length=len(binascii.hexlify(Resource.read()).decode())/2
        Resource.seek(0x18)
        ModelMeshOffset=int.from_bytes(Resource.read(4),"little")
        Resource.seek(ModelMeshOffset+572)
        ModelMeshHash=Resource.read(4)
        if int.from_bytes(ModelMeshHash,"little") < 2155872256:
            u=1
        else:
            ModelMeshHash=binascii.hexlify(ModelMeshHash).decode()
            EntryA=GetEntryA(path,PackageCache,ModelMeshHash)
            if EntryA == "0x80806f07":
                MeshFiles.append(ModelMeshHash)
        Resource.seek(0xC4)
        SubResource=binascii.hexlify(Resource.read(4)).decode()
        if SubResource == "8f6d8080":
            TexplateStart=int.from_bytes(Resource.read(4),"little")
            Resource.seek(TexplateStart+0x3C0)
            MapCount=int.from_bytes(Resource.read(4),"little")
            Resource.read(4)
            MaterialMapOffset=int.from_bytes(Resource.read(4),"little")
            Resource.seek(TexplateStart+0x3C8+MaterialMapOffset+0x10)
            MaterialMapping=[]
            for i in range(MapCount):
                MaterialMapping.append([int.from_bytes(Resource.read(4),"little"),int.from_bytes(Resource.read(4),"little"),int.from_bytes(Resource.read(4),"little")])
            Resource.seek(TexplateStart+0x400)
            MaterialHashCount=int.from_bytes(Resource.read(4),"little")
            Resource.read(4)
            MaterialHashOffset=int.from_bytes(Resource.read(4),"little")
            Resource.seek(TexplateStart+0x418+MaterialHashOffset)
            ExternalMaterials=[]
            for i in range(MaterialHashCount):
                ExternalMaterials.append(binascii.hexlify(Resource.read(4)).decode())
        Resource.close()
    file.close()
    Exists=os.path.isfile(os.getcwd()+"/data/Dynamics/"+Input+".fbx")
    if Exists:
        MeshFiles=[]
    if MeshFiles != []:
        outfile=open(custom_direc+"/data/Materials/"+Input+".txt","w")
        memory_manager = fbx.FbxManager.Create()
        scene = fbx.FbxScene.Create(memory_manager, '')
        MeshFileCount=0
        for MeshFile in MeshFiles:
            #print("MeshFile "+MeshFile)
            DumpHash(path,PackageCache,MeshFile)
            MeshFile=binascii.hexlify(bytes(hex_to_little_endian(MeshFile))).decode('utf-8')
            new=ast.literal_eval("0x"+MeshFile)
            pkg = Hex_String(Package_ID(new))
            ent = Hex_String(Entry_ID(new))
            Bank=pkg+"-"+ent+".bin"
            MeshFileData=open(custom_direc+"/out/"+Bank,"rb")
            MeshFileData.seek(0x18)
            BufferStorageOffset=int.from_bytes(MeshFileData.read(4),"little")
            MeshFileData.seek(96)
            MeshXOff=ReadFloat32(binascii.hexlify(bytes(MeshFileData.read(4))).decode())
            MeshYOff=ReadFloat32(binascii.hexlify(bytes(MeshFileData.read(4))).decode())
            MeshZOff=ReadFloat32(binascii.hexlify(bytes(MeshFileData.read(4))).decode())
            MeshScale=ReadFloat32(binascii.hexlify(bytes(MeshFileData.read(4))).decode())
            MeshFileData.seek(BufferStorageOffset+0x28)
            VertexHeader=binascii.hexlify(bytes(MeshFileData.read(4))).decode()
            UvHeader=binascii.hexlify(bytes(MeshFileData.read(4))).decode()
            Weights=binascii.hexlify(bytes(MeshFileData.read(4))).decode()
            MeshFileData.seek(MeshFileData.tell()+4)
            IndexHeader=binascii.hexlify(bytes(MeshFileData.read(4))).decode()
            VertexColor=binascii.hexlify(bytes(MeshFileData.read(4))).decode()
            SinglePassSkinningBuffer=binascii.hexlify(bytes(MeshFileData.read(4))).decode()
            MeshFileData.seek(0x70)
            if UvHeader != "ffffffff":
                UVXScale=struct.unpack('!f', bytes.fromhex(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(MeshFileData.read(4))).decode()))).decode('utf-8')))[0]
                UVYScale= struct.unpack('!f', bytes.fromhex(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(MeshFileData.read(4))).decode()))).decode('utf-8')))[0]
                UVXOff= struct.unpack('!f', bytes.fromhex(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(MeshFileData.read(4))).decode()))).decode('utf-8')))[0]
                UVYOff= struct.unpack('!f', bytes.fromhex(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(MeshFileData.read(4))).decode()))).decode('utf-8')))[0]
                UVData=ReadUV(path,UvHeader,PackageCache,UVXScale,UVXOff,UVYScale,UVYOff)
            MeshFileData.seek(BufferStorageOffset+0xB8)
            MaterialCount=int.from_bytes(MeshFileData.read(4),"little")
            MeshFileData.seek(0xC+MeshFileData.tell())
            Verts=GetVerts(path,VertexHeader,PackageCache,MeshScale)
            is32=Get32(path,IndexHeader,PackageCache)
            Buffer=GetEntryA(path,PackageCache,IndexHeader)
            flipped=binascii.hexlify(bytes(hex_to_little_endian(Buffer[2:]))).decode('utf-8')
            DumpHash(path,PackageCache,flipped)
            new=ast.literal_eval(Buffer)
            pkg = Hex_String(Package_ID(new))
            ent = Hex_String(Entry_ID(new))
            Bank=pkg+"-"+ent+".bin"
            ind=open(custom_direc+"/out/"+Bank,"rb")
            MatCount=0
            for j in range(MaterialCount):
                Material=binascii.hexlify(bytes(MeshFileData.read(4))).decode()
                VarientShaderIndex=int.from_bytes(MeshFileData.read(2),"little")
                PrimitiveType=int.from_bytes(MeshFileData.read(2),"little")
                IndexOffset=int.from_bytes(MeshFileData.read(4),"little")
                IndexCount=int.from_bytes(MeshFileData.read(4),"little")
                MeshFileData.seek(MeshFileData.tell()+13)
                LoD=int.from_bytes(MeshFileData.read(1),"little")
                MeshFileData.seek(MeshFileData.tell()+0x6)
                if LoD > 3:
                    continue
                my_mesh = fbx.FbxMesh.Create(scene, str(Input+"_"+str(MeshFileCount)+"_"+str(MatCount)))
                
                uvLayer = fbx.FbxLayerElementUV.Create(my_mesh, "uv")
                uvLayer.SetMappingMode(fbx.FbxLayerElement.EMappingMode.eByControlPoint)
                uvLayer.SetReferenceMode(fbx.FbxLayerElement.EReferenceMode.eDirect)
                writtenParts=[]
                Verticies=[]   
                IndexData=Model.ReadIndexData(PrimitiveType,is32,IndexOffset,IndexCount,ind)
                for List in IndexData:
                    for Val in List:
                        bisect.insort(Verticies, Val) 
                count=0
                for Vert in Verticies:
                    try:
                        v = fbx.FbxVector4(Verts[Vert][0]+MeshXOff, Verts[Vert][1]+MeshYOff, Verts[Vert][2]+MeshZOff)
                    except IndexError:
                        break
                    my_mesh.SetControlPointAt( v, count )
                    count+=1
                for Face in IndexData:
                    my_mesh.BeginPolygon()
                    vertex_index = binary_search_single(Verticies,int(Face[0]))
                    my_mesh.AddPolygon(vertex_index)
                    vertex_index = binary_search_single(Verticies,int(Face[1]))
                    my_mesh.AddPolygon(vertex_index)
                    vertex_index = binary_search_single(Verticies,int(Face[2]))
                    my_mesh.AddPolygon(vertex_index)
                    my_mesh.EndPolygon()
                cubeLocation = (0, 0, 0)
                cubeScale    = (1, 1, 1)
                layer = my_mesh.GetLayer(0)
                for Vert in Verticies:
                    try:
                        UVData[Vert]
                    except IndexError:
                        continue
                    uvLayer.GetDirectArray().Add(fbx.FbxVector2(float(UVData[Vert][0]),float(UVData[Vert][1])))
                try:
                    layer.SetUVs(uvLayer)
                except AttributeError:
                    u=1
                count=0
                newNode = addNode(scene, Input+"_"+str(MeshFileCount)+"_"+str(MatCount), location = cubeLocation)
                rootNode = scene.GetRootNode()
                rootNode.AddChild( newNode )
                newNode.SetNodeAttribute( my_mesh )
                newNode.ScalingActive.Set(1)
                px = fbx.FbxDouble3(1, 1, 1)
                normLayer = fbx.FbxLayerElementNormal.Create(my_mesh, "")
                normLayer.SetMappingMode(fbx.FbxLayerElement.EMappingMode.eByControlPoint)
                normLayer.SetReferenceMode(fbx.FbxLayerElement.EReferenceMode.eDirect)
                count=0
                lLayer = my_mesh.GetLayer(0)
                MappedMaterials=[]
                name=Input+"_"+str(MeshFileCount)+"_"+str(MatCount)
                if Material != "ffffffff":
                    MeshMats=ParseMaterial(Material,outfile,H64Sort,path,PackageCache,Input+"_"+str(MeshFileCount)+"_"+str(MatCount))
                    MatsToPrint=",".join(MeshMats)
                    if len(MeshMats) != 0:
                        outfile.write(name+" : "+Material+" : "+MatsToPrint+"\n")
                else:
                    try:
                        MaterialMapping[VarientShaderIndex][0]
                    except IndexError:
                        u=1
                    else:
                        for x in range(MaterialMapping[VarientShaderIndex][0]):
                            MeshMats=ParseMaterial(ExternalMaterials[MaterialMapping[VarientShaderIndex][1]+x],outfile,H64Sort,path,PackageCache,Input+"_"+str(MeshFileCount)+"_"+str(MatCount))
                            MatsToPrint=", ".join(MeshMats)
                            if len(MeshMats) != 0:
                                if [name,MatsToPrint] not in writtenParts:
                                    writtenParts.append([name,MatsToPrint])
                                    outfile.write(name+" : "+ExternalMaterials[MaterialMapping[VarientShaderIndex][1]+x]+" : "+MatsToPrint+"\n")
                        
                            
                        
                    
                MatCount+=1
            MeshFileCount+=1
        filename = output+"\\data\\Dynamics\\"+Input+".fbx"
        FbxCommon.SaveScene(memory_manager, scene, filename)
        outfile.close()
        memory_manager.Destroy()



    
        




#filename=name+".bin"
#exporter.export(scene)

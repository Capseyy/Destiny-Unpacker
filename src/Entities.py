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
import bisect, sys

#path = "E:\SteamLibrary\steamapps\common\Destiny2\packages" #Path to your packages folder.
#path="C:\oldd2\packages"
#custom_direc = os.getcwd()+"/out" #Where you want the bin files to go

#custom_direc = os.getcwd()+"/out" #Where you want the bin files to go

#custom_direc=output
#print(custom_direc)
#output=
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
    #global path
    flipped=binascii.hexlify(bytes(hex_to_little_endian(Val))).decode('utf-8')
    new=int(ast.literal_eval("0x"+flipped))
    pkg=Hex_String(Package_ID(new))
    temp=ast.literal_eval("0x"+stripZeros(pkg))
    print(temp)
    Index=binary_search(PackageCache,int(temp))
    Package=PackageCache[Index][0]
    ent=Hex_String(Entry_ID(new))
    EntryA=ExtractSingleEntry.GetEntryA(path,custom_direc,Package,ent)
    DumpHash(path,PackageCache,binascii.hexlify(bytes(hex_to_little_endian(EntryA[2:]))).decode('utf-8'))
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
def DumpHash(path,PackageCache,Val):
    #global path
    flipped=binascii.hexlify(bytes(hex_to_little_endian(Val))).decode('utf-8')
    new=int(ast.literal_eval("0x"+flipped))
    pkg=Hex_String(Package_ID(new))
    temp=ast.literal_eval("0x"+stripZeros(pkg))
    print(temp)
    Index=binary_search(PackageCache,int(temp))
    Package=PackageCache[Index][0]
    ent=Hex_String(Entry_ID(new))
    #print(path,custom_direc,Package,ent)
    ExtractSingleEntry.unpack_entry_ext(path,custom_direc+"/out",Package,ent)
import ast,fbx,struct
from fbx import FbxManager
import FbxCommon
#ans=input("y/n")
#if ans.lower() == "y":
def ExtractEntity(path,PackageCache,Input):
    #global path
    #PackageCache=GeneratePackageCache()
    vertFound=False
    indFound=False
    #unpack_all(path, custom_direc)
    #Input="2E66B880"   #80c1ffce
    DumpHash(path,PackageCache,Input)
    Input=binascii.hexlify(bytes(hex_to_little_endian(Input))).decode('utf-8')
    new=ast.literal_eval("0x"+Input)
    pkg = Hex_String(Package_ID(new))
    #print(result)
    ent = Hex_String(Entry_ID(new))
    Bank=pkg+"-"+ent+".bin"
    print(Bank)
    Dyn2s=[]
    MaterialsToGet=[]
    Materials=True

    file=open(custom_direc+"/out/"+Bank,"rb")
    file.seek(0xA0)
    ResourceCount=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(file.read(4))).decode()))).decode('utf-8')))
    file.seek(0xb0)
    DumpHash(path,PackageCache,binascii.hexlify(bytes(file.read(4))).decode())
    file.seek(0xb0)
    Entity1=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(file.read(4))).decode()))).decode('utf-8')))
    pkg = Hex_String(Package_ID(Entity1))
    #print(result)
    ent = Hex_String(Entry_ID(Entity1))
    Bank=pkg+"-"+ent+".bin"
    file2=open(custom_direc+"/out/"+Bank,"rb")
    file2.seek(0x18)
    Offset=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(file2.read(4))).decode()))).decode('utf-8')))
    print(Offset)
    file2.seek(Offset+4+24)
    Skeleton=False
    ExistingDyn3s=[]
    SkeleCheck=binascii.hexlify(bytes(file2.read(4))).decode()
    print(SkeleCheck+"    Skele")
    if (SkeleCheck == "dd818080") or (SkeleCheck == "d5818080"):
        Skeleton=True
    if Skeleton == True:
        file.seek(0xBC)
        Dyn=binascii.hexlify(bytes(file.read(4))).decode()
        Dyn2s.append(Dyn)
        file.seek(0xC8)
        Dyn=binascii.hexlify(bytes(file.read(4))).decode()
        Dyn2s.append(Dyn)
    else:
        file.seek(0xB0)
        Dyn=binascii.hexlify(bytes(file.read(4))).decode()
        Dyn2s.append(Dyn)
        file.seek(0xBC)
        Dyn=binascii.hexlify(bytes(file.read(4))).decode()
        Dyn2s.append(Dyn)

    print(Skeleton)
    for Dyn in Dyn2s:
        DumpHash(path,PackageCache,Dyn)
        DynHash=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Dyn))).decode('utf-8')))
        pkg = Hex_String(Package_ID(DynHash))
        ent = Hex_String(Entry_ID(DynHash))
        Bank=pkg+"-"+ent+".bin"
        print(Bank)
        DynData=open(custom_direc+"/out/"+Bank,"rb")
        Length=len(binascii.hexlify(bytes(DynData.read())).decode())
        if Length == 0:
            Dyn2s.remove(Dyn)
        DynData.seek(0x18)
        Offset=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(DynData.read(4))).decode()))).decode('utf-8')))
        if (Offset+572-4) >= int(Length/2):
            print("Dynamic has no mesh data (C), skipping...")
            continue
        DynData.seek(Offset+572)
        Dyn3Hash=binascii.hexlify(bytes(DynData.read(4))).decode()
        print(Dyn3Hash)
        DumpHash(path,PackageCache,Dyn3Hash)
        Check=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Dyn3Hash))).decode('utf-8')))
        if Check < 2155872256:
            print("Dynamic has no mesh data (D), skipping...")
            continue
        pkg = Hex_String(Package_ID(Check))
        ent = Hex_String(Entry_ID(Check))
        Bank=pkg+"-"+ent+".bin"
        
        file3=open(custom_direc+"/out/"+Bank,"rb")
        print(Bank)
        ExistingDyn3s.append(Dyn3Hash)
        if Materials == True:
            DynData.seek(0x48)
            Offset=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(DynData.read(4))).decode()))).decode('utf-8')))
            Offset+=0x48-8
            Found=False
            while True:
                DynData.seek(Offset)
                temp=binascii.hexlify(bytes(DynData.read(4))).decode()
                if temp == "14008080":
                    Found=True
                    Offset-=8
                    break
                elif temp == "b89f8080":
                    break
                Offset-=4
            if Found == True:
                DynData.seek(Offset)    
                count=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(DynData.read(4))).decode()))).decode('utf-8')))
                Offset+=16
                for i in range(Offset,Offset+count*4,4):
                    DynData.seek(i)
                    Mat=binascii.hexlify(bytes(DynData.read(4))).decode()
                    MaterialsToGet.append(Mat)
                    print(Mat+ " mat")
                    print("mat found")
    print(ExistingDyn3s)
    for Dyn3 in ExistingDyn3s:
        #print("Dyn3s")
        Dyn3=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Dyn3))).decode('utf-8')))
        pkg = Hex_String(Package_ID(Dyn3))
        ent = Hex_String(Entry_ID(Dyn3))
        Bank=pkg+"-"+ent+".bin"
        print(Bank+ "  Dyn3")
        Dyn3=open(custom_direc+"/out/"+Bank,"rb")
        Dyn3.seek(0x18)
        Offset=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(Dyn3.read(4))).decode()))).decode('utf-8')))
        Offset+=24
        Dyn3.seek(96)
        MeshXOff=binascii.hexlify(bytes(Dyn3.read(4))).decode()
        MeshXOff=struct.unpack('!f', bytes.fromhex(binascii.hexlify(bytes(hex_to_little_endian(MeshXOff))).decode('utf-8')))[0]
        MeshYOff=binascii.hexlify(bytes(Dyn3.read(4))).decode()
        MeshYOff=struct.unpack('!f', bytes.fromhex(binascii.hexlify(bytes(hex_to_little_endian(MeshYOff))).decode('utf-8')))[0]
        MeshZOff=binascii.hexlify(bytes(Dyn3.read(4))).decode()
        MeshZOff=struct.unpack('!f', bytes.fromhex(binascii.hexlify(bytes(hex_to_little_endian(MeshZOff))).decode('utf-8')))[0]
        MeshScale=binascii.hexlify(bytes(Dyn3.read(4))).decode()
        MeshScale=struct.unpack('!f', bytes.fromhex(binascii.hexlify(bytes(hex_to_little_endian(MeshScale))).decode('utf-8')))[0]
        Dyn3.seek(0x10)
        Count=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(Dyn3.read(4))).decode()))).decode('utf-8')))
        
        GroupCount=0
        for i in range(Offset, Offset + Count * 0x80, 0x80):
            Dyn3.seek(i+0x10+0x10)
            HeaderHash=binascii.hexlify(bytes(Dyn3.read(4))).decode()
            Index=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(HeaderHash))).decode('utf-8')))
            DumpHash(path,PackageCache,HeaderHash)
            pkg = Hex_String(Package_ID(Index))
            ent = Hex_String(Entry_ID(Index))
            Bank=pkg+"-"+ent+".bin"
            print(Bank+"   IndexHeader")
            IndexName=ast.literal_eval(GetEntryA(path,PackageCache,HeaderHash))
            pkg = Hex_String(Package_ID(IndexName))
            ent = Hex_String(Entry_ID(IndexName))
            IndexName=pkg+"-"+ent+".bin"
            IndexHeader=open(custom_direc+"/out/"+Bank,"rb")
            IndexHeader.seek(1)
            is32=False
            Check32=binascii.hexlify(bytes(IndexHeader.read(1))).decode()
            if Check32 == "01":
                is32=True
            Dyn3.seek(i+0x10)
            VHeaderHash=binascii.hexlify(bytes(Dyn3.read(4))).decode()
            Vertex=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(VHeaderHash))).decode('utf-8')))
            VertexName=ast.literal_eval(GetEntryA(path,PackageCache,VHeaderHash))
            pkg = Hex_String(Package_ID(VertexName))
            ent = Hex_String(Entry_ID(VertexName))
            VertexName=pkg+"-"+ent+".bin"
            DumpHash(path,PackageCache,VHeaderHash)
            pkg = Hex_String(Package_ID(Vertex))
            ent = Hex_String(Entry_ID(Vertex))
            Bank=pkg+"-"+ent+".bin"
            VertexHeader=open(custom_direc+"/out/"+Bank,"rb")
            VertexHeader.seek(4)
            Stride=binascii.hexlify(bytes(VertexHeader.read(2))).decode()
            Stride=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Stride))).decode('utf-8')))
            Dyn3.seek(i+0x10+4)
            UVFileHash=binascii.hexlify(bytes(Dyn3.read(4))).decode()
            if UVFileHash != "ffffffff":
                DumpHash(path,PackageCache,UVFileHash)
                UVFile=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(UVFileHash))).decode('utf-8')))
                pkg = Hex_String(Package_ID(UVFile))
                ent = Hex_String(Entry_ID(UVFile))
                Bank=pkg+"-"+ent+".bin"
                print(Bank+"   uvHeader")
                FindUV=True
                UVName=ast.literal_eval(GetEntryA(path,PackageCache,UVFileHash))
                pkg = Hex_String(Package_ID(UVName))
                ent = Hex_String(Entry_ID(UVName))
                DumpHash(path,PackageCache,UVFileHash)
                UVName=pkg+"-"+ent+".bin"
                Dyn3.seek(112)
                UVXScale=binascii.hexlify(bytes(Dyn3.read(4))).decode()
                UVXScale=struct.unpack('!f', bytes.fromhex(binascii.hexlify(bytes(hex_to_little_endian(UVXScale))).decode('utf-8')))[0]
                UVYScale=binascii.hexlify(bytes(Dyn3.read(4))).decode()
                UVYScale=struct.unpack('!f', bytes.fromhex(binascii.hexlify(bytes(hex_to_little_endian(UVYScale))).decode('utf-8')))[0]
                UVXOff=binascii.hexlify(bytes(Dyn3.read(4))).decode()
                UVXOff=struct.unpack('!f', bytes.fromhex(binascii.hexlify(bytes(hex_to_little_endian(UVXOff))).decode('utf-8')))[0]
                UVYOff=binascii.hexlify(bytes(Dyn3.read(4))).decode()
                UVYOff=struct.unpack('!f', bytes.fromhex(binascii.hexlify(bytes(hex_to_little_endian(UVYOff))).decode('utf-8')))[0]
            pkg = Hex_String(Package_ID(Vertex))
            ent = Hex_String(Entry_ID(Vertex))
            Bank=pkg+"-"+ent+".bin"
            #Submech table
            Dyn3.seek(i+0x10+0x10+0x10)
            SubTableCount=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(Dyn3.read(4))).decode()))).decode('utf-8')))
            Dyn3.seek(i+0x10+0x10+0x18)
            SubTableOffset=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(Dyn3.read(4))).decode()))).decode('utf-8')))
            SubTableStart=SubTableOffset+i+0x10+0x10+0x18+16
            Submeshes=[]
            for k in range(SubTableStart, SubTableStart + SubTableCount * 0x24, 0x24):
                Dyn3.seek(k)
                Submesh=[]
                MaterialHash=binascii.hexlify(bytes(Dyn3.read(4))).decode()
                Null=binascii.hexlify(bytes(Dyn3.read(2))).decode()
                PrimitiveType=binascii.hexlify(bytes(Dyn3.read(2))).decode()
                IndexOffset=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(Dyn3.read(4))).decode()))).decode('utf-8')))
                IndexCount=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(Dyn3.read(4))).decode()))).decode('utf-8')))
                Dyn3.seek(Dyn3.tell()+13)
                LoD=binascii.hexlify(bytes(Dyn3.read(1))).decode()
                #print(LoD)
                LoD=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(LoD))).decode('utf-8')))
                Submesh=[MaterialHash,PrimitiveType,IndexOffset,IndexCount,LoD]
                ExtractMesh=[PrimitiveType,IndexOffset,IndexCount,LoD]
                if ExtractMesh not in Submeshes:
                    Submeshes.append(ExtractMesh)
                #break
            
            print(VertexName)
            Vert=open(custom_direc+"/out/"+VertexName,"rb")
            Length=binascii.hexlify(bytes(Vert.read())).decode()
            Vert.seek(0x0)
            print(len(Length))
            num=len(Length)/(Stride*2)
            print(num)
            norms=[]
            Xs=[]
            Ys=[]
            Zs=[]
            verts=[]
            VertCount=0
            for i in range(int(num)):
                s = binascii.hexlify(bytes(Vert.read(Stride))).decode()
                Data=[s[i:i+4] for i in range(0, len(s), 4)]
                x= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[0]))).decode('utf-8'),16)/32767)*(MeshScale)
                y= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[1]))).decode('utf-8'),16)/32767)*(MeshScale)
                z= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[2]))).decode('utf-8'),16)/32767)*(MeshScale)
                verts.append([x,y,z,VertCount])
                VertCount+=1
        

            #FindUV=False
            if FindUV == True:
                UV=open(custom_direc+"/out/"+UVName,"rb")
                Data=binascii.hexlify(bytes(UV.read())).decode()
                Length=len(Data)/8
                UV.seek(0)
                UVData=[]
                for i in range(int(Length)):
                    Data=binascii.hexlify(bytes(UV.read(4))).decode()
                    Uvs=[Data[i:i+4] for i in range(0, len(Data), 4)]
                    U= ((twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Uvs[0]))).decode('utf-8'),16)/32767)* float(UVXScale))+float(UVXOff)
                    V= ((twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Uvs[1]))).decode('utf-8'),16)/32767)* float(-UVYScale)) + (1 - float(UVYOff))
                    #print(U,V)
                    UVData.append([U,V])
            print(IndexName)
            ind=open(custom_direc+"/out/"+IndexName,"rb")
            faces=[]
            Length = binascii.hexlify(bytes(ind.read())).decode()
            ind.seek(0x00)
            triCount=0
            IndexTest=[]
            while True:
                v1 = binascii.hexlify(bytes(ind.read(2))).decode()
                if v1 == "":
                    break
                if v1 != "ffff":
                    v1=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(v1))).decode('utf-8')))
                    IndexTest.append(ind.tell()-2)
                
            #print(IndexTest)
                

            #print(faces[len(faces)-1]) 
            faces=[]
            currentFace=[]
            MinLod=99
            #for Part in Submeshes:
                #if int(Part[3]) < MinLod:
                    #MinLod=Part[3]
            memory_manager = fbx.FbxManager.Create()
            scene = fbx.FbxScene.Create(memory_manager, '')
            for Part in Submeshes:
                if int(Part[3]) >= 4:
                    continue
                usedVerts=[]
                IndexData=[]
                my_mesh = fbx.FbxMesh.Create(scene, str(Input+"_"+str(Part[3])+"_"+str(GroupCount)))
                count=0
                print(Part)
                if Part[0] == "0500":
                    print(is32)
                    if is32 == False:
                        triCount=0
                        ind.seek(Part[1]*2)
                        Start=ind.tell()
                        if ind.read(2) != "ffff":
                            ind.seek(ind.tell()-2)
                        while ind.tell()+4-Start < Part[2]*2:
                            i1=binascii.hexlify(bytes(ind.read(2))).decode()
                            i2=binascii.hexlify(bytes(ind.read(2))).decode()
                            i3=binascii.hexlify(bytes(ind.read(2))).decode()
                            if i3 == "ffff":
                                triCount=0
                                continue
                            i1=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(i1))).decode('utf-8')))
                            i2=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(i2))).decode('utf-8')))
                            i3=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(i3))).decode('utf-8')))
                            if triCount % 2 == 0:
                                IndexData.append([i1,i2,i3])
                            else:
                                IndexData.append([i2,i1,i3])
                            ind.seek(ind.tell()-4)
                            triCount+=1
                    else:
                        ind.seek(Part[1]*4)
                        Start=ind.tell()
                        while ind.tell()+8-Start < Part[2]*4:
                            i1=binascii.hexlify(bytes(ind.read(4))).decode()
                            i2=binascii.hexlify(bytes(ind.read(4))).decode()
                            i3=binascii.hexlify(bytes(ind.read(4))).decode()
                            if i3 == "ffffffff":
                                triCount=0
                                continue
                            temp=[i1,i2,i3]
                            if "" in temp:
                                break
                            #print(temp)
                            i1=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(i1))).decode('utf-8')))
                            i2=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(i2))).decode('utf-8')))
                            i3=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(i3))).decode('utf-8')))
                            if triCount % 2 == 0:
                                IndexData.append([i1,i2,i3])
                            else:
                                IndexData.append([i2,i1,i3])
                            ind.seek(ind.tell()-8)
                            triCount+=1
                            if len(IndexData) == Part[2]:
                                break
                else:
                    if is32 == False:
                        ind.seek(Part[1]*2)
                        for j in range(0,int(Part[2]),3):
                            s = binascii.hexlify(bytes(ind.read(6))).decode()
                            Inds=[s[i:i+4] for i in range(0, len(s), 4)]
                            #print(s)
                            if len(Inds) < 3:
                                break
                            i1=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Inds[0]))).decode('utf-8')))
                            i2=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Inds[1]))).decode('utf-8')))
                            i3=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Inds[2]))).decode('utf-8')))
                            IndexData.append([i1,i2,i3])
                    else:
                        ind.seek(Part[1]*4)
                        for j in range(0,int(Part[2]),3):
                            s = binascii.hexlify(bytes(ind.read(12))).decode()
                            Inds=[s[i:i+8] for i in range(0, len(s), 8)]
                            #print(s)
                            if len(Inds) < 3:
                                break
                            i1=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Inds[0]))).decode('utf-8')))
                            i2=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Inds[1]))).decode('utf-8')))
                            i3=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Inds[2]))).decode('utf-8')))
                            IndexData.append([i1,i2,i3])
                #print(IndexData)
                usedVerts=[]
                tempcheck=[]
                Verticies=[]
                count=0

                    
                
                uvLayer = fbx.FbxLayerElementUV.Create(my_mesh, "uv")
                uvLayer.SetMappingMode(fbx.FbxLayerElement.EMappingMode.eByControlPoint)
                uvLayer.SetReferenceMode(fbx.FbxLayerElement.EReferenceMode.eDirect)

                    
                for List in IndexData:
                    for Val in List:
                        bisect.insort(Verticies, Val) 

                for Vert in Verticies:
                    v = fbx.FbxVector4(verts[Vert][0]+MeshXOff, verts[Vert][1]+MeshYOff, verts[Vert][2]+MeshZOff)
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
                #layer = my_mesh.GetLayer(0)
                #layer.SetUVs(uvLayer)
                #cubeLocation = (xScale, yScale, zScale)
                cubeLocation = (0, 0, 0)
                cubeScale    = (1, 1, 1)
                layer = my_mesh.GetLayer(0)
                for Vert in Verticies:
                    uvLayer.GetDirectArray().Add(fbx.FbxVector2(float(UVData[Vert][0]),float(UVData[Vert][1])))
                layer.SetUVs(uvLayer)
    #for UV in UVData:
                count=0
                newNode = addNode(scene, Input+"_"+str(Part[3]), location = cubeLocation)
                rootNode = scene.GetRootNode()
                #rootNode.LclTranslation.set(fbx.FbxDouble3(xScale, yScale, zScale))
                rootNode.AddChild( newNode )

                newNode.SetNodeAttribute( my_mesh )
                newNode.ScalingActive.Set(1)
                px = fbx.FbxDouble3(1, 1, 1)
                normLayer = fbx.FbxLayerElementNormal.Create(my_mesh, "")
                normLayer.SetMappingMode(fbx.FbxLayerElement.EMappingMode.eByControlPoint)
                normLayer.SetReferenceMode(fbx.FbxLayerElement.EReferenceMode.eDirect)
                
                
                # Create the materials.
                # Each polygon face will be assigned a unique material.
                count=0
                lLayer = my_mesh.GetLayer(0)
                #break
            GroupCount+=1
            filename = output+"\\data\\Dynamics\\"+Input+"_"+str(GroupCount)+".fbx"
            FbxCommon.SaveScene(memory_manager, scene, filename)
            #exporter = fbx.FbxExporter.Create(memory_manager, filename)
            
            #filename = os.getcwd()+"\\Statics\\"+OutName+".fbx"
            #status = exporter.Initialize(filename, -1, memory_manager.GetIOSettings())
            #scene.save()
            #exporter.Export(scene)
            #print(status)
            #exporter.Destroy()
            memory_manager.Destroy()
        #break
        




#filename=name+".bin"
#exporter.export(scene)

from dataclasses import dataclass, fields, field
from typing import List
import os
import sys
import binascii
import io
import fnmatch
import time
import ast,fbx,struct
from fbx import FbxManager
import FbxCommon
from ctypes import *
#path = "E:\SteamLibrary\steamapps\common\Destiny2\packages" #Path to your packages folder.
#path="C:\Program Files (x86)\Steam\steamapps\common\Destiny2\packages"
#path="D:/oldd2/packages"
custom_direc = os.getcwd()+"/out" #Where you want the bin files to go
oodlepath = os.getcwd()+"/ThirdParty/oo2core_9_win64.dll" #Path to Oodle DLL in Destiny 2/bin/x64.dle DLL in Destiny 2/bin/x64.
useful=[]
def hex_to_little_endian(hex_string):
    little_endian_hex = bytearray.fromhex(hex_string)[::-1]
    return little_endian_hex
def hex_to_big_endian(hex_string):
    return bytearray.fromhex(hex_string)
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
def Hash64Search(Hash64Data,Input):
    Found=False
    ans=binary_search2(Hash64Data,int(Input))
    #print(ans)
    if str(ans) != "-1":
        Found=True
    if Found == True:
        return Hash64Data[ans][1]
    else:
        return False
def GetFileReference(Hash,PackageCache):
    flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
    new=int(ast.literal_eval("0x"+flipped))
    #print(Val)
    pkg=Hex_String(Package_ID(new))
    #print(pkg)
    temp=ast.literal_eval("0x"+stripZeros(pkg))
    #print(temp)
    Index=binary_search(PackageCache,int(temp))
    Package=PackageCache[Index][0]
    ent=Hex_String(Entry_ID(new))
    Data=ExtractSingleEntry.GetEntryA(path,custom_direc,Package,ent)
    #print(Data)
    return Data            

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
def GetBufferInfo(MainPath):
    data=open(MainPath+"/cache/ModelDataTable.txt","r").read()
    data=data.split("\n")
    data.remove("")
    BufferData=[]
    for Entry in data:
        temp=Entry.split(" : ")
        BufferData.append([temp[0],int(ast.literal_eval(temp[1]))])
    BufferData.sort(key=lambda x: x[1])
    return BufferData    
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

import ast,fbx,struct
from fbx import FbxManager
import FbxCommon, ExtractSingleEntry
def GetFileData(path,Hash,PackageCache):
    flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
    new=int(ast.literal_eval("0x"+flipped))
    #print(Val)
    pkg=Hex_String(Package_ID(new))
    #print(pkg)
    temp=ast.literal_eval("0x"+stripZeros(pkg))
    #print(temp)
    Index=binary_search(PackageCache,int(temp))
    Package=PackageCache[Index][0]
    ent=Hex_String(Entry_ID(new))
    Data=ExtractSingleEntry.unpack_entry(path,custom_direc,Package,ent)
    #print(ExtractSingleEntry.GetEntryA(path,custom_direc,Package,ent))
    #print(Data)
    return Data
def twos_complement(hexstr, bits):
    value = int(hexstr, 16)
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value
def ParseEntityFile(path,entry,PackageCache,H64Sort,top):
    output=open(os.getcwd()+"/cache/directive.txt","w")
    Data=entry.get()
    Data=Data.split(",")
    #print(Data)
    Entities=[]
    EntityFile=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Data[3]))).decode('utf-8')))
    PkgID=Hex_String(Package_ID(EntityFile))
    EntryID=Hex_String(Entry_ID(EntityFile))
    EntityFile=PkgID+"-"+EntryID
    output.write("\nEntity File : "+EntityFile+"\n") 
    EntityFileData=GetFileData(path,Data[3],PackageCache)
    EntityFileData=GetFileData(path,EntityFileData[48:56],PackageCache)
    EntityResources=EntityFileData[128:]
    EntityResources=[EntityResources[i:i+8] for i in range(0, len(EntityResources), 8)]
    First=True
    for Resource in EntityResources:
        EntityIDMapper=open(os.getcwd()+"/data/EntityIDMapper.txt","a")
        ObjectName="unknown"
        EntityFileData=GetFileData(path,Resource,PackageCache)
        count=0
        if EntityFileData[64:72] != "ffffffff":
            EntityFileData2=GetFileData(path,EntityFileData[64:72],PackageCache)
            if (EntityFileData2[208:216] != "ffffffff") and (EntityFileData2[208:216] != "00000000"):
                print(EntityFileData[64:72])
                CombatOffset=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(EntityFileData2[208:216]))).decode('utf-8')))
                CombatTableCount=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(EntityFileData2[192:200]))).decode('utf-8')))
                for i in range(CombatTableCount):
                    Offset=208+(2*CombatOffset)+32+(i*16)
                    print(Offset)
                    EntityTable=EntityFileData2[Offset:Offset+16]
                    EntityTableOffset=twos_complement(binascii.hexlify(bytes(hex_to_little_endian(EntityTable[:8]))).decode('utf-8'),32)
                    print(EntityTableOffset)
                    Hash64Val=EntityFileData2[Offset+(2*EntityTableOffset)+16:Offset+(2*EntityTableOffset)+32]
                    print(Hash64Val)
                    try:
                        Hash64Int=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Hash64Val))).decode('utf-8')))
                    except SyntaxError:
                        continue
                    else:
                        Ans=Hash64Search(H64Sort,Hash64Int)
                        if Ans != False:
                            print(str(i)+" entity found "+str(Ans))
                            print(EntityFileData[64:72])
                            InstanceData=False
                            DevNameID=False
                            if (EntityFileData2[368:376] != "00000000"):
                                InstanceOffset=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(EntityFileData2[368:376]))).decode('utf-8')))
                                InstanceData=EntityFileData2[(368+16+(InstanceOffset*2)):(368+16+(InstanceOffset*2)+64)]
                                DevNameID=EntityFileData2[80+(InstanceOffset*2):88+(InstanceOffset*2)]
                            Entities.append([Ans,EntityFileData2[Offset+(2*EntityTableOffset)+32:Offset+(2*EntityTableOffset)+40],InstanceData,EntityFileData[64:72],DevNameID])
            
                
        EntityIDMapper.close()                
    
    output.close() 
    outname=Data[0].split(".")[0]
    #OutputAct2(outname) 
    #GetDynTextures(PackageCache)
    return Entities
    

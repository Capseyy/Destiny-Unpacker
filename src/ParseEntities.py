from dataclasses import dataclass, fields, field
import numpy as np
from typing import List
import gf
import os
from ctypes import cdll, c_char_p, create_string_buffer
from Crypto.Cipher import AES
import binascii
import io
import fnmatch
import time
from ctypes import *
import bisect 
global custom_direc

path = "E:\SteamLibrary\steamapps\common\Destiny2\packages" #Path to your packages folder.
path="C:\oldd2\packages"
custom_direc = os.getcwd()+"/data" #Where you want the bin files to go
temp=os.getcwd()
temp=temp.split("\\")
print(temp)
custom_direc="/".join(temp[:len(temp)-1])
print(custom_direc)
oodlepath = "E:/oo2core_9_win64.dll" #Path to Oodle DLL in Destiny 2/bin/x64.dle DLL in Destiny 2/bin/x64.

filelist = []
for file in os.listdir(path)[::-1]:
    if fnmatch.fnmatch(file,'w64_sr_comb*'):       #Customize this to what pkgs you need from. Can wildcard with * for all packages, or all of a certain type.
        filelist.append(file)
        #print(file) #for debugging



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
def GetBufferInfo():
    data=open("ModelDataTable.txt","r").read()
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
import ast,struct
#from fbx import FbxManager
import  ExtractSingleEntry
def GetFileData(Hash,PackageCache):
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
    print(ExtractSingleEntry.GetEntryA(path,custom_direc,Package,ent))
    #print(Data)
    return Data
def DumpHash(PackageCache,Val):
    global custom_direc
    flipped=binascii.hexlify(bytes(hex_to_little_endian(Val))).decode('utf-8')
    new=int(ast.literal_eval("0x"+flipped))
    #print(Val)
    pkg=Hex_String(Package_ID(new))
    #print(pkg)
    temp=ast.literal_eval("0x"+stripZeros(pkg))
    print(temp)
    Index=binary_search(PackageCache,int(temp))
    Package=PackageCache[Index][0]
    #print(Package)
    #print(ent)
    
    ent=Hex_String(Entry_ID(new))
    print(custom_direc)
    ExtractSingleEntry.unpack_entry_ext(path,custom_direc+"/out",Package,ent)
    print(ExtractSingleEntry.GetEntryA(path,custom_direc,Package,ent))
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
#ans=input("y/n")
Input="2e66b880"
dec=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Input))).decode('utf-8')))
PkgID=Hex_String(Package_ID(dec))
EntryID=Hex_String(Entry_ID(dec))
DirName=PkgID+"-"+EntryID
file=open(custom_direc+"/out/"+DirName+".bin","rb")
file.seek(0x10)
Offset=int.from_bytes(file.read(4), "little")
file.seek(0x10+Offset)
Count=int.from_bytes(file.read(4), "little")
file.seek(0x20+Offset)
Resources=[]
for i in range(Count):
    Resources.append(binascii.hexlify(bytes(file.read(4))).decode())
    file.read(8)
PackageCache=GeneratePackageCache()
for EResource in Resources:
    DumpHash(PackageCache,EResource)
    


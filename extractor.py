from dataclasses import dataclass, fields, field
import os, sys, shutil
sys.path.append(os.getcwd()+"/ThirdParty")
import numpy as np
from typing import List
import gf, subprocess
import tkinter.messagebox
from ctypes import cdll, c_char_p, create_string_buffer , c_uint32
from Crypto.Cipher import AES
import binascii
import io
import fnmatch
import time,ast,struct
import fbx
from fbx import FbxManager
import FbxCommon
from ast import literal_eval
from tkinter import *
from tkinter import ttk
from functools import partial
global custom_direc,useful ,path,Hash64Data
#path = "E:\SteamLibrary\steamapps\common\Destiny2\packages" #Path to your packages folder.
path="E:/SteamLibrary/steamapps/common/Destiny2/packages"
#path="D:/oldd2/packages"
custom_direc = os.getcwd()+"/out" #Where you want the bin files to go
oodlepath = os.getcwd()+"/oo2core_9_win64.dll" #Path to Oodle DLL in Destiny 2/bin/x64.dle DLL in Destiny 2/bin/x64.
useful=[]

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
def ReadHash64():
    file=open("h64.txt","r")
    data=file.read()
    Hash64Data=data.split("\n")
    return Hash64Data
            
def hex_to_little_endian(hex_string):
    little_endian_hex = bytearray.fromhex(hex_string)[::-1]
    return little_endian_hex
def hex_to_big_endian(hex_string):
    return bytearray.fromhex(hex_string)

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

class File:
    def __init__(self,Name,FileType,StrData):
        self.Name=Name
        self.FileType=FileType
        #self.Tags=[]
        self.Data=[]
        self.StrData=StrData
        self.Hashes=[]
        self.Strings=[]
        self.ReadFile()
        #self.FindTags()
        #self.ReadFile64()
        self.FindHashes()
        self.ActName=[]
        self.QueHashes=[]
        self.Banks=[]
        output=open("Directive.txt","a")
        output.write("Activity File: \n")
        output.write(self.Name+"\n")
        output.close()
    def GetDialogue(self):
        Lines=[self.Raw[i:i+32] for i in range(0, len(self.Raw), 32)]
        count=0
        print("finding dial")
        found=False
        for Line in Lines:
            Hashes=[Line[i:i+8] for i in range(0, len(Line), 8)]
            for Hash in Hashes:
                if Hash.lower() == "b7978080":
                    Hash64=Lines[count+1][16:]
                    found=True
            count+=1
        if found == True:
            print(Hash64)
            flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash64))).decode('utf-8')
            HashToFind="0x"+flipped
            print(HashToFind)
            Dat64=ReadHash64()
            found=False
            for Hash in Dat64:
                temp=Hash.split(": ")
                if HashToFind == temp[0]:
                    DiaTable=temp[1]
                    print("FOUND DIALOGUE")
                    found=True
                    break
            if found == True:
                dec = ast.literal_eval(DiaTable)
                PkgID=Hex_String(Package_ID(dec))
                EntryID=Hex_String(Entry_ID(dec))
                DirName=PkgID+"-"+EntryID
                output=open("Directive.txt","a")
                output.write("Dialogue Table \n")
                output.write(DirName+"\n")
                    
                print("try")
                with open(custom_direc+"/audio/"+DirName+".tab", 'rb') as f:
                    s = binascii.hexlify(bytes(f.read())).decode()
                    Data=[s[i:i+8] for i in range(0, len(s), 8)]
                    count=0
                    lines=[]
                    for Hash in Data:
                        #print(Hash)
                       
                        flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
                        #print(flipped)
                        dec = ast.literal_eval("0x"+flipped)
                        #print(dec)
                        #for Dat in StrData:
                            #if Dat[0] == str(dec):
                                #output.write(Dat[0]+" : "+Dat[1]+"\n")
                        ans=binary_search(self.StrData,int(dec))
                        #print(ans)
                        if str(ans) != "-1":
                            #print("written")
                            output.write(str(self.StrData[ans][0])+" : "+self.StrData[ans][1]+"\n")
                    f.close()
                output.write("\n\n\n")
                        
                count+=1
                output.close()
        print("done dia")        
                
                    
    def ReadFile(self):
        File=open(custom_direc+"/"+self.Name,"rb")
        Data=binascii.hexlify(bytes(File.read())).decode()
        self.Raw=Data
        self.Data=[Data[i:i+8] for i in range(0, len(Data), 8)]
        File.close()
    def ReadFile64(self):
        File=open(custom_direc+"/"+self.Name,"rb")
        Data=binascii.hexlify(bytes(File.read())).decode()
        temp=[Data[i:i+16] for i in range(0, len(Data), 16)]
        File.close()
        for Hash in temp:
            flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
            dec = "0x"+flipped
            Found=False
            #print(dec)
            for Line in Hash64Data:
                Lines=Line.split(": ")
                #print(Lines)
                if Lines[0] == str(dec):
                    Found=True
                    AudioFile=Lines[1]
                    #print(str(AudioFile)+"    64")
                    new=literal_eval(AudioFile)
                    PkgID=Hex_String(Package_ID(new))
                    EntryID=Hex_String(Entry_ID(new))
                    DirName=PkgID.upper()+"-"+EntryID.upper()+".bin"
                    print(DirName)

    def FindTags(self):
        Count=0
        for Hash in self.Data:
            Hash=[Hash[i:i+4] for i in range(0, len(Hash), 4)]
            try:
                Except=Hash[1]
            except IndexError:
                break
            else:
                if Hash[1] == "8080":
                    self.Tags.append(["".join(Hash),Count])
        
            Count+=4
    def FindHashes(self):
        Count=0
        Hashes=[]
        print("FindingHashes")
        #print(self.Name)
        for Hash in self.Data:
            Dir=False
            Mus=False
            Flip=binascii.hexlify(hex_to_little_endian(Hash)).decode()
            #print(Flip)
            Data=[Flip[i:i+2] for i in range(0, len(Flip), 2)]
            #print(Data)
            if (Data[0] == "80") and (Data[1] != "80"):
                Hashes.append("".join(Data))
                Hash="".join(Data)
                hash2="0x"+Hash
                new=literal_eval(hash2)
                PkgID=Hex_String(Package_ID(new))
                EntryID=Hex_String(Entry_ID(new))
                DirName=PkgID.upper()+"-"+EntryID.upper()+".directive"
                MusName=PkgID.upper()+"-"+EntryID.upper()+".mus"
                for File in os.listdir(custom_direc):
                    if File.lower() == DirName.lower():
                        Dir=True
                    if File.lower() == MusName.lower():
                        Mus=True
                if Dir == True and Mus == True:
                    break
        print("Done Getting Hashes")
        self.Hashes=Hashes
    def PullStrings(self):
        output=open("Directive.txt","a")
        output.write("\nMusic Script + Loadzones : \n")
        if self.ActName != []:
            output.write(self.ActName+"\n")
        for Hash in self.Data:
            if "0000" not in Hash:
                dat=StringHash(Hash,self.StrData)
                if dat != False:
                    if [dat,Hash] not in self.Strings:
                        self.Strings.append([dat,Hash])
                        output.write(dat+"\n")

        output.close()
        #print(self.Strings)
    def GetName(self):
        count=0
        for Bytes in self.Data:
            if Bytes == "65008080":
                length=self.Data[count+1]
                ActName="".join(self.Data[count+3:len(self.Data)-1])
                self.ActName=str(binascii.unhexlify(ActName).decode())
                break
            count+=1
    def GetMusAndDir(self):
        #getdir
        FoundDir=False
        FoundMus=False
        self.AudioFound=False
        print(self.Hashes)
        for Hash in self.Hashes:
            hash2="0x"+Hash
            new=literal_eval(hash2)
            PkgID=Hex_String(Package_ID(new))
            EntryID=Hex_String(Entry_ID(new))
            DirName=PkgID.upper()+"-"+EntryID.upper()+".directive"
            MusName=PkgID.upper()+"-"+EntryID.upper()+".mus"
            print(MusName)
            for File in os.listdir(custom_direc):
                if File == DirName:
                    self.StrDirectory=DirName
                    FoundDir=True
                elif File == MusName:
                    self.MusDirectory=MusName
                    FoundMus=True
                if FoundDir == True and FoundMus == True:
                    break
    
        if FoundDir == True:
            self.PrintDirect()
        if FoundMus == True:
            self.PrintMus()
        if self.AudioFound == True:
            self.BnkSearch()
        #BNKExplorer
        output=open("Directive.txt","a")
        output.write("\n\n\n\n")
        output.close()
            
    def BnkSearch(self):
        flipped=binascii.hexlify(bytes(hex_to_little_endian(self.AudioDir))).decode('utf-8')
        dec = "0x"+flipped
        print(str(dec))
        Found=False
        print("finding music BNK")
        for Line in Hash64Data:
            Lines=Line.split(": ")
            #print(Lines)
            if Lines[0] == str(dec).lower():
                Found=True
                AudioFile=Lines[1]
                break
        if Found == True:
            new=literal_eval(AudioFile)
            PkgID=Hex_String(Package_ID(new))
            EntryID=Hex_String(Entry_ID(new))
            AudioDrive=PkgID.upper()+"-"+EntryID.upper()+".aud"
            print(AudioDrive)
            for File in os.listdir(custom_direc+"/audio"):
                if File == AudioDrive:
                    print("AudioFileExists !!!")
                    newFile=open(custom_direc+"/audio/"+AudioDrive,"rb")
                    newFile.seek(0x18)
                    BankName=binascii.hexlify(bytes(newFile.read(4))).decode()
                    newFile.close()
                    flipped=binascii.hexlify(bytes(hex_to_little_endian(BankName))).decode('utf-8')
                    new="0x"+flipped
                    new=literal_eval(new)
                    PkgID=Hex_String(Package_ID(new))
                    EntryID=Hex_String(Entry_ID(new))
                    AudioDrive1=PkgID.upper()+"-"+EntryID.upper()+".aud2"
                    for File1 in os.listdir(custom_direc+"/audio"):
                        if File1 == AudioDrive1:
                            print("AudioFileExists2 !!!")
                            newFile=open(custom_direc+"/audio/"+AudioDrive1,"rb")
                            BankName=binascii.hexlify(bytes(newFile.read())).decode()
                            flipped=binascii.hexlify(bytes(hex_to_little_endian(BankName))).decode('utf-8')
                            new="0x"+flipped
                            print(new)
                            new=literal_eval(new)
                            PkgID=Hex_String(Package_ID(new))
                            EntryID=Hex_String(Entry_ID(new))
                            AudioDrive2=PkgID.upper()+"-"+EntryID.upper()+".bnk"
                            output=open("Directive.txt","a")
                            output.write("\nSoundBank: \n")
                            output.write(AudioDrive2)
                            output.close()
                            break
                                
                    break
        
            

    def PrintDirect(self):
        Direct=open(custom_direc+"/"+self.StrDirectory,"rb")
        Data=binascii.hexlify(bytes(Direct.read())).decode()
        Direct.close()
        output=open("Directive.txt","a")
        output.write("\nDIRECTIVE: \n")
        self.Direct=[Data[i:i+8] for i in range(0, len(Data), 8)]
        for Hash in self.Direct:
            if "0000" not in Hash:
                dat=StringHash(Hash,self.StrData)
                if dat != False:
                    if [dat,Hash] not in self.Strings:
                        self.Strings.append([dat,Hash])
                        output.write(dat+"\n")
        output.close()
    def PrintMus(self):
        count=0
        file=open(custom_direc+"/"+self.MusDirectory,"rb")
        Data=binascii.hexlify(bytes(file.read())).decode()
        count=0
        Lines=[Data[i:i+32] for i in range(0, len(Data), 32)]
        for Line in Lines:
            Hashes=[Line[i:i+8] for i in range(0, len(Line), 8)]
            if "e8bf8080" in Line:
                Type = "e8bf8080"
                flipped=binascii.hexlify(bytes(hex_to_little_endian(Hashes[0]))).decode('utf-8')
                Len=ast.literal_eval("0x"+stripZeros(flipped))
                StartingOffset=(count+1)*16
                break
            elif "fa458080" in Line:
                Type = "fa458080"
                flipped=binascii.hexlify(bytes(hex_to_little_endian(Hashes[0]))).decode('utf-8')
                Len=ast.literal_eval("0x"+stripZeros(flipped))
                StartingOffset=(count+1)*16
                break
            elif "fb458080" in Line:
                Type = "fa458080"
                flipped=binascii.hexlify(bytes(hex_to_little_endian(Hashes[0]))).decode('utf-8')
                Len=ast.literal_eval("0x"+stripZeros(flipped))
                StartingOffset=(count+1)*16
                break
            count+=1
                
        Dev=open("Directive.txt","a")
        Dev.write("\n\n\nMusic Cue List\n")
        file.seek(0xA0)
        #StartingOffset=176
        count=0
        Pointers=[]
        HashCache=[]
        test=[]
        if Type == "e8bf8080":
            print("New Type")
            file.seek(StartingOffset)
            for i in range(Len):
                #file.seek(StartingOffset)
                Data=binascii.hexlify(bytes(file.read(48))).decode() #0 unk 1 00000000 2 RelativePointer(in hex) 3 00000000 4 StrCheck 5 StrCheck 6 Hash 7 00000000 unk----
                Hashes=[Data[i:i+8] for i in range(0, len(Data), 8)]
                #print(Hashes)
                MusHash=binascii.hexlify(bytes(hex_to_little_endian(Hashes[6]))).decode('utf-8')
                HashCache.append(str(ast.literal_eval("0x"+MusHash)))
                #print(Hashes[2])
                if Hashes[2] == "00000000": #end of file
                    Pointers.append(0)
                    test.append(0)
                   
                else:
                    Pointer=stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Hashes[2]))).decode('utf-8'))
                    temp=ast.literal_eval("0x"+Pointer)
                    test.append(temp)
                    Pos=StartingOffset+(48*i)+temp+8
                    Pointers.append(Pos)
                #print(Pos)
                #print(test[i])
                count+=1
        else:
            file.seek(StartingOffset)
            for i in range(Len):
                
                Data=binascii.hexlify(bytes(file.read(32))).decode() #0 unk 1 00000000 2 RelativePointer(in hex) 3 00000000 4 StrCheck 5 01? 6 Hash 7 00000000
                Hashes=[Data[i:i+8] for i in range(0, len(Data), 8)]
                
                print(Hashes)
                MusHash=binascii.hexlify(bytes(hex_to_little_endian(Hashes[6]))).decode('utf-8')
                HashCache.append(str(ast.literal_eval("0x"+MusHash)))
                #print(Hashes[2])
                if Hashes[2] == "00000000": #end of file
                    Pointers.append(0)
                    test.append(0)
                   
                else:
                    Pointer=stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Hashes[2]))).decode('utf-8'))
                    temp=ast.literal_eval("0x"+Pointer)
                    test.append(temp)
                    Pos=StartingOffset+(32*i)+temp+8
                    Pointers.append(Pos)
                #print(Pos)
                #print(test[i])
                count+=1
            #print(count)
        count=0
        for Pointer in Pointers:
            #Hash=binascii.hexlify(bytes(hex_to_little_endian(HashCache[count]))).decode('utf-8')
            Hash=HashCache[count]
            #print(str(Pointers[count+1]) +" - "+str(Pointer))
            
            try:
                Difference=int(Pointers[count+1])-int(Pointer)
            except IndexError:
                file.seek(Pointer)
                try:
                    Event=file.read().decode()
                except UnicodeDecodeError:
                    continue
                else:
                    Dev.write(str(Hash)+": "+str(Event)+" \n")
                
                break
            else:
                if str(Pointers[count+1]) == "0":
                    count+=1
                    continue
                file.seek(Pointer)
                try:
                    Event=file.read(Difference).decode()
                except ValueError:
                    print("L")
                else:
                    Dev.write(str(Hash)+": "+str(Event)+" \n")
            #print(Event)
           
            count+=1
        Dev.close()
        count=0
        Direct=open(custom_direc+"/"+self.MusDirectory,"rb")
        Data=binascii.hexlify(bytes(Direct.read())).decode()
        Direct.close()
        self.Mus=[Data[i:i+32] for i in range(0, len(Data), 32)]
        for Hash in self.Mus:
            split=[Hash[i:i+8] for i in range(0, len(Hash), 8)]
            if "f5458080" in split:
                print("MusicDrive Found")
                Line=self.Mus[count+2]
                temp=[Line[i:i+8] for i in range(0, len(Line), 8)]
                self.AudioDir=temp[0]+temp[1]
                self.AudioFound=True                            
            if split[0].upper() == "C59D1C81":
                if split[2] !="00000000":
                    self.QueHashes.append(split[2])
                    print("QueHash found")
            count+=1
        #output.close()
                
    
        
   

def get_file_typename(file_type, file_subtype, ref_id, ref_pkg):
    if file_type == 8:
        return '8080xxxx Structure File'
    elif file_type == 33:
        return 'DirectX Bytecode Header'
    elif file_type == 41:
        return 'DirectX Bytecode Data'
    else:
        return 'Unknown'


def calculate_pkg_id(entry_a_data):
    ref_pkg_id = (entry_a_data >> 13) & 0x3FF
    ref_unk_id = entry_a_data >> 23

    ref_digits = ref_unk_id & 0x3
    if ref_digits == 1:
        return ref_pkg_id
    else:
        return ref_pkg_id | 0x100 << ref_digits


# All of these decoding functions use the information from formats.c on how to decode each entry
def decode_entry_a(entry_a_data):
    ref_id = entry_a_data & 0x1FFF
    # ref_pkg_id = (entry_a_data >> 13) & 0x3FF
    ref_pkg_id = calculate_pkg_id(entry_a_data)
    ref_unk_id = (entry_a_data >> 23) & 0x1FF

    return np.uint16(ref_id), np.uint16(ref_pkg_id), np.uint16(ref_unk_id)


def decode_entry_b(entry_b_data):
    file_subtype = (entry_b_data >> 6) & 0x7
    file_type = (entry_b_data >> 9) & 0x7F
    #print(entry_b_data)
    return np.uint8(file_type), np.uint8(file_subtype)


def decode_entry_c(entry_c_data):
    starting_block = entry_c_data & 0x3FFF
    #print(starting_block)
    starting_block_offset = ((entry_c_data >> 14) & 0x3FFF) << 4
    return starting_block, starting_block_offset


def decode_entry_d(entry_c_data, entry_d_data):
    file_size = (entry_d_data & 0x3FFFFFF) << 4 | (entry_c_data >> 28) & 0xF
    unknown = (entry_d_data >> 26) & 0x3F

    return np.uint32(file_size), np.uint8(unknown)


class OodleDecompressor:
    """
    Oodle decompression implementation.
    Requires Windows and the external Oodle library.
    """

    def __init__(self, library_path: str) -> None:
        """
        Initialize instance and try to load the library.
        """
        if not os.path.exists(library_path):
            raise Exception("Could not open Oodle DLL, make sure it is configured correctly.")

        try:
            self.handle = cdll.LoadLibrary(library_path)
        except OSError as e:
            raise Exception(
                "Could not load Oodle DLL, requires Windows and 64bit python to run."
            ) from e

    def decompress(self, payload: bytes) -> bytes:
        """
        Decompress the payload using the given size.
        """
        force_size = int('0x40000', 16)
        output = create_string_buffer(force_size)
        self.handle.OodleLZ_Decompress(
            c_char_p(payload), len(payload), output, force_size,
            0, 0, 0, None, None, None, None, None, None, 3)
        return output.raw


class PkgHeader:
    def __init__(self, pbin):
        self.PackageID = gf.get_int16(pbin, 0x10)
        self.PackageIDH = gf.fill_hex_with_zeros(hex(self.PackageID)[2:], 4)
        self.PatchID = gf.get_int16(pbin, 0x30)

        self.EntryTableOffset = gf.get_int32(pbin, 0x44)
        # self.EntryTableLength = get_int_hex(0x48, phex)
        self.EntryTableSize = gf.get_int32(pbin, 0x60)
        self.EntryTableLength = self.EntryTableSize * 0x16

        self.BlockTableSize = gf.get_int32(pbin, 0x68)
        self.BlockTableOffset = gf.get_int32(pbin, 0x6C)


@dataclass
class SPkgEntry:
    EntryA: np.uint32 = np.uint32(0)
    EntryB: np.uint32 = np.uint32(0)
    EntryC: np.uint32 = np.uint32(0)
    EntryD: np.uint32 = np.uint32(0)

    '''
     [             EntryD              ] [             EntryC              ] 
     GGGGGGFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFEEEE EEEEEEEE EEDDDDDD DDDDDDDD

     [             EntryB              ] [             EntryA              ]
     00000000 00000000 TTTTTTTS SS000000 CCCCCCCC CBBBBBBB BBBAAAAA AAAAAAAA

     A:RefID: EntryA & 0x1FFF
     B:RefPackageID: (EntryA >> 13) & 0x3FF
     C:RefUnkID: (EntryA >> 23) & 0x1FF
     D:StartingBlock: EntryC & 0x3FFF
     E:StartingBlockOffset: ((EntryC >> 14) & 0x3FFF) << 4
     F:FileSize: (EntryD & 0x3FFFFFF) << 4 | (EntryC >> 28) & 0xF
     G:Unknown: (EntryD >> 26) & 0x3F

     Flags (Entry B)
     S:SubType: (EntryB >> 6) & 0x7
     T:Type:  (EntryB >> 9) & 0x7F
    '''


@dataclass
class SPkgEntryDecoded:
    ID: np.uint16 = np.uint16(0)
    FileName: str = ''
    FileType: str = ''
    RefID: np.uint16 = np.uint16(0)  # uint13
    RefPackageID: np.uint16 = np.uint16(0)  # uint9
    RefUnkID: np.uint16 = np.uint16(0)  # uint10
    Type: np.uint8 = np.uint8(0)  # uint7
    SubType: np.uint8 = np.uint8(0)  # uint3
    StartingBlock: np.uint16 = np.uint16(0)  # uint14
    StartingBlockOffset: np.uint32 = np.uint32(0)  # uint14
    FileSize: np.uint32 = np.uint32(0)  # uint30
    Unknown: np.uint8 = np.uint8(0)  # uint6
    EntryA: int = ''


@dataclass
class SPkgEntryTable:
    Entries: List[SPkgEntryDecoded] = field(default_factory=list)  # This list of of length [EntryTableSize]


@dataclass
class SPkgBlockTableEntry:
    ID: int = 0  # 0x0
    Offset: np.uint32 = np.uint32(0)  # 0x4
    Size: np.uint32 = np.uint32(0)  # 0x8
    PatchID: np.uint16 = np.uint16(0)  # 0xC
    Flags: np.uint16 = np.uint16(0)  # 0xE
    Hash: List[np.uint8] = field(default_factory=list)  # [0x14] = 20  # 0x22
    GCMTag: List[np.uint8] = field(default_factory=list)  # [0x10] = 16  # 0x32


@dataclass
class SPkgBlockTable:
    Entries: List[SPkgBlockTableEntry] = field(default_factory=list)  # This list of length [BlockTableSize]


class Package:
    BLOCK_SIZE = int('0x40000', 16)

    AES_KEY_0 = [
        "0xD6", "0x2A", "0xB2", "0xC1", "0x0C", "0xC0",
        "0x1B", "0xC5", "0x35", "0xDB", "0x7B",
        "0x86", "0x55", "0xC7", "0xDC", "0x3B",
    ]
    AES_KEY_1 = [
        "0x3A", "0x4A", "0x5D", "0x36", "0x73", "0xA6",
        "0x60", "0x58", "0x7E", "0x63", "0xE6",
        "0x76", "0xE4", "0x08", "0x92", "0xB5",
    ]

    def __init__(self, package_directory,useful):
        self.package_directory = package_directory
        if '_en_' in self.package_directory:
            self.t_package_id = self.package_directory[-13:-9]
        else:
            self.t_package_id = self.package_directory[-10:-6]
        self.package_header = None
        self.entry_table = None
        self.block_table = None
        self.all_patch_ids = []
        self.max_pkg_bin = None
        self.nonce = None
        self.useful=useful
        self.aes_key_0 = binascii.unhexlify(''.join([x[2:] for x in self.AES_KEY_0]))
        self.aes_key_1 = binascii.unhexlify(''.join([x[2:] for x in self.AES_KEY_1]))

    def extract_package(self, custom_direc, extract=True, largest_patch=True):
        self.get_all_patch_ids()
        if largest_patch:
            self.set_largest_patch_directory()
        print(f"Extracting files for {self.package_directory}")

        self.max_pkg_bin = open(self.package_directory, 'rb').read()
        self.package_header = self.get_header()
        self.entry_table = self.get_entry_table()
        self.block_table = self.get_block_table()

        if extract:
            self.process_blocks(custom_direc)

    def get_all_patch_ids(self):
        all_pkgs = [x for x in os.listdir(self.package_directory.split('/w64')[0]) if self.t_package_id in x]
        all_pkgs.sort()
        self.all_patch_ids = [int(x[-5]) for x in all_pkgs]

    def set_largest_patch_directory(self):
        if 'unp1' in self.package_directory:
            all_pkgs = [x for x in os.listdir(self.package_directory.split('/w64')[0]) if x[:-6] in self.package_directory]
        else:
            all_pkgs = [x for x in os.listdir(self.package_directory.split('/w64')[0]) if self.t_package_id in x]
        sorted_all_pkgs, _ = zip(*sorted(zip(all_pkgs, [int(x[-5]) for x in all_pkgs])))
        self.package_directory = self.package_directory.split('/w64')[0] + '/' + sorted_all_pkgs[-1]
        return

    def get_header(self):
        """
        Given a pkg directory, this gets the header data and uses SPkgHeader() struct to fill out the fields of that struct,
        making a header struct with all the correct data.
        :param pkg_dir:
        :return: the pkg header struct
        """
        header_length = int('0x16F', 16)
        # The header data is 0x16F bytes long, so we need to x2 as python reads each nibble not each byte
        header = self.max_pkg_bin[:header_length]
        pkg_header = PkgHeader(header)
        #print(pkg_header)
        return pkg_header

    def get_entry_table(self):
        """
        After we've got the header data for each pkg we know where the entry table is. Using this information, we take each
        row of 16 bytes (128 bits) as an entry and separate the row into EntryA, B, C, D for decoding
        :param pkg_data: the hex data from pkg
        :param entry_table_size: how long this entry table is in the pkg data
        :param entry_table_offset: hex offset for where the entry table starts
        :return: the entry table made
        """

        entry_table = SPkgEntryTable()
        entries_to_decode = []
        entry_table_start = self.package_header.EntryTableOffset
        #print(entry_table_start)
        entry_table_data = self.max_pkg_bin[entry_table_start:entry_table_start+self.package_header.EntryTableLength]
        #table=open("entrytable.bin","wb")
        #table.write(entry_table_data)
        #time.sleep(60)
        #print(self.package_header.EntryTableSize)
        #for i in range(0, self.package_header.EntryTableSize * 16, 16):
        #    print(entry_table_data,)
        for i in range(0, self.package_header.EntryTableSize * 16, 16):
            entry = SPkgEntry(gf.get_int32(entry_table_data, i),
                              gf.get_int32(entry_table_data, i+4),
                              gf.get_int32(entry_table_data, i+8),
                              gf.get_int32(entry_table_data, i+12))
            #print(entry)
            entries_to_decode.append(entry)
        #print(len(entries_to_decode))
        #time.sleep(10)
        entry_table.Entries = self.decode_entries(entries_to_decode)
        return entry_table

    def decode_entries(self, entries_to_decode):
        """
        Given the entry table (and hence EntryA, B, C, D) we can decode each of them into data about each (file? block?)
        using bitwise operators.
        :param entry_table: the entry table struct to decode
        :return: array of decoded entries as struct SPkgEntryDecoded()
        """
        #print(entries_to_decode)
        entries = []
        count = 0
        for entry in entries_to_decode:
            # print("\n\n")
            ref_id, ref_pkg_id, ref_unk_id = decode_entry_a(entry.EntryA)
            if (hex(entry.EntryA) in self.useful) or (self.useful == ["All"]) or (self.useful == ["Cube"]) or (self.useful == ["Norm"]) or (self.useful == ["Map"]):
                file_type, file_subtype = decode_entry_b(entry.EntryB)
                starting_block, starting_block_offset = decode_entry_c(entry.EntryC)
                file_size, unknown = decode_entry_d(entry.EntryC, entry.EntryD)
                file_name = f"{self.package_header.PackageIDH}-{gf.fill_hex_with_zeros(hex(count)[2:], 4)}"
                file_typename = get_file_typename(file_type, file_subtype, ref_id, ref_pkg_id)

                decoded_entry = SPkgEntryDecoded(np.uint16(count), file_name, file_typename,
                                                 ref_id, ref_pkg_id, ref_unk_id, file_type, file_subtype, starting_block,
                                                 starting_block_offset, file_size, unknown, hex(entry.EntryA))
                entries.append(decoded_entry)
                #print("Here")
                #if len(entries) > 50:
                 #   print(entries)
                  #  time.sleep(60)
            count += 1
            
            #(count)
        return entries

    def get_block_table(self):
        block_table = SPkgBlockTable()
        block_table_data = self.max_pkg_bin[self.package_header.BlockTableOffset:self.package_header.BlockTableOffset + self.package_header.BlockTableSize*48]
        reduced_bt_data = block_table_data
        for i in range(self.package_header.BlockTableSize):
            block_entry = SPkgBlockTableEntry(ID=i)
            for fd in fields(block_entry):
                if fd.type == np.uint32:
                    value = gf.get_int32(reduced_bt_data, 0)
                    setattr(block_entry, fd.name, value)
                    reduced_bt_data = reduced_bt_data[4:]
                elif fd.type == np.uint16:
                    value = gf.get_int16(reduced_bt_data, 0)
                    setattr(block_entry, fd.name, value)
                    reduced_bt_data = reduced_bt_data[2:]
                elif fd.type == List[np.uint8] and fd.name == 'Hash':
                    flipped = gf.get_flipped_bin(reduced_bt_data, 20)
                    value = [c for c in flipped]
                    setattr(block_entry, fd.name, value)
                    reduced_bt_data = reduced_bt_data[20:]
                elif fd.type == List[np.uint8] and fd.name == 'GCMTag':
                    flipped = gf.get_flipped_bin(reduced_bt_data, 16)
                    value = [c for c in flipped]
                    setattr(block_entry, fd.name, value)
                    reduced_bt_data = reduced_bt_data[16:]
            block_table.Entries.append(block_entry)
        return block_table

    def process_blocks(self, custom_direc):
        all_pkg_bin = []
        for i in self.all_patch_ids:
            bin_data = open(f'{self.package_directory[:-6]}_{i}.pkg', 'rb').read()
            all_pkg_bin.append(bin_data)

        self.set_nonce()
        #print(all_pkg_bin)
        self.output_files(all_pkg_bin, custom_direc)

    def decrypt_block(self, block, block_bin):
        if block.Flags & 0x4:
            key = self.aes_key_1
        else:
            key = self.aes_key_0
        cipher = AES.new(key, AES.MODE_GCM, nonce=self.nonce)
        plaintext = cipher.decrypt(block_bin)
        #print(str(plaintext).split("\\x"))
        #time.sleep(10)
        return plaintext

    def set_nonce(self):
        nonce_seed = [
            0x84, 0xDF, 0x11, 0xC0,
            0xAC, 0xAB, 0xFA, 0x20,
            0x33, 0x11, 0x26, 0x99,
        ]

        nonce = nonce_seed
        package_id = self.package_header.PackageID

        nonce[0] ^= (package_id >> 8) & 0xFF
        nonce[1] = 0xEA
        nonce[11] ^= package_id & 0xFF


        self.nonce = binascii.unhexlify(''.join([gf.fill_hex_with_zeros(hex(x)[2:], 2) for x in nonce]))

    def decompress_block(self, block_bin):
        decompressor = OodleDecompressor(oodlepath)
        decompressed = decompressor.decompress(block_bin)
        return decompressed

    def output_files(self, all_pkg_bin, custom_direc):
        refFile=open("refFile.txt","w")
        for entry in self.entry_table.Entries[::-1]:
            #print(entry)
            current_block_id = entry.StartingBlock
            block_offset = entry.StartingBlockOffset
            block_count = int(np.floor((block_offset + entry.FileSize - 1) / self.BLOCK_SIZE))
            #print(str(block_offset)+" - "+str(block_count))
            last_block_id = current_block_id + block_count
            file_buffer = b''  # string of length entry.Size
            while current_block_id <= last_block_id:
                current_block = self.block_table.Entries[current_block_id]
                if current_block.PatchID not in self.all_patch_ids:
                    print(f"Missing PatchID {current_block.PatchID}")
                    return
                current_pkg_data = all_pkg_bin[self.all_patch_ids.index(current_block.PatchID)]
                current_block_bin = current_pkg_data[current_block.Offset:current_block.Offset + current_block.Size]
                # We only decrypt/decompress if need to
                if current_block.Flags & 0x2:
                    # print('Going to decrypt')
                    current_block_bin = self.decrypt_block(current_block, current_block_bin)
                if current_block.Flags & 0x1:
                    # print(f'Decompressing block {current_block.ID}')
                    current_block_bin = self.decompress_block(current_block_bin)
                if current_block_id == entry.StartingBlock:
                    file_buffer = current_block_bin[block_offset:]
                else:
                    file_buffer += current_block_bin
                #print(file_buffer)
                current_block_id += 1
            fileFormat=""
            #print(entry.EntryA)
            #time.sleep(5)
            
            if entry.EntryA == "0x808045eb":
                fileFormat=".mus"
            elif entry.EntryA == "0x80808ec7": #directive table
                fileFormat=".directive"
            elif entry.EntryA == "0x80808e8e":
                fileFormat=".act"
            elif entry.EntryA == "0x80809738":  #["0x80809738","0x80808363","0x808097b8"]
                fileFormat=".aud"
            elif entry.EntryA == "0x80808363":
                fileFormat=".aud2"
            elif entry.EntryA == "0x80808e8b":
                fileFormat=".act"
            elif entry.EntryA == "0x808090d5":
                fileFormat=".amb"
            elif entry.EntryA == "0x808097b8":
                fileFormat=".tab"
            elif entry.EntryA == "0x808099f1":
                fileFormat=".str"
            elif entry.EntryA == "0x808099ef":
                fileFormat=".ref"
            
            else:
                fileFormat=".bin"
            if self.useful == ["All"]:
                fileFormat=".bin"
            if self.useful==["Cube"]:
                if entry.Type == 32:
                    if entry.SubType == 2:
                        fileFormat=".cube"
                    #elif entry.SubType == 1:
                        #fileFormat=".norm"
                elif entry.Type == 48:
                    if entry.SubType == 2:
                        fileFormat=".cdat"
            if self.useful == ["Norm"]:
                if entry.Type == 40:
                    if entry.SubType == 1:
                        fileFormat=".ndat"
                if entry.Type == 32:
                    if entry.SubType == 1:
                        refFile.write(entry.FileName.upper()+" : "+entry.EntryA+"\n")
                        fileFormat=".norm"
            if self.useful == ["Map"]:
                if entry.EntryA == "0x808093ad":  #0x28 leads to modelocclusionbounds                         #LHash->Dt->
                    fileFormat=".load"
                elif entry.EntryA == "0x80806d44":
                    fileFormat=".model"
                elif entry.EntryA == "0x80806daa": 
                    fileFormat=".model"
                elif entry.EntryA == "0x80806d30":  #modelData
                    fileFormat=".sub"
                elif entry.EntryA == "0x80808707":   #contains all data to make map  points to .dt 's
                    fileFormat=".Lhash"
                elif entry.EntryA == "0x80809883":   #A map data table, containing data entries  85988080 table for Entities and Statics 0x90 per  DynStaMapPointers
                    fileFormat=".dt"
                elif entry.EntryA == "0x8080891e":   #1 per load  Name at 0x18
                    fileFormat=".top"
                elif entry.EntryA == "0x80808701":
                    fileFormat=".mref"
                elif entry.EntryA == "0x808093b1":
                    fileFormat=".occlu"
                elif entry.EntryA == "0x80806a0d":  #points to .Load
                    fileFormat=".test"
                else:
                    fileFormat=".bin"
                if entry.Type == 40:
                    if entry.SubType == 4:
                        fileFormat=".vert"
                        #refs.write(entry.FileName+" : "+entry.EntryA+"\n")
                    if entry.SubType == 6:
                        fileFormat=".index"
                        #refs.write(entry.FileName+" : "+entry.EntryA+"\n")
            if (fileFormat != ".bin") or (self.useful == ["All"]):
                #try:
                #    os.makedirs(custom_direc + self.package_directory.split('/w64')[-1][1:-6])
                #except FileExistsError:
                #    pass
                file = io.FileIO(f'{custom_direc}/{entry.FileName.upper()}'+fileFormat, 'wb')
                # print(entry.FileSize)
                if entry.FileSize != 0:
                    writer = io.BufferedWriter(file, buffer_size=entry.FileSize)
                    writer.write(file_buffer[:entry.FileSize])
                    writer.flush()
                else:
                    with open(f'{custom_direc}/{entry.FileName.upper()}'+fileFormat, 'wb') as f:
                        f.write(file_buffer[:entry.FileSize])

            #print(f"Wrote to {entry.FileName} successfully")
        refFile.close()
def check_input(event):
    value = event.widget.get()

    if value == '':
        combo_box['values'] = lst
    else:
        data = []
        for item in lst:
            if value.lower() in item.lower():
                data.append(item)

        combo_box['values'] = data



def unpack_all(path, custom_direc, useful,filelist):
    all_packages = filelist
    i=0
    for thing in range(len(all_packages)):
        #print(i)
        if "video" in all_packages[i].split("_"):
            all_packages.remove(all_packages[i]) #videos break???
        else:
            i+=1
    #print(all_packages)
    single_pkgs = dict()
    for pkg in all_packages:
        single_pkgs[pkg[:-6]] = pkg
    #print(single_pkgs.items())
    for pkg, pkg_full in single_pkgs.items():
        if "audio" in pkg.split("_"):
            pkg = Package(f'{path}/{pkg_full}',useful)
            if useful == ["0x808099ef","0x808099f1"]:
                pkg.extract_package(extract=True, custom_direc=custom_direc)
            else:
                pkg.extract_package(extract=True, custom_direc=custom_direc+"/audio")
        elif "dialog" in pkg.split("_"):
            pkg = Package(f'{path}/{pkg_full}',useful)
            if useful == ["0x808099ef","0x808099f1"]:
                pkg.extract_package(extract=True, custom_direc=custom_direc)
            else:
                pkg.extract_package(extract=True, custom_direc=custom_direc+"/audio")
        else:
            pkg = Package(f'{path}/{pkg_full}',useful)
            pkg.extract_package(extract=True, custom_direc=custom_direc)
    print("done")
def setD2Location(loc,top):
    path=loc.get()
    MainWindow(top)

def DataView(top):
    for widget in top.winfo_children():
        widget.destroy()
    bg = PhotoImage(file = os.getcwd()+"/ThirdParty/destiny.png")
    label1 = Label(top, image = bg)
    
    Back = Button(top, text="Back", height=1, width=15,command=partial(ActivityMenu,top))
    Back.place(x=10, y=10)
    file = open("Directive.txt","r").read()
    T = Text(top, height = 500, width = 110)
    T.insert(END,file)
    T.pack()
    label1.place(x=0,y=0)
    top.mainloop()

def CutsceneView(top):
    lst=[]
    for widget in top.winfo_children():
        widget.destroy()
    for File in os.listdir(path):
        temp=File.split("_")
        if "video" in temp:
            new="_".join(temp[:(len(temp)-1)])
            if new not in lst:
                lst.append(new)
    bg = PhotoImage(file = os.getcwd()+"/ThirdParty/destiny.png")
    label1 = Label(top, image = bg)
    label1.pack()
    useful=[]
    combo_box = ttk.Combobox(top,height=20, width=30)
    combo_box['values'] = lst
    combo_box.bind('<KeyRelease>', check_input)
    combo_box.place(x=500, y=125)
    Activity = Button(top, text="Extract Cutscene (will take a while)", height=1, width=30,command=partial(CutsceneRip,combo_box))
    Activity.place(x=500, y=175)
    Back = Button(top, text="Back", height=1, width=15,command=partial(MainWindow,top))
    Back.place(x=10, y=10)
    filelist = []
    top.mainloop()
    
def CutsceneRip(box):
    global path
    currentPath=os.getcwd()
    os.chdir(currentPath+"/ThirdParty")
    pkg=box.get()
    pkgID=pkg.split("_")[len(pkg.split("_"))-1]
    print(pkgID)
    pkgPath=path
    cmd='d2.exe '+str(pkgID)+' "'+pkgPath+'"'
    print(cmd)
    temp=currentPath.split("\\")
    newPath="/".join(temp)
    ans=subprocess.call(cmd, shell=True)
    path = newPath+"/Cutscenes/"+str(pkgID)
    # Check whether the specified path exists or not
    isExist = os.path.exists(path)
    if not isExist:

       # Create a new directory because it does not exist
       os.makedirs(path)
       print("The new directory is created!")
    for File in os.listdir(currentPath+"/ThirdParty/output/"+str(pkgID)):
        shutil.move(newPath+"/ThirdParty/output/"+str(pkgID)+"/"+File,newPath+"/Cutscenes/"+str(pkgID)+"/"+File)
    os.chdir(currentPath+"/ThirdParty")
    for file in os.listdir(currentPath+"/Cutscenes/"+pkgID+"/"):
        path2file=(newPath+"/Cutscenes/"+pkgID+"/"+file)
        binFile=open(path2file,"rb")
        data=str(binFile.read(3))
        binFile.close()
        print(data)
        if data.split("'")[1] == "CRI":
            print("USM Found")
            #converting to usm
            base = os.path.splitext(path2file)[0]
            print(base)
            isExist = os.path.exists(base+".usm")
            if isExist == True:
                print("USM already exists")
                os.remove(path2file)
            else:
                os.rename(path2file, base + ".usm")
        else:
            os.remove(path2file)
    #input()
    directory=os.listdir(currentPath+"/Cutscenes/"+pkgID+"/")
    for file in directory:
        path2file=(currentPath+"/Cutscenes/"+pkgID+"/"+file)    
        cmd=("UsmToolkit.exe extract "+path2file)
        #print(cmd)
        ans=subprocess.call(cmd, shell=True)
        #print("TOOLKIT USED")
        count=0
        for subfile in os.listdir(currentPath+"/Cutscenes/"+pkgID+"/"):
            if subfile.split(".")[1] == "adx":
                print(subfile)
                count+=1
                
                if count > 2:
                    os.remove(currentPath+"/Cutscenes/"+pkgID+"/"+subfile)
                else:
                    cmd="vgmstream -o "+currentPath+"/Cutscenes/"+pkgID+"/"+subfile.split(".")[0]+".wav "+currentPath+"/Cutscenes/"+pkgID+"/"+subfile
                    print(cmd)
                    ans=subprocess.call(cmd, shell=True)
        
       
         #Combine backing and audio
        

        
        tracks=[]
        for subfile in os.listdir(currentPath+"/Cutscenes/"+pkgID+"/"):
            if subfile.split(".")[1] == "wav":
                
                #convert to mp3
                cmd="ffmpeg -i "+currentPath+"/Cutscenes/"+pkgID+"/"+subfile+" -vn -ar 44100 -ac 2 -b:a 192k "+currentPath+"/Cutscenes/"+pkgID+"/"+subfile.split(".")[0]+".mp3"
                print(cmd)
                ans=subprocess.call(cmd, shell=True,cwd=currentPath+"/ThirdParty")
                tracks.append(subfile.split(".")[0]+".mp3")
                    
                    
            elif subfile.split(".")[1] == "m2v":
                m2vFile=subfile
        #first combine
        if len(tracks) != 2:
            print("Files were not deleted or found placeholder cutscene")
            for subfile in os.listdir(currentPath+"/Cutscenes/"+pkgID+"/"):
                if subfile.split(".")[1] == "mp3":
                    os.remove(currentPath+"/Cutscenes/"+pkgID+"/"+subfile)
                elif subfile.split(".")[1] == "m2v":
                    os.remove(currentPath+"/Cutscenes/"+pkgID+"/"+subfile)
                elif subfile.split(".")[1] == "wav":
                    os.remove(currentPath+"/Cutscenes/"+pkgID+"/"+subfile)
            
        else:
            cmd="ffmpeg -i "+currentPath+"/Cutscenes/"+pkgID+"/"+m2vFile+" -i "+currentPath+"/Cutscenes/"+pkgID+"/"+tracks[0]+" -c copy "+currentPath+"/Cutscenes/"+pkgID+"/tempoutput.mp4"
            print(cmd)
            ans=subprocess.call(cmd, shell=True,cwd=currentPath+"/ThirdParty")
            "ffmpeg -i video.mkv -i audio.mp3 -map 0 -map 1:a -c:v copy -shortest output.mkv"
            cmd='ffmpeg -i '+currentPath+'/Cutscenes/'+pkgID+'/tempoutput.mp4 -i '+currentPath+'/Cutscenes/'+pkgID+'/'+tracks[1]+' -filter_complex "[0:a][1:a]amerge=inputs=2[a]" -map 0:v -map "[a]" -c:v copy -ac 2 -shortest '+currentPath+"/Cutscenes/"+pkgID+"/"+m2vFile.split(".")[0]+".mp4"
            ans=subprocess.call(cmd, shell=True,cwd=currentPath+"/ThirdParty")
            #cleanup
            for subfile in os.listdir(currentPath+"/Cutscenes/"+pkgID+"/"):
                if subfile.split(".")[1] == "mp3":
                    os.remove(currentPath+"/Cutscenes/"+pkgID+"/"+subfile)
                elif subfile.split(".")[1] == "m2v":
                    os.remove(currentPath+"/Cutscenes/"+pkgID+"/"+subfile)
                elif subfile.split(".")[1] == "wav":
                    os.remove(currentPath+"/Cutscenes/"+pkgID+"/"+subfile)
                elif subfile.split(".")[1] == "adx":
                    os.remove(currentPath+"/Cutscenes/"+pkgID+"/"+subfile)
            os.remove(currentPath+"/Cutscenes/"+pkgID+"/tempoutput.mp4")
            os.remove(path2file)
        #input()
    os.chdir(currentPath)
    Popup()

def ActivityRipper(entry):
    print("Starting ACT")
    output=open("Directive.txt","w")   #Comment out to not clear on reset
    filelist=[]
    filelist2=[]
    num=len(os.listdir(custom_direc+"/audio"))
    if entry.get() != "All":
        for file in os.listdir(path)[::-1]:
            if fnmatch.fnmatch(file,entry.get()+"*"):       #Customize this to what pkgs you need from. Can wildcard with * for all packages, or all of a certain type.
                filelist.append(file)
            if int(num) < 10:
                if fnmatch.fnmatch(file,'w64_sr_audio*'):
                    filelist2.append(file)
                if fnmatch.fnmatch(file,'w64_sr_dia*'):
                    filelist2.append(file)
    else:
        for file in os.listdir(path)[::-1]:
            if fnmatch.fnmatch(file,"w64*"):       #Customize this to what pkgs you need from. Can wildcard with * for all packages, or all of a certain type.
                filelist.append(file)
            if int(num) < 10:
                if fnmatch.fnmatch(file,'w64_sr_audio*'):
                    filelist2.append(file)
                if fnmatch.fnmatch(file,'w64_sr_dia*'):
                    filelist2.append(file)
    
    useful=["0x808045eb","0x80808e8e","0x80808ec7","0x80808e8b","0x80809650","0x80809738","0x80808363","0x808090d5","0x808097b8"]
    print("run unpack")
    unpack_all(path,custom_direc,useful,filelist)
    print(filelist2)
    useful=["0x80809738","0x80808363","0x808097b8"]
    if int(num) < 10:
        unpack_all(path,custom_direc,useful,filelist2)
    Files=[]
    print("Starting Process")
    file=open("output.txt","r")
    data=file.read()
    StrData=data.split("\n")
    file.close()
    newStrData=[]
    for String in StrData:
        try:
            int(String.split(" // ")[0])
        except ValueError:
            continue
        try:
            newStrData.append([int(String.split(" // ")[0]),String.split(" // ")[1]])
            
        except IndexError:
            #print(String)
            continue
        #print(newStrData)
    newStrData.sort(key=lambda x: x[0])
    StrData=newStrData
    for FileName in os.listdir(custom_direc):
        if FileName != "audio":
            if FileName.split(".")[1] == "act":
                file=File(FileName,FileName.split(".")[1],StrData)
                Files.append(file)
                print(FileName)
                file.FindHashes()
                print("Got HAshes")
                file.GetName()
                print("GotName")
                file.PullStrings()
                print("Got Strings")
                file.GetMusAndDir()
                print("Get Mus and Dir")
                file.GetDialogue()
    print("done")
    for file in os.listdir(custom_direc):
        if file != "audio":
            os.remove(custom_direc+"/"+file)
    Popup()
    DataView(top)
    
    
def binary_search(arr, x):
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
def StringHash(Hash,StrData):
    flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
    #print(flipped)
    dec = ast.literal_eval("0x"+flipped)
    Found=False
    ans=binary_search(StrData,int(dec))
    #print(ans)
    if str(ans) != "-1":
        Found=True
    if Found == True:
        return StrData[ans][1]
    else:
        return False
            
def ActivityMenu(top):
    lst=["All"]
    for widget in top.winfo_children():
        widget.destroy()
    bg = PhotoImage(file = os.getcwd()+"/ThirdParty/destiny.png")
    label1 = Label(top, image = bg)
    label1.pack()
    for File in os.listdir(path):
        temp=File.split("_")
        new="_".join(temp[:(len(temp)-2)])
        if new not in lst:
            lst.append(new)
    #print(lst)
    useful=[]
    combo_box = ttk.Combobox(top,height=20, width=30)
    combo_box['values'] = lst
    combo_box.bind('<KeyRelease>', check_input)
    combo_box.place(x=500, y=125)
    Activity = Button(top, text="Extract Activity Data", height=1, width=15,command=partial(ActivityRipper,combo_box))
    Activity.place(x=500, y=175)
    Back = Button(top, text="Back", height=1, width=15,command=partial(MainWindow,top))
    Back.place(x=10, y=10)
    filelist = []
    top.mainloop()
    


def Strings(ans):
    useful=[]
    filelist = []
    for file in os.listdir(path)[::-1]:
        if fnmatch.fnmatch(file,'w64*'):
            if ans == "y":
                filelist.append(file)
 
    useful=["0x808099ef","0x808099f1"]
    unpack_all(path,custom_direc,useful,filelist)
    strPath=custom_direc
    print("Outputting...")
    output=open("output.txt","w")
    output.close()
    allRefs=[]
    Files=os.listdir(strPath)
    #print(Files)
    for File in  Files:
        #print(File)
        if File != "audio":
            if File.split(".")[1] == "ref":
                allRefs.append(File)
    for Ref in allRefs:
        #print(Ref)
        file=open((strPath+"/"+Ref),"rb")
        length=len(binascii.hexlify(bytes(file.read())))
        file.close()
        RefHeader=[]
        RefLocations=[]
        RefUnknown=[] #B89F8080
        RefHashes=[]
        file=open((strPath+"/"+Ref),"rb")
        iterations=(length//8)
        for i in range(6):
            RefHeader.append(binascii.hexlify(bytes(file.read(4))).decode('utf-8'))
        count=0
        for i in range(iterations-6):
            data=binascii.hexlify(bytes(file.read(4)))
            #print(data.decode('utf-8'))
            if data.decode() == "b89f8080":
                count += 1
                break
            RefLocations.append(data.decode('utf-8'))
            count += 1
        for i in range(4):
            data=binascii.hexlify(bytes(file.read(4)))
            RefUnknown.append(data.decode('utf-8'))
        for i in range((iterations-6)-(count)-4):
            data=binascii.hexlify(bytes(file.read(4)))
            RefHashes.append(data.decode('utf-8'))
        #print(RefHeader)
        #print(RefLocations)
        #print(RefUnknown)
        #print(RefHashes)
        
        file.close()
        #output=open("outputold.txt","a")
        stringBnk=[]
        for i in range(len(RefHashes)):
            RefHashes[i]=binascii.hexlify(bytes(hex_to_little_endian(RefHashes[i]))).decode('utf-8')
            #print(int(flippedHash,16))
            
            #print(flippedLoc)
            #BnkLoc=flippedLoc.split("80a0")[1]
            #print(data)
            #print(BnkLoc)
            
        #print(stringBnk)
        flippedLoc=binascii.hexlify(bytes(hex_to_little_endian(RefLocations[0]))).decode('utf-8')
        Hash1=int("0x"+flippedLoc,base=16)
        #BnkLoc=flippedLoc.split("80a0")[1]
        #stringBnk.append(Ref.split("-")[0]+"-"+BnkLoc+".str")
        BnkHeader=[]
        BnkLengths=[]
        BnkStrings=[]
        BnkGap=[]
        #print(Hash)
        
        #RefHashes=[]
        #print(stringBnk[0])
        # Example usage
        #print(int(Hash))
        pkg = Hex_String(Package_ID(int(Hash1)))
        #print(result)
        ent = Hex_String(Entry_ID(int(Hash1)))
        Bank=pkg+"-"+ent+".str"
        try:
            Bnk=open(strPath+"/"+Bank,"rb")
        except FileNotFoundError:
            continue
        #print(Bank)
        #print("opened bnk")
        tooSmall=0
        while True:
            data=binascii.hexlify(bytes(Bnk.read(4))).decode("utf-8")
            if data == "f7998080":
                break
            BnkHeader.append(data)
            tooSmall+=1
            if tooSmall == 30:
                break
            #print("stuck")
            #print(data)
        #print(BnkHeader)
        if tooSmall == 30:
            continue
        while True:
            data=binascii.hexlify(bytes(Bnk.read(4))).decode("utf-8")
            if data == "c59d1c81":
                StrData=[]
                data=binascii.hexlify(bytes(Bnk.read(4))).decode("utf-8")
                if data == "b89f8080":
                    break
                else:
                    StrData.append(data)
                    for i in range(4):
                        data=binascii.hexlify(bytes(Bnk.read(4))).decode("utf-8")
                    data=binascii.hexlify(bytes(Bnk.read(4))).decode("utf-8")
                    StrData.append(data)
                    BnkLengths.append(StrData)
            elif data == "05008080":
                break
            #print("stuck")
        #print("notstuck")
        #for i in range(4):
        data=binascii.hexlify(bytes(Bnk.read(4))).decode("utf-8")
        BnkGap.append(data)
        #onto Str
        #print(BnkLengths)
        
        num=0
        
        for String in BnkLengths:
            out=open("output.txt","a")
            if str(list(String[0])[2]+list(String[0])[3]) != "00":
                #print("CHAT COMMAND DETECTED")
                #print(list(String[0]))
                StrLength=str(list(String[0])[2]+list(String[0])[3]+list(String[0])[0]+list(String[0])[1])
                #print(strLength)
                #break
            else:
                StrLength=str(list(String[0])[0]+list(String[0])[1])
            length=int(StrLength,16)
            #print(length)
            try:
                text=Bnk.read(length).decode()
            except UnicodeDecodeError:
                #end of file
                break
            try:
                Hash=int(RefHashes[num],16)
            except IndexError:
                #hashbroke
                Hash="HashBroke"
            #print(text)
            #print(str(Hash))
            
            textout=str(Hash)+" // "+text+"\n"
            #print(textout)
            try:
                out.write(textout)
            except UnicodeEncodeError:
                out.write(str(Hash)+" // ?\n")
            else:
                if text != "":
                    num+=1
            out.close()
                
            #print("written")
            
        Bnk.close()
        #break
    for file in os.listdir(custom_direc):
        if file != "audio":
            os.remove(custom_direc+"/"+file)
            
    Popup()

def RefDataRead():
    file=open("refFile.txt","r")
    dat=file.read()
    RefDat=dat.split("\n")
    file.close()
    return RefDat

class DDS:
    def __init__(self,Name,Type):
        self.CWD=os.getcwd()
        if Type == "Cube":
            self.SaveLoc=os.getcwd()+"/Textures/Cubemaps"
        else:
            self.SaveLoc=os.getcwd()+"/Textures"
        self.FileName=Name
        self.ReadData()
        if Type == "Norm":
            self.RefDat=RefDataRead()
            self.ProcessNorm()
            self.OutputNorm()
        else:
            self.Process()
            self.Output()
    def ReadData(self):
        File=open(custom_direc+"/"+self.FileName,"rb")
        File.seek(0x4)
        self.texFormat=binascii.hexlify(bytes(File.read(2))).decode()
        File.seek(0x22)
        self.width=binascii.hexlify(bytes(File.read(2))).decode()
        flipped=binascii.hexlify(bytes(hex_to_little_endian(self.width))).decode('utf-8')
        self.width=(ast.literal_eval("0x"+flipped))
        #print(self.width)
        self.height=binascii.hexlify(bytes(File.read(2))).decode()
        flipped=binascii.hexlify(bytes(hex_to_little_endian(self.height))).decode('utf-8')
        self.height=(ast.literal_eval("0x"+flipped))
        #print(self.height)
        File.seek(0x28)
        self.arraySize=binascii.hexlify(bytes(File.read(2))).decode()
        flipped=binascii.hexlify(bytes(hex_to_little_endian(self.arraySize))).decode('utf-8')
        self.arraySize=ast.literal_eval("0x"+stripZeros(flipped))
        File.seek(0x3C)
        self.Hash=binascii.hexlify(bytes(File.read(4))).decode()
        self.Hash=binascii.hexlify(bytes(hex_to_little_endian(self.Hash))).decode('utf-8')
        File.close()
    def ProcessNorm(self):
        self.dxtmiscFlags2 = ""
        self.compressed=False
        flipped=binascii.hexlify(bytes(hex_to_little_endian(self.texFormat))).decode('utf-8')
        new=ast.literal_eval("0x"+stripZeros(flipped))
        #print(new)
        if (70< new < 99):
            self.compressed=True
        self.Norm=new
        self.texFormat=c_uint32(new)
        self.MagicNumber = c_uint32(542327876)
        self.dwSize = c_uint32(124)
        self.dwFlags = c_uint32((0x1 + 0x2 + 0x4 + 0x1000) + 0x8)
        self.dwHeight = c_uint32(self.height)
        self.dwWidth= c_uint32(self.width)
        self.dwPitchOrLinearSize = c_uint32(0)
        self.dwDepth = c_uint32(0)
        self.dwMipMapCount = c_uint32(0)
        self.dwReserved1 = c_uint32(0)
        self.dwPFSize = c_uint32(32)
        self.dwPFRGBBitCount = c_uint32(0)
        self.dwPFRGBBitCount = c_uint32(32)
        self.dwPFRBitMask = c_uint32(0xFF)
        self.dwPFGBitMask = c_uint32(0xFF00)
        self.dwPFBBitMask = c_uint32(0xFF0000)
        self.dwPFABitMask = c_uint32(0xFF000000)
        self.dwCaps = c_uint32(0x1000)
        self.dwCaps2 = c_uint32(0x0)
        self.dwCaps3 = c_uint32(0)
        self.dwCaps4 = c_uint32(0)
        self.dwReserved2 = c_uint32(0)
        #print(self.compressed)
        if self.compressed == True:
            self.dwPFFlags = c_uint32(0x1 + 0x4) 
            self.dwPFFourCC = c_uint32(808540228)
            self.dxtdxgiFormat = c_uint32(new)
            self.dxtresourceDimension = c_uint32(3)
            if (self.arraySize % 6) == 0:
                self.dxtmiscFlag = c_uint32(4)
                self.dxtArraySize = c_uint32(self.arraySize // 6)
            else:
                self.dxtmiscFlag = c_uint32(0)
                self.dxtArraySize = c_uint32(1)
        else:
            self.dwPFFlags = c_uint32(0x1 + 0x4)  # contains alpha data + contains uncompressed RGB data
            self.dwPFFourCC = c_uint32(808540228)
            self.dxtmiscFlag = c_uint32(0)
            self.dxtArraySize = c_uint32(1)
            self.dxtmiscFlags2 = c_uint32(0x1)
            self.dxtdxgiFormat = c_uint32(new)
            self.dxtresourceDimension = c_uint32(3)
        self.arraySize=c_uint32(self.arraySize)
    def Process(self):
        self.dxtmiscFlags2 = ""
        self.compressed=False
        flipped=binascii.hexlify(bytes(hex_to_little_endian(self.texFormat))).decode('utf-8')
        new=ast.literal_eval("0x"+stripZeros(flipped))
        if (70< new < 99):
            self.compressed=True
        self.texFormat=c_uint32(new)
        self.MagicNumber = c_uint32(542327876)
        self.dwSize = c_uint32(124)
        self.dwFlags = c_uint32((0x1 + 0x2 + 0x4 + 0x1000) + 0x8)
        self.dwHeight = c_uint32(self.height)
        self.dwWidth= c_uint32(self.width)
        self.dwPitchOrLinearSize = c_uint32(0)
        self.dwDepth = c_uint32(0)
        self.dwMipMapCount = c_uint32(0)
        self.dwReserved1 = c_uint32(0)
        self.dwPFSize = c_uint32(32)
        self.dwPFRGBBitCount = c_uint32(0)
        self.dwPFRGBBitCount = c_uint32(32)
        self.dwPFRBitMask = c_uint32(0xFF)
        self.dwPFGBitMask = c_uint32(0xFF00)
        self.dwPFBBitMask = c_uint32(0xFF0000)
        self.dwPFABitMask = c_uint32(0xFF000000)
        self.dwCaps = c_uint32(0x1000)
        self.dwCaps2 = c_uint32(0x200)
        self.dwCaps3 = c_uint32(0)
        self.dwCaps4 = c_uint32(0)
        self.dwReserved2 = c_uint32(0)
        if self.compressed == True:
            self.dwPFFlags = c_uint32(0x1 + 0x4 ) 
            self.dwPFFourCC = c_uint32(808540228)
            self.dxtdxgiFormat = self.texFormat
            self.dxtresourceDimension = c_uint32(3)
            if (self.arraySize % 6) == 0:
                self.dxtmiscFlag = c_uint32(4)
                self.dxtArraySize = c_uint32(self.arraySize // 6)
            else:
                self.dxtmiscFlag = c_uint32(0)
                self.dxtArraySize = c_uint32(1)
        else:
            self.dxtdwPFFlags = c_uint32(0x1 + 0x40)  # contains alpha data + contains uncompressed RGB data
            self.dxtdwPFFourCC = c_uint32(0)
            self.dxtmiscFlag = c_uint32(0)
            self.dxtArraySize = c_uint32(1)
            self.dxtmiscFlags2 = c_uint32(0x1)
        self.arraySize=c_uint32(self.arraySize)
    def OutputNorm(self):
        File=open(self.FileName.split(".")[0]+".dds","wb")
        thingsToAdd=[self.MagicNumber,self.dwSize,self.dwFlags,self.dwHeight,self.dwWidth,self.dwPitchOrLinearSize,self.dwDepth,self.dwMipMapCount,self.dwReserved1,self.dwReserved1,self.dwReserved1,self.dwReserved1,self.dwReserved1,self.dwReserved1,self.dwReserved1,self.dwReserved1,self.dwReserved1,self.dwReserved1,self.dwReserved1,self.dwPFSize,self.dwPFFlags,self.dwPFFourCC,self.dwPFRGBBitCount,self.dwPFRBitMask,self.dwPFGBitMask,self.dwPFBBitMask,self.dwPFABitMask,self.dwCaps,self.dwCaps2,self.dwCaps3,self.dwCaps4,self.dwReserved2]
        new=0
        for thing in thingsToAdd:
            File.write(thing)
        thingsToAdd=[self.dxtdxgiFormat,self.dxtresourceDimension,self.dxtmiscFlag,self.dxtArraySize]
        for thing in thingsToAdd:
            File.write(thing)
        if self.dxtmiscFlags2 != "":
            File.write(c_uint32(659757824))
        else:
            File.write(c_uint32(0))
        if self.Hash.upper() == "FFFFFFFF":
            for Line in self.RefDat:
                temp=Line.split(" : ")
                if temp[0].upper() == self.FileName.split(".")[0].upper():
                    new=ast.literal_eval(temp[1])
        else:
            new=ast.literal_eval("0x"+self.Hash)
        DirName=Hex_String(Package_ID(new))+"-"+Hex_String(Entry_ID(new))+".ndat"
        try:
            file2=open(self.CWD+"/out/"+DirName,"rb")
        except FileNotFoundError:
            print("Other Package, use other tool")
        else:
            Data=file2.read()
            file2.close()
            File.write(Data)
            File.close()       
            #cmd="texassemble.exe h-cross "+self.FileName.split(".")[0]+".dds"+" -y -nologo -o "+self.FileName.split(".")[0]+".bmp"
            #os.system('cmd /c '+cmd)
            DXGI_FORMAT = [
            "UNKNOWN",
            "R32G32B32A32_TYPELESS",
            "R32G32B32A32_FLOAT",
            "R32G32B32A32_UINT",
            "R32G32B32A32_SINT",
            "R32G32B32_TYPELESS",
            "R32G32B32_FLOAT",
            "R32G32B32_UINT",
            "R32G32B32_SINT",
            "R16G16B16A16_TYPELESS",
            "R16G16B16A16_FLOAT",
            "R16G16B16A16_UNORM",
            "R16G16B16A16_UINT",
            "R16G16B16A16_SNORM",
            "R16G16B16A16_SINT",
            "R32G32_TYPELESS",
            "R32G32_FLOAT",
            "R32G32_UINT",
            "R32G32_SINT",
            "R32G8X24_TYPELESS",
            "D32_FLOAT_S8X24_UINT",
            "R32_FLOAT_X8X24_TYPELESS",
            "X32_TYPELESS_G8X24_UINT",
            "R10G10B10A2_TYPELESS",
            "R10G10B10A2_UNORM",
            "R10G10B10A2_UINT",
            "R11G11B10_FLOAT",
            "R8G8B8A8_TYPELESS",
            "R8G8B8A8_UNORM",
            "R8G8B8A8_UNORM_SRGB",
            "R8G8B8A8_UINT",
            "R8G8B8A8_SNORM",
            "R8G8B8A8_SINT",
            "R16G16_TYPELESS",
            "R16G16_FLOAT",
            "R16G16_UNORM",
            "R16G16_UINT",
            "R16G16_SNORM",
            "R16G16_SINT",
            "R32_TYPELESS",
            "D32_FLOAT",
            "R32_FLOAT",
            "R32_UINT",
            "R32_SINT",
            "R24G8_TYPELESS",
            "D24_UNORM_S8_UINT",
            "R24_UNORM_X8_TYPELESS",
            "X24_TYPELESS_G8_UINT",
            "R8G8_TYPELESS",
            "R8G8_UNORM",
            "R8G8_UINT",
            "R8G8_SNORM",
            "R8G8_SINT",
            "R16_TYPELESS",
            "R16_FLOAT",
            "D16_UNORM",
            "R16_UNORM",
            "R16_UINT",
            "R16_SNORM",
            "R16_SINT",
            "R8_TYPELESS",
            "R8_UNORM",
            "R8_UINT",
            "R8_SNORM",
            "R8_SINT",
            "A8_UNORM",
            "R1_UNORM",
            "R9G9B9E5_SHAREDEXP",
            "R8G8_B8G8_UNORM",
            "G8R8_G8B8_UNORM",
            "BC1_TYPELESS",
            "BC1_UNORM",
            "BC1_UNORM_SRGB",
            "BC2_TYPELESS",
            "BC2_UNORM",
            "BC2_UNORM_SRGB",
            "BC3_TYPELESS",
            "BC3_UNORM",
            "BC3_UNORM_SRGB",
            "BC4_TYPELESS",
            "BC4_UNORM",
            "BC4_SNORM",
            "BC5_TYPELESS",
            "BC5_UNORM",
            "BC5_SNORM",
            "B5G6R5_UNORM",
            "B5G5R5A1_UNORM",
            "B8G8R8A8_UNORM",
            "B8G8R8X8_UNORM",
            "R10G10B10_XR_BIAS_A2_UNORM",
            "B8G8R8A8_TYPELESS",
            "B8G8R8A8_UNORM_SRGB",
            "B8G8R8X8_TYPELESS",
            "B8G8R8X8_UNORM_SRGB",
            "BC6H_TYPELESS",
            "BC6H_UF16",
            "BC6H_SF16",
            "BC7_TYPELESS",
            "BC7_UNORM",
            "BC7_UNORM_SRGB",
            "AYUV",
            "Y410",
            "Y416",
            "NV12",
            "P010",
            "P016",
            "420_OPAQUE",
            "YUY2",
            "Y210",
            "Y216",
            "NV11",
            "AI44",
            "IA44",
            "P8",
            "A8P8",
            "B4G4R4A4_UNORM",
            "P208",
            "V208",
            "V408",
            "SAMPLER_FEEDBACK_MIN_MIP_OPAQUE",
            "SAMPLER_FEEDBACK_MIP_REGION_USED_OPAQUE",
            "FORCE_UINT"]
            dxgiFormat = DXGI_FORMAT[self.Norm]
            if str(self.Norm) == "28":
                dxgiFormat=dxgiFormat+"_SRGB"
            os.chdir(self.CWD+"/ThirdParty")   
            cmd='texconv.exe "'+self.CWD+"\\"+self.FileName.split(".")[0]+'.dds" -y -nologo -srgb -ft PNG -f '+dxgiFormat+' -o '+self.SaveLoc
            print(cmd)
            subprocess.call(cmd, shell=True)
            os.chdir(self.CWD)
            #os.remove(self.FileName.split(".")[0]+".bmp")
            os.remove(self.FileName.split(".")[0]+".dds")
    def Output(self):
        File=open(self.FileName.split(".")[0]+".dds","wb")
        thingsToAdd=[self.MagicNumber,self.dwSize,self.dwFlags,self.dwHeight,self.dwWidth,self.dwPitchOrLinearSize,self.dwDepth,self.dwMipMapCount,self.dwReserved1,self.dwReserved1,self.dwReserved1,self.dwReserved1,self.dwReserved1,self.dwReserved1,self.dwReserved1,self.dwReserved1,self.dwReserved1,self.dwReserved1,self.dwReserved1,self.dwPFSize,self.dwPFFlags,self.dwPFFourCC,self.dwPFRGBBitCount,self.dwPFRBitMask,self.dwPFGBitMask,self.dwPFBBitMask,self.dwPFABitMask,self.dwCaps,self.dwCaps2,self.dwCaps3,self.dwCaps4,self.dwReserved2]
        for thing in thingsToAdd:
            File.write(thing)
        thingsToAdd=[self.dxtdxgiFormat,self.dxtresourceDimension,self.dxtmiscFlag,self.dxtArraySize]
        for thing in thingsToAdd:
            File.write(thing)
        if self.dxtmiscFlags2 != "":
            File.write(self.dxtmiscFlags2)
        else:
            File.write(c_uint32(0))
        new=ast.literal_eval("0x"+self.Hash)
        DirName=Hex_String(Package_ID(new))+"-"+Hex_String(Entry_ID(new))+".cdat"
        file2=open(custom_direc+"/"+DirName,"rb")
        Data=file2.read()
        file2.close()
        File.write(Data)
        File.close()
        os.chdir(self.CWD+"/ThirdParty")
        cmd="texassemble.exe h-cross "+self.CWD+"/"+self.FileName.split(".")[0]+".dds"+" -y -nologo -o "+self.CWD+"/"+self.FileName.split(".")[0]+".bmp"
        print(cmd)
        subprocess.call(cmd, shell=True) 
        DXGI_FORMAT = [
        "UNKNOWN",
	"R32G32B32A32_TYPELESS",
	"R32G32B32A32_FLOAT",
	"R32G32B32A32_UINT",
	"R32G32B32A32_SINT",
	"R32G32B32_TYPELESS",
	"R32G32B32_FLOAT",
	"R32G32B32_UINT",
	"R32G32B32_SINT",
	"R16G16B16A16_TYPELESS",
	"R16G16B16A16_FLOAT",
	"R16G16B16A16_UNORM",
	"R16G16B16A16_UINT",
	"R16G16B16A16_SNORM",
	"R16G16B16A16_SINT",
	"R32G32_TYPELESS",
	"R32G32_FLOAT",
	"R32G32_UINT",
	"R32G32_SINT",
	"R32G8X24_TYPELESS",
	"D32_FLOAT_S8X24_UINT",
	"R32_FLOAT_X8X24_TYPELESS",
	"X32_TYPELESS_G8X24_UINT",
	"R10G10B10A2_TYPELESS",
	"R10G10B10A2_UNORM",
	"R10G10B10A2_UINT",
	"R11G11B10_FLOAT",
	"R8G8B8A8_TYPELESS",
	"R8G8B8A8_UNORM",
	"R8G8B8A8_UNORM_SRGB",
	"R8G8B8A8_UINT",
	"R8G8B8A8_SNORM",
	"R8G8B8A8_SINT",
	"R16G16_TYPELESS",
	"R16G16_FLOAT",
	"R16G16_UNORM",
	"R16G16_UINT",
	"R16G16_SNORM",
	"R16G16_SINT",
	"R32_TYPELESS",
	"D32_FLOAT",
	"R32_FLOAT",
	"R32_UINT",
	"R32_SINT",
	"R24G8_TYPELESS",
	"D24_UNORM_S8_UINT",
	"R24_UNORM_X8_TYPELESS",
	"X24_TYPELESS_G8_UINT",
	"R8G8_TYPELESS",
	"R8G8_UNORM",
	"R8G8_UINT",
	"R8G8_SNORM",
	"R8G8_SINT",
	"R16_TYPELESS",
	"R16_FLOAT",
	"D16_UNORM",
	"R16_UNORM",
	"R16_UINT",
	"R16_SNORM",
	"R16_SINT",
	"R8_TYPELESS",
	"R8_UNORM",
	"R8_UINT",
	"R8_SNORM",
	"R8_SINT",
	"A8_UNORM",
	"R1_UNORM",
	"R9G9B9E5_SHAREDEXP",
	"R8G8_B8G8_UNORM",
	"G8R8_G8B8_UNORM",
	"BC1_TYPELESS",
	"BC1_UNORM",
	"BC1_UNORM_SRGB",
	"BC2_TYPELESS",
	"BC2_UNORM",
	"BC2_UNORM_SRGB",
	"BC3_TYPELESS",
	"BC3_UNORM",
	"BC3_UNORM_SRGB",
	"BC4_TYPELESS",
	"BC4_UNORM",
	"BC4_SNORM",
	"BC5_TYPELESS",
	"BC5_UNORM",
	"BC5_SNORM",
	"B5G6R5_UNORM",
	"B5G5R5A1_UNORM",
	"B8G8R8A8_UNORM",
	"B8G8R8X8_UNORM",
	"R10G10B10_XR_BIAS_A2_UNORM",
	"B8G8R8A8_TYPELESS",
	"B8G8R8A8_UNORM_SRGB",
	"B8G8R8X8_TYPELESS",
	"B8G8R8X8_UNORM_SRGB",
	"BC6H_TYPELESS",
	"BC6H_UF16",
	"BC6H_SF16",
	"BC7_TYPELESS",
	"BC7_UNORM",
	"BC7_UNORM_SRGB",
	"AYUV",
	"Y410",
	"Y416",
	"NV12",
	"P010",
	"P016",
	"420_OPAQUE",
	"YUY2",
	"Y210",
	"Y216",
	"NV11",
	"AI44",
	"IA44",
	"P8",
	"A8P8",
	"B4G4R4A4_UNORM",
	"P208",
	"V208",
	"V408",
	"SAMPLER_FEEDBACK_MIN_MIP_OPAQUE",
	"SAMPLER_FEEDBACK_MIP_REGION_USED_OPAQUE",
	"FORCE_UINT"]
        #dxgiFormat = DXGI_FORMAT[self.texFormat]
        cmd="texconv.exe "+self.CWD+"\\"+self.FileName.split(".")[0]+".bmp -y -nologo -ft PNG -o "+self.SaveLoc
        subprocess.call(cmd, shell=True)
        #print(cmd)
        os.chdir(self.CWD)
        os.remove(self.FileName.split(".")[0]+".bmp")
        os.remove(self.FileName.split(".")[0]+".dds")
    
def Hash64(packagesPath):
    file1=open("h64.txt","w")
    filelist = []
    for file in os.listdir(packagesPath)[::-1]:
        if fnmatch.fnmatch(file,'w64_*'):
            filelist.append(file)
    pkgIDs = set()
    hash64Table = {}
    # Getting all packages
    count=0
    for entry in filelist:
        count+=1
        pkgPath = packagesPath+"/"+entry
        #print(pkgPath)
        with open(pkgPath, "rb") as pkgFile:
            # Hash64 Table
            pkgFile.seek(0xB8)
            hash64TableCountBytes = pkgFile.read(4)
            hash64TableCount = struct.unpack("<I", hash64TableCountBytes)[0]
            #print(hash64TableCount)
            if hash64TableCount == 0:
                #print("empty")
                continue
            hash64TableOffsetBytes = pkgFile.read(4)
            hash64TableOffset = struct.unpack("<I", hash64TableOffsetBytes)[0]
            hash64TableOffset += 64 + 0x10

            for i in range(hash64TableOffset, hash64TableOffset + hash64TableCount * 0x10, 0x10):
                pkgFile.seek(i)
                h64ValBytes = binascii.hexlify(bytes(pkgFile.read(8))).decode()
                flipped=binascii.hexlify(bytes(hex_to_little_endian(h64ValBytes))).decode('utf-8')
                hValBytes = binascii.hexlify(bytes(pkgFile.read(4))).decode()
                flipped2=binascii.hexlify(bytes(hex_to_little_endian(hValBytes))).decode('utf-8')
                file1.write(str("0x"+flipped)+": "+str("0x"+flipped2)+"\n")
    file1.close()
def ClearDir(top):
    for file in os.listdir(os.getcwd()+"/out"):
        if file != "audio":
            os.remove(os.getcwd()+"/out/"+file)
    Popup()
def ClearMaps(top):
    for file in os.listdir(os.getcwd()+"/data/Statics/Statics"):
        os.remove(os.getcwd()+"/data/Statics/Statics/"+file)
    for file in os.listdir(os.getcwd()+"/data/Statics/Instances"):
        os.remove(os.getcwd()+"/data/Statics/Instances/"+file)
    Popup()
def ClearTextures(top):
    for file in os.listdir(os.getcwd()+"/Textures"):
        if file != "cubemaps":
            os.remove(os.getcwd()+"/Textures/"+file)
    for file in os.listdir(os.getcwd()+"/Textures/Cubemaps"):
        os.remove(os.getcwd()+"/Textures/Cubemaps/"+file)
    Popup()
def ClearAudio(top):
    for File in os.listdir(os.getcwd()+"/out/audio"):
        os.remove(os.getcwd()+"/out/audio/"+File)
    Popup()
    #MainWindow(top)
def DevMenu():
    lst=[]
    for widget in top.winfo_children():
        widget.destroy()
    bg = PhotoImage(file = os.getcwd()+"/ThirdParty/destiny.png")
    label1 = Label(top, image = bg)
    label1.pack()
    for File in os.listdir(path):
        temp=File.split("_")
        new="_".join(temp[:(len(temp)-2)])
        if new not in lst:
            lst.append(new)
    #print(lst)
    useful=[]
    combo_box = ttk.Combobox(top,height=20, width=30)
    combo_box['values'] = lst
    combo_box.bind('<KeyRelease>', check_input)
    combo_box.place(x=500, y=125)
    Activity = Button(top, text="Extract Dev Strings", height=1, width=15,command=partial(DevRipper,combo_box))
    Activity.place(x=500, y=175)
    Back = Button(top, text="Back", height=1, width=15,command=partial(MainWindow,top))
    Back.place(x=10, y=10)
    filelist = []
    top.mainloop()
def DevRipper(entry):
    filelist=[]
    for file in os.listdir(path)[::-1]:
            if fnmatch.fnmatch(file,entry.get()+"*"):       #Customize this to what pkgs you need from. Can wildcard with * for all packages, or all of a certain type.
                filelist.append(file)
 
    useful=["All"]
    unpack_all(path,custom_direc,useful,filelist)
    Dev=open("mechout.txt","w")
    Dev.close()
    Dev=open("mechout.txt","a")
    for File in os.listdir(custom_direc):
        if File != "audio":
            file=open(custom_direc+"/"+File,"rb")
            Data=binascii.hexlify(bytes(file.read())).decode()
            count=0
            Data=[Data[i:i+8] for i in range(0, len(Data), 8)]
            for Hash in Data:
                if Hash == "65008080":
                    string="".join(Data[count+2:])
                    #print(File)
                    try:
                        temp=bytearray.fromhex(string).decode()
                    except:
                        continue
                    else:
                        temp2=temp.split(" ")
                        
                        Dev.write("/".join(temp2)+"\n")
                
                                   
                count+=1
    Dev.close()
    for file in os.listdir(os.getcwd()+"/out"):
        if file != "audio":
            os.remove(os.getcwd()+"/out/"+file)
    Popup()
def Popup():
    tkinter.messagebox.showinfo(" ", "Done")
def NormalRipper(entry,Type):
    filelist=[]
    if Type == "Single":
        for file in os.listdir(path)[::-1]:
            if fnmatch.fnmatch(file,entry.get()+"*"):
                filelist.append(file)
    else:
        temp=entry.get().split("_")
        print(temp)
        new="_".join(temp[:len(temp)-1])
        print(new)
        for file in os.listdir(path)[::-1]:
            if fnmatch.fnmatch(file,new+"*"):
                filelist.append(file)
    useful=["Norm"]
    unpack_all(path,custom_direc,useful,filelist)
    lengths=[]
    for File in os.listdir(custom_direc):
        if File != "audio":
            if File.split(".")[1] == "norm":
                Tex=DDS(File,"Norm")
    for file in os.listdir(os.getcwd()+"/out"):
        if file != "audio":
            os.remove(os.getcwd()+"/out/"+file)
    Popup()
def twos_complement(hexstr, bits):
    value = int(hexstr, 16)
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value
class LoadZone:
    def __init__(self,Name,InstCount,Ref):
        self.FileName=Name
        self.Statics=[]
        self.StaticMeta=[]
        self.Ref=Ref
        self.CWD=os.getcwd()
        self.DynNames=[]
        self.DynInstances=[]
        self.PullStatics()
        self.ExtractFBX()
        self.InstCount=InstCount
        #if ans.upper() == "Y":
        #self.RipStatics()
        self.RipOwnStatics()
        self.PullStaticMeta()
        self.PullStaticData()
        self.OutputCFG()
        #self.PullDyns()
        #self.RipDyns()
        
        #print(self.Statics)
        #print(str(len(self.Statics)))
    def RipDyns(self):
        for Dyn in self.DynNames:
            cmd='MDE -p "'+path+'" -o "C:/Users/sjcap/Desktop/MyUnpacker/DestinyUnpackerNew/new/MapExtracter/data/Statics/Statics" -i '+Dyn.upper()
            print(cmd)
            ans=subprocess.call(cmd, shell=True)
            
            
    def PullDyns(self):
        print(self.Ref)
        file=open(custom_direc+"/"+self.Ref,"rb")
        Tables=[]
        file.seek(0x50)
        dat=binascii.hexlify(bytes(file.read())).decode()
        Data=[dat[i:i+8] for i in range(0, len(dat), 8)]
        file.close()
        self.DynNames=[]
        self.DynInstances=[]
        for Hash in Data:
            flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
            num=ast.literal_eval("0x"+flipped)
            Name=Hex_String(Package_ID(num))+"-"+Hex_String(Entry_ID(num))
            if Name not in Tables:
                Tables.append(Name)
        for Table in Tables:
            file=open(custom_direc+"/"+Table+".dt","rb")
            Length=file.read()
            if len(Length) < 144:
                continue
            file.close()
            file=open(custom_direc+"/"+Table+".dt","rb")
            file.seek(0x20)
            Num=binascii.hexlify(bytes(file.read(1))).decode()
            Num=ast.literal_eval("0x"+Num)
            file.seek(0x28)
            temp=binascii.hexlify(bytes(file.read(4))).decode()

            if temp == "85988080":
                #print(Table)
                file.seek(0x30)
                Data=binascii.hexlify(bytes(file.read())).decode()
                Data=[Data[i:i+288] for i in range(0, len(Data), 288)]
                count=0
                for Dyn in Data:
                    if count >= Num:
                        break
                    #print(Dyn)
                    count+=1
                    DynDat=[Dyn[i:i+8] for i in range(0, len(Dyn), 8)]
                    #print(DynDat)
                    rotX=binascii.hexlify(bytes(hex_to_little_endian(DynDat[0]))).decode('utf-8')
                    rotY=binascii.hexlify(bytes(hex_to_little_endian(DynDat[1]))).decode('utf-8')
                    rotZ=binascii.hexlify(bytes(hex_to_little_endian(DynDat[2]))).decode('utf-8')
                    rotW=binascii.hexlify(bytes(hex_to_little_endian(DynDat[3]))).decode('utf-8')
                    PosX=binascii.hexlify(bytes(hex_to_little_endian(DynDat[4]))).decode('utf-8')
                    PosY=binascii.hexlify(bytes(hex_to_little_endian(DynDat[5]))).decode('utf-8')
                    PosZ=binascii.hexlify(bytes(hex_to_little_endian(DynDat[6]))).decode('utf-8')
                    ScaleX=binascii.hexlify(bytes(hex_to_little_endian(DynDat[7]))).decode('utf-8')
                    rotX=struct.unpack('!f', bytes.fromhex(rotX))[0]
                    rotY=struct.unpack('!f', bytes.fromhex(rotY))[0]
                    rotZ=struct.unpack('!f', bytes.fromhex(rotZ))[0]
                    rotW=struct.unpack('!f', bytes.fromhex(rotW))[0]
                    PosX=struct.unpack('!f', bytes.fromhex(PosX))[0]
                    PosY=struct.unpack('!f', bytes.fromhex(PosY))[0]
                    PosZ=struct.unpack('!f', bytes.fromhex(PosZ))[0]
                    ScaleX=struct.unpack('!f', bytes.fromhex(ScaleX))[0]
                    Name=binascii.hexlify(bytes(hex_to_little_endian(DynDat[12]+DynDat[13]))).decode('utf-8')
                    ValidDyn=False
                    for Line1 in Hash64Data:
                        Lines=Line1.split(": ")
                        #print(Lines)
                        if Lines[0].lower() == str("0x"+Name):
                            temp=list(Lines[1])
                            temp="".join(temp[2:])
                            DynHash=binascii.hexlify(bytes(hex_to_little_endian(temp))).decode('utf-8')
                            print(DynHash)
                            if DynHash not in self.DynNames:
                                
                                print(Table)
                                self.DynNames.append(DynHash)
                            ValidDyn=True
                    if ValidDyn == True:
                        file1=open("C:/Users/sjcap/Desktop/MyUnpacker/DestinyUnpackerNew/new/MapExtracter/data/Statics/Instances/"+DynHash.lower()+".inst","a")
                        file1.write(str(rotX)+","+str(rotY)+","+str(rotZ)+","+str(rotW)+","+str(PosX)+","+str(PosY)+","+str(PosZ)+","+str(ScaleX)+"\n")
                        file1.close()


                    
                    
                    
                
                    
        
    def PullStatics(self):
        print(self.FileName)
        file=open(custom_direc+"/"+self.FileName,"rb")
        Data=binascii.hexlify(bytes(file.read())).decode()
        Data=[Data[i:i+8] for i in range(0, len(Data), 8)]
        count=0
        for Hash in Data:
            if Hash == "bd938080":
                for Hash2 in Data[count+2:len(Data)]:
                    if Hash2 == "b89f8080":
                        break
                    else:
                        if Hash2 == "00000000":
                            break
                        else:
                            self.Statics.append(Hash2)
                break
            count+=1
        #print("STATLEN")
        #print(len(self.Statics))
        #print(self.Statics)
    def PullStaticMeta(self):
        file=open(custom_direc+"/"+self.FileName,"rb")
        Data=binascii.hexlify(bytes(file.read())).decode()
        Data=[Data[i:i+16] for i in range(0, len(Data), 16)]
        count=0
        self.StaticMeta=[]
        for StaticDat in Data:
            if "286d8080" in StaticDat:
                self.StaticMeta=Data[count+1:len(Data)]
            count+=1
        #print("META")
        #print(self.StaticMeta)

    def OutputCFG(self):
        count=0
        countAll=0
        #print(len(self.StaticMeta))
        print(len(self.StaticData))
        print(self.InstCount)
        #print(len(self.Statics))
        count=0
        Tally=0
        for Static in self.StaticMeta:
            Data=[Static[i:i+4] for i in range(0, len(Static), 4)]
            #print(Data[1])#Static[0] Count [1]-Offset [2]=Index 3[unk]
            #print(count)
            flipped=binascii.hexlify(bytes(hex_to_little_endian(Data[0]))).decode('utf-8')
            #flippedTest=binascii.hexlify(bytes(hex_to_little_endian(Data[1]))).decode('utf-8')
            #print(ast.literal_eval("0x"+stripZeros(flippedTest)))
            flipped2=binascii.hexlify(bytes(hex_to_little_endian(Data[2]))).decode('utf-8')
            NumofInstance=ast.literal_eval("0x"+stripZeros(flipped))
            print(count)
            Index=ast.literal_eval("0x"+stripZeros(flipped2))
            Tally+=NumofInstance
            #print(Index)
            #print(NumofInstance)
            #print(self.Statics[Index])
            file=open(self.CWD+"/data/Statics/Instances/"+self.Statics[Index]+".inst","a")
      
            for i in range(int(NumofInstance)):
                try:
                    data=",".join(self.StaticData[count])
                except IndexError:
                    print("RanOutofData")
                    break
                text=str(data)
                file.write(text+"\n")
                count+=1
            #print(count)
            file.close()
        print(Tally)
            
            
    def PullStaticData(self):
        self.StaticData=[]
        file=open(custom_direc+"/"+self.FileName,"rb")
        print(self.FileName)
        Data=binascii.hexlify(bytes(file.read())).decode()
        file.close()
        Data=[Data[i:i+32] for i in range(0, len(Data), 32)]
        print(Data[0])
        count=0
        dataStarted=False
        for Line in Data:
            temp=[Line[i:i+8] for i in range(0, len(Line), 8)]
            #print(temp)
            if "406d8080" in temp:
                dataStarted=True
                countStart=count
                tempData=Data[countStart+1:countStart+int((self.InstCount)*4)]
                break
            count+=1
        Data="".join(tempData)
        Data=[Data[i:i+128] for i in range(0, len(Data), 128)]
        Data=Data[:int(self.InstCount)-1]
        for StatDat in Data:
            temp=[StatDat[i:i+2] for i in range(0, len(StatDat), 2)]
            Rotations="".join(temp[0:16])
            Position="".join(temp[16:28])
            Scale="".join(temp[28:40])
            RotDat=[Rotations[i:i+8] for i in range(0, len(Rotations), 8)]
            rotX=binascii.hexlify(bytes(hex_to_little_endian(RotDat[0]))).decode('utf-8')
            rotY=binascii.hexlify(bytes(hex_to_little_endian(RotDat[1]))).decode('utf-8')
            rotZ=binascii.hexlify(bytes(hex_to_little_endian(RotDat[2]))).decode('utf-8')
            rotW=binascii.hexlify(bytes(hex_to_little_endian(RotDat[3]))).decode('utf-8')
            PosDat=[Position[i:i+8] for i in range(0, len(Position), 8)]
            PosX=binascii.hexlify(bytes(hex_to_little_endian(PosDat[0]))).decode('utf-8')
            PosY=binascii.hexlify(bytes(hex_to_little_endian(PosDat[1]))).decode('utf-8')
            PosZ=binascii.hexlify(bytes(hex_to_little_endian(PosDat[2]))).decode('utf-8')
            ScaleDat=[Scale[i:i+8] for i in range(0, len(Scale), 8)]
            ScaleX=binascii.hexlify(bytes(hex_to_little_endian(ScaleDat[0]))).decode('utf-8')
            rotX=struct.unpack('!f', bytes.fromhex(rotX))[0]
            rotY=struct.unpack('!f', bytes.fromhex(rotY))[0]
            rotZ=struct.unpack('!f', bytes.fromhex(rotZ))[0]
            rotW=struct.unpack('!f', bytes.fromhex(rotW))[0]
            PosX=struct.unpack('!f', bytes.fromhex(PosX))[0]
            PosY=struct.unpack('!f', bytes.fromhex(PosY))[0]
            PosZ=struct.unpack('!f', bytes.fromhex(PosZ))[0]
            ScaleX=struct.unpack('!f', bytes.fromhex(ScaleX))[0]
            self.StaticData.append([str(rotX),str(rotY),str(rotZ),str(rotW),str(PosX),str(PosY),str(PosZ),str(ScaleX)])
        #print(self.StaticData[0])
        #print(self.StaticData[len(self.StaticData)-1])
    def ExtractFBX(self):
        for Static in self.Statics:
            #attempt to pull
            print(Static)
            flipped=binascii.hexlify(bytes(hex_to_little_endian(Static))).decode('utf-8')
            new=ast.literal_eval("0x"+flipped)
            PkgID=Hex_String(Package_ID(new))
            EntryID=Hex_String(Entry_ID(new))
            DirName=PkgID.upper()+"-"+EntryID.upper()+".model"
            for File in os.listdir(custom_direc):
                if File == DirName:
                    Model=open(custom_direc+"/"+File,"rb")
                    Data=binascii.hexlify(bytes(Model.read())).decode()
                    Data=[Data[i:i+8] for i in range(0, len(Data), 8)]
                    SubfileHash=Data[2]
                    flipped=binascii.hexlify(bytes(hex_to_little_endian(SubfileHash))).decode('utf-8')
                    new=ast.literal_eval("0x"+flipped)
                    PkgID=Hex_String(Package_ID(new))
                    EntryID=Hex_String(Entry_ID(new))
                    DirName=PkgID.upper()+"-"+EntryID.upper()+".sub"
                    print(DirName)
                    #model exists
            break
            
    def RipStatics(self):
        os.chdir(self.CWD+"/ThirdParty")
        for Static in self.Statics:
            cmd='d2staticextractor.exe -p "'+path+'" -o '+self.CWD+'/data/Statics/Statics -i '+Static
            print(cmd)
            ans=subprocess.call(cmd, shell=True)
            #print(ans)
            try:
                os.rename(self.CWD+"/data/Statics/Statics/"+Static.lower()+".fbx",self.CWD+"/data/Statics/Statics/"+Static.upper()+".fbx")
            except FileNotFoundError:
                print("L")
        os.chdir(self.CWD)
    def RipOwnStatics(self):
        for Static in self.Statics:
            start=binascii.hexlify(bytes(hex_to_little_endian(Static))).decode('utf-8')
            new=ast.literal_eval("0x"+start)

            pkg = Hex_String(Package_ID(new))
            #print(result)
            ent = Hex_String(Entry_ID(new))
            Bank=pkg+"-"+ent+".model"
            print(Bank)
            file=open(os.getcwd()+"/out/"+Bank,"rb")
            file.seek(0x8)

            s = binascii.hexlify(bytes(file.read(4))).decode()
            file.seek(0x50)
            x=binascii.hexlify(bytes(file.read(4))).decode()
            xScale=struct.unpack('!f', bytes.fromhex(binascii.hexlify(bytes(hex_to_little_endian(x))).decode('utf-8')))[0]  #vert
            y=binascii.hexlify(bytes(file.read(4))).decode()
            yScale=struct.unpack('!f', bytes.fromhex(binascii.hexlify(bytes(hex_to_little_endian(y))).decode('utf-8')))[0]
            z=binascii.hexlify(bytes(file.read(4))).decode()
            zScale=struct.unpack('!f', bytes.fromhex(binascii.hexlify(bytes(hex_to_little_endian(z))).decode('utf-8')))[0]
            print(x,y,z)
            print(s)
            flipped=binascii.hexlify(bytes(hex_to_little_endian(s))).decode('utf-8')
            print(flipped)
            new=ast.literal_eval("0x"+flipped)

            pkg = Hex_String(Package_ID(new))
            #print(result)
            ent = Hex_String(Entry_ID(new))
            Bank=pkg+"-"+ent+".sub" #subfile
            print(Bank)
            sub=open(os.getcwd()+"/out/"+Bank,"rb")
            SubData=binascii.hexlify(bytes(sub.read())).decode()
            sub.seek(0x4C)
            Scale=binascii.hexlify(bytes(sub.read(4))).decode()
            Scale=struct.unpack('!f', bytes.fromhex(stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Scale))).decode('utf-8'))))[0]
            print(Scale)
            DataHashes=[]
            SubData=[SubData[i:i+8] for i in range(0, len(SubData), 8)]
            for Hash in SubData:
                temp=[Hash[i:i+2] for i in range(0, len(Hash), 2)]
                if (temp[3] == "80") or (temp[3] == "81"):
                    if temp[2] != "80":
                    #isHash
                        flipped=binascii.hexlify(bytes(hex_to_little_endian("".join(temp)))).decode('utf-8')
                        DataHashes.append(flipped)  #index at 0 vert at 1
            if len(DataHashes) < 2:
                continue
            new=ast.literal_eval("0x"+DataHashes[1])
            new=new+1
            pkg = Hex_String(Package_ID(new))
            #print(result)
            ent = Hex_String(Entry_ID(new))
            print(DataHashes)
            HashDiff=int(ast.literal_eval("0x"+DataHashes[len(DataHashes)-1]))-int(ast.literal_eval("0x"+DataHashes[0]))+3
            vertFound=False
            indFound=False
            for i in range(int(HashDiff)):
                new=int(ast.literal_eval("0x"+DataHashes[0]))+i-1
                #new=ast.literal_eval("0x"+DataHashes[1])

                pkg = Hex_String(Package_ID(new))
                ent = Hex_String(Entry_ID(new))
                
                if vertFound == False:     #very poor way of finding buffers
                    Bank=pkg+"-"+ent+".vert"
                    try:
                        vert=open(os.getcwd()+"/out/"+Bank,"rb") #hash +1???
                    except FileNotFoundError:
                        u=1
                    else:
                        vertFound=True
                   
                if indFound==False:
                    Bank=pkg+"-"+ent+".index"
                    try:
                        ind=open(os.getcwd()+"/out/"+Bank,"rb") #hash +1???
                    except FileNotFoundError:
                        u=1
                    else:
                        indFound=True
            if (vertFound == True) and (indFound == True):
                verts=[]
                print("RUNNING")
                Length=binascii.hexlify(bytes(vert.read())).decode()
                vert.seek(0x0)
                print(len(Length))
                num=len(Length)/32
                print(num)
                for i in range(int(num)):
                    s = binascii.hexlify(bytes(vert.read(16))).decode()
                    Data=[s[i:i+4] for i in range(0, len(s), 4)]
                    #x=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Data[0]))).decode('utf-8')))/32767
                    #y=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Data[1]))).decode('utf-8')))/32767  #i = struct.unpack('<I', padded)
                    #z=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Data[2]))).decode('utf-8')))/32767
                    x= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[0]))).decode('utf-8'),16)/32767)*(Scale*10)
                    y= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[1]))).decode('utf-8'),16)/32767)*(Scale*10)
                    z= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[2]))).decode('utf-8'),16)/32767)*(Scale*10)
                    verts.append([x,y,z])
                #print(verts)
                new=ast.literal_eval("0x"+DataHashes[0])
                new=new-1
                pkg = Hex_String(Package_ID(new))
                #print(result)
                ent = Hex_String(Entry_ID(new))
                Bank=pkg+"-"+ent+".index"
                #ind=open(os.getcwd()+"/data/"+Bank,"rb") #hash +1???
                faces=[]
                Length = binascii.hexlify(bytes(ind.read())).decode()
                ind.seek(0x00)
                for i in range(int(len(Length)/4)):
                    s = binascii.hexlify(bytes(ind.read(2))).decode()
                    #print(s)
                    data=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(s))).decode('utf-8')))
                    faces.append(data)

                #print(faces[len(faces)-1]) 
                
       
                memory_manager = fbx.FbxManager.Create()
                scene = fbx.FbxScene.Create(memory_manager, '')
                my_mesh = fbx.FbxMesh.Create(scene, Static)
                count=0
                my_mesh.InitControlPoints(len(verts))
                for Set in verts:
                    v = fbx.FbxVector4(Set[0]/10, Set[1]/10, Set[2]/10)
                    my_mesh.SetControlPointAt( v, count )
                    count+=1
                print(verts[0])
                #for i in range(0,int(len(faces)/3),3):
                #    data=[faces[i],faces[i+1],faces[i+2]]
                #    my_mesh.addface(data)
                print(len(faces)/ 3)
                for i in range(0, len(faces), 3):
                        my_mesh.BeginPolygon()
                        for j in range(3):
                            vertex_index = faces[i + j]
                            my_mesh.AddPolygon(vertex_index)
                        my_mesh.EndPolygon()
                        
                cubeLocation = (xScale, yScale, zScale)
                cubeScale    = (Scale, Scale, Scale)

                newNode = addNode(scene, Static, location = cubeLocation)
                rootNode = scene.GetRootNode()
                #rootNode.LclTranslation.set(fbx.FbxDouble3(xScale, yScale, zScale))
                rootNode.AddChild( newNode )

                newNode.SetNodeAttribute( my_mesh )
                newNode.ScalingActive.Set(1)
                px = fbx.FbxDouble3(1, 1, 1)
                #if not memory_manager.GetIOSettings():
                #    ios = fbx.IOSettings.Create(memory_manager, IOSROOT)
                #    memory_manager.SetIOSettings(ios)
                #io_settings = memory_manager.GetIOSettings()
                #io_settings.SetBoolProp(fbx.FbxBoolProperty.eEXP_FBX_MATERIAL, True)
                #newNode.LclScaling.Set(px)
                #root_node.AddChild(my_mesh)
                #scene.add(my_mesh)
                filename = os.getcwd()+"\\data\\Statics\\Statics\\"+Static+".fbx"
                FbxCommon.SaveScene(memory_manager, scene, filename)
                #exporter = fbx.FbxExporter.Create(memory_manager, filename)
                
                #filename = os.getcwd()+"\\Statics\\"+OutName+".fbx"
                #status = exporter.Initialize(filename, -1, memory_manager.GetIOSettings())
                #scene.save()
                #exporter.Export(scene)
                #print(status)
                #exporter.Destroy()
                memory_manager.Destroy()
            else:
                print("Skipped")
def addNode( pScene, nodeName, **kwargs ):
    
    # Obtain a reference to the scene's root node.
    #scaling = kwargs["scaling"]
    location = kwargs["location"]
    newNode = fbx.FbxNode.Create( pScene, nodeName )
    newNode.LclScaling.Set(fbx.FbxDouble3(1, 1, 1))
    newNode.LclTranslation.Set(fbx.FbxDouble3(location[0]*1, location[1]*1, location[2]*1))
    return newNode
           
def CubeRipper(entry):
    filelist=[]
    temp=entry.get().split("_")
    new="_".join(temp[:len(temp)-1])
    print(new)
    for file in os.listdir(path)[::-1]:
        if fnmatch.fnmatch(file,new+"*"):
            filelist.append(file)
    useful=["Cube"]
    unpack_all(path,custom_direc,useful,filelist)
    lengths=[]
    for File in os.listdir(custom_direc):
        if File != "audio":
            if File.split(".")[1] == "cube":
                Tex=DDS(File,"Cube")
                print("ran")
    for file in os.listdir(os.getcwd()+"/out"):
        if file != "audio":
            os.remove(os.getcwd()+"/out/"+file)
    Popup()
def RipAllTextures(entry):
    currentPath=os.getcwd()
    filelist=[]
    pkgID=entry.get().split("_")[len(entry.get().split("_"))-1]
    
    cmd= 'D2TextureRipper.exe -p "'+path+'" -o '+os.getcwd()+'/Textures -i '+pkgID
    os.chdir(os.getcwd()+"/ThirdParty")
    ans=subprocess.call(cmd, shell=True)
    os.chdir(currentPath)
    Popup()
def TextureWindow(top):
    lst=[]
    for widget in top.winfo_children():
        widget.destroy()
    bg = PhotoImage(file = os.getcwd()+"/ThirdParty/destiny.png")
    label1 = Label(top, image = bg)
    label1.pack()
    for File in os.listdir(path):
        temp=File.split("_")
        if "video" not in temp:
            new="_".join(temp[:(len(temp)-1)])
            if new not in lst:
                lst.append(new)
    #print(lst)
    useful=[]
    combo_box = ttk.Combobox(top,height=20, width=40)
    combo_box['values'] = lst
    combo_box.bind('<KeyRelease>', check_input)
    combo_box.place(x=500, y=125)
    Normal = Button(top, text="Extract Normal", height=1, width=30,command=partial(NormalRipper,combo_box,"Single"))
    Normal.place(x=500, y=175)
    NormalBulk = Button(top, text="Extract Normal(Bulk)", height=1, width=30,command=partial(NormalRipper,combo_box,"Bulk"))
    NormalBulk.place(x=500, y=225)
    Better = Button(top, text="Third Party (recommended)", height=1, width=30,command=partial(RipAllTextures,combo_box))
    Better.place(x=500, y=275)
    Cubemap = Button(top, text="Extract Cube", height=1, width=30,command=partial(CubeRipper,combo_box))
    Cubemap.place(x=750, y=175)
    Back = Button(top, text="Back", height=1, width=15,command=partial(MainWindow,top))
    Back.place(x=10, y=10)
    ClearTex = Button(top, text="Clear Textures", height=1, width=15,command=partial(ClearTextures,top))
    ClearTex.place(x=1000, y=470)
    filelist = []
    top.mainloop()
def LoadNames(top):
    for widget in top.winfo_children():
        widget.destroy()
    lengths=[]
    Rotations=[]
    Translations=[]
    DynamicHashes=[]
    LoadNames=[]
    file=open("output.txt","r")
    data=file.read()
    StrData=data.split("\n")
    file.close()
    for File in os.listdir(custom_direc):
        if File != "audio":
             if File.split(".")[1] == "top":
                 file=open(custom_direc+"/"+File,"rb")
                 file.seek(0x8)
                 Hash=binascii.hexlify(bytes(file.read(4))).decode()
                 flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
                 new=ast.literal_eval("0x"+flipped)
                 RefHash=Hex_String(Package_ID(new))+"-"+Hex_String(Entry_ID(new))+".mref"
                 file.seek(0x18)
                 Hash=binascii.hexlify(bytes(file.read(4))).decode()
                 file.close()
                 flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
                 new=ast.literal_eval("0x"+flipped)
                 LoadHash=new
                 StringTxt=""
                 possibleNames=[]
                 for String in StrData:
                     Lines=String.split(" // ")
                     try:
                         Lines[1]
                     except IndexError:
                         pass
                     else:
                         if Lines[0] == str(new):
                             StringTxt=Lines[1]
                             possibleNames.append(StringTxt)
                             
                 LoadNames.append([str([possibleNames]),File,RefHash])
    count=0
    for Load in LoadNames:
        file=open(custom_direc+"/"+Load[2],"rb")#mref
        print(Load[2])
        Data=binascii.hexlify(bytes(file.read())).decode()
        data=[Data[i:i+32] for i in range(0, len(Data), 32)]
        file.close() ##############################################################################################
        LoadHashes=[]
        First=True
        #print(len(data))
        for Line in data:
            split=[Line[i:i+8] for i in range(0, len(Line), 8)]
            if split[0].lower() == "ffffffff":
                Hash=str(split[2])+str(split[3])
                flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
                #print(flipped)
                for Line1 in Hash64Data:
                    Lines=Line1.split(": ")
                    #print(Lines)
                    if Lines[0].lower() == str("0x"+flipped):
                        LhashFile=Lines[1]
                        LoadNames[count].append(LhashFile)
                        break
        count+=1     
                    
    #print(LoadNames)           
    count=0    
    for Load in LoadNames:
        count+=1
        print(str(count)+" "+Load[0]+Load[2])
    lst=[]
    lst=LoadNames
    #answer=int(input("Enter which Load you want to pull from: "))
    bg = PhotoImage(file = os.getcwd()+"/ThirdParty/destiny.png")
    label1 = Label(top, image = bg)
    label1.pack()
    #print(lst)
    useful=[]
    combo_box = ttk.Combobox(top,height=20, width=80)
    combo_box['values'] = lst
    combo_box.bind('<KeyRelease>', check_input)
    combo_box.place(x=500, y=125)
    Map = Button(top, text="Extract Load", height=1, width=30,command=partial(MapExtractor,combo_box,LoadNames))
    Map.place(x=500, y=175)
    Back = Button(top, text="Back", height=1, width=15,command=partial(MainWindow,top))
    Back.place(x=10, y=10)
    top.mainloop()



def MapExtractor(entry,LoadNames):
    things=entry.get().split(" ")
    count=0
    for Load in LoadNames:
        if Load[2] in things:
            answer=count
        count+=1
            
    lengths=[]
    Rotations=[]
    Translations=[]
    DynamicHashes=[]        
    SubLoads=LoadNames[answer][3:]
    count5=1
    LoadFiles=[]
    print(SubLoads)
    InstCount=[]
    count3=0
    Dts=[]
    refs=[]
    for SubLoad in SubLoads:
        num=ast.literal_eval(SubLoad)
        EntityDts=[]
        print("SUB")
        Name=Hex_String(Package_ID(num))+"-"+Hex_String(Entry_ID(num))+".lhash"
        save=Name
        for File in os.listdir(custom_direc):
            if File != "Statics":
                if File.lower() == Name:  #change back to LHash
                    Tables=[]
                    file=open(custom_direc+"/"+File,"rb")
                    file.seek(0x50)
                    dat=binascii.hexlify(bytes(file.read())).decode()
                    Data=[dat[i:i+8] for i in range(0, len(dat), 8)]
                    for Hash in Data:
                        flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
                        num=ast.literal_eval("0x"+flipped)
                        Name=Hex_String(Package_ID(num))+"-"+Hex_String(Entry_ID(num))
                        if Name not in Tables:
                            Tables.append(Name)
                    count=0
                    
                    for Table in Tables:
                        for File in os.listdir(custom_direc):
                            if File != "audio":
                                if Table.lower() == File.split(".")[0].lower():   #opens multiple dts
                                    #print(File)
                                    tempName=File
                                    EntityDts.append(str(File))
                                    #print(EntityDts)
                                    H64=""
                                    StaticLz=""
                                    file=open(custom_direc+"/"+File,"rb")
                                    length=binascii.hexlify(bytes(file.read())).decode()
                                    file.close()
                                    if len(length) < 144:
                                        continue
                                    File=open(custom_direc+"/"+File,"rb")
                                    File.seek(0x20)
                                    Num=binascii.hexlify(bytes(File.read(8))).decode()
                                    flipped=binascii.hexlify(bytes(hex_to_little_endian(Num))).decode('utf-8')
                                    Length=ast.literal_eval("0x"+stripZeros(flipped))
                                    File.seek(0x30)
                                    #Data=binascii.hexlify(bytes(File.read(288*int(Length)))).decode()
                                    dat=[]
                                    count=0
                                    
                                    for i in range(Length):
                                        count+=1
                                        temp=binascii.hexlify(bytes(File.read(144))).decode()
                                        dat.append(temp)
                                        #print(temp)
                                        EntityDts=[]
                                    for Model in dat:
                                        Dat=[Model[i:i+8] for i in range(0, len(Model), 8)]
                                        #print(Dat)
                                        QuatX=(struct.unpack("<I", bytes.fromhex(Dat[0]))[0])*-1
                                        QuatY=(struct.unpack("<I", bytes.fromhex(Dat[1]))[0])*-1
                                        QuatZ=(struct.unpack("<I", bytes.fromhex(Dat[2]))[0])*-1
                                        QuatW=struct.unpack("<I", bytes.fromhex(Dat[3]))[0]
                                        fx=struct.unpack("<I", bytes.fromhex(Dat[4]))[0]
                                        fy=struct.unpack("<I", bytes.fromhex(Dat[5]))[0]
                                        fz=struct.unpack("<I", bytes.fromhex(Dat[6]))[0]
                                        lzscale=struct.unpack("<I", bytes.fromhex(Dat[7]))[0]
                                        Rotations.append([QuatX,QuatY,QuatZ,QuatW])
                                        Translations.append([fx,fy,fz,lzscale])
                                        File.read(4)
                                        Ref=binascii.hexlify(bytes(File.read(4))).decode()
                                        if Ref == "c96c8080":  #statics
                                            print("THISONE")
                                            File.read(16)
                                            Hash=binascii.hexlify(bytes(File.read(4))).decode()
                                            File.close()
                                            flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
                                            new=ast.literal_eval("0x"+flipped)
                                            DirName=Hex_String(Package_ID(new))+"-"+Hex_String(Entry_ID(new))
                                            #print(DirName+".test")
                                            File=open(custom_direc+"/"+DirName+".test","rb")
                                            File.seek(0x8)
                                            Hash=binascii.hexlify(bytes(File.read(4))).decode()
                                            #print(Hash)
                                            flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
                                            new=ast.literal_eval("0x"+flipped)
                                            DirName2=Hex_String(Package_ID(new))+"-"+Hex_String(Entry_ID(new))+".load"
                                            #print(DirName)
                                            File.close()
                                            #print(DirName2)
                                            File=open(custom_direc+"/"+DirName2,"rb")
                                            File.seek(0x50)
                                            Length=binascii.hexlify(bytes(File.read(2))).decode()
                                            File.close()
                                            flipped=binascii.hexlify(bytes(hex_to_little_endian(Length))).decode('utf-8')
                                            new=ast.literal_eval("0x"+stripZeros(flipped))
                                            print(str(count5)+" "+str(SubLoad)+" Instances: "+str(new))
                                            InstCount.append(str(new))
                                            count5+=1
                                            LoadFiles.append(DirName2)
                                            refs.append(save)
                                        
                                        
                                   
                
        
        #print(Dts)
                                            
    print(refs)                                   
    #print(LoadFiles)                                       
    #ans2=int(input("Enter which Load to extract from: "))
    InitialiseMapFiles(LoadFiles,InstCount,refs)
def InitialiseMapFiles(loadfile,InstCount,Ref):
    lengths=[]
    count=0
    for Load in loadfile:
        for File in os.listdir(custom_direc):
            if File != "audio":
                if File.lower() == Load:
                    Load=LoadZone(Load,InstCount[count],Ref[count])
                    lengths.append([File,str(len(Load.Statics))])
                    count+=1
    Popup()
def MapRipper(entry,top):
    filelist=[]
    for file in os.listdir(path)[::-1]:
        if fnmatch.fnmatch(file,entry.get()+"*"):
            filelist.append(file)
    useful=["Map"]
    unpack_all(path,custom_direc,useful,filelist)
    LoadNames(top)
def QuitOut(top):
    top.destroy()
    sys.exit()
def MapWindow(top):
    lst=[]
    for widget in top.winfo_children():
        widget.destroy()
    bg = PhotoImage(file = os.getcwd()+"/ThirdParty/destiny.png")
    label1 = Label(top, image = bg)
    label1.pack()
    for File in os.listdir(path):
        temp=File.split("_")
        if "video" not in temp:
            new="_".join(temp[:(len(temp)-2)])
            if new not in lst:
                lst.append(new)
    #print(lst)
    useful=[]
    combo_box = ttk.Combobox(top,height=20, width=40)
    combo_box['values'] = lst
    combo_box.bind('<KeyRelease>', check_input)
    combo_box.place(x=500, y=125)
    Map = Button(top, text="Extract Map", height=1, width=30,command=partial(MapRipper,combo_box,top))
    Map.place(x=500, y=175)
    Back = Button(top, text="Back", height=1, width=15,command=partial(MainWindow,top))
    Back.place(x=10, y=10)
    ClearMap = Button(top, text="Clear Maps", height=1, width=15,command=partial(ClearMaps,top))
    ClearMap.place(x=1000, y=420)
    top.mainloop()
    
def MainWindow(top):
    for widget in top.winfo_children():
        widget.destroy()
    bg = PhotoImage(file = os.getcwd()+"/ThirdParty/destiny.png")
    label1 = Label(top, image = bg)
    label1.pack()
    String = Button(top, text="Generate String DB", height=1, width=15,command=partial(Strings,"y"))
    String.place(x=500, y=125)
    String2 = Button(top, text="No Ext (Debug)", height=1, width=15,command=partial(Strings,"n"))
    String2.place(x=700, y=125)
    Activity = Button(top, text="Extract Activity Data", height=1, width=15,command=partial(ActivityMenu,top))
    Activity.place(x=500, y=175)
    Map = Button(top, text="Map Extractor", height=1, width=15,command=partial(MapWindow,top))
    Map.place(x=500, y=225)
    #Map["state"] = DISABLED
    Texture = Button(top, text="Texture Ripper", height=1, width=15,command=partial(TextureWindow,top))
    Texture.place(x=500, y=275)
    #Texture["state"] = DISABLED
    Cutscene = Button(top, text="Cutscene Extractor", height=1, width=15,command=partial(CutsceneView,top))
    Cutscene.place(x=500, y=325)
    Dev = Button(top, text="Script Extractor", height=1, width=15,command=partial(DevMenu))
    Dev.place(x=500, y=375)
    Clear = Button(top, text="Clear Audio", height=1, width=15,command=partial(ClearAudio,top))
    Clear.place(x=1000, y=550)
    ClearOut = Button(top, text="Clear Out", height=1, width=15,command=partial(ClearDir,top))
    ClearOut.place(x=1000, y=510)
    ClearTex = Button(top, text="Clear Textures", height=1, width=15,command=partial(ClearTextures,top))
    ClearTex.place(x=1000, y=470)
    ClearMap = Button(top, text="Clear Maps", height=1, width=15,command=partial(ClearMaps,top))
    ClearMap.place(x=1000, y=420)
    Quit = Button(top, text="Quit", height=1, width=15,command=partial(QuitOut,top))
    Quit.place(x=100, y=510)
    
    top.mainloop()
    
if __name__ == '__main__':
    Hash64(path)
    Hash64Data=ReadHash64()
    top = Tk()
    top.title("The Tech")
    top.geometry("1200x600")
    bg = PhotoImage(file = os.getcwd()+"/ThirdParty/destiny.png")
    label1 = Label(top, image = bg)
    label1.pack()
    entry1 = Entry(top)
    entry1.place(x=500,y=105)
    turn_on = Button(top, text="Set D2 Location", height=1, width=12,command=partial(setD2Location, entry1,top))
    turn_on.place(x=500, y=125)

    
    #turn_on.pack()

    top.mainloop()
    

    

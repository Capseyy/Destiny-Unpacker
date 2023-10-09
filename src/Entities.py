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


path = "E:\SteamLibrary\steamapps\common\Destiny2\packages" #Path to your packages folder.
#path="D:\oldd2\packages"
custom_direc = os.getcwd()+"/data" #Where you want the bin files to go
oodlepath = "E:\oo2core_9_win64.dll" #Path to Oodle DLL in Destiny 2/bin/x64.dle DLL in Destiny 2/bin/x64.

filelist = []
for file in os.listdir(path)[::-1]:
    if fnmatch.fnmatch(file,'w64_sr_comb*'):       #Customize this to what pkgs you need from. Can wildcard with * for all packages, or all of a certain type.
        filelist.append(file)
        #print(file) #for debugging


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

    def __init__(self, package_directory):
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
            #useful=["0x808045eb","0x808045f0","0x808045f7","0x808097b8","0x80809345","0x80809ec5","0x8080986a","0x808090d5","0x80808e8b","0x80808c0d","0x808099f1","0x80805a09","0x80809fb8","0x80800065","0x80809b06","0x80800000","0x80808e8e","0x808045f0","0x80808ec7"]
            ref_id, ref_pkg_id, ref_unk_id = decode_entry_a(entry.EntryA)
            #if hex(entry.EntryA) in useful:
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
        VertexLogger=open(os.getcwd()+"/ModelDataTable.txt","a")
        for entry in self.entry_table.Entries[::-1]:
            #print(entry)
            current_block_id = entry.StartingBlock
            block_offset = entry.StartingBlockOffset
            block_count = int(np.floor((block_offset + entry.FileSize - 1) / self.BLOCK_SIZE))
            #rint(str(block_offset)+" - "+str(block_count))
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
            fileFormat=".bin"
            #print(entry.EntryA)
            #time.sleep(5)
            
            if entry.Type == 40:
                
                if entry.SubType == 4:
                    fileFormat=".vert"
                    
                if entry.SubType == 6:
                    fileFormat=".index"
                    
            else:
                fileFormat=".bin"
            if entry.EntryA == "0x80809ad8":
                fileFormat = ".entity"#8F6D8080
            if entry.EntryA == "0x80806d8f":
                fileFormat = ".map"
            VertexLogger.write(entry.FileName+" : "+entry.EntryA+"\n")
            #fileFormat=".bin"
            #if entry.FileName.upper() == "03C3-16EC":
                #print(entry.EntryA)
                #print(f'{custom_direc}{self.package_directory.split("/w64")[-1][1:-6]}/{entry.FileName.upper()}'+fileFormat)
            if fileFormat != ".zzz":
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
        VertexLogger.close()

def unpack_all(path, custom_direc):
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
        pkg = Package(f'{path}/{pkg_full}')
        pkg.extract_package(extract=True, custom_direc=custom_direc)
    print("done")

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
import ast,fbx,struct
from fbx import FbxManager
import FbxCommon
#ans=input("y/n")
#if ans.lower() == "y":
BufferData=GetBufferInfo()
vertFound=False
indFound=False
#unpack_all(path, custom_direc)
Input="80e1e09f"   #80c1ffce
new=ast.literal_eval("0x"+Input)
pkg = Hex_String(Package_ID(new))
#print(result)
ent = Hex_String(Entry_ID(new))
Bank=pkg+"-"+ent+".entity"
print(Bank)
Dyn2s=[]
MaterialsToGet=[]
Materials=True
BufferData=GetBufferInfo()
file=open(os.getcwd()+"/data/"+Bank,"rb")
file.seek(0xA0)
ResourceCount=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(file.read(4))).decode()))).decode('utf-8')))
file.seek(0xb0)
Entity1=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(file.read(4))).decode()))).decode('utf-8')))
pkg = Hex_String(Package_ID(Entity1))
#print(result)
ent = Hex_String(Entry_ID(Entity1))
Bank=pkg+"-"+ent+".bin"
file2=open(os.getcwd()+"/data/"+Bank,"rb")
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
#file.seek(0xB0)
#for i in range(10):
#    Dyn=binascii.hexlify(bytes(file.read(12))).decode()
#    Dyn2s.append(Dyn[:8])
print(Skeleton)
for Dyn in Dyn2s:
    DynHash=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Dyn))).decode('utf-8')))
    pkg = Hex_String(Package_ID(DynHash))
    ent = Hex_String(Entry_ID(DynHash))
    Bank=pkg+"-"+ent+".bin"
    print(Bank)
    DynData=open(os.getcwd()+"/data/"+Bank,"rb")
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
    Check=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Dyn3Hash))).decode('utf-8')))
    if Check < 2155872256:
        print("Dynamic has no mesh data (D), skipping...")
        continue
    pkg = Hex_String(Package_ID(Check))
    ent = Hex_String(Entry_ID(Check))
    Bank=pkg+"-"+ent+".bin"
    
    file3=open(os.getcwd()+"/data/"+Bank,"rb")
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
print(ExistingDyn3s)
for Dyn3 in ExistingDyn3s:
    #print("Dyn3s")
    Dyn3=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Dyn3))).decode('utf-8')))
    pkg = Hex_String(Package_ID(Dyn3))
    ent = Hex_String(Entry_ID(Dyn3))
    Bank=pkg+"-"+ent+".bin"
    print(Bank+ "  Dyn3")
    Dyn3=open(os.getcwd()+"/data/"+Bank,"rb")
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
        Index=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(Dyn3.read(4))).decode()))).decode('utf-8')))
        index=binary_search(BufferData, Index)
        if index != -1:
            IndexName=BufferData[index][0]+".index"
        pkg = Hex_String(Package_ID(Index))
        ent = Hex_String(Entry_ID(Index))
        Bank=pkg+"-"+ent+".bin"
        print(Bank+"   IndexHEader")
        IndexHeader=open(os.getcwd()+"/data/"+Bank,"rb")
        IndexHeader.seek(1)
        is32=False
        Check32=binascii.hexlify(bytes(IndexHeader.read(1))).decode()
        if Check32 == "01":
            is32=True
        Dyn3.seek(i+0x10)
        Vertex=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(binascii.hexlify(bytes(Dyn3.read(4))).decode()))).decode('utf-8')))
        index=binary_search(BufferData, Vertex)
        if index != -1:
            VertexName=BufferData[index][0]+".vert"
        pkg = Hex_String(Package_ID(Vertex))
        ent = Hex_String(Entry_ID(Vertex))
        Bank=pkg+"-"+ent+".bin"
        VertexHeader=open(os.getcwd()+"/data/"+Bank,"rb")
        VertexHeader.seek(4)
        Stride=binascii.hexlify(bytes(VertexHeader.read(2))).decode()
        Stride=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Stride))).decode('utf-8')))
        Dyn3.seek(i+0x10+4)
        UVFile=binascii.hexlify(bytes(Dyn3.read(4))).decode()
        if UVFile != "ffffffff":
            UVFile=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(UVFile))).decode('utf-8')))
            pkg = Hex_String(Package_ID(UVFile))
            ent = Hex_String(Entry_ID(UVFile))
            Bank=pkg+"-"+ent+".bin"
            print(Bank+"   uvHeader")
            FindUV=True
            index=binary_search(BufferData, UVFile)
            if index != -1:
                UVName=BufferData[index][0]+".vert"
            print(UVName+"   uv")
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
        Vert=open(os.getcwd()+"/data/"+VertexName,"rb")
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
            UV=open(os.getcwd()+"/data/"+UVName,"rb")
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
        ind=open(os.getcwd()+"/data/"+IndexName,"rb")
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
        for Part in Submeshes:
            if int(Part[3]) < MinLod:
                MinLod=Part[3]
        memory_manager = fbx.FbxManager.Create()
        scene = fbx.FbxScene.Create(memory_manager, '')
        for Part in Submeshes:
            #if int(Part[3]) >= 4:
                #continue
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
                ind.seek(Part[1]*2)
                for i in range(int(Part[2])):
                    s = binascii.hexlify(bytes(ind.read(6))).decode()
                    Inds=[s[i:i+4] for i in range(0, len(s), 4)]
                    #print(s)
                    i1=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Inds[0]))).decode('utf-8')))
                    i2=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Inds[0]))).decode('utf-8')))
                    i3=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Inds[0]))).decode('utf-8')))
                    IndexData.append([i1,i2,i3])

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
        filename = os.getcwd()+"\\Statics\\"+Input+"_"+str(GroupCount)+".fbx"
        FbxCommon.SaveScene(memory_manager, scene, filename)
        #exporter = fbx.FbxExporter.Create(memory_manager, filename)
        
        #filename = os.getcwd()+"\\Statics\\"+OutName+".fbx"
        #status = exporter.Initialize(filename, -1, memory_manager.GetIOSettings())
        #scene.save()
        #exporter.Export(scene)
        #print(status)
        #exporter.Destroy()
        memory_manager.Destroy()
    break
        




#filename=name+".bin"
#exporter.export(scene)

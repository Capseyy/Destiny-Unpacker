import bpy
import json
import mathutils
import os
import binascii
import ast
import math
import struct
#!!!DO NOT MANUALLY IMPORT THE FBX, THE SCRIPT WILL DO IT FOR YOU!!!

#Adapted from Monteven's UE5 import script
installLoc="C:/Users/sjcap/Desktop/MyUnpacker/DestinyUnpackerNew/new/GUI/"
objects = bpy.data.objects
scene = bpy.context.scene

def hex_to_little_endian(hex_string):
    little_endian_hex = bytearray.fromhex(hex_string)[::-1]
    return little_endian_hex


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


currentPath=os.getcwd()

count=0
for Fbx in os.listdir(installLoc+"data/Statics/Statics"):
    
    split=Fbx.split(".")
    if split[1] == "fbx":
        path=installLoc+"data/Statics/Statics/"+Fbx
        print("ran")
        bpy.ops.object.select_all(action='DESELECT')
        thing=(0,0,0)
        bpy.context.scene.cursor.rotation_euler = (0, 0, 0)
        bpy.data.collections.new(str(split[0]).upper())
        bpy.context.scene.collection.children.link(bpy.data.collections[str(split[0]).upper()])
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[str(split[0]).upper()]
        bpy.ops.import_scene.fbx(filepath=path)
        #for Obj in bpy.data.objects:
        #    split=Obj.name.split("_")
        #    if split[1] == "0":
        #        bpy.data.objects.remove(Obj)
        #for Obj in bpy.data.objects:
        bpy.ops.object.select_all(action='DESELECT')
        newobjects = bpy.data.collections[str(split[0]).upper()].objects
        #newobjects = bpy.data.collections[str(Name)].objects
        #for obj in newobjects:
        #    #deselect all objects
        #    bpy.ops.object.select_all(action='DESELECT')
        #    tmp.append(obj.name[:8])
            #print(obj.name[:8])
            
        count=0
        MSH_OBJS = [m for m in bpy.data.collections[str(split[0]).upper()].objects if m.type == 'MESH']
        bpy.ops.outliner.orphans_purge()
        for OBJS in MSH_OBJS:
            #Select all mesh objects
            OBJS.select_set(state=True)
            bpy.context.view_layer.objects.active = OBJS
        bpy.ops.object.join()
        #break    
        count+=1
        flipped=binascii.hexlify(bytes(hex_to_little_endian(split[0]))).decode('utf-8')
        print(flipped)
        new=ast.literal_eval("0x"+flipped)
        PkgID=Hex_String(Package_ID(new))
        EntryID=Hex_String(Entry_ID(new))
        DirName=PkgID.upper()+"-"+EntryID.upper()+".model"
        modelExists=False
        for file in os.listdir(installLoc+"/out"):
            if file != "audio":
                if file == DirName:
                    print("modelexists")
                    modelExists=True
        if modelExists == True:
            file=open(installLoc+"/out/"+DirName,"rb")
            data=Data=binascii.hexlify(bytes(file.read())).decode()
            Data=[data[i:i+32] for i in range(0, len(data), 32)]
            Vert=Data[5]
            Dat=[Vert[i:i+8] for i in range(0, len(Vert), 8)] #X,Y,Z,Scale
            x=binascii.hexlify(bytes(hex_to_little_endian(Dat[0]))).decode('utf-8')
            y=binascii.hexlify(bytes(hex_to_little_endian(Dat[1]))).decode('utf-8')
            z=binascii.hexlify(bytes(hex_to_little_endian(Dat[2]))).decode('utf-8')
            scale=binascii.hexlify(bytes(hex_to_little_endian(Dat[3]))).decode('utf-8')
            X=struct.unpack('!f', bytes.fromhex(x))[0]
            Y=struct.unpack('!f', bytes.fromhex(y))[0]
            Z=struct.unpack('!f', bytes.fromhex(z))[0]
            Scale=struct.unpack('!f', bytes.fromhex(scale))[0]
            location=[X*-1,Y*-1,Z]
            print(location)
            bpy.ops.object.join()
            for obj in bpy.context.selected_objects:
                if 7<Scale<8:
                    obj.scale=([Scale/10])*3
                obj.rotation_mode = 'XYZ'
                #obj.location=[0,0,0]
            #currentRotation=bpy.data.objects[len(bpy.data.objects)-1].rotation_euler[0]
            #print(currentRotation)
                
                obj.location=location
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                obj.rotation_euler=[math.radians(0),math.radians(0),math.radians(180)]
            #XRot=bpy.data.objects[len(bpy.data.objects)-1].rotation_euler[0]
            #YRot=bpy.data.objects[len(bpy.data.objects)-1].rotation_euler[1]
            #ZRot=bpy.data.objects[len(bpy.data.objects)-1].rotation_euler[2]
            #print(math.radians(180))
            #bpy.data.objects[len(bpy.data.objects)-1].rotation_euler=[math.radians(-90),math.radians(YRot),math.radians(ZRot)]
            #bpy.data.objects[len(bpy.data.objects)-1].scale=(Scale/10,Scale/10,Scale/10)
            #bpy.context.scene.cursor.location=location
            #print(location)
            
            
            
            #break
for Obj in bpy.data.objects:
    
    Obj.location=[0,0,0]
#    print(Obj.name)
#    split=Obj.name.split("_")
#    if split[1] != "1":
#        bpy.data.objects.remove(Obj)

        

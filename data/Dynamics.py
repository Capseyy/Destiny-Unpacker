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

def euler_from_quaternion(x, y, z, w):
    if 1 == 1:
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)
     
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)
     
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)
     
        return roll_x, pitch_y, yaw_z # in radians
#installLoc="C:/Users/sjcap/Desktop/MyUnpacker/DestinyUnpackerNew/new/GUI/"
Filepath = os.path.abspath(bpy.context.space_data.text.filepath+"/..") #"OUTPUT_DIR"
def InstanceDyn(Object,HasRoot):
    #print(HasRoot)
    try:
        file=open(Filepath+"/Instances/"+(str(Object.name)[:8]).lower()+".inst","r")
    except:
        print("no file")
    else:
        
        data=file.read().split("\n")#
        file.close()
        #print(data)
        data.remove('')
        #print(data)
        #print(Object.name)               
        #flipped=binascii.hexlify(bytes(hex_to_little_endian(Object.name[:8]))).decode('utf-8')
#print(flipped)
        for instance in data:
            instance=instance.split(",")
            ob_copy = bpy.data.objects[Object.name].copy()
            bpy.context.collection.objects.link(ob_copy) #makes the instances

            location = [float(instance[4]), float(instance[5]), float(instance[6])]
            #Reminder that blender uses WXYZ, the order in the confing file is XYZW, so W is always first
            quat = mathutils.Quaternion([float(instance[3]), float(instance[0]), float(instance[1]), float(instance[2])])
            x,y,z=euler_from_quaternion(float(instance[0]),float(instance[1]),float(instance[2]),float(instance[3]))
            ob_copy.location = location
            #ob_copy.rotation_mode = 'QUATERNION'
            x=x+1.5708
            if x > 1.57079632679:
                x=1.57079632679-(x-1.57079632679)
            elif x < 1.57079632679:
                x=1.57079632679+(1.57079632679-x)
            ob_copy.rotation_euler= (x,y*-1,z+3.1415)
            if HasRoot == True:
                ob_copy.delta_scale=[0.01]*3
            #if 7<Scale<8:
            
                #ob_copy.delta_scale=([Scale/10])*3
            ob_copy.scale = [float(instance[7])]*3
            #count=0
for Fbx in os.listdir(Filepath+"/Dynamics"):
    #break
    
    split=Fbx.split(".")
    #f split[0] != "5085df80":
        #ontinue
    if split[1] == "fbx":
        #print(count)
        print(Fbx)
        path=Filepath+"/Dynamics/"+Fbx
        print("ran")
        bpy.ops.object.select_all(action='DESELECT')
        thing=(0,0,0)
        bpy.context.scene.cursor.rotation_euler = (0, 0, 0)
        bpy.data.collections.new(str(split[0]).upper())
        bpy.context.scene.collection.children.link(bpy.data.collections[str(split[0]).upper()])
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[str(split[0]).upper()]
        bpy.ops.import_scene.fbx(filepath=path, use_custom_normals=True, ignore_leaf_bones=True, automatic_bone_orientation=True)
        
        HasRoot=False
        #bpy.ops.object.select_all(action='DESELECT')
        newobjects = bpy.data.collections[str(split[0]).upper()].objects
        Keep=[]
        #bpy.ops.outliner.orphans_purge()
        for Obj in newobjects:
            if Obj.name[:4] == "root":
                #Obj.parent = None
                Obj.select_set(state=True)
                print("found")
                bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                HasRoot=True
           
                #bpy.context.view_layer.objects.active = bpy.context.selected_objects
        #MSH_OBJS = [m for m in bpy.data.collections[str(split[0]).upper()].objects if m.type == 'MESH']
        bpy.ops.outliner.orphans_purge()
        for OBJS in newobjects:
            #Select all mesh objects
            OBJS.parent = None
            OBJS.select_set(state=True)
            bpy.context.view_layer.objects.active = OBJS
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        bpy.ops.object.join()

       
        modelExists=True
        if modelExists == True:
            #count+=1
            for obj in bpy.context.selected_objects:
                
                obj.location=[0,0,0]
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                InstanceDyn(obj,HasRoot)
        bpy.ops.object.select_all(action='DESELECT')
        for Obj in bpy.data.objects:
            if Obj.name[:4] == "root":
                Obj.select_set(state=True)
        bpy.ops.object.delete()

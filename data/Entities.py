import bpy
import json
import mathutils
import os
import binascii
import ast
import math
import struct
#!!!DO NOT MANUALLY IMPORT THE FBX, THE SCRIPT WILL DO IT FOR YOU!!!



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
#Adapted from Monteven's UE5 import script
#installLoc="C:/Users/sjcap/Desktop/MyUnpacker/DestinyUnpackerNew/new/GUI/"
Filepath = os.path.abspath(bpy.context.space_data.text.filepath+"/..") #"OUTPUT_DIR"
def InstanceEnt(Object,HasRoot):
    try:
        file=open(Filepath+"/Instances/"+(str(Object.name)[:8]).lower()+".inst","r")
    except:
        print("no file")
    else:
        
        data=file.read().split("\n")
        file.close()
        #print(data)
        data.remove('')
        #print(data)
        #print(Object.name)
        for instance in data:
            instance=instance.split(",")
            ob_copy = bpy.data.objects[Object.name].copy()
            bpy.context.collection.objects.link(ob_copy) #makes the instances

            location = [float(instance[4]), float(instance[5]), float(instance[6])]
            #Reminder that blender uses WXYZ, the order in the confing file is XYZW, so W is always first
            quat = mathutils.Quaternion([float(instance[3]), float(instance[0]), float(instance[1]), float(instance[2])])
            x,y,z=euler_from_quaternion(float(instance[0]),float(instance[1]),float(instance[2]),float(instance[3]))

            ob_copy.location = location
            x=x+1.5708
            if x > 1.57079632679:
                x=1.57079632679-(x-1.57079632679)
            elif x < 1.57079632679:
                x=1.57079632679+(1.57079632679-x)
            ob_copy.rotation_euler= (x,y*-1,z+3.1415)
            #if 7<Scale<8:
            if HasRoot == True:
                ob_copy.delta_scale=[0.01]*3
            
                #ob_copy.delta_scale=([Scale/10])*3
            ob_copy.scale = [float(instance[7])]*3

for Fbx in os.listdir(Filepath+"/Entities"):
    #break
    split=Fbx.split(".")
    
    if split[1] == "fbx":
        print(split[0])
        path=Filepath+"/Entities/"+Fbx
        print("ran")
        bpy.ops.object.select_all(action='DESELECT')
        thing=(0,0,0)
        bpy.context.scene.cursor.rotation_euler = (0, 0, 0)

        bpy.ops.import_scene.fbx(filepath=path, use_custom_normals=True, ignore_leaf_bones=True, automatic_bone_orientation=True)
        
        HasRoot=False
        #bpy.ops.object.select_all(action='DESELECT')
        #bpy.ops.object.select_all(action='DESELECT')
        Keep=[]
        for Obj in bpy.context.selected_objects:
            if Obj.name[:4] == "root":
                Obj.parent = None
                bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                HasRoot=True
        
        #bpy.ops.object.select_all(action='DESELECT')
        for Obj in bpy.data.objects:
            Obj.parent = None
            if Obj.name[:8] == split[0]:
                Obj.select_set(state=True)
       
        modelExists=True
        if modelExists == True:
            
            for obj in bpy.context.selected_objects:
                
                obj.location=[0,0,0]
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                InstanceEnt(obj,HasRoot)

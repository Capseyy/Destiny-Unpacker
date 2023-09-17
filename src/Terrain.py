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
import FbxCommon
def ExtractTerrain(MainPath,Hashes):
    for TerrainHash in Hashes:
        Input=binascii.hexlify(bytes(hex_to_little_endian(TerrainHash))).decode('utf-8')
        new=ast.literal_eval("0x"+Input)
        pkg = Hex_String(Package_ID(new))
        #print(result)
        ent = Hex_String(Entry_ID(new))
        Bank=pkg+"-"+ent+".terrain"
        #rint(Bank)
        BufferData=GetBufferInfo(MainPath)
        file=open(MainPath+"/out/"+Bank,"rb")
        mainData=binascii.hexlify(bytes(file.read())).decode()
        file.seek(0x8)
        s = binascii.hexlify(bytes(file.read(4))).decode()
        #GetInstance
        file.seek(0x10)
        InstanceData=binascii.hexlify(bytes(file.read(32))).decode()
        InstanceData=[InstanceData[i:i+8] for i in range(0, len(InstanceData), 8)]
        x1=binascii.hexlify(bytes(hex_to_little_endian(InstanceData[0]))).decode('utf-8')
        y1=binascii.hexlify(bytes(hex_to_little_endian(InstanceData[1]))).decode('utf-8')
        z1=binascii.hexlify(bytes(hex_to_little_endian(InstanceData[2]))).decode('utf-8')
        Scale1=binascii.hexlify(bytes(hex_to_little_endian(InstanceData[3]))).decode('utf-8')
        x1=struct.unpack('!f', bytes.fromhex(x1))[0]
        y1=struct.unpack('!f', bytes.fromhex(y1))[0]
        z1=struct.unpack('!f', bytes.fromhex(z1))[0]
        Scale1=struct.unpack('!f', bytes.fromhex(Scale1))[0]
        x2=binascii.hexlify(bytes(hex_to_little_endian(InstanceData[4]))).decode('utf-8')
        y2=binascii.hexlify(bytes(hex_to_little_endian(InstanceData[5]))).decode('utf-8')
        z2=binascii.hexlify(bytes(hex_to_little_endian(InstanceData[6]))).decode('utf-8')
        Scale2=binascii.hexlify(bytes(hex_to_little_endian(InstanceData[7]))).decode('utf-8')
        x2=struct.unpack('!f', bytes.fromhex(x2))[0]
        y2=struct.unpack('!f', bytes.fromhex(y2))[0]
        z2=struct.unpack('!f', bytes.fromhex(z2))[0]
        Scale2=struct.unpack('!f', bytes.fromhex(Scale2))[0]
        InstX=(x1+x2)/2
        InstY=(y1+y2)/2
        InstZ=(z1+z2)/2
        file.seek(0x60)
        Vertex1=binascii.hexlify(bytes(file.read(4))).decode()
        Vertex2=binascii.hexlify(bytes(file.read(4))).decode()
        Index1=binascii.hexlify(bytes(file.read(4))).decode()
        Vertex1=binascii.hexlify(bytes(hex_to_little_endian(Vertex1))).decode('utf-8')
        Vertex2=binascii.hexlify(bytes(hex_to_little_endian(Vertex2))).decode('utf-8')
        Index1=binascii.hexlify(bytes(hex_to_little_endian(Index1))).decode('utf-8')
        file.seek(0x88)
        Vertex3=binascii.hexlify(bytes(file.read(4))).decode()
        Vertex4=binascii.hexlify(bytes(file.read(4))).decode()
        Index2=binascii.hexlify(bytes(file.read(4))).decode()
        Vertex3=binascii.hexlify(bytes(hex_to_little_endian(Vertex3))).decode('utf-8')
        Vertex4=binascii.hexlify(bytes(hex_to_little_endian(Vertex4))).decode('utf-8')
        Index2=binascii.hexlify(bytes(hex_to_little_endian(Index2))).decode('utf-8')
        new=ast.literal_eval("0x"+Vertex1)
        new-=1
        Value=int(ast.literal_eval("0x"+Index1))
        Index=binary_search(BufferData, Value)
        if Index != -1:
            IndexName=BufferData[Index][0]+".index"
            indFound=True
        Value=int(ast.literal_eval("0x"+Vertex1))
        Index=binary_search(BufferData, Value)
        if Index != -1:
            VertexName=BufferData[Index][0]+".vert"
            vertFound=True
        FindUV=False
        Scale=1
        if (vertFound == True) and (indFound == True):
            print(VertexName)
            print(IndexName)
            verts=[]
            print("RUNNING")
            Vert=open(MainPath+"/out/"+VertexName,"rb")
            Length=binascii.hexlify(bytes(Vert.read())).decode()
            Vert.seek(0x0)
            print(len(Length))
            num=len(Length)/16
            print(num)
            norms=[]
            Xs=[]
            Ys=[]
            Zs=[]
            for i in range(int(num)):
                s = binascii.hexlify(bytes(Vert.read(8))).decode()
                Data=[s[i:i+4] for i in range(0, len(s), 4)]
                if "" in Data:
                    break
                x= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[0]))).decode('utf-8'),16)/32767)
                y= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[1]))).decode('utf-8'),16)/32767)
                z= (twos_complement(binascii.hexlify(bytes(hex_to_little_endian(Data[2]))).decode('utf-8'),16)/32767)
                w= ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Data[3]))).decode('utf-8')))
                if w > 0:
                    z=z+(2*w)
                Xs.append(x)
                Ys.append(y)    
                Zs.append(z)
                verts.append([x,y,z,w])
            

            GlobalX=[(max(Xs)+min(Xs))/2,(max(Ys)+min(Ys))/2,(max(Zs)+min(Zs))/2]
            FindUV=False
            PartData=[]
            ind=open(MainPath+"/out/"+IndexName,"rb")
            faces=[]
            Length = binascii.hexlify(bytes(ind.read())).decode()
            ind.seek(0x00)
            triCount=0
            faces=[]
            currentFace=[]
            #j=0
            BreakOp=False
            IndexData=[]
            while True:
                v1 = binascii.hexlify(bytes(ind.read(2))).decode()
                v2 = binascii.hexlify(bytes(ind.read(2))).decode()
                v3 = binascii.hexlify(bytes(ind.read(2))).decode()
                temp=[v1,v2,v3]
                if v3 == "ffff":
                    #break
                    continue
                if "" in temp:
                    break
                #print(temp)
                v1=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(v1))).decode('utf-8')))
                v2=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(v2))).decode('utf-8')))
                v3=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(v3))).decode('utf-8')))
                #temp=[v1,v2,v3]
                if "ffff" in temp:
                    continue
                IndexData.append([v1,v2,v3])
                ind.seek(ind.tell()-4)
                
            memory_manager = fbx.FbxManager.Create()
            scene = fbx.FbxScene.Create(memory_manager, '')
            if 1 == 1:
                usedVerts=[]
                
                my_mesh = fbx.FbxMesh.Create(scene, TerrainHash)
                count=0
                #print(IndexCount)
                tempcheck=[]
                Verticies=[]
                for vert in verts:
                    Verticies.append([(vert[0]-GlobalX[0])*1024,(vert[1]-GlobalX[1])*1024,(vert[2]-GlobalX[2])*8,vert[3]])
                count=0
                my_mesh.InitControlPoints(len(Verticies))
                for Set in Verticies:
                    v = fbx.FbxVector4(Set[0]/2, Set[1]/2, Set[2]/2,Set[3]/2)
                    my_mesh.SetControlPointAt( v, count )
                    count+=1
                tempcheck.sort(key=lambda x: x[0])
                #print(IndexData)
                for List in IndexData:
                    my_mesh.BeginPolygon()
                    vertex_index = List[0]
                    my_mesh.AddPolygon(vertex_index)
                    vertex_index = List[1]
                    my_mesh.AddPolygon(vertex_index)
                    vertex_index = List[2]
                    my_mesh.AddPolygon(vertex_index)
                    my_mesh.EndPolygon()
                        
                #cubeLocation = (xScale, yScale, zScale)
                cubeLocation = (0, 0, 0)
                cubeScale    = (Scale, Scale, Scale)

                newNode = addNode(scene, TerrainHash, location = cubeLocation)
                rootNode = scene.GetRootNode()
                #rootNode.LclTranslation.set(fbx.FbxDouble3(xScale, yScale, zScale))
                rootNode.AddChild( newNode )

                newNode.SetNodeAttribute( my_mesh )
                newNode.ScalingActive.Set(1)
                px = fbx.FbxDouble3(1, 1, 1)
                count=0
                #lLayer = my_mesh.GetLayer(0)
                
            filename = MainPath+"\\data\\Terrain\\"+TerrainHash+".fbx"
            FbxCommon.SaveScene(memory_manager, scene, filename)
            memory_manager.Destroy()
            InstFile=open(MainPath+"/data/Instances/"+TerrainHash+".inst","a")
            InstFile.write("0,0,0,0,"+str(InstX)+","+str(InstY)+","+str(InstZ)+",1")
            InstFile.close()





#filename=name+".bin"
#exporter.export(scene)

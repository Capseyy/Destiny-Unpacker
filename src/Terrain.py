from dataclasses import dataclass, fields, field
from typing import List
import os
import numpy as np
import sys
sys.path.append("E:/MyUnpacker/DestinyUnpackerNew/new/MultiCore/ThirdParty")
import binascii
import io
import fnmatch
import time
import ast,fbx,struct
from fbx import FbxManager
import FbxCommon
from ctypes import *
temp=os.getcwd()
temp=temp.split("\\")
output="/".join(temp[:len(temp)])
sys.byteorder="little"
sys.path.append(output+"/ThirdParty")
sys.path.append(output)
custom_direc=output
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
def UnpackEntry(Hash,PackageCache,path):
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
    ExtractSingleEntry.unpack_entry_ext(path,custom_direc+"/out",Package,ent)
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
def GetFileReference(Hash,PackageCache,path):
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
import ast,fbx,struct
from fbx import FbxManager
import FbxCommon, ExtractSingleEntry
def ReadFaces(ind,IndexOffset,IndexCount):
    IndexData=[]
    triCount=0
    ind.seek(IndexOffset*2)
    Start=ind.tell()
    if binascii.hexlify(bytes(ind.read(2))).decode() != "ffff":
        ind.seek(ind.tell()-2)
    while (ind.tell()+4-Start) < (IndexCount*2):
        i1=binascii.hexlify(bytes(ind.read(2))).decode()
        i2=binascii.hexlify(bytes(ind.read(2))).decode()
        i3=binascii.hexlify(bytes(ind.read(2))).decode()
        if i3 == "ffff":
            triCount=0
            continue
        if i1 == "":
            break
        if i2 == "":
            break
        if i3 == "":
            break
        i1=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(i1))).decode('utf-8')))
        i2=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(i2))).decode('utf-8')))
        i3=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(i3))).decode('utf-8')))
        if 65535 in [i1,i2,i3]:
            print([i1,i2,i3])
        if triCount % 2 == 0:
            IndexData.append([i1,i2,i3])
        else:
            IndexData.append([i2,i1,i3])
        ind.seek(ind.tell()-4)
        triCount+=1
        if len(IndexData) == IndexCount:
            break
    return IndexData
import bisect
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
def ReadFloat32(Input):
    return struct.unpack('!f', bytes.fromhex(binascii.hexlify(bytes(hex_to_little_endian(Input))).decode('utf-8')))[0]    
def TransformTexcord(UVData,vec):
    TransData=[]
    for Val in UVData:
        TransData.append([Val[0]*vec[0]+vec[2],Val[1]+vec[1]+(1-vec[3])])
    return TransData
def ReadUV(Header,UVName):
    Header=binascii.hexlify(bytes(hex_to_little_endian(Header))).decode('utf-8')
    new=ast.literal_eval("0x"+Header)
    pkg = Hex_String(Package_ID(new))
    ent = Hex_String(Entry_ID(new))
    Bank=pkg+"-"+ent+".vheader"
    VHeader=open(custom_direc+"/out/"+Bank,"rb")
    VBufferSize=int.from_bytes(VHeader.read(4),"little")
    Stride=int.from_bytes(VHeader.read(2),"little")
    VHeader.close()
    UVData=[]
    UV=open(custom_direc+"/out/"+UVName,"rb")
    for i in range(int(VBufferSize/Stride)):
    #for i in range(int(2)):
        UV.seek((i*0xC)+8)
        x=UV.read(2)
        y=UV.read(2)
        U= np.frombuffer(x, dtype =np.float16)[0]
        V= np.frombuffer(y, dtype =np.float16)[0]
        #print(U)
        #print(V)
        UVData.append([U,V])
   
       
    UV.close()
    return UVData
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
def ParseMaterial(Material,H64Sort):
    #DumpHash(path,PackageCache,Material)
    Header=binascii.hexlify(bytes(hex_to_little_endian(Material))).decode('utf-8')
    new=ast.literal_eval("0x"+Header)
    pkg = Hex_String(Package_ID(new))
    ent = Hex_String(Entry_ID(new))
    Bank=pkg+"-"+ent+".mat"
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

            PartMats.append(pkg+"-"+ent)
    return PartMats            
def ExtractTerrain(MainPath,TerrainHash,PackageCache,path,H64Sort):
    vertFound=False
    indFound=False
    Input=binascii.hexlify(bytes(hex_to_little_endian(TerrainHash))).decode('utf-8')
    new=ast.literal_eval("0x"+Input)
    pkg = Hex_String(Package_ID(new))
    #print(result)
    ent = Hex_String(Entry_ID(new))
    Bank=pkg+"-"+ent+".terrain"
    #rint(Bank)
    try:
        file=open(MainPath+"/out/"+Bank,"rb")
    except FileNotFoundError:
        UnpackEntry(TerrainHash,PackageCache,path)
        file=open(MainPath+"/out/"+pkg+"-"+ent+".bin","rb")

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
    if Index1 != "ffffffff":
        IndexBufferHash=GetFileReference(binascii.hexlify(bytes(hex_to_little_endian(Index1))).decode('utf-8'),PackageCache,path)
        IndexBuffer=int(ast.literal_eval(IndexBufferHash))
        pkg = Hex_String(Package_ID(IndexBuffer))
        ent = Hex_String(Entry_ID(IndexBuffer))
        IndexName=pkg+"-"+ent+".index"
        indFound=True
    if Vertex1 != "ffffffff":
        VertexBufferHash=GetFileReference(binascii.hexlify(bytes(hex_to_little_endian(Vertex1))).decode('utf-8'),PackageCache,path)
        VertexBuffer=int(ast.literal_eval(VertexBufferHash))
        pkg = Hex_String(Package_ID(VertexBuffer))
        ent = Hex_String(Entry_ID(VertexBuffer))
        VertexName=pkg+"-"+ent+".vert"
        vertFound=True
    if Vertex2 != "ffffffff":
        UVBufferHash=GetFileReference(binascii.hexlify(bytes(hex_to_little_endian(Vertex2))).decode('utf-8'),PackageCache,path)
        UVBuffer=int(ast.literal_eval(UVBufferHash))
        pkg = Hex_String(Package_ID(UVBuffer))
        ent = Hex_String(Entry_ID(UVBuffer))
        UVName=pkg+"-"+ent+".vert"
        UVFound=True
        UVData=ReadUV(binascii.hexlify(bytes(hex_to_little_endian(Vertex2))).decode('utf-8'),UVName)
        #print(UVData)
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
        #print(len(Length))
        num=len(Length)/16
        #print(num)
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
        Verts=[]
        GlobalX=[(max(Xs)+min(Xs))/2,(max(Ys)+min(Ys))/2,(max(Zs)+min(Zs))/2]
        for vert in verts:
            #print(vert)
            Verts.append([(vert[0]-GlobalX[0])*1024,(vert[1]-GlobalX[1])*1024,(vert[2]-GlobalX[2])*8,vert[3]])
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
        triCount=0
        file.seek(0x80)
        PartOffset=int.from_bytes(file.read(4),"little")
        #print(PartOffset)
        file.seek(0x80+PartOffset)
        PartCount=int.from_bytes(file.read(4),"little")
        Parts=[]
        for i in range(PartCount):
            file.seek(0x80+PartOffset+16+(i*0xC))
            Material=binascii.hexlify(bytes(file.read(4))).decode()
            IndexOffset=int.from_bytes(file.read(4),"little")
            IndexCount=int.from_bytes(file.read(2),"little")
            GroupIndex=int.from_bytes(file.read(1),"little")
            DetailLevel=int.from_bytes(file.read(1),"little")
            Parts.append([Material,IndexOffset,IndexCount,GroupIndex,DetailLevel])
        file.seek(0x58)
        MeshGroupOffsets=int.from_bytes(file.read(4),"little")
        file.seek(0x58+MeshGroupOffsets)
        MeshGroupCount=int.from_bytes(file.read(4),"little")
        MeshGroupVectors=[]
        for i in range(MeshGroupCount):
            file.seek(0x58+MeshGroupOffsets+0x10+(i*0x60)+0x20)
            Vector=[ReadFloat32(binascii.hexlify(bytes(file.read(4))).decode()),ReadFloat32(binascii.hexlify(bytes(file.read(4))).decode()),ReadFloat32(binascii.hexlify(bytes(file.read(4))).decode()),ReadFloat32(binascii.hexlify(bytes(file.read(4))).decode())]
            MeshGroupVectors.append(Vector)
            #Scalex Scaley transx transy
        memory_manager = fbx.FbxManager.Create()
        scene = fbx.FbxScene.Create(memory_manager, '')
        PartCount=0
        MinLod=99
        for Part in Parts:
           
            if Part[4] < MinLod:
                MinLod=Part[4]
        OutputtedSubmeshes=[]
        for Part in Parts:
            #print(Part)
            if Part[2] == 0:
                #PartCount+=1
                continue
            if Part[4] > MinLod:
                #PartCount+=1
                continue
            #UVData=TransformTexcord(UVData,MeshGroupVectors[Part[3]])
            #print(UVData)
            OutputtedSubmeshes.append([Part[0],TerrainHash+"_"+str(Part[3])+"_"+str(PartCount)])
            usedVerts=[]
            IndexData=ReadFaces(ind,Part[1],Part[2])
            my_mesh = fbx.FbxMesh.Create(scene, TerrainHash+"_"+str(Part[3])+"_"+str(PartCount))
            Verticies=[]   
            for List in IndexData:
                for Val in List:
                    check=binary_search_single(Verticies,Val)
                    if check == -1:
                        bisect.insort(Verticies, Val)
            count=0
            #print(IndexCount)
            tempcheck=[]
            #
            # print(Verticies)
            Vertexs=[]
            #print(Vert)
            count=0
            my_mesh.InitControlPoints(len(Verticies))
            for Set in Verticies:
                #print(Set)
                v = fbx.FbxVector4(Verts[Set][0]/2, Verts[Set][1]/2, Verts[Set][2]/2, Verts[Set][3]/2)
                my_mesh.SetControlPointAt( v, count )
                count+=1

            #ScaleX,ScaleY,TransX,TransY=TransformTexcord(MeshGroupVectors[Part[3]])
            #print(ScaleY)
            #tempcheck.sort(key=lambda x: x[0])
            #print(IndexData)
            for Face in IndexData:
                my_mesh.BeginPolygon()
                vertex_index = binary_search_single(Verticies,int(Face[0]))
                my_mesh.AddPolygon(vertex_index)
                vertex_index = binary_search_single(Verticies,int(Face[1]))
                my_mesh.AddPolygon(vertex_index)
                vertex_index = binary_search_single(Verticies,int(Face[2]))
                my_mesh.AddPolygon(vertex_index)
                my_mesh.EndPolygon()
            uvLayer = fbx.FbxLayerElementUV.Create(my_mesh, "uv")
            uvLayer.SetMappingMode(fbx.FbxLayerElement.EMappingMode.eByControlPoint)
            uvLayer.SetReferenceMode(fbx.FbxLayerElement.EReferenceMode.eDirect)
            layer = my_mesh.GetLayer(0)
            for Vert in Verticies:
                uvLayer.GetDirectArray().Add(fbx.FbxVector2(float(UVData[Vert][0]) * MeshGroupVectors[Part[3]][0] + MeshGroupVectors[Part[3]][2],float(UVData[Vert][1])*(MeshGroupVectors[Part[3]][1]*-1)+1-MeshGroupVectors[Part[3]][3]))
                #uvLayer.GetDirectArray().Add(fbx.FbxVector2(float(UVData[Vert][0]),float(UVData[Vert][1])))
            try:
                layer.SetUVs(uvLayer)
            except AttributeError:
                u=1   
            #cubeLocation = (xScale, yScale, zScale)
            cubeLocation = (0, 0, 0)
            cubeScale    = (Scale, Scale, Scale)

            newNode = addNode(scene, TerrainHash+"_"+str(Part[3])+"_"+str(PartCount), location = cubeLocation)
            rootNode = scene.GetRootNode()
            #rootNode.LclTranslation.set(fbx.FbxDouble3(xScale, yScale, zScale))
            rootNode.AddChild( newNode )

            newNode.SetNodeAttribute( my_mesh )
            newNode.ScalingActive.Set(1)
            px = fbx.FbxDouble3(1, 1, 1)
            count=0
            #lLayer = my_mesh.GetLayer(0)

            PartCount+=1
            
        filename = MainPath+"\\data\\Terrain\\"+TerrainHash+".fbx"
        FbxCommon.SaveScene(memory_manager, scene, filename)
        memory_manager.Destroy()
        InstFile=open(MainPath+"/data/Instances/"+TerrainHash+".inst","a")
        InstFile.write("0,0,0,0,"+str(InstX)+","+str(InstY)+","+str(InstZ)+",1")
        InstFile.close()
        MatOut=open(os.getcwd()+"/data/Materials/"+TerrainHash+".txt","w")
        for Mesh in OutputtedSubmeshes:
            Textures=ParseMaterial(Mesh[0],H64Sort)
            if Textures != []:
                Textures=",".join(Textures)
                MatOut.write(Mesh[1]+" : "+Mesh[0]+" : "+Textures+"\n")
        MatOut.close()




def GeneratePackageCache(path):
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
PackageCache=GeneratePackageCache("E:\SteamLibrary\steamapps\common\Destiny2\packages")
#ExtractTerrain("E:/MyUnpacker/DestinyUnpackerNew/new/MultiCore","5b75fc80",PackageCache,"E:\SteamLibrary\steamapps\common\Destiny2\packages","")
#filename=name+".bin"
#a=struct.unpack("<e",b'\xfa\xf7')
#print(np.frombuffer((b'\xfa\xf7'), dtype=np.float16)[0])


#exporter.export(scene)

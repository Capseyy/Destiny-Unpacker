import bpy
import json
import mathutils
import os, binascii, ast, os, struct
#!!!DO NOT MANUALLY IMPORT THE FBX, THE SCRIPT WILL DO IT FOR YOU!!!

#Adapted from Monteven's UE5 import script

#Globally gets all the objects in the scene
objects = bpy.data.objects
scene = bpy.context.scene

#Info
Type = "Map"
Name = "Test"
Filepath = os.path.abspath(bpy.context.space_data.text.filepath+"/..") #"OUTPUT_DIR"
installLoc="C:/Users/sjcap/Desktop/MyUnpacker/DestinyUnpackerNew/new/GUI/"

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

#Files to open
info_name = Name + "_info.cfg"
FileName = Filepath + "\\" + Name + ".fbx" 
#

static_names = {} #original static objects

def assemble_map():
    print(f"Starting import on {Type}: {Name}")
    
    #make a collection with the name of the imported fbx for the objects
    bpy.data.collections.new(str(Name))
    bpy.context.scene.collection.children.link(bpy.data.collections[str(Name)])
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[str(Name)]

    bpy.ops.import_scene.fbx(filepath=FileName, use_custom_normals=True, ignore_leaf_bones=True, automatic_bone_orientation=True) #Just imports the fbx, no special settings needed
    
    #assign_materials()
    add_to_collection() 

    newobjects = bpy.data.collections[str(Name)].objects
    objects = bpy.data.objects
    for O in objects:
        print(str(O.name)[:8])
    #print(newobjects)
    print(f"Imported {Type}: {Name}")
    
    #Merge statics, create instances for maps only
    if Is_Map():
        print("Merging Map Statics... ")
        tmp = []
        bpy.ops.object.select_all(action='DESELECT')
     
        #merge static parts into one object
        #for obj in tmp:
        #    bpy.ops.object.select_all(action='DESELECT')
        #    for meshes, mats in config["Parts"].items():
        #        if meshes[:8] == obj and meshes in bpy.context.view_layer.objects:
        #            print(meshes + " belongs to " + obj)
        #            bpy.data.objects[meshes].select_set(True)
        #            bpy.context.view_layer.objects.active = bpy.data.objects[meshes]
        #    bpy.ops.object.join()
        #bpy.ops.outliner.orphans_purge()

        #merge static parts into one object, Old method
        # for x in range(0, 4): #For some reason one pass doesnt work, this slows the import down a bit, idk a better fix
        #     for obj in tmp:
        #         bpy.ops.object.select_all(action='DESELECT')
        #         #print(obj)
        #         for obj2 in newobjects:
        #             if obj2.name[:8] == obj and obj in tmp:
        #                 tmp.remove(obj)
        #                 obj2.select_set(True)
        #                 bpy.context.view_layer.objects.active = obj2
        #         bpy.ops.object.join()
        #         bpy.ops.outliner.orphans_purge()

        newobjects = [] #Clears the list just in case
        newobjects = bpy.data.collections[str(Name)].objects #Readds the objects in the collection to the list

        print("Instancing...")
        
        for Object in bpy.data.objects:
            try:
                file=open(installLoc+"data/Statics/Instances/"+str(Object.name)[:8]+".inst","r")
            except:
                print("no file")
            else:
                
                data=file.read().split("\n")
                file.close()
                #print(data)
                data.remove('')
                #print(data)
                print(Object.name)               
                flipped=binascii.hexlify(bytes(hex_to_little_endian(Object.name[:8]))).decode('utf-8')
        #print(flipped)
                new=ast.literal_eval("0x"+flipped)
                PkgID=Hex_String(Package_ID(new))
                EntryID=Hex_String(Entry_ID(new))
                DirName=PkgID.upper()+"-"+EntryID.upper()+".model"
                #print(data)
                try:
                    file=open(installLoc+"/data/"+DirName,"rb")
                except FileNotFoundError:
                    Scale=0
                else:
                    data1=binascii.hexlify(bytes(file.read())).decode()
                    file.close()
                    Data=[data1[i:i+32] for i in range(0, len(data1), 32)]
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
                #print(data)
                for instance in data:
                    instance=instance.split(",")
                    ob_copy = bpy.data.objects[Object.name].copy()
                    bpy.context.collection.objects.link(ob_copy) #makes the instances

                    location = [float(instance[4]), float(instance[5]), float(instance[6])]
                    #Reminder that blender uses WXYZ, the order in the confing file is XYZW, so W is always first
                    quat = mathutils.Quaternion([float(instance[3]), float(instance[0]), float(instance[1]), float(instance[2])])
                #flipped=binascii.hexlify(bytes(hex_to_little_endian(static))).decode('utf-8')
                #print(flipped)
                #new=ast.literal_eval("0x"+flipped)
                #PkgID=Hex_String(Package_ID(new))
                #EntryID=Hex_String(Entry_ID(new))
                #DirName=PkgID.upper()+"-"+EntryID.upper()+".model"
                #file=open("C:/Users/sjcap/Desktop/MyUnpacker/DestinyUnpackerNew/new/MapExtracter/data/"+DirName,"rb")
                #data=Data=binascii.hexlify(bytes(file.read())).decode()
                #file.close()
                #Data=[data[i:i+32] for i in range(0, len(data), 32)]
                #Vert=Data[5]
                #Dat=[Vert[i:i+8] for i in range(0, len(Vert), 8)] #X,Y,Z,Scale
                #x=binascii.hexlify(bytes(hex_to_little_endian(Dat[0]))).decode('utf-8')
                #y=binascii.hexlify(bytes(hex_to_little_endian(Dat[1]))).decode('utf-8')
                #z=binascii.hexlify(bytes(hex_to_little_endian(Dat[2]))).decode('utf-8')
                #X=struct.unpack('!f', bytes.fromhex(x))[0]
                #Y=struct.unpack('!f', bytes.fromhex(y))[0]
                #Z=struct.unpack('!f', bytes.fromhex(z))[0]
                #location = [instance["Translation"][0], instance["Translation"][1], instance["Translation"][2]]
                    ob_copy.location = location
                    ob_copy.rotation_mode = 'QUATERNION'
                    ob_copy.rotation_quaternion = quat
                    if 7<Scale<8:
                    
                        ob_copy.delta_scale=([Scale/10])*3
                    ob_copy.scale = [float(instance[7])]*3
        
        if "Terrain" in Type:
            for x in newobjects:
                x.select_set(True)
                bpy.ops.object.rotation_clear(clear_delta=False) #Clears the rotation of the terrain

    if not Is_Map():
        for x in newobjects:
            x.select_set(True)
            #Clear the scale and rotation of the entity
            bpy.ops.object.rotation_clear(clear_delta=False)
            bpy.ops.object.scale_clear(clear_delta=False)

    cleanup()


                
def find_nodes_by_type(material, node_type):
    """ Return a list of all of the nodes in the material
        that match the node type.
        Return an empty list if the material doesn't use
        nodes or doesn't have a tree.
    """
    node_list = []
    if material.use_nodes and material.node_tree:
            for n in material.node_tree.nodes:
                if n.type == node_type:
                    node_list.append(n)
    return node_list

def link_diffuse(material):
    """ Finds at least one image texture in the material
        and at least one Principled shader.
        If they both exist and neither have a link to
        the relevant input socket, connect them.
        There are many ways this can fail.
        if there's no image; if there's no principled
        shader; if the selected image/principled sockets
        are already in use.
        Returns false on any detected error.
        Does not try alternatives if there are multiple
        images or multiple principled shaders.
    """
    it_list = find_nodes_by_type(material, 'TEX_IMAGE')
    s_list = find_nodes_by_type(material, 'BSDF_PRINCIPLED')
    if len(s_list) == 0:
        return False  
    image_node = it_list[0]
    shader_node = s_list[0]
    image_socket = image_node.outputs['Color']
    shader_socket = shader_node.inputs['Base Color']
    if shader_socket.is_linked:
        return
    material.node_tree.links.new(shader_socket, image_socket)


def link_normal(material, num = 0):
    it_list = find_nodes_by_type(material, 'TEX_IMAGE')
    s_list = find_nodes_by_type(material, 'NORMAL_MAP')
    if len(s_list) == 0:
        return False
    image_node = it_list[num]
    #print(len(image_node.items()))
    shader_node = s_list[0]
    if image_node.image.colorspace_settings.name == "Non-Color":
        image_socket = image_node.outputs['Color']
        shader_socket = shader_node.inputs['Color']
        if shader_socket.is_linked:
            return
        material.node_tree.links.new(shader_socket, image_socket)
                     
def cleanup():
    print(f"Cleaning up...")
    #Delete all the objects in static_names
    if Is_Map():
        for name in static_names.values():
            bpy.data.objects.remove(bpy.data.objects[name[0]])
        
    #Removes unused data such as duplicate images, materials, etc.
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)

    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)
    print("Done cleaning up!")

def add_to_collection():
    # List of object references
    objs = bpy.context.selected_objects
    # Set target collection to a known collection 
    coll_target = bpy.context.scene.collection.children.get(str(Name))
    # If target found and object list not empty
    if coll_target and objs:
        # Loop through all objects
        for ob in objs:
            # Loop through all collections the obj is linked to
            for coll in ob.users_collection:
                # Unlink the object
                coll.objects.unlink(ob)
            # Link each object to the target collection
            coll_target.objects.link(ob)

def Is_Map():
    if "Map" in Type:
        return True
    if "Terrain" in Type:
        return True
    else:
        return False

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


if __name__ == "__main__":
    #Shows a message box with a message, custom title, and a specific icon
    ShowMessageBox(f"Importing {Name}", "This might take some time! (Especially on multiple imports)", 'ERROR')
    #To give the message box a chance to show up
    bpy.app.timers.register(assemble_map, first_interval=0.3)
    #Deselect all objects just in case 
    bpy.ops.object.select_all(action='DESELECT')

import unreal
import os
#import unreal_engine as ue
Path=os.path.dirname(os.path.realpath(__file__))

def importAssets():
    """
    Import assets into project.
    """
    # list of files to import
    Statics=[]
    print("ran")
    for Static in os.listdir(Path+"/Statics"):
        Statics.append([Path+"/Statics/"+Static,Static])
    for Static in Statics:
        task = unreal.AssetImportTask()
        task.set_editor_property("automated", True)
        task.set_editor_property("destination_path", "/Game/Content/Maps/Statics")
        task.set_editor_property("filename", Static[0])
        task.set_editor_property("replace_existing", True)
        task.set_editor_property("save", True)
        options = unreal.FbxImportUI()
        options.set_editor_property('import_mesh', True)
        options.set_editor_property('import_textures', False)
        options.set_editor_property('import_materials', False)
        options.set_editor_property('import_as_skeletal', False)
        task.set_editor_property("options", options)
        
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
def instanceObjs():
    Statics = unreal.EditorAssetLibrary.list_assets("/Game/Content/Maps/Statics")
    for Static in Statics:
        Name=Static.split("/")[len(Static.split("/"))-1].split(".")[1][9:]
        print(Name)
        try:
            file=open(Path+"/Instances/"+Name[:8]+".inst","r")
        except FileNotFoundError:
            continue
        data=file.read().split("\n")
        data.remove("")
        new_mesh_material=[]
        new_mesh_materials,Samples=CreateMaterials(Name)
        sm = unreal.EditorAssetLibrary.load_asset(Static)
        mesh = unreal.load_asset(Static)
        MatCount=0
        for Val in new_mesh_materials:
            temp=unreal.load_asset("/Game/Content/Maps/Materials/"+Val)
            new_mesh_material.append(temp)
            sm.set_material(MatCount,temp)
            MatCount+=1
        #mesh_materials = mesh.get_editor_property("static_materials")
        #print(new_mesh_materials)        
            #mesh.set_editor_property("material", temp)
        for Instance in data:
            instance=Instance.split(",")
            quat = unreal.Quat(float(instance[0]), float(instance[1]), float(instance[2]), float(instance[3]))         
            euler = quat.euler()
            rotator = unreal.Rotator(euler.x-90, euler.y, -euler.z-180)
            location = [-float(instance[4])*1, float(instance[5])*1, float(instance[6])*1]
            s = unreal.EditorLevelLibrary.spawn_actor_from_object(sm, location=location, rotation=rotator)  # l must be UE4 Object
            s.set_actor_label(s.get_actor_label() + f"_{instance[7]}")
            s.set_actor_relative_scale3d([float(instance[7])]*3)
        
def importTextures():
    Textures=[]
    for Texture in os.listdir(Path+"/Textures"):
        Textures.append([Path+"/Textures/"+Texture,Texture])
    for Texture in Textures:
        task = unreal.AssetImportTask()
        task.set_editor_property("automated", True)
        task.set_editor_property("destination_path", "/Game/Content/Maps/Textures")
        task.set_editor_property("filename", Static[0])
        task.set_editor_property("replace_existing", True)
        task.set_editor_property("save", True)
        options = unreal.FbxImportUI()
        options.set_editor_property('import_mesh', False)
        options.set_editor_property('import_textures', True)
        options.set_editor_property('import_materials', False)
        options.set_editor_property('import_as_skeletal', False)
        task.set_editor_property("options", options)
        
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
def CreateMaterials(Material):
    file=open(Path+"/Materials/"+Material[:8]+".txt","r")
    data=file.read().split("\n")
    data.remove("")
    MatNames=[]
    for Mat in data:
        temp=Mat.split(" : ")
        MatNames.append(temp[1])
        #try:
        random=unreal.EditorAssetLibrary.load_asset("/Game/Content/Maps/Materials/"+temp[1])
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(temp[1], "/Game/Content/Maps/Materials", unreal.Material, unreal.MaterialFactoryNew())
        tex_factory = unreal.TextureFactory()
        tex_factory.set_editor_property('supported_class', unreal.Texture2D)
        names=temp[2].split(",")
        import_tasks=[]
        count=0
        Samples=[]
        for name in names:
            asset_import_task = unreal.AssetImportTask()
            asset_import_task.set_editor_property('filename', Path+"/Textures/"+name+".png")
            asset_import_task.set_editor_property('destination_path', '/Game/Content/Maps/Textures')
            asset_import_task.set_editor_property('save', True)
            asset_import_task.set_editor_property('replace_existing', False)  # dont do extra work if we dont need to
            asset_import_task.set_editor_property('automated', True)
            import_tasks.append(asset_import_task)
            unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([asset_import_task])
            texture_sample = unreal.MaterialEditingLibrary.create_material_expression(material, unreal.MaterialExpressionTextureSample, -1000, -500 + 250 * count)
            ts_TextureUePath = "/Game/Content/Maps/Textures/"+name
            ts_LoadedTexture = unreal.EditorAssetLibrary.load_asset(ts_TextureUePath)
            texture_sample.set_editor_property('texture', ts_LoadedTexture)
            texture_sample.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
            unreal.EditorAssetLibrary.save_loaded_asset(ts_LoadedTexture)
            count+=1
            Samples.append(texture_sample)
            
            unreal.MaterialEditingLibrary.connect_material_property(texture_sample, "BaseColor", unreal.MaterialProperty.MP_BASE_COLOR)
            
    return MatNames,Samples


                
unreal.EditorAssetLibrary.make_directory("/Game/Content/Maps/Statics")
importAssets()
#importTextures()
#CreateMaterials()
instanceObjs()

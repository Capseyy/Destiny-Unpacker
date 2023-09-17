#path="E:/d2_output/data"
import os,binascii,ast

def stripZeros(txt):
    #print(txt)
    if txt == "00000000":
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
import sys
sys.setrecursionlimit(1500)
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

def FileParser(name,StrData,StringRef):
    file2=open(MainPath+"/ExtractedFiles/Investment/InvestmentDump.txt","a")
    DataToWrite=[]
    num=0
    #print(name)
    try:
        file=open(MainPath+"/out/"+name,"rb")
    except FileNotFoundError:
        print("skip")
    else:
        
        Data=binascii.hexlify(bytes(file.read())).decode()
        file.close()
        count=0
        Data2=[Data[i:i+8] for i in range(0, len(Data), 8)]
        for Hash in Data2:
            #print("looped")
            if len(Hash) == 8:
                if Hash == "00000000":
                    continue
                if Hash == "c59d1c81":
                    continue
                temp=[Hash[i:i+2] for i in range(0, len(Hash), 2)]
                temp2=[Hash[i:i+4] for i in range(0, len(Hash), 4)]
                if str(temp2[1]) == "8080":
                    continue
                if temp[3] == "80":
                    flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
                    dec=ast.literal_eval("0x"+stripZeros(flipped))
                    #dec=ast.literal_eval("0x"+Hash)
                    PkgID=Hex_String(Package_ID(dec))
                    EntryID=Hex_String(Entry_ID(dec))
                    DirName=PkgID+"-"+EntryID+".bin"
                    #print(Hash)
                    #FileParser(DirName,StrData)
                
                Dat=StringHash(Hash,StrData,StringRef)
                if Dat != False:
                    DataToWrite.append(Dat)
                    file2.write(Dat+"\n")
                    #print(Dat)
    file2.close()        
    return DataToWrite
        
def FileParser2(name,StrData,StringRef):
    file2=open("Test.txt","a")
    num=0
    #print(name)
    try:
        file=open(MainPath+"/out/"+name,"rb")
    except FileNotFoundError:
        print("skip")
    else:
        
        Data=binascii.hexlify(bytes(file.read())).decode()
        file.close()
        count=0
        Data2=[Data[i:i+8] for i in range(0, len(Data), 8)]
        for Hash in Data2:
            #print("looped")
            if len(Hash) == 8:
                if Hash == "00000000":
                    continue
                if Hash == "c59d1c81":
                    continue
                temp=[Hash[i:i+2] for i in range(0, len(Hash), 2)]
                temp2=[Hash[i:i+4] for i in range(0, len(Hash), 4)]
                if str(temp2[1]) == "8080":
                    continue
                
                Dat=StringHash(Hash,StrData,StringRef)
                if Dat != False:
                    file2.write(Dat+"\n")
                    #print(Dat)
                    break
                    
           
    file2.close()
    return Dat



def find_equal_neighbours(lst, index):
    Vals=[]
    low_index = index
    high_index = index
    value = lst[index][1]
    while low_index - 1 >= 0 and lst[low_index - 1][1] == value:
        low_index -= 1
    while high_index + 1 < len(lst) and lst[high_index + 1][1] == value:
        high_index += 1
    for i in range(low_index, high_index + 1):
        #print('Number Found at index:', i)
        Vals.append(i)
    if Vals != []:
        return Vals
    else:
        return False



def hex_to_little_endian(hex_string):
    little_endian_hex = bytearray.fromhex(hex_string)[::-1]
    return little_endian_hex
def StringHash(Hash,StrData,StringRef):
    #print(Ref)
    flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
    #print(flipped)
    dec = ast.literal_eval("0x"+flipped)
    Found=False
    ans=binary_search(StrData,int(dec))
    #print(ans)
    if str(ans) != "-1":
        Found=True
    if Found == True:
        if StringRef != "":
            Vals=find_equal_neighbours(StrData,ans)
            for Val in Vals:
                if StrData[Val][0].upper() == StringRef.upper():
                    ans=Val
                    break
                    
        return StrData[ans][2]
    else:
        return False
def ApiHashSearch(Hash,ApiData):
    #print(Ref)
    
    Found=False
    ans=binary_search2(ApiData,int(Hash))
    #print(ans)
    if str(ans) != "-1":
        Found=True
    if Found == True:
        #print(ApiData[int(ans)])
        return ApiData[int(ans)][1]
    else:
        return False
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
def pullPerks(DirName):
    file=open(MainPath+"/out/"+DirName,"rb")
    data=binascii.hexlify(bytes(file.read())).decode()
    #print(data)
    Data=[data[i:i+32] for i in range(0, len(data), 32)]
    count=0
    perks=[]
    currentOffset=0
    for Line in Data:
        temp=[Line[i:i+8] for i in range(0, len(Line), 8)]
        currentOffset+=16
        if "d5778080" in temp:
            file.seek(currentOffset+32)
            #print("perked")
            data=binascii.hexlify(bytes(file.read(2))).decode()
            #print(data)
            flipped=binascii.hexlify(bytes(hex_to_little_endian(data))).decode('utf-8')
            temp=stripZeros(flipped)
            perks.append(int(ast.literal_eval("0x"+temp)))
    return perks
def SortH64(Hash64Data):
    newH64=[]
    for Line in Hash64Data:
        if Line == "":
            continue
        temp=Line.split(": ")
        new=ast.literal_eval(temp[0])
        newH64.append([int(new),temp[1]])
    newH64.sort(key=lambda x: x[0])
    #for row in newH64:
    #    print(row)
    return newH64
    
def Hash64Search(Hash64Data,Input):
    #print(Input)
    Found=False
    ans=binary_search2(Hash64Data,int(Input))
    #print(ans)
    if str(ans) != "-1":
        Found=True
    if Found == True:
        return Hash64Data[ans][1]
    else:
        return False
def ExtractWeaponRolls(Main):
    global MainPath
    MainPath=Main
    file=open(MainPath+"/cache/h64.txt","r")
    data=file.read()
    file.close()
    for File in os.listdir(MainPath+"/ExtractedFiles/Investment"):
        os.remove(MainPath+"/ExtractedFiles/Investment/"+File)
    Hash64Data=data.split("\n")
    Hash64Data=SortH64(Hash64Data)
    file=open(MainPath+"/cache/output.txt","r")
    data=file.read()
    StrData=data.split("\n")
    file.close()
    newStrData=[]
    for String in StrData:
        try:
            String.split(" // ")[1]
        except IndexError:
            continue
        try:
            int(String.split(" // ")[1])
        except ValueError:
            continue
            
        try:
            newStrData.append([(String.split(" // ")[0]),int(String.split(" // ")[1]),String.split(" // ")[2]])
        except IndexError:
            #print(String)
            continue
        
        #print(newStrData)
    newStrData.sort(key=lambda x: x[1])
    #StrData=newStrData
    IndexHashes=[]
    PlugSets=[]
    sys.setrecursionlimit(1500)
    for File in os.listdir(MainPath+"/out"):
        if File == "audio":
            continue
        if "indexer" == File.split(".")[1]:
            file=open(MainPath+"/out/"+File,"rb")
            file.seek(0x30)
            data=binascii.hexlify(bytes(file.read())).decode()
            #print(data)
            Data=[data[i:i+64] for i in range(0, len(data), 64)]
            
        elif "imgmap" == File.split(".")[1]:
            file=open(MainPath+"/out/"+File,"rb")
            file.seek(0x30)
            imgdata=binascii.hexlify(bytes(file.read())).decode()
            #print(data)
            imgData=[imgdata[i:i+64] for i in range(0, len(imgdata), 64)]
        elif "main2" == File.split(".")[1]:
            file=open(MainPath+"/out/"+File,"rb")
            file.seek(0x30)
            main2=binascii.hexlify(bytes(file.read())).decode()
            #print(data)
            main2=[main2[i:i+64] for i in range(0, len(main2), 64)]
        elif "test" == File.split(".")[1]:
            file=open(MainPath+"/out/"+File,"rb")
            file.seek(0x40)
            test2=binascii.hexlify(bytes(file.read())).decode()
            #print(data)
            test2=[test2[i:i+16] for i in range(0, len(test2), 16)]
        elif "smap" == File.split(".")[1]:
            file=open(MainPath+"/out/"+File,"rb")
            file.seek(0x30)
            smap=binascii.hexlify(bytes(file.read())).decode()
            #print(data)
            smap=[smap[i:i+64] for i in range(0, len(smap), 64)]
        elif "plug" == File.split(".")[1]:
            file=open(MainPath+"/out/"+File,"rb")
            file.seek(0x20)
            smap=binascii.hexlify(bytes(file.read(2))).decode()
            flipped=binascii.hexlify(bytes(hex_to_little_endian(smap))).decode('utf-8')
            temp=stripZeros(flipped)
            Length=ast.literal_eval("0x"+temp)
            file.seek(0x30)
            count=0
            PlugSetFile=File
            currentOffset=48
            for i in range(Length):
                data=binascii.hexlify(bytes(file.read(0x18))).decode()
                data=[data[i:i+8] for i in range(0, len(data), 8)]
                PlugSets.append([int(ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(data[0]))).decode('utf-8')))),int(ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(data[2]))).decode('utf-8')))),int(ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(data[4]))).decode('utf-8')))),currentOffset+16])
                count+=1
                currentOffset+=24
                
    ImgHashes=[]
    MainHashes=[]
    count=1
    #for Input in imgData:
    #    temp=[Input[i:i+8] for i in range(0, len(Input), 8)]
    #    ImgHashes.append([int(ast.literal_eval(stripZeros("0x"+binascii.hexlify(bytes(hex_to_little_endian(temp[0]))).decode('utf-8')))),binascii.hexlify(bytes(hex_to_little_endian(temp[4]))).decode('utf-8'),count])
    #    count+=1
    #count=1
    for Input in Data: #Indexer
        temp=[Input[i:i+8] for i in range(0, len(Input), 8)]
        dataToAdd=[int(ast.literal_eval("0x"+binascii.hexlify(bytes(hex_to_little_endian(temp[0]))).decode('utf-8'))),binascii.hexlify(bytes(hex_to_little_endian(temp[4]))).decode('utf-8'),count]
        IndexHashes.append(dataToAdd)
        count+=1
    count=1
    for Input in main2:
        temp=[Input[i:i+8] for i in range(0, len(Input), 8)]
        MainHashes.append([int(ast.literal_eval("0x"+binascii.hexlify(bytes(hex_to_little_endian(temp[0]))).decode('utf-8'))),binascii.hexlify(bytes(hex_to_little_endian(temp[4]))).decode('utf-8'),count])
        count+=1
    newHashes=[]
    for Input in test2:
        temp=[Input[i:i+8] for i in range(0, len(Input), 8)]
        newHashes.append([int(ast.literal_eval("0x"+binascii.hexlify(bytes(hex_to_little_endian(temp[0]))).decode('utf-8'))),ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(temp[1]))).decode('utf-8')))])
        count+=1
    count=0
    StringMapping=[]
    for Input in smap:
        temp=[Input[i:i+8] for i in range(0, len(Input), 8)]
        #print(temp)
        StringMapping.append([int(ast.literal_eval("0x"+binascii.hexlify(bytes(hex_to_little_endian(temp[0]))).decode('utf-8'))),binascii.hexlify(bytes(hex_to_little_endian(temp[4]+temp[5]))).decode('utf-8'),count])
        count+=1
    #print(ApiHashes)
    #for thing in ApiHashes:
    #    if thing[0] == 3078487919:
    #        print("BNS is "+str(thing))
    HashesToSearch=[]
    ApiHash="1363886209"
    Hash=[]
    oldStringMapping=StringMapping
    notSortedMain=MainHashes
    oldIndexHashes=IndexHashes
    IndexHashes.sort(key=lambda x: x[0])
    #StringMapping.sort(key=lambda x: x[0])
    MainHashes.sort(key=lambda x: x[0])
    ImgHashes.sort(key=lambda x: x[0])
    #for Entry in ApiHashes:
    #    new=ast.literal_eval("0x"+Entry[0])
    #    if str(new) == ApiHash:
    #        Hash=Entry[1]
    for Entry in IndexHashes:
        ObjectHash=str(Entry[0])
        Hash=ApiHashSearch(int(Entry[0]),MainHashes) #Search specific
        dec=ast.literal_eval("0x"+Hash)
        PkgID=Hex_String(Package_ID(dec))
        EntryID=Hex_String(Entry_ID(dec))
        DirName=PkgID+"-"+EntryID+".bin"
        DirWrite=DirName
        SHash=GetStringIndex(DirName,oldStringMapping)
        if SHash == False:
            continue
        StrRef=Hash64Search(Hash64Data,ast.literal_eval("0x"+SHash))
        #print(StrRef) 
        dec=ast.literal_eval(StrRef)
        PkgID=Hex_String(Package_ID(dec))
        EntryID=Hex_String(Entry_ID(dec))
        StringDir=PkgID+"-"+EntryID
        Name=FileParser2(DirName,newStrData,StringDir)
        if Name == False:
            continue
        temp=Name.split(",")
        new=" ".join(temp)
        temp=new.split(".")
        new=" ".join(temp)
        temp=new.split("-")
        new=" ".join(temp)
        temp=new.split('"')
        new=" ".join(temp)
        temp=new.split('?')
        new=" ".join(temp)
        temp=new.split("'")
        new=" ".join(temp)
        temp=new.split("/")
        new=" ".join(temp)
        #temp=list(new)
        #ew="".join(temp[:15])
        
        Hash=ApiHashSearch(int(Entry[0]),IndexHashes) #Search specific
        dec=ast.literal_eval("0x"+Hash)
        PkgID=Hex_String(Package_ID(dec))
        EntryID=Hex_String(Entry_ID(dec))
        
        DirWrite2=DirName
        perks=pullPerks(PkgID+"-"+EntryID+".bin")
        rolls=pullRolls2(PkgID+"-"+EntryID+".bin",PlugSets)
        #print(rolls)
        #for Roll in rolls:
         #   print(PlugSets[int(Roll)])
        #print(rolls) 
        try:
            fileout=open(MainPath+"/ExtractedFiles/Investment/"+new+" "+ObjectHash+".txt","w")
        except OSError:
            continue
        #print(DirName)
        thingsWritten=0
        fileout.write(new+"\n--------------------")
        fileout.write("\n\n\n\n")
        useless=["Restore Defaults","Restores your gear to its default colors.","All in a Day's Work","The total number of opponents defeated in Crucible matches.","Default Shader","Traveler's Mark","The Rout","Defeat opponents in the Iron Banner. Earn bonus progress by landing final blows on opponents with a higher Power level.","Dismantle"]
        for Entry in newHashes:
            if int(Entry[1]) in perks:
                Hash=ApiHashSearch(Entry[0],MainHashes) #Search specific
                dec=ast.literal_eval("0x"+Hash)
                PkgID=Hex_String(Package_ID(dec))
                EntryID=Hex_String(Entry_ID(dec))
                DirName=PkgID+"-"+EntryID+".bin"
                DataToWrite=FileParser(DirName,newStrData,"")
                if DataToWrite != []:
                    if len(DataToWrite) > 1:
                        for thing in DataToWrite:
                             if thing not in useless:
                                fileout.write(thing+"\n")
                                thingsWritten+=1
                fileout.write("\n\n")
        
        
        if rolls != False:
            
            fileout.write("\n\n\nRANDOM ROLLS\n")
            fileout.write("\n\n\n\n")
            for roll in rolls:
                file=open(MainPath+"/out/"+PlugSetFile,"rb")
                Offset=PlugSets[int(roll)][2]+PlugSets[int(roll)][3]+16
                file.seek(Offset)
                SocketPerks=[]
                for i in range(int(PlugSets[int(roll)][1])):
                    data=binascii.hexlify(bytes(file.read(64))).decode()#16
                    temp=[data[i:i+4] for i in range(0, len(data), 4)]
                    SocketPerks.append(ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(temp[16]))).decode('utf-8'))))
                #print(SocketPerks)
                for Entry in newHashes:
                    if int(Entry[1]) in SocketPerks:
                        Hash=ApiHashSearch(Entry[0],MainHashes) #Search specific
                        dec=ast.literal_eval("0x"+Hash)
                        PkgID=Hex_String(Package_ID(dec))
                        EntryID=Hex_String(Entry_ID(dec))
                        DirName=PkgID+"-"+EntryID+".bin"
                        DataToWrite=FileParser(DirName,newStrData,"")
                        if DataToWrite != []:
                            if len(DataToWrite) > 1:
                                for thing in DataToWrite:
                                    if thing not in useless:
                                        fileout.write(thing+"\n")
                                        thingsWritten+=1
                        fileout.write("\n\n")
        fileout.close()                
                           
        
        #if thingsWritten < 3:
        #    os.remove(os.getcwd()+"/output/"+new+" "+ObjectHash+".txt")
        #break

def GetStringIndex(DirName,oldStringMapping):
    file=open(MainPath+"/out/"+DirName,"rb")
    file.seek(0x8C)
    
    data=binascii.hexlify(bytes(file.read(2))).decode()
    #print(data)
    flipped=binascii.hexlify(bytes(hex_to_little_endian(data))).decode('utf-8')
    temp=ast.literal_eval("0x"+stripZeros(flipped))
    try:
        oldStringMapping[int(temp)][1]
    except IndexError:
        return False
    else:
        return oldStringMapping[int(temp)][1]
def FindEntries(Data,oldApiHashes,ApiHashes):
    min1=ApiHashes[0][0]
    max1=ApiHashes[len(ApiHashes)-1][0]
    correlations=[]
    Data3=[Data[i:i+4] for i in range(0, len(Data), 4)]
    for Index in Data3:
        flipped=binascii.hexlify(bytes(hex_to_little_endian(Index))).decode('utf-8')
        temp=stripZeros(flipped)
        if temp == "":
            continue
        new=ast.literal_eval("0x"+temp)
        if int(new) < len(ApiHashes):
            if oldApiHashes[new][0] not in correlations:
                if min1 <= oldApiHashes[new+1][0] <= max1:
                    correlations.append(int(oldApiHashes[new][0]))

        
    return correlations
def pullRolls2(DirName,PlugSets):
    file=open(MainPath+"/out/"+DirName,"rb")
    data=binascii.hexlify(bytes(file.read())).decode()
    file.seek(0x0)
    RollIndexes=[]
    RollsFound=False
    temp=binascii.hexlify(bytes(file.read())).decode()
    Data=[temp[i:i+32] for i in range(0, len(temp), 32)]
    currentOffset=0
    RollsFound=False
    for Line in Data:
        currentOffset+=16
        Hashes=[Line[i:i+8] for i in range(0, len(Line), 8)]
        if "c3778080" in Hashes:
            Length=ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Hashes[0]))).decode('utf-8')))
            RollsFound=True
            break
    if RollsFound == True:
        PlugSetIndexes=[]
        file.seek(currentOffset)
        for i in range(Length):
            data=binascii.hexlify(bytes(file.read(0x58))).decode()
            Hashes=[data[i:i+4] for i in range(0, len(data), 4)]
            if Hashes[20] != "ffff":
                if Hashes[20] != "0000":
                    if ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Hashes[20]))).decode('utf-8'))) not in PlugSetIndexes:
                        PlugSetIndexes.append(ast.literal_eval("0x"+stripZeros(binascii.hexlify(bytes(hex_to_little_endian(Hashes[20]))).decode('utf-8'))))
            
            
            
        
    
        return PlugSetIndexes
    else:
        return False
def pullRolls(DirName,PlugSets):
    file=open(MainPath+"/out/"+DirName,"rb")
    data=binascii.hexlify(bytes(file.read())).decode()
    file.seek(0x0)
    RollIndexes=[]
    RollsFound=False
    for i in range(int(len(data)/8)):
        temp=binascii.hexlify(bytes(file.read(4))).decode()
        if temp == "c3778080":
            RollsFound=True
            break
    while True:
        temp=binascii.hexlify(bytes(file.read(4))).decode()
        dats=[temp[i:i+4] for i in range(0, len(temp), 4)]
        if temp == "b89f8080":
            break
        for dat in dats:
            if dat == "ffff":
                continue
            if dat == "0000":
                continue
            print(dat)
            thing=binascii.hexlify(bytes(hex_to_little_endian(dat))).decode('utf-8')
            Index=ast.literal_eval("0x"+stripZeros(thing))
            if 0 < int(Index) <len(PlugSets):
                if Index not in RollIndexes:
                    RollIndexes.append(Index)
        
    
    return RollIndexes



def RipAll(Main):
    global MainPath
    MainPath=Main
    file=open(MainPath+"/cache/h64.txt","r")
    data=file.read()
    file.close()
    #for File in os.listdir(MainPath+"/ExtractedFiles/Investment"):
    #    os.remove(MainPath+"/ExtractedFiles/Investment/"+File)
    Hash64Data=data.split("\n")
    Hash64Data=SortH64(Hash64Data)
    file=open(MainPath+"/cache/output.txt","r")
    data=file.read()
    StrData=data.split("\n")
    file.close()
    newStrData=[]
    for String in StrData:
        try:
            String.split(" // ")[1]
        except IndexError:
            continue
        try:
            int(String.split(" // ")[1])
        except ValueError:
            continue
            
        try:
            newStrData.append([(String.split(" // ")[0]),int(String.split(" // ")[1]),String.split(" // ")[2]])
        except IndexError:
            #print(String)
            continue
        
        #print(newStrData)
    newStrData.sort(key=lambda x: x[1])
    for File in os.listdir(MainPath+"/out"):
        if File == "audio":
            continue
        if File.split(".")[1] == "record":
            print("GO")
            FileParser(File,newStrData,"")
        elif File.split(".")[1] == "ActIndex":
            print("GO")
            FileParser(File,newStrData,"")

#ExtractWeaponRolls("C:/Users/sjcap/Desktop/MyUnpacker/DestinyUnpackerNew/new/Public")







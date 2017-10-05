###############################################################################
# INTRODUCTION                                                                #
###############################################################################
# This module exists as a repo of entity merging

# algorithm works in this order:
# NOTE: can only merge if sex NOT opposite
    
#1. sort by descending length order
#2. nameA>=2w, nameB>=2w, shorter in longer                     [multi]
#3. NOHONnameA>=2w, NOHONnameB>=2w, shorter in longer           [multi no-hon]
#4. NOHONnameA>=2w, NOHONnameB==1w, first string matches        [first names]
#5. nameA>=2w, nameB>=2w, first/last match, point array         [middle names]
#... plus 5 additional stages not described here :)
    

def merge_all_entities(name_dict):
    
    #1. sort by descending length order
    namelist = name_dict.keys()
    namelist.sort()
    namelist.sort(key=len, reverse=True)
    
    #2. nameA>=2w, nameB>=2w, shorter in longer                 [multi]
    for i in xrange(len(namelist)-1,-1,-1):
        nameA = namelist[i]
        nameAsplit = nameA.split()
        if len(nameAsplit)<=1: continue
        for j in xrange(len(namelist)-1,i,-1):
            nameB = namelist[j]
            nameBsplit = nameB.split()
            if len(nameBsplit)<=1 or is_oppsex(name_dict,nameA,nameB): continue
            if nameA.find(nameB) != -1:
                name_dict,delname = merge(name_dict,nameA,nameB,True)
                namelist.remove(delname)
                print (nameA + " <-> " + nameB)
    
    #3. NOHONnameA>=2w, NOHONnameB>=2w, shorter in longer       [multi no-hon]            
    for i in xrange(len(namelist)-1,-1,-1):
        nameA = namelist[i]
        nameAsplit = strip_split_honorific(nameA)
        nameAnohon = ' '.join(nameAsplit)
        if len(nameAsplit)<=1 or nameAnohon==nameA: continue
        for j in xrange(len(namelist)-1,i,-1):
            nameB = namelist[j]
            nameBsplit = strip_split_honorific(nameB)
            nameBnohon = ' '.join(nameBsplit)
            if len(nameBsplit)<=1 or is_oppsex(name_dict,nameA,nameB): continue
            if nameAnohon.find(nameBnohon) != -1:
                name_dict,delname = merge(name_dict,nameA,nameB,True)
                namelist.remove(delname)
                print (nameA + " <-> " + nameB)
                
    #4. NOHONnameA>=2w, NOHONnameB==1w, first string matches    [first names]
    for i in xrange(len(namelist)-1,-1,-1):
        nameA = namelist[i]
        nameAsplit = strip_split_honorific(nameA)
        nameAnohon = ' '.join(nameAsplit)
        if len(nameAsplit)<=1 or nameAnohon==nameA: continue
        for j in xrange(len(namelist)-1,i,-1):
            nameB = namelist[j]
            nameBsplit = strip_split_honorific(nameB)
            if len(nameBsplit)!=1 or is_oppsex(name_dict,nameA,nameB): continue
            nameBnohon = ' '.join(nameBsplit)
            if nameAsplit[0]==nameBsplit[0]:
                name_dict,delname = merge(name_dict,nameA,nameB,True)
                namelist.remove(delname)
                print (nameA + " <-> " + nameB)
    
#    #4. nameA>=2w, nameB>=2w, first/last match, point vector    [middle names]
#    for i in xrange(len(namelist)-1,-1,-1):
#        nameA = namelist[i]
#        nameAsplit = nameA.split()
#        if len(nameAsplit)<=1: continue
#        for j in xrange(len(namelist)-1,i,-1):
#            nameB = namelist[j]
#            nameBsplit = nameB.split()
#            if len(namseAsplit)<=1 or is_oppsex(name_dict,nameA,nameB): continue
#            if 
#                name_dict,delname = merge(name_dict,nameA,nameB,True)
#                namelist.remove(delname)
#                print (nameA + " <-> " + nameB)
    return name_dict

def is_honorific(string):
    hons = ["admiraal","admiral","amb","ambassador","aunt","auntie","baron","baroness","bgen","brig","brigadier","briggen","brother","capt","captain","cardinal","chief","cmdr","col","colonel","commander","commissioner","commodore","congressman","corporal","count","countess","dean","democrat","doctor","dr","drs","elder","emperor","ensign","father","friar","gen","general","gov","governor","hon","honorable","honourable","hr","judge","justice","lady","lieut","lieutenant","lord","lt","madam","madame","maj","major","marshal","master","mayor","mdme","miss","mister","monsieur","monsignor","mother","mr","mrs","ms","msgr","pastor","president","priest","priestess","prince","princess","prof","professor","rabbi","rep","republican","representative","rev","reverend","sargeant","secretary","senator","sergeant","sgt","sir","sister","sr","uncle","vice","wizard"]
    if string.lower() in hons:
        return True
    return False
    
def strip_split_honorific(name):
    """
    given: name
    return: name split without leading honorifics
    """
    name = name.split()
    while len(name)>0 and is_honorific(name[0]):
        name = name[1:]
    return name

def is_oppsex(nameDict,nameA,nameB):
    if nameDict[nameA]['sex'] != nameDict[nameB]['sex'] and nameDict[nameA]['sex']!=None and nameDict[nameB]['sex']!=None:
        return True
    return False

def merge(nameDict,nameA,nameB,return_deleted=False,force=False):
    """
    given: dict, 2 names
    do: merge into one, return dict
    combines locations, sex, and aliases.
    nameA is treates as dominant
    """
    # swap if nameB is more popular than nameA
    if force==False and len(nameDict[nameA])<len(nameDict[nameB]):
        nameA,nameB = nameB,nameA
    
    # merge other items
    nameDict[nameA]['locs'] = nameDict[nameA]['locs'] + nameDict[nameB]['locs']
    nameDict[nameA]['aliases'] = nameDict[nameA]['aliases'] + nameDict[nameB]['aliases']
    
    # merge conditional items
    if not nameDict[nameA]['sex']: #sex of dominant, else use recessive
        nameDict[nameA]['sex'] = nameDict[nameB]['sex']
    del nameDict[nameB]
    if return_deleted==True:
        return nameDict,nameB
    return nameDict
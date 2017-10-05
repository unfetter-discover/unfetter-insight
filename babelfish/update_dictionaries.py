# -*- coding: utf-8 -*-

    
import re
import os
import sys
import json
import pickle
from tqdm import tqdm
from text_tools.parsing import extract_web_text
    
def update_dictionaries(JSONfilepath):
    """
    @param JSONfilepath : unfetter json used to define ATT&CK categories
    given a json, retrains the babelfish coefficient sets.
    """
    json_data=open(JSONfilepath).read()
    data = json.loads(json_data)
    patterns = data['attack_patterns']
    
    # get all attach chain phases and patterns
    attack_chains=[]
    for i in range(len(patterns)): 
        for j in range(len(patterns[i]['kill_chain_phases'])): 
            attack_chains = attack_chains + [patterns[i]['kill_chain_phases'][j]['phase_name'].encode('ascii','ignore')]
    attack_chains = set(attack_chains)
    
    # create dict_attackchain  THIS IS CURRENTLY INCORRECT
    dict_attackchain = {name: [] for name in attack_chains}
    for i in range(len(patterns)):
        pattern = patterns[i]['name']
        for j in range(len(patterns[i]['kill_chain_phases'])):
            dict_attackchain[patterns[i]['kill_chain_phases'][j]['phase_name'].encode('ascii','ignore')].append(pattern.encode('ascii','ignore'))    
    for k,v in dict_attackchain.iteritems(): v.sort() 
    
    # build dict_wiki from parsed webpages
    dict_wiki = {}
    re_id = re.compile(r'^(.*?)ID\|')
    re_lr = re.compile(r'\n',flags=re.IGNORECASE)
    re_platform = re.compile(r'(Platform\|)(.*?)(   )')
    for i in tqdm(range(len(patterns))):
    
        # initialize
        pattern = patterns[i]['name']
        url =     patterns[i]['external_references'][0]['url']
        text = extract_web_text(url)
        text = re.sub(re_lr,r' ',text)          #line returns not useful
        text = re.sub(re_id,r'',text)           #remove all text up to ID tag
        text = re.sub(re_platform,r' ',text)    #platform does not add useful info
        
        # find end of body text
        try:
            end = text.index("## References")
        except:
            try:
                end = text.index("|  v ***** d ***** e ")
            except:
                print 'CAUTION: Cannot find References index of \'' + patterns[i]['name'] + '\ in its wiki page. This will negatively effect training!'
            end = len(text)
            
        # insert into dictionary
        text = text[0:end]
        dict_wiki[pattern.encode('ascii','ignore')] = text.encode('ascii','ignore')
    
    # dump the new pickles and retrain
    dir_sp = sys.path
    coefdir = None
    for i in range(len(dir_sp)):
        if os.path.isdir(os.path.join(dir_sp[i],'babelfish')):
            coefdir = os.path.join(dir_sp[i],'babelfish')
            break
    assert coefdir!=None, "Could not locate site-packages directory with babelfish. Aborting."
    with open(os.path.join(coefdir,'dict_wiki'),'wb') as f:
        pickle.dump(dict_wiki,f)
    with open(os.path.join(coefdir,'dict_attackchain'),'wb') as f:
        pickle.dump(dict_attackchain,f)
        
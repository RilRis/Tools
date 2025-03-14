#!/usr/bin/env python3

from flatten_json import flatten
from itertools import islice
import re

class jsonpeek:
    @staticmethod
    def json_head(json_object, lines=10, nest_sep="."): 
        #if the outermost structure of the json is a dictionary...
        if type(json_object) is dict:
            #just flatten it before continuing on
            inpt = flatten(json_object, nest_sep)
            
        #if the json is NOT a dictionary but IS a list of dictionaries....
        elif type(json_object) is list and all(isinstance(item, dict) for item in json_object):
            #turn it into a dictionary by giving it a temporary key
            toflatten = {'tempkey': json_object}
            #flatten the dictionary we made
            intermed = flatten(toflatten, nest_sep)
            #now remove the evidence of that temporary key
            inpt = {}
            for temp_key, val in intermed.items():
                orig_key = re.sub('^tempkey.', '', temp_key)
                inpt[orig_key] = val
        else:
            sys.exit(f"ERROR: json_object \'{json_object}\' is not a dictionary or list of dictionaries")
    
    
        partial_dic = dict(islice(inpt.items(), lines))
        
        for key, val in partial_dic.items():
            print(f'{key}: {val}')
            
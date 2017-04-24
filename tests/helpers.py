# Some useful helper functions here
import json


# We could use pyjq but installing from pip introduces system dependencies
# and requires gcc that may not be available on all building platforms
def filter_dict_by_parent_and_child_key(sourcedict, parentkey, childkey, childvalue, result=[]):
    """
    Filter a dict (typically from JSON) recursively for matches of {parentkey : {childkey: childvalue}}
    anywhere in its structure
    """
    for k, v in sourcedict.items():
        if k == parentkey:
            return {k1: v1 for k1, v1 in sourcedict[k].items() if k1 == childkey and
                    (v1 == childvalue or childvalue in v1.keys())}
        if type(v) == dict:
            res = filter_dict_by_parent_and_child_key(v, parentkey, childkey, childvalue, result)
            if type(res) == dict:
                result.append(res)
    return result

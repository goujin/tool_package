import pymel.core as pm

def pymel_to_maya_cmds(*args):
    def _type_repacking(return_type, converted_list):
        """takes type_string to return all other args in order in the desired type"""
        if return_type == "list":
            return list(converted_list)
        elif return_type == "tuple":
            return tuple(converted_list)
        elif return_type == "set":
            return set(converted_list)

    def _convert(target):
        if isinstance(target, pm.PyNode):
            return target.__melobject__()
        else:
            return target

    def _get_to_bottom(arg):
        return_type=type(arg).__name__
        converted_list = []
        for each in arg:
            if hasattr(each, "__iter__"):
                converted_list.append(_get_to_bottom(each))
            else:
                converted_list.append(_convert(each))
        return _type_repacking(return_type,converted_list)
    return _get_to_bottom(args)

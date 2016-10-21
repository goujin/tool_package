import pymel.core as pm

def getSel_channelBox(return_pynode=False):
    pymel_attr_list=[]
    attr_string=pm.channelBox("mainChannelBox",query=True,sma=True)
    if return_pynode == True:
        selection=pm.selected()
        for ev in selection:
            for attribute in attr_string:
                pynode_attr=ev.attr(attribute)
                pymel_attr_list.append(pynode_attr)
        
        return pymel_attr_list
        
    else:
        return attr_string
import pymel.core as pm


##attribute function

def next_available(attribute): #todo this is bad, look at check_free_index. It is better.
    '''next_available(attribute_without_index),will return array[attribute+[index],index]. 
    Functions looks for one attribute whitch is not connected, this is a while loop a safety was added at index 100000 to break'''
    pymel_object_attr=pm.PyNode(attribute)
    index=0
    while(index!=1000):        
        attribute_index=pm.PyNode(pymel_object_attr.name()+'['+str(index)+']')        
        if not attribute_index.isConnected():
            return [attribute_index,index]
            break
        else:
            index+=1

def check_free_index(attribute):
    connections_list = attribute.connections(connections=True, plugs=True)
    if not connections_list:
        return 0
    else:
        index = connections_list[-1][
            0].index()  # we take the last one to be able to list the input index attribute from the last listed connection
        for x in range(index + 2):
            if not attribute[x].isConnected():
                return x

def attr_lock(*args):  
    for each_list in args:
        for each in each_list:
            each.lock()

def attr_unlock(*args):  
    for each_list in args:
        for each in each_list:
            each.unlock()           


def translate_matrix((translatex,translatey,translatez)):    
    Matrix=pm.datatypes.Matrix([[1.0,0.0,0.0,0.0],[0.0,1.0,0.0,0.0],[0.0,0.0,1.0,0.0],[translatex,translatey,translatez,1.0]])
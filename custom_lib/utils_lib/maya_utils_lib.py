'''doc test '''
import pymel.core as pymel


##attribute function

def next_available(attribute):
    '''next_available(attribute_without_index),will return array[attribute+[index],index]. 
    Functions looks for one attribute whitch is not connected, this is a while loop a safety was added at index 100000 to break'''
    pymel_object_attr=pymel.PyNode(attribute)
    index=0
    while(index!=1000):        
        attribute_index=pymel.PyNode(pymel_object_attr.name()+'['+str(index)+']')        
        if not attribute_index.isConnected():
            return [attribute_index,index]
            break
        else:
            index+=1


import pymel.core as pm

## duplicate_dicting classes in a copy all script
object=pm.selected()


def duplicate(object):

    prefix='driven_'

    #############

    pm.select(object,hi=True)
    selection_list=pm.ls(selection=True,type='transform')
    name_driven_selection_list=maya.cmds.ls(selection=True,type='transform',shortNames=True)


    dirty_duplicate_selection_list=pm.duplicate(selection_list,renameChildren=True)

    duplicate_selection_list=pm.ls(dirty_duplicate_selection_list,type='transform')

    results_dict={}
    #renamming
    for ev in selection_list:
        pm.rename(ev,prefix+ev.name())
    for x, ev in enumerate(duplicate_selection_list):
        pm.rename(ev,name_driven_selection_list[x])
        results_dict[ev]=selection_list[x]
    

    return results_dict
    
    
def is_connected(attribute,target_attribute):
    if target_attribute.isLocked():
        was_locked=True
    else:
        was_locked=False
    target_attribute.unlock()
    pm.connectAttr(attribute,target_attribute)
    if was_locked:
        target_attribute.lock()
    
   
def connect(source_attribute,attribute):
    if source_attribute.isLocked():
        was_locked=True
    else:
        was_locked=False
    source_attribute.unlock()
    pm.connectAttr(source_attribute,attribute)
    if was_locked:
        source_attribute.lock()
    


duplicate_dict=duplicate(object)

for new_object in duplicate_dict:
    
    if type(new_object) == pm.nodetypes.Constraint:
        pm.delete(new_object)
        
    else:
        list_attributes=pm.listAttr(duplicate_dict[new_object],keyable=True)      
        object_list_attributes=[]
        driven_list_attributes=[]
        for attribute_holder in list_attributes:    
            driven_list_attributes.append(pm.PyNode(duplicate_dict[new_object].name()+'.'+attribute_holder))
            object_list_attributes.append(pm.PyNode(new_object.name()+'.'+attribute_holder))

        for x,attribute in enumerate(driven_list_attributes):
            
            print attribute
            
            if attribute.isConnected():   
                    
                print 'Connected'
                is_connected(attribute,object_list_attributes[x])
            
            if attribute.isConnectable() and not attribute.isConnected() :        
                print 'Connect'
                connect(object_list_attributes[x],attribute)
        
            
#exemple
'''
foo = ('a', 'b', 'c')
bar = (1, 2, 3)
dict((k, v) for k, v in zip(foo, bar))
'''
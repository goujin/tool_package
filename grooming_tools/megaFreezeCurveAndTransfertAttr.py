#This is to clean so massively broken curves. The why they broke in the first place was not found. They seem to break often.

import pymel.core as pm
yeti_node=pm.PyNode('pgYetiMaya1')
selection=pm.selected()
list_curves_must_transfer=[]


yeti_node.visibility.set(False)


for curve in selection:
    if new_curve.getShape().nodeType() =='nurbsCurve':
        new_curve=pm.rebuildCurve(curve,ch=False,rpo=False,rt=False,end=True,kr=True,kcp=True,kep=True,kt=True,s=4,d=3,tol=0.01)[0]
        
        #renaming shapes before deleting history
        curve_name=curve.name()
        pm.rename(curve,curve_name+'_old')
        pm.rename(new_curve,curve_name)
        
        if curve.getParent():
            parent_object=curve.getParent()            
        guide_set=pm.listConnections(curve.instObjGroups)[0]    
                
        pm.connectAttr(new_curve.instObjGroups[0],guide_set.dagSetMembers,nextAvailable=True)
        pm.parent(new_curve,parent_object)            
        list_curves_must_transfer.append((curve,new_curve))

    else:

        pm.error("you must not select other object type then a nurbsCurve transform. Problematic object:"+curve.name())
        
        
#yeti needs to trigger to refresh, You need to force the redraw of the viewport + using dirty all just in case
#forcing evaluation to let Yeti create his own attributes    

yeti_node.visibility.set(True)
pm.dgdirty(a=True)
pm.refresh(f=True)
yeti_node.visibility.set(False)
pm.dgdirty(a=True)
pm.refresh(f=True)

#listing the only yeti attributes that an artist would change by himself on a guide
important_attr_list=['.weight','.lengthWeight','.innerRadius','.outerRadius','.density','.baseAttraction','.tipAttraction','.attractionBias',
     '.randomAttraction','.twist','.surfaceDirectionLimit','.surfaceDirectionLimitFalloff']


#transfering values of old_curves to new_curves for all yeti attributes
for old_curve,new_curve in list_curves_must_transfer:

    #Trying to copy all possible yeti attr to the new shape
    for attr in important_attr_list:
        
       value=pm.getAttr(old_curve.getShape().name()+attr)
       
       pm.setAttr(pm.PyNode(new_curve.getShape().name()+attr),value)
       
    pm.makeIdentity(new_curve,a=True,r=True,t=True,s=True)
    pm.bakePartialHistory(new_curve)
    pm.delete(old_curve)



    
    
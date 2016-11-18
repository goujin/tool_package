#Bounding box check test
import pymel.core as pm

objects=pm.selected()

if not pm.objExists("ctrl_assembly_set"):
    assembly_set=pm.createNode("objectSet",name="ctrl_assembly_set")

else:
    assembly_set=pm.PyNode("ctrl_assembly_set")
    
for current_object in objects:
    
    controller_name=current_object.name().replace('_geo','').replace('_grp','')+'_ctrl'
    circle_controller=pm.circle(n=controller_name,normal=(0,1,0))[0]
    pm.delete(circle_controller,constructionHistory=True)
    #order: xmin ymin zmin xmax ymax zmax.

    bounding_box=pm.xform(current_object,query=True,boundingBox=True)
    (bb_x_min,bb_y_min,bb_z_min,bb_x_max,bb_y_max,bb_z_max)=tuple(pm.xform(current_object,query=True,boundingBox=True))

    #controller position world
    x_coordinate=(bb_x_min+bb_x_max)*0.5
    y_coordinate=bb_y_min
    z_coordinate=(bb_z_min+bb_z_max)*0.5


    #float("{:.2f}".format(z_coordinate)) formating example

    circle_controller.translate.set(x_coordinate,y_coordinate,z_coordinate)

    #controller size
    scale_ratio=1.44

    x_length=abs(bb_x_max-bb_x_min)
    z_length=abs(bb_z_max-bb_z_min)

    ctrl_scaleX_value=x_length/2*scale_ratio
    ctrl_scaleZ_value=z_length/2*scale_ratio

    circle_controller.scale.set(ctrl_scaleX_value,1,ctrl_scaleZ_value)
    name_parent=circle_controller.name().replace('_ctrl','_zero')
    ctrl_zero=pm.createNode("transform",n=name_parent)
    
    ctrl_zero.translate.set(circle_controller.translate.get())
    ctrl_zero.rotate.set(circle_controller.rotate.get())
    ctrl_zero.scale.set(circle_controller.scale.get())
    
    pm.parent(circle_controller,ctrl_zero)
    pm.makeIdentity(circle_controller,translate=True,rotate=True,scale=True)
    
    pm.parentConstraint(circle_controller,current_object,maintainOffset=True)    
    pm.scaleConstraint(circle_controller,current_object,maintainOffset=True)
    current_object.inheritsTransform.set(False)
    
    ctrl_zero.instObjGroups.connect(assembly_set.dagSetMembers,nextAvailable=True )
    
    
    
list_objects_connected=[]    
list_ctrls=[]
for ev in assembly_set.dagSetMembers.connections():
        
    list_objects_connected.append(ev.getChildren()[0].translate.connections(shapes=True)[0].getParent())
    list_ctrls.append(ev.getChildren()[0])


for constrained_object,ctrl in zip(list_objects_connected,list_ctrls):
    
    while not constrained_object.getParent()==None:
        constrained_object=constrained_object.getParent()
        if constrained_object.translateX.isConnected():
            object_index=list_objects_connected.index(constrained_object)
            pm.parent(ctrl.getParent(),list_ctrls[object_index])

        break
            
#cleaning render Grp
for childs in pm.listRelatives("render_Grp",ad=True,shapes=False):
    if not childs in list_objects_connected and type(childs)==pm.nodetypes.Transform:
        childs.inheritsTransform.set(True)
    

    
    
        





















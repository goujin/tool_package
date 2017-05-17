#general sandbox of spring tools

#set joints on curve
import pymel.core as pm

curve_list = pm.selected()

for curve in curve_list:
    group=pm.createNode("transform")
    for point_data in curve.getCVs():
        joint=pm.createNode("joint")
        joint.setTranslation(point_data)
        joint.setParent(group)


#to transfer skin from one to another
import pymel.core as pm

selection=pm.selected()
b=selection.pop(-1)
a=selection
pm.select(b.verts,a)

maya.mel.eval("CopySkinWeights")


#create dummy grp for spring setup
import pymel.core as pm

selection=pm.selected()

for ev in selection:
    
    name= ev.name().replace("_Ctrl","_dummy") 
    dummy=pm.createNode("transform",n=name)
    dummy.setParent(ev)
    pm.makeIdentity(dummy,t=True,rotate=True,scale=True)
    dummy.translateX.set(0.2)

#select controler's vertex from selection
import pymel.core as pm 

selection=pm.selected()
pm.select(cl=True)
for ev in selection:
    points=ev.getShape().cv
    pm.select(points,add=True)
    
#chain renamer
name="Top_HairStrand"
selection=pm.selected()
for x,ev in enumerate(selection):
    pm.select(ev,hi=True)
    pm.rename(ev,"{name}_{x}_00_Jnt".format(name=name,x=str(x).zfill(2)))
    for y,each in enumerate(pm.selected()[1:]):
        joint_name="{name}_{x}_{y}_Jnt".format(name=name,x=str(x).zfill(2),y=str(y+1).zfill(2))
        pm.rename(each,joint_name)
pm.select(selection)


# Hide draw style of joints
import pymel.core as pm
pm.select(hi=True)
for ev in pm.selected():
#    if "_Ctrl" not in ev.name():
#        continue
    if isinstance(ev,pm.nodetypes.Joint):
        ev.drawStyle.set(2)
        


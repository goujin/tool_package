"""
#follicle helper
import pymel.core as pm
fol=pm.selected()[0]
joint=pm.createNode("joint")
name=fol.name().replace("Fol","Jnt")
pm.rename(joint,name)
joint.setParent(fol)
m1=fol.getMatrix(worldSpace=True)
joint.setMatrix(m1,worldSpace=True)

"""
    
#Ik Helper script
target1=pm.selected()[0]
target2=pm.selected()[1]
m1=target1.getMatrix(worldSpace=True)
m2=target2.getMatrix(worldSpace=True)
bin_name=target2.name().split("_")[1]
joint1=pm.createNode("joint",n=bin_name+"_IK_{position}_Jnt".format(position="Start"))
joint2=pm.createNode("joint",n=bin_name+"_IK_{position}_Jnt".format(position="End"))

root=pm.group(joint1)
joint2.setParent(joint1)
joint1.setMatrix(m1,worldSpace=True)
joint2.setMatrix(m2,worldSpace=True) 

IK=pm.ikHandle(ee=joint2,sj=joint1)[0]

distance=joint2.translateX.get()
distance_var=distance/4
ctrl1_shape=pm.PyNode("wireController1")
ctrl2_shape=pm.PyNode("wireController2")
ctrl3_shape=pm.PyNode("wireController3")
for x in range(0,5):
    if x==0:
        #joint on joint1
        start_joint=pm.createNode("joint",n=bin_name+"_IK_{position}_Jnt".format(position="00"))
        start_joint.setMatrix(m1,worldSpace=True)
        start_ctrl=pm.duplicate(ctrl3_shape)[0]
        start_ctrl.setParent(root)
        zero=pm.group(start_ctrl,n=bin_name+"_IK_{position}_ZERO".format(position="00"))
        zero.setMatrix(m1,worldSpace=True)
        pm.parentConstraint(start_ctrl,start_joint)
        
        continue
    elif x==4:
        #controller on joint2
        end_ctrl=pm.duplicate(ctrl2_shape)[0]
        end_ctrl.setParent(joint2)
        pm.rename(end_ctrl,joint2.name().replace("Jnt","Ctrl"))
        pm.makeIdentity(end_ctrl,t=1,r=1)
        zero=pm.group(end_ctrl,name=end_ctrl.name().replace("Ctrl","ZERO"))
        zero.setParent(root)
        pm.parentConstraint(end_ctrl,IK)
        
    #joint and controller
    distance_pos=distance_var*x
    new_joint_name=bin_name+"_IK_{position}_Jnt".format(position=str(x).zfill(2))
    new_controller=pm.duplicate(ctrl1_shape)[0]
    new_controller.setParent(joint1)
    pm.makeIdentity(new_controller,t=1,r=1)
    pm.rename(new_controller,new_joint_name.replace("Jnt","Ctrl"))
    zero=pm.group(new_controller,n=new_joint_name.replace("Jnt","ZERO"))
    zero.translateX.set(distance_pos)
    zero.setParent(root)
    
    m3=new_controller.getMatrix(worldSpace=True)    
    joint=pm.createNode("joint",n=new_joint_name)
    joint.setParent(joint1)
    joint.setMatrix(m3,worldSpace=True)
    pm.parentConstraint(new_controller,joint)
    pm.parentConstraint(joint1,zero,mo=True)
    
    
distanceMesure=pm.createNode("distanceDimShape")
loc1=pm.spaceLocator(n=bin_name+"_IK_{position}_Loc".format(position="Start"))
loc2=pm.spaceLocator(n=bin_name+"_IK_{position}_Loc".format(position="End"))
loc1.setMatrix(m1)
pm.parentConstraint(end_ctrl,loc2,mo=False)

mult=pm.createNode("multiplyDivide")
mult.input2X.set(distance)
mult.operation.set(2)
distanceMesure.distance.connect(mult.input1X)
loc1.getShape().worldPosition[0].connect(distanceMesure.startPoint)
loc2.getShape().worldPosition[0].connect(distanceMesure.endPoint)
mult.outputX.connect(joint1.scaleX)
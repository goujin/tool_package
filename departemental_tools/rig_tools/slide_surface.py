import pymel.core as pm
"""
This is made to make joints slide on a surface with a custom attributes.  Select surface then controller and run the code.
#template
surface=pm.selected()[0].getShape()
ctrl=pm.selected()[1]
nbJoints=8
max_value=50
make_joint_slide(surface,nbJoints,ctrl,max_value)
"""

def _aim_module(surface,target,aimed_object):
    cons=pm.normalConstraint(surface,target,upVector=(0,1,0),worldUpType=2,aimVector=(0,0,1),worldUpVector=(0,1,0))
    aimed_object.worldMatrix.connect(cons.worldUpMatrix)
    cons.restRotate.set(0,0,0)
    
    
def make_joint_slide(surface,nb_joints,ctrl,slide_max):
    if not ctrl.hasAttr("slide"):
        pm.addAttr(ctrl,ln="slide",min=0,max=slide_max,defaultValue=slide_max,k=True)
    if not isinstance(surface,pm.nodetypes.NurbsSurface):
        pm.error("stoping. Select surface first")
        
    _u_spacing=1.0/float(nb_joints)
    previous_aimed_object=None
    U_variation=1.0/float(slide_max)
    reversed_range=range(0,nb_joints+1)
    reversed_range.reverse()
    
    for x in reversed_range:
        PoSi=pm.createNode("pointOnSurfaceInfo")    
        U_value=_u_spacing*x
        
        if x==reversed_range[0]:
            
            fol_shape=pm.createNode("follicle")
            fol=fol_shape.getParent()
            
            fol_shape.outRotate.connect(fol.rotate)
            fol_shape.outTranslate.connect(fol.translate)
            surface.worldSpace[0].connect(fol_shape.inputSurface)
            fol_shape.parameterU.set(0)
            fol_shape.parameterV.set(0.5)
            previous_aimed_object=fol
            continue
            
        if x==0:
            loc=pm.spaceLocator()
            U_variation=1.0/float(slide_max)
            
            
            multiply=pm.createNode("multiplyDivide")
            minus=pm.createNode("plusMinusAverage")
            clamp=pm.createNode("clamp")
            
            minus.operation.set(2)
            ctrl.slide.connect(multiply.input1X)
            multiply.input2X.set(U_variation)
            multiply.outputX.connect(minus.input1D[0])
            ctrl.slide.connect(minus.input1D[1])
            minus.input1D[1].disconnect()
            minus.input1D[1].set(U_value)
            
            minus.output1D.connect(clamp.inputR)
            clamp.minR.set(0)
            clamp.maxR.set(1)
            
            
            clamp.outputR.connect(PoSi.parameterU)
            PoSi.parameterV.set(0.5)
            surface.worldSpace[0].connect(PoSi.inputSurface)
            PoSi.position.connect(loc.translate)
            _aim_module(surface,loc,previous_aimed_object)
            #cons=pm.normalConstraint(surface,loc,aimVector=(0,1,0),upVector=(-1,0,0))
            #cons.restRotate.set(0,0,0)
            previous_aimed_object=loc
            continue
        
        
        multiply=pm.createNode("multiplyDivide")
        minus=pm.createNode("plusMinusAverage")
        clamp=pm.createNode("clamp")
        
        minus.operation.set(2)
        ctrl.slide.connect(multiply.input1X)
        multiply.input2X.set(U_variation)
        multiply.outputX.connect(minus.input1D[0])
        ctrl.slide.connect(minus.input1D[1])
        minus.input1D[1].disconnect()
        minus.input1D[1].set(U_value)
        
        minus.output1D.connect(clamp.inputR)
        clamp.minR.set(0)
        clamp.maxR.set(1)
        
        clamp.outputR.connect(PoSi.parameterU)
        PoSi.parameterV.set(0.5)
        surface.worldSpace[0].connect(PoSi.inputSurface)
        
        joint=pm.createNode("joint")
        PoSi.position.connect(joint.translate)
        
        _aim_module(surface,joint,previous_aimed_object)
        previous_aimed_object=joint
        
surface=pm.selected()[0].getShape()
ctrl=pm.selected()[1]
nbJoints=8
max_value=50
make_joint_slide(surface,nbJoints,ctrl,max_value)
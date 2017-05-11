import pymel.core as pm

surface=pm.selected()[0].getShape()
ctrl=pm.selected()[1]
nbJoints=8
_u_spacing=1.0/float(nbJoints)
if not isinstance(surface,pm.nodetypes.NurbsSurface):
    pm.error("stoping. Select surface first")
if not ctrl.hasAttr("slide"):
    pm.addAttr(ctrl,ln="slide",min=0,max=1,k=True)
for x in range(1,nbJoints+1):
    PoSi=pm.createNode("pointOnSurfaceInfo")    
    U_value=_u_spacing*x
    
    minus=pm.createNode("plusMinusAverage")
    clamp=pm.createNode("clamp")
    
    minus.operation.set(2)
    ctrl.slide.connect(minus.input1D[0])
    ctrl.slide.connect(minus.input1D[1])
    minus.input1D[1].disconnect()
    minus.input1D[1].set(1-U_value)
    
    minus.output1D.connect(clamp.inputR)
    clamp.minR.set(0)
    clamp.maxR.set(1)
    
    clamp.outputR.connect(PoSi.parameterU)
    PoSi.parameterV.set(0.5)
    surface.worldSpace[0].connect(PoSi.inputSurface)
    
    joint=pm.createNode("joint")
    PoSi.position.connect(joint.translate)
    pm.normalConstraint(surface,joint)
    
    

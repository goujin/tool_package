import pymel.core as pm

selection=pm.selected()[1:]
nurbsCircle=pm.selected()[0]

for curve in selection:
    if not curve.getShape().nodeType()=='nurbsCurve':
        pm.error('nodeType is not supported. Name:'+curve.name())
    pm.extrude(nurbsCircle,curve,fixedPath=True,useComponentPivot=1,useProfileNormal=True)
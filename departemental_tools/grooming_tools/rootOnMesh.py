import pymel.core as pm

#tool to get root on geometry
selection=pm.selected()
if selection[-1].getChildren()[0].nodeType()!='mesh':
    pm.warning('Last selected object is not a mesh transform!')

targetShape=selection[-1].getChildren()[0]

#little sanity check    
for curve in selection[0:-1]:
    curveChild=curve.getChildren()[0]
    if curveChild.nodeType()!='nurbsCurve':
        pm.error('Warning curve transform not selected')



#dataNode is needed to get the nearest position on mesh
dataNode=pm.createNode('closestPointOnMesh',n='groomingArtifact',ss=True)        
targetShape.worldMesh.connect(dataNode.inMesh)


for curveTransform in selection:         
    
    curve=curveTransform.getChildren()[0]
        
        
    
    if isinstance(curve, pymel.nodetypes.NurbsCurve):
    
        
        curve.getCv(0)=pm.PyNode(curve.name()+'.cv[0]')
        
        inPositionData=pm.xform(root,q=True,t=True,ws=True)
        
        dataNode.inPosition.set(inPositionData)
        
        resultData=dataNode.result.position.get()
        
        pm.xform(root,t=resultData,ws=True)
    else:
        pass
        
pm.delete(dataNode)        
import pymel.core as pm

skinCluster=pm.PyNode("skinCluster229")
index="empty"
for ev in pm.selected():
    for skin in ev.worldMatrix[0].outputs(plugs=True):
        if skin.node() == skinCluster:
            index=skin.index()
            break
    
    parent=ev.getParent().worldInverseMatrix[0]
    parent.connect(skinCluster.bindPreMatrix[index],force=True)

dir(pm.selected()[0].getCVs())

#same as above but inversed way of doing it
skinCluster=pm.PyNode("skinCluster187")
for worldMatrix in skinCluster.matrix.connections(plugs=True):
    joint=worldMatrix.node()
    for skin in joint.worldMatrix[0].outputs(plugs=True):
        if skin.node() == skinCluster:
            index=skin.index()
            break

    parent=joint.getParent().worldInverseMatrix[0]
    parent.connect(skinCluster.bindPreMatrix[index],force=True)
    
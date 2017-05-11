import pymel.core as pm
import itertools as iter
selection=pm.selected()
for ev in pm.selected():
    pm.select(ev)
    #surface rebuilder

    surface=pm.selected()[0].getShape()

    maxUV=surface.spansUV.get()
    maxU=int(maxUV[0])+1
    maxV=int(maxUV[1])+1

    test=pm.nurbsPlane(d=1)[0].getShape()
    pm.delete(test,ch=True)
    for point1,point2 in zip(iter.product((0,1),(1,0)),((0,0),(0,maxV),(maxU,0),(maxU,maxV))):    
        u1,v1=point1
        u2,v2=point2
        test.setCV(u1,v1,surface.getCV(u2,v2,space="world"),space="world")
        
        if False:
            if not pm.objExists(locator):
                locator=pm.spaceLocator()
            data=surface.getCV(u2,v2,space="world")
            locator.setTranslation(data)
pm.select(selection)
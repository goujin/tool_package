import pymel.core as pm
#TODO make UI
#dup curve in-between tool
 
nbCopies=1 #TODO user variable import gui variable

selection=pm.selected()
#little sanity check
for curve in selection:
    curveChild=curve.getChildren()[0]
    if curveChild.nodeType()!='nurbsCurve':
        pm.error('Warning curve transform not selected')
#blending a duplicated curve with selection with a ratio 1/nb of copies that do a smart variation of the copies created    
weightRatio=1.0/(nbCopies+1)

#for math reasons I am pushing the range of times +1 because I can't multiply 0 and code is clearer afterwards
for times in range(1,nbCopies+1):
    newCurve=pm.duplicate(selection[0])
    pm.blendShape(selection[0],selection[1],newCurve,w=[(0,weightRatio*times),(1,weightRatio*times)],o='world') #TODO fix this
    pm.delete(newCurve,ch=True)
    



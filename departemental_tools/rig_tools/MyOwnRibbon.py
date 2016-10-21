import pymel.core as pm
import maya.mel as mel
import math as math
everything=dir(math)
#Okay so this tool is made to as be as much intuitive as posible on a existing nurbsSurface.
#condition1:the nurbs still has the history from it's creation? cool it will be redivided to fit the number of bones that skin the nurbs as written in the script here.
#condition2:the nurbs has no history and has already it's division lvl? fine it will take the highest division lvl and use it as the number of bones to skin the nurbs.
#TODO:the nurbs surface must be planar(not curved) before running this script and plane TO THE GRID. NEVER FREEEEZE IT. ALSO TRY TO ADJUST AS MOST AS POSIBLE IT'S LENGHT WITH THE SCALE.
#WARNING: bones that skin the nurbs won't have mathching orientation with the nurbs placement if the nurbs is not built planar ON THE GRID. Their orientation will be world.
#Also auto won't work if nurbs ain't scale for matching the size you need primerly.
#####################################
'''parameters'''
auto=True
numP=10
UVvalue='U'
definition=20
layers=None

#####################################
def bla(surface,UVvalue=UVvalue,definition=definition,layers=layers):
    pass

#DON'T TOUCH LOWER PART OF THIS SCRIPT
history=True
#set the nurbs
pm.select(hi=True)
nurbsSurf=pm.ls(sl=1,type='nurbsSurface')[0]
#edit surface precision
pm.setAttr(nurbsSurf+'.curvePrecision',14)

#if auto mode is On look for the biggest len with scale values
if auto==True:
    scaleX=nurbsSurf.getParent().scaleX.get()
    scaleZ=nurbsSurf.getParent().scaleZ.get()
    if scaleX>scaleZ:
        UVvalue='U'
    if scaleX<scaleZ:
        UVvalue='V'

#check if you can use the script to use the history on the orig shape
create=pm.connectionInfo(nurbsSurf+'.create',sfd=True) 
if create=='' or create==[]:
    history=False
elif pm.objectType(create)=='makeNurbPlane':
    create=create.split('.')[0]
    create=pm.PyNode(create)
else:
    history=False

#if history set the attribute of the nurbs with script
if history==True:
    if UVvalue=='U':
        pm.setAttr(create+'.patchesU',numP)
        pm.setAttr(create+'.patchesV',1)
    if UVvalue=='V':
        pm.setAttr(create+'.patchesV',numP)
        pm.setAttr(create+'.patchesU',1)
    pm.select(nurbsSurf)
    mel.eval('DeleteHistory')
    
#get the highest definition value on the nurbs
else:    
    UVu=pm.getAttr(nurbsSurf+'.spansUV')[0]
    UVv=pm.getAttr(nurbsSurf+'.spansUV')[1]
    if UVu>UVv:
        numP=UVu
        UVvalue='U'
    if UVu<UVv:
        numP=UVv
        UVvalue='V'
    
#place skin surface with bones
posi=pm.createNode('pointOnSurfaceInfo')
Cjo_grp=[]
nurbsSurf.worldSpace.connect(posi.inputSurface)
name2='bn_CJoint_'
ratio=1.0/numP
if UVvalue=='U':    
    posi.parameterV.set(0.5)    
    for x in range (numP+1):  
        pm.select(cl=True)      
        posi.parameterU.set(x*ratio)
        Cjo=pm.joint(p=posi.position.get(),n=name2+str(x),rad=0.5)
        Cjo_grp.append(Cjo)
if UVvalue=='V':    
    posi.parameterU.set(0.5)
    for x in range (numP+1):
        pm.select(cl=True)
        posi.parameterV.set(x*ratio)
        Cjo=pm.joint(p=posi.position.get(),n=name2+str(x),rad=0.5)
        Cjo_grp.append(Cjo)
pm.delete(posi)
boneCCC_grp=pm.group(Cjo_grp,n='boneCCC_grp')



#create fol
folQ=[]
name='ribbonFol_' 
newRatio=1.0/definition
if UVvalue=='U':   
    for x in range(definition+1):
        fol=pm.createNode('follicle')
        pm.rename(fol.getParent(),name+str(x))
        nurbsSurf.local.connect(fol.inputSurface)
        nurbsSurf.worldMatrix.connect(fol.inputWorldMatrix)
        folQ.append(fol)
        fol.outRotate.connect(fol.getParent().rotate)
        fol.outTranslate.connect(fol.getParent().translate) 
        fol.parameterU.set(x*newRatio)
        fol.parameterV.set(0.5)	
if UVvalue=='V':    
    for x in range(definition+1):
        fol=pm.createNode('follicle',n=name+str(x))
        nurbsSurf.local.connect(fol.inputSurface)
        nurbsSurf.worldMatrix.connect(fol.inputWorldMatrix)
        folQ.append(fol)
        fol.outRotate.connect(fol.getParent().rotate)
        fol.outTranslate.connect(fol.getParent().translate)
        fol.parameterU.set(0.5)
        fol.parameterV.set(x*newRatio)
folGroup=pm.group(folQ,n='folGroup_grp')

#if layer==1:
#get orient
orient=pm.createNode('transform',n='tempOrientation_grp')
aimed=pm.createNode('transform',n='tempAimed_grp')
data=pm.xform(folQ[0].getParent(),q=True,t=True)
pm.xform(orient,t=data)

data=pm.xform(folQ[-1].getParent(),q=True,t=True)
pm.xform(aimed,t=data)

cons=pm.aimConstraint(aimed,orient,mo=False,
                      u=(0,1,0),wut='scene',
                      aim=(1,0,0))
pm.delete(cons,aimed)

orientation=pm.xform(orient,q=True,ro=True,ws=True)
pm.delete(orient)

#orient Cjo_grp
for ev in Cjo_grp:    
    pm.group(ev,n=ev+'_sdk')
    pm.xform(ev.getParent(),ro=orientation,ws=True)

#skin the surface
pm.skinCluster(Cjo_grp,nurbsSurf,mi=1,omi=True)

#attach bones to fol
bone_grp=[]

for x, ev in enumerate(folQ):
    ev=ev.getParent()
    name='bn_'+ev.getParent()
    dat=pm.xform(ev,q=True,t=True,ws=True)
    jo=pm.joint(p=dat,n='bn_'+name,rad=0.2)
    pm.parent(jo,ev)
    bone_grp.append(jo)
pm.group(nurbsSurf,folGroup,boneCCC_grp,n='ribbonSpline')
for ev in [nurbsSurf.getParent(),folGroup]:
    ev.inheritsTransform.set(0)

pm.warning('BWAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH!')
pm.warning('Please rename the ribbonSpline that was created.')
#################################################################



#delete each «number» the object TESTED
import pymel.core as pm
selection=pm.selected()
deleteEachNumber=2 #delete number

for x, object in enumerate(selection):
    if x % deleteEachNumber == 0:
        pm.delete(object)
    else:
        pass
        


#select cv on Curve TESTED
import pymel.core as pm
cvPick= 3 #TODO import the value from user
selection=pm.selected()
cvList=[]

for curveTransform in selection:
    curve=curveTransform.getChildren()[0]
    tempHolder=pm.PyNode(curve.name()+'.cv['+str(cvPick)+']')
    cvList.append(tempHolder) 
pm.select(cvList)

#set pivot on curve root TESTED
import pymel.core as pm
selection=pm.selected()
for curve in selection:
    root=pm.PyNode(curve.name()+'.cv[0]')
    rootPosition=pm.xform(root,q=True,t=True,ws=True)
    pm.xform(curve,rp=rootPosition,sp=rootPosition)
print 'done'    


#reverse curve TESTED
import pymel.core as pm
pm.reverseCurve()


#rebuild curve option toolbox
nb_cv=5 #import user var
pm.rebuildCurve(keepEndPoints=True,keepRange=1,degree=3,span=nb_cv)

#remove cv by index
import pymel.core as pm

userVariable=[3,4,5]    #user input.split(',') to get multiple index to delete at the same time
curve_selection=pm.selected()
curve_selection.span(userVariable)# span is a mistake that indicates I want a comparable manner then polyMesh.cv(0,1,3) to get cv's

'''
#freeze root
#unfreeze
'''
import pymel.core as pm
test=pm.selected()






#particle geo sphere creation
import pymel.core as pm

curve_selection=pm.selected()
data_position_list=[]
curve_root_list=[]
yeti_outerRadius=[]
for curve in curve_selection:
    cv_root=pm.PyNode(curve.name()+'.cv[0]')
    curve_root_list.append(cv_root)
    
for root in curve_root_list:    
    data_position=root.getPosition(space='world')
    data_position_list.append(data_position)

clean_particle_group=pm.createNode('transform',name='Yeti_OutterRadius_grp',)

for number ,position in enumerate(data_position_list):    
    particle=pm.particle(p=[0,0,0],name=curve_selection[number].name()+'_'+str(number)+'_particle')
    particle[0].translate.set(position)
    particle[1].particleRenderType.set(4)
    
    pm.parent(particle[0],clean_particle_group)









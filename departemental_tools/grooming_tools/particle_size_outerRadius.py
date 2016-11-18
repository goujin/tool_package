#particle geo sphere creation
import pymel.core as pm

curve_selection=pm.selected()
data_position_list=[]
curve_root_list=[]
yeti_outerRadius=[]

for object in curve_selection:
    if object.getChildren()[0].isInstance('NurbsCurve') or not object.getChildren()[0].outerRadius.exists():
        pm.error('WARNING: do not select other things then guides with Yeti attribute on!')


if pm.objExists('Yeti_OutterRadius_grp'):
    pm.delete('Yeti_OutterRadius_grp')

for curve in curve_selection:
    cv_root=pm.PyNode(curve.name()+'.cv[0]')
    curve_root_list.append(cv_root)
    
for root in curve_root_list:    
    data_position=root.getPosition(space='world')
    data_position_list.append(data_position)

clean_particle_group=pm.createNode('transform',name='Yeti_OutterRadius_grp',)

for number ,position in enumerate(data_position_list):    
    particle=pm.particle(p=[0,0,0],name=curve_selection[number].name()+'_'+str(number)+'_particle')
    yeti_outerRadius=curve_selection[number].getChildren()[0].outerRadius.get()
    
    particle[0].translate.set(position)        
    particle[0].scale.set([yeti_outerRadius,yeti_outerRadius,yeti_outerRadius])
    particle[1].particleRenderType.set(4)
    
    pm.parent(particle[0],clean_particle_group)



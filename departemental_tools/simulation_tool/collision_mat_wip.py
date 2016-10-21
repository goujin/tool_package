import pymel.core as pm
from sstk.maya.libs import libRender #TODO remove dependency with omtk
selection=pm.selected()
selection_children=[]

#little check for geometry transform only
for object in selection:
    if not (object.getShapes()[0].nodeType()=='mesh') and not len(object.getShape())==1:
        pm.warning('Must select Mesh transform only')
    else:
        selection_children.append(object.getShapes()[0])
        
#create lambert mat function
def create_mat(color_name,color_double3):
    shading_engine=pm.sets( renderable=True, noSurfaceShader=True, empty=True, name= color_name+'_lambert_SG' )
    lambert_mat=pm.createNode('lambert',name=color_name+'_collision_mat')
    lambert_mat.outColor.connect(shading_engine.surfaceShader)
    lambert_mat.color.set(color_double3)
    return lambert_mat
    
#materials won't be created multiple times, all picker base flashy color except yellow. Yellow is kept for the solver only.
if not pm.objExists('green_collision_mat'):
    green_mat=create_mat('green',(0,1,0))
if not pm.objExists('red_collision_mat'):
    red_mat=create_mat('red',(1,0,0))
if not pm.objExists('blue_collision_mat'):
    blue_mat=create_mat('blue',(0,0,1))
if not pm.objExists('pink_collision_mat'):
    pink_mat=create_mat('pink',(1,0,1))
if not pm.objExists('teal_collision_mat'):
    teal_mat=create_mat('teal',(0,1,1))

#making a material list to iterate through
collision_mat=[green_mat,red_mat,blue_mat,pink_mat,teal_mat]

#this is leftovers, I wish I was able to do my own function to assign my materials
for iterator, geometry in enumerate(selection_children):
     pm.select(geometry)
     pm.hyperShade( geometry,assign=collision_mat[iterator%5])
pm.select(selection)        

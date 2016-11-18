import pymel.core as pm
import sys
sys.path.append("/home/jgoulet/dev/tool_package/custom_lib/utils_lib")
import maya_utils.attribute_utils
#dependencie with omtk libRigging #Todo fix this issue
from omtk.libs import libRigging as rig_lib

def args_filter(default,*args):
    '''filters which attributes will be used in case of using different keyword variables for the same action. ex: (default,keep_orient, ko)'''
    for ev in args:
            if ev != None:
                return ev
    return default

def snap(slave,master,keep_orient=None,ko=None,world=True):
    orient=args_filter(True,keep_orient,ko)
    m1=master.getMatrix(worldSpace=True)
    if orient==True:
        slave.setMatrix(m1,worldSpace=True)
    else:
        pm.xform(slave,t=m1.translate,ws=True)



def display_override(pymel_object_list,active=True,display_type="reference"):
    display_type_dict={"normal":0,"template":1,"reference":2}
    for each in pymel_object_list:
        each.overrideEnabled.set(active)
        each.overrideDisplayType.set(display_type_dict[display_type])

def zeroOut(*args):
    new_grps=[]
    for all in args:
        if type(all) != list:
            all=[all]
        for ev in all:
            if isinstance(ev,pm.PyNode):
                m1=ev.getMatrix(worldSpace=True)
                group=pm.group(empty=True,n=ev.name()+"_Grp")
                group.setMatrix(m1)
                pm.parent(group,ev.getParent())
                pm.parent(ev,group)
                new_grps.append(group)
    return new_grps



def target_closestPosition_on_object(object_surface=None,vector_list=[],return_position=False,return_UV=False,clean_delete=True):
    """test(object_surface=,vector_list=[],return_position=True,return_UV=False,clean_delete=True)
    return a tuple of the position and/or UV on the surface"""
    position_return=[]
    uv_position_return=[]
    returnable=[]
    is_curve=False

    if type(vector_list) is not list:
        raise TypeError("vector_list must be of type list")

    if isinstance(object_surface.getShape(),pm.nodetypes.Mesh):
        if not pm.objExists("general_script_cpom"): pm.createNode("closestPointOnMesh",n="general_script_cpom")
        node=pm.PyNode("general_script_cpom")
        object_surface.worldMesh.connect(node.inMesh)

    elif isinstance(object_surface.getShape(),pm.nodetypes.NurbsSurface):
        if not pm.objExists("general_script_cpos"): pm.createNode("closestPointOnSurface",n="general_script_cpos")
        node=pm.PyNode("general_script_cpos")
        object_surface.worldSpace.connect(node.inputSurface,force=True)

    elif isinstance(object_surface.getShape(),pm.nodetypes.NurbsCurve):
        if not pm.objExists("general_script_npoc"): pm.createNode("nearestPointOnCurve",n="general_script_npoc")
        node=pm.PyNode("general_script_npoc")
        object_surface.worldSpace.connect(node.inputCurve,force=True)
        is_curve=True

    else:
        print "No valid surface found"
        return None


    if return_position:
        for each_position in vector_list:
            node.inPosition.set(each_position)
            position=node.result.position.get()
            position_return.append(position)
        returnable.append(position_return)

    if return_UV and not is_curve:
        for each_position in vector_list:
            node.inPosition.set(each_position)
            uv_position=node.result.parameterU.get(),node.result.parameterV.get()
            uv_position_return.append(uv_position)
        returnable.append(uv_position_return)

    elif return_UV and is_curve:
        for each_position in vector_list:
            node.inPosition.set(each_position)
            parameter_value=node.parameter.get()
            uv_position_return.append(parameter_value)
        returnable.append(uv_position_return)

    if clean_delete==True:
        if pm.objExists("general_script_cpom"):pm.delete("general_script_cpom")
        if pm.objExists("general_script_cpos"):pm.delete("general_script_cpos")
        if pm.objExists("general_script_npoc"):pm.delete("general_script_npoc")

    return tuple(returnable)

def create_fol(surface,name=None,UV_position=None):
    if name is not None:fol=pm.createNode("follicle",n=name)
    else: fol=pm.createNode("follicle")
    if isinstance(surface.getShape(),pm.nodetypes.Mesh):
        surface.getShape().worldMesh.connect(fol.inputMesh)
    elif isinstance(surface.getShape(),pm.nodetypes.NurbsSurface):
        surface.getShape().worldSpace.connect(fol.inputSurface)

    fol.outTranslate.connect(fol.getParent().translate)
    fol.outRotate.connect(fol.getParent().rotate)
    if len(UV_position)==2:
        up,vp=UV_position
        fol.parameterU.set(up)
        fol.parameterV.set(vp)
    return fol

def normalize_UV(uv_value,surface):
    minU,maxU=surface.getShape().minMaxRangeU.get()
    minV,maxV=surface.getShape().minMaxRangeV.get()
    newU_value=abs((uv_value[0]-minU)/(maxU-minU))
    newV_value=abs((uv_value[1]-minV)/(maxV-minV))

    return newU_value,newV_value

def set_bones_on_surface(surface,nb_bonesU=3,nb_bonesV=1,joint_name="joint",uv_direction="U",
                         layerLvl="A", has_middle_chain=True):
    """Will set bones on surface. It will return you a list of the joints created and the middle chain unless you ask for it to be false. Changing uv_direction is not yet implemented."""
    temp_posi=rig_lib.create_utility_node("pointOnSurfaceInfo",inputSurface=surface.worldSpace[0])
    
    ruleOfMiddleChain="You must always give a amout of joins for V that will be odd, so there is joints in the middle always"
    joint_order=[]
    middle_chain=[]

    uv_nb_bones=[nb_bonesV,nb_bonesU]
    uv_parameter=["parameterV","parameterU"]
    UV_string=["V","U"]
    if uv_direction=="V":
        uv_nb_bones.reverse()
        uv_parameter.reverse()
        UV_string.reverse()

    for y in range(uv_nb_bones[0]):
        if has_middle_chain:
            if not (uv_nb_bones[0]%2==1 or uv_nb_bones[0]==1): pm.error(ruleOfMiddleChain)
            
        for x in range(uv_nb_bones[1]):
            new_joint=pm.createNode("joint",name=("{}_{}{}_{}{}_Jnt".format(joint_name,UV_string[1],str(x),UV_string[0],str(y))))
            escapeMechanism=False
            if uv_nb_bones[0]==0 or uv_nb_bones[0]==1:
                temp_posi.attr(uv_parameter[0]).set(0.5)
                escapeMechanism=True
            else: 
                temp_posi.attr(uv_parameter[0]).set(1.0/(uv_nb_bones[0]-1)*y)

            if uv_nb_bones[1]==0 or uv_nb_bones[1]==1:
                temp_posi.parameterU.set(0.5)
            else: 
                temp_posi.attr(uv_parameter[1]).set(1.0/(uv_nb_bones[1]-1)*x)
            
            if has_middle_chain:
                if y==int(uv_nb_bones[0]*0.5)+1 or escapeMechanism: middle_chain.append(new_joint)

            position=temp_posi.result.position.get()
            
            pm.xform(new_joint,ws=True,t=position)
            joint_order.append(new_joint)
            new_joint.radius.set(4)
            
    pm.delete(temp_posi)
    layer_group = pm.group(joint_order,n="Layer{}_Grp".format(layerLvl))

    if has_middle_chain: return [joint_order,middle_chain,layer_group]
    else :               return [joint_order,[],layer_group]

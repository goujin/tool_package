import pymel.core as pm
import sys

sys.path.append("/home/jgoulet/dev/tool_package/custom_lib/utils_lib")
import maya_utils.attribute_utils
# dependencie with omtk libRigging #Todo fix this issue
from omtk.libs import libRigging as rig_lib


def args_filter(default, *args):
    '''filters which attributes will be used in case of using different keyword variables for the same action. ex: (default,keep_orient, ko)'''
    for ev in args:
        if ev != None:
            return ev
    return default


def snap(slave, master, keep_orient=None, ko=None, world=True):
    orient = args_filter(True, keep_orient, ko)
    m1 = master.getMatrix(worldSpace=True)
    if orient == True:
        slave.setMatrix(m1, worldSpace=True)
    else:
        pm.xform(slave, t=m1.translate, ws=True)


def display_override(pymel_object_list, active=True, display_type="reference"):
    display_type_dict = {"normal": 0, "template": 1, "reference": 2}
    for each in pymel_object_list:
        each.overrideEnabled.set(active)
        each.overrideDisplayType.set(display_type_dict[display_type])


def zeroOut(*args):
    new_grps = []
    for all in args:
        if type(all) != list:
            all = [all]
        for ev in all:
            if isinstance(ev, pm.PyNode):
                m1 = ev.getMatrix(worldSpace=True)
                group = pm.group(empty=True, n=ev.name() + "_Grp")
                group.setMatrix(m1)
                if ev.getParent(): pm.parent(group, ev.getParent())
                pm.parent(ev, group)
                new_grps.append(group)
    return new_grps


def target_closestPosition_on_object(object_surface=None, vector_list=[], return_position=False, return_UV=False,
                                     clean_delete=True):
    """test(object_surface=,vector_list=[],return_position=True,return_UV=False,clean_delete=True)
    return a tuple of the position and/or UV on the surface"""
    position_return = []
    uv_position_return = []
    returnable = []
    is_curve = False

    if type(vector_list) is not list:
        raise TypeError("vector_list must be of type list")

    if isinstance(object_surface.getShape(), pm.nodetypes.Mesh):
        if not pm.objExists("general_script_cpom"): pm.createNode("closestPointOnMesh", n="general_script_cpom")
        node = pm.PyNode("general_script_cpom")
        object_surface.worldMesh.connect(node.inMesh)

    elif isinstance(object_surface.getShape(), pm.nodetypes.NurbsSurface):
        if not pm.objExists("general_script_cpos"): pm.createNode("closestPointOnSurface", n="general_script_cpos")
        node = pm.PyNode("general_script_cpos")
        object_surface.worldSpace.connect(node.inputSurface, force=True)

    elif isinstance(object_surface.getShape(), pm.nodetypes.NurbsCurve):
        if not pm.objExists("general_script_npoc"): pm.createNode("nearestPointOnCurve", n="general_script_npoc")
        node = pm.PyNode("general_script_npoc")
        object_surface.worldSpace.connect(node.inputCurve, force=True)
        is_curve = True

    else:
        print "No valid surface found"
        return None

    if return_position:
        for each_position in vector_list:
            node.inPosition.set(each_position)
            position = node.result.position.get()
            position_return.append(position)
        returnable.append(position_return)

    if return_UV and not is_curve:
        for each_position in vector_list:
            node.inPosition.set(each_position)
            uv_position = node.result.parameterU.get(), node.result.parameterV.get()
            uv_position_return.append(uv_position)
        returnable.append(uv_position_return)

    elif return_UV and is_curve:
        for each_position in vector_list:
            node.inPosition.set(each_position)
            parameter_value = node.parameter.get()
            uv_position_return.append(parameter_value)
        returnable.append(uv_position_return)

    if clean_delete == True:
        if pm.objExists("general_script_cpom"): pm.delete("general_script_cpom")
        if pm.objExists("general_script_cpos"): pm.delete("general_script_cpos")
        if pm.objExists("general_script_npoc"): pm.delete("general_script_npoc")

    return tuple(returnable)


def create_fol(surface, name=None, UV_position=None):
    if name is not None:
        fol = pm.createNode("follicle", n=name)
    else:
        fol = pm.createNode("follicle")
    if isinstance(surface.getShape(), pm.nodetypes.Mesh):
        surface.getShape().worldMesh.connect(fol.inputMesh)
    elif isinstance(surface.getShape(), pm.nodetypes.NurbsSurface):
        surface.getShape().worldSpace.connect(fol.inputSurface)

    fol.outTranslate.connect(fol.getParent().translate)
    fol.outRotate.connect(fol.getParent().rotate)
    if len(UV_position) == 2:
        up, vp = UV_position
        fol.parameterU.set(up)
        fol.parameterV.set(vp)
    return fol


def normalize_UV(uv_value, surface):
    minU, maxU = surface.getShape().minMaxRangeU.get()
    minV, maxV = surface.getShape().minMaxRangeV.get()
    newU_value = abs((uv_value[0] - minU) / (maxU - minU))
    newV_value = abs((uv_value[1] - minV) / (maxV - minV))

    return newU_value, newV_value


def set_bones_on_surface(surface, nb_bonesU=3, nb_bonesV=1, joint_name="joint", uv_direction="U",
                         layerLvl="A", has_middle_chain=True):
    """Will set bones on surface. It will return you a list of the joints created and the middle chain unless you ask for it to be false. Changing uv_direction is not yet implemented."""

    temp_follicle = create_utility_node("follicle", inputSurface=surface.worldSpace[0])

    ruleOfMiddleChain = "You must always give a amount of joins for V that will be odd, so there is joints in the middle always"
    joint_order = []
    middle_chain = []

    uv_nb_bones = [nb_bonesV, nb_bonesU]
    uv_parameter = ["parameterV", "parameterU"]
    UV_string = ["V", "U"]

    # if uv_direction is "V", then all the important list order is reversed to make the operation work on V
    if uv_direction == "V":
        uv_nb_bones.reverse()
        uv_parameter.reverse()
        UV_string.reverse()

    for y in range(uv_nb_bones[0]):
        if has_middle_chain:
            if not (uv_nb_bones[0] % 2 == 1 or uv_nb_bones[0] == 1): pymel.error(ruleOfMiddleChain)

        for x in range(uv_nb_bones[1]):
            # creating new joint before giving it a position
            new_joint = pymel.createNode("joint", name=(
                "{}_{}{}{}{}_Jnt".format(joint_name, UV_string[1], str(x), UV_string[0], str(y))))
            escapeMechanism = False

            # making the uv calculation.
            if uv_nb_bones[0] == 0 or uv_nb_bones[0] == 1:
                temp_follicle.attr(uv_parameter[0]).set(0.5)
                escapeMechanism = True
            else:
                surface_min, surface_max = surface.attr("minMaxRange{}".format(UV_string[0])).get()
                normalized_value = abs(
                    (surface_max / (float(uv_nb_bones[0]) - 1.0) * y - surface_min) / (surface_max - surface_min))
                temp_follicle.attr(uv_parameter[0]).set(normalized_value)

            if uv_nb_bones[1] == 0 or uv_nb_bones[1] == 1:
                temp_follicle.parameterU.set(0.5)
            else:
                surface_min, surface_max = surface.attr("minMaxRange{}".format(UV_string[1])).get()
                normalized_value = abs(
                    (surface_max / (float(uv_nb_bones[1]) - 1.0) * x - surface_min) / (surface_max - surface_min))
                temp_follicle.attr(uv_parameter[1]).set(normalized_value)

            if has_middle_chain:
                if y == int(uv_nb_bones[0] * 0.5) + 1 or escapeMechanism: middle_chain.append(new_joint)

            position = temp_follicle.outTranslate.get()
            # joint placement.
            pymel.xform(new_joint, ws=True, t=position)
            joint_order.append(new_joint)

    pymel.delete(temp_follicle.getParent())
    layer_group = pymel.group(joint_order, n="Layer{}_Grp".format(layerLvl))

    if has_middle_chain:
        return [joint_order, middle_chain, layer_group]
    else:
        return [joint_order, [], layer_group]


def get_vector_diff_from_object(object1, object2):
    """compares translation values "world" from both objects given"""
    position1_vector = object1.getTranslation(space="world")
    position2_vector = object2.getTranslation(space="world")
    length = position1_vector - position2_vector
    return length


class tuple_util(object):
    # todo all this needs to be cleared and removed or do some big introception on your life

    def __init__(self):
        tuple_data = None

    def __isub__(self, other):
        if not isinstance(other, tuple_util):
            raise TypeError("substracted data must be of: tuple_util")
        x1, y1, z1 = self.tuple_data
        x2, y2, z2 = other.tuple_data
        return tuple_util(x1 - x2, y1 - y2, z1 - z2)

    def __iadd__(self, other):
        if not isinstance(other, tuple_util):
            raise TypeError("added data must be of: tuple_util")
        x1, y1, z1 = self.tuple_data
        x2, y2, z2 = other.tuple_data
        return tuple_util(x1 + x2, y1 + y2, z1 + z2)

    def __imul__(self, other):
        if isinstance(other, float):
            return tuple_util([ev * other for ev in self.tuple_data])

    def __idiv__(self, other):
        if isinstance(other, float):
            return tuple_util([ev / other for ev in self.tuple_data])


def insert_joints_inBetween(object1, object2, name="default", nbJoints=3, make_hierchy=None,
                            orient_blend=True, **kwargs):
    """inserts joints between two joints. object1 is the starting point, object2 is the end point"""

    if make_hierchy == None:
        # this will check if both joints are of the same hierachy
        x = 0
        _undirect_hierachy = False
        while True and x != 1000:
            parent = object2
            parent = parent.getParent()
            if parent == object1:
                is_same_hierachy = True
                break
            elif parent == None:
                is_same_hierachy = False
                break
            elif isinstance(parent, pm.nodetypes.Joint):
                _undirect_hierachy = True

            x += 1

    _all_are_joints = False
    if isinstance(object1, pm.nodetypes.Joint) and isinstance(object2, pm.nodetypes.Joint):
        _all_are_joints = True

    # create joint chain
    position_vector = get_vector_diff_from_object(object1, object2)
    chunk_vector = position_vector / nbJoints + 1
    start_vector = object1.getTranslation(space="world")

    # todo big cleanup here, officially take a step back
    if not _undirect_hierachy:
        pass

    orientation1_tupple = pm.dt.Vector(object1.rotate.get())

    if _all_are_joints:
        pass
    for x in range(nbJoints):
        if x + 1 == nbJoints:
            # to not do the last joint witch should be the position of object 2
            break
        if _all_are_joints:
            pass

        joint_name = "%_%_Jnt".format(name, str(x + 1))
        new_position = start_vector + chunk_vector * (x + 1)
        new_joint = pm.joint(n=joint_name, p=new_position)


def controller_matcher(selection=pm.selected(), mirror_prefix=["L_", "R_"]):
    """it will try to find it's match on the other side of the rig
    Select controls curves (ex. 'leg_front_l_ik_ctrl'), and set the mirror prefix ('_l_', '_r_')"""

    def safety_check(check_object=None, check_curve_list=None):
        if check_object:
            if not isinstance(check_object, pm.nodetypes.Transform):
                return False
        elif check_curve_list:
            for each in check_curve_list:
                if not isinstance(each, pm.nodetypes.NurbsCurve):
                    return False

    def get_previous_controller_info(previous_controler):
        # this implementation assumes your only using one shape or that the the first shape of children shapes is representative of the lot
        assumed_only_shape = previous_controler.getShape()

        if assumed_only_shape.overrideEnabled.get():  # will return False if it isn't activated
            if assumed_only_shape.overrideRGBColors.get():
                rgb_color = assumed_only_shape.overrideColorRGB.get()
                color_info = [True, True, rgb_color]
            else:
                index_color = assumed_only_shape.overrideColor.get()
                color_info = [True, False, index_color]
        else:
            color_info = [False, False, []]

        if assumed_only_shape.visibility.isConnected():
            visibility_connection_info = assumed_only_shape.visibility.connections(plugs=True)[0]

        else:
            visibility_connection_info = False

        return (color_info, visibility_connection_info)

    for selected_object in selection:
        _possible_sides = list(mirror_prefix)
        # safety check removed temporarly, Felipe brought to my attention that some people likes to parent their under lot's and many different things
        '''
        if safety_check(selected_object):
            # Check that user doesn't give out shapes or joints per inadvertance
            pm.warning("This is not a valid transform node.\n Node:{},\nnodeType:{}".format(selected_object.name(),
                                                                                            str(type(selected_object))))
        '''
        dup = pm.duplicate(selected_object, rc=1)[0]
        tmp = pm.createNode('transform')
        pm.parent(tmp, dup)
        pm.xform(tmp, t=(0, 0, 0), ro=(0, 0, 0), scale=(1, 1, 1))
        pm.parent(tmp, w=1)
        for sh in dup.getShapes():
            pm.parent(sh, tmp, r=1, s=1)

        pm.delete(dup)
        neg = pm.createNode('transform')
        pm.parent(tmp, neg)
        neg.scaleX.set(-1)

        skip_mechanism = False  # This is in place to protect from possible controller having no mirror prefix at all

        if _possible_sides[0] in selected_object.name():
            current_side = _possible_sides.pop(0)

        elif _possible_sides[1] in selected_object.name():
            current_side = _possible_sides.pop(1)

        else:
            skip_mechanism = True

        if skip_mechanism:
            pm.delete(neg)

        else:
            # selected_object.replace(left, right)
            target = pm.PyNode(selected_object.name().replace(current_side, _possible_sides[0]))
            if pm.objExists(target):
                pm.parent(tmp, target)
                pm.makeIdentity(tmp, apply=True, t=True, r=True, s=True)
                pm.parent(tmp, w=1)
                shapesDel = target.getShapes()
                color_info, vis_master = get_previous_controller_info(target)
                if shapesDel:
                    pm.delete(shapesDel)
                shapes = pm.listRelatives(tmp, shapes=1)
                for sh in shapes:
                    pm.parent(sh, target, r=1, s=1)
                    pm.rename(sh.name(), target.name() + "Shape")

                    if color_info[0]:
                        if color_info[1]:
                            sh.overrideEnabled.set(True)
                            sh.overrideRGBColors.set(1)
                            sh.overrideColorRGB.set(color_info[2])

                        else:
                            sh.overrideEnabled.set(True)
                            sh.overrideRGBColors.set(0)
                            sh.overrideColor.set(color_info[2])

                    else:
                        sh.overrideEnabled.set(False)

                    if vis_master:
                        vis_master.connect(sh.visibility)
            else:
                pm.warning('{} not found!'.format(target.name()))
            pm.delete(tmp, neg)


def controller_matcher_on_selection(selection=pm.selected(), flip=False):
    """it will replace the shape of selected2 with the shapes of selected1"""

    def get_previous_controller_info(previous_controler):
        # this implementation assumes your only using one shape or that the the first shape of children shapes is representative of the lot
        assumed_only_shape = previous_controler.getShape()

        if assumed_only_shape.overrideEnabled.get():  # will return False if it isn't activated
            if assumed_only_shape.overrideRGBColors.get():
                rgb_color = assumed_only_shape.overrideColorRGB.get()
                color_info = [True, True, rgb_color]
            else:
                index_color = assumed_only_shape.overrideColor.get()
                color_info = [True, False, index_color]
        else:
            color_info = [False, False, []]

        if assumed_only_shape.visibility.isConnected():
            visibility_connection_info = assumed_only_shape.visibility.connections(plugs=True)[0]

        else:
            visibility_connection_info = False

        return (color_info, visibility_connection_info)

    source = selection[0]

    dup = pm.duplicate(source, rc=1)[0]
    tmp = pm.createNode('transform')
    pm.parent(tmp, dup)
    pm.xform(tmp, t=(0, 0, 0), ro=(0, 0, 0), scale=(1, 1, 1))
    pm.parent(tmp, w=1)
    for sh in dup.getShapes():
        pm.parent(sh, tmp, r=1, s=1)

    pm.delete(dup)
    temp_grp_negScale = pm.createNode('transform')
    pm.parent(tmp, temp_grp_negScale)
    if flip:
        temp_grp_negScale.scaleX.set(-1)

    target = selection[1]

    pm.parent(tmp, target)
    pm.makeIdentity(tmp, t=True)  # this brings everything puts translate and rotate values at 0 before scale freezing
    pm.makeIdentity(tmp, apply=True, t=True, r=True, s=True)
    pm.parent(tmp, w=1)
    shapesDel = target.getShapes()
    color_info, vis_master = get_previous_controller_info(target)
    if shapesDel:
        pm.delete(shapesDel)
    shapes = pm.listRelatives(tmp, shapes=1)
    for sh in shapes:
        pm.parent(sh, target, r=1, s=1)
        pm.rename(sh.name(), target.name() + "Shape")

        if color_info[0]:
            if color_info[1]:
                sh.overrideEnabled.set(True)
                sh.overrideRGBColors.set(1)
                sh.overrideColorRGB.set(color_info[2])

            else:
                sh.overrideEnabled.set(True)
                sh.overrideRGBColors.set(0)
                sh.overrideColor.set(color_info[2])

        else:
            sh.overrideEnabled.set(False)

        if vis_master:
            vis_master.connect(sh.visibility)

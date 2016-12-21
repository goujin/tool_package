import pymel.core as pm
import pymel.core as pm
import maya.mel as mel
from omtk.libs import libRigging
from omtk.libs.libRigging import create_utility_node


def get_zero_grp(target):
    return target.getParent().getParent().getParent()


def get_dynamic_parent(target):
    return target.getParent().getParent()


def get_animation_layer(target):
    return target.getParent()


def localize_matrice_value(world_source,
                           holdMatrix,
                           previous_influence=None):  # world_source must be a locator in chain before feeding it to local target.

    # world source is the sim locator
    # bind_pose is is the kept parent of the ctrl data, child to the sim locator
    # third is the loc2 sim
    #
    if previous_influence is None:
        raise Exception("the ik spring behavior is not ready. previous influence is needed!")
    else:

        attr_world_bindpose = libRigging.create_utility_node(
            'multMatrix',
            matrixIn=(
                holdMatrix.outMatrix,
                previous_influence.worldMatrix
            )
        ).matrixSum

        attr_world_bindpose_inv = libRigging.create_utility_node(
            'inverseMatrix',
            inputMatrix=attr_world_bindpose
        ).outputMatrix

        attr_local_tm = libRigging.create_utility_node(
            'multMatrix',
            matrixIn=(
                world_source.worldMatrix,
                attr_world_bindpose_inv
            )
        ).matrixSum

        decompose_m = libRigging.create_utility_node(
            'decomposeMatrix',
            inputMatrix=attr_local_tm
        )

    return decompose_m


def prepare_ctrl(ctrl, master=False):
    """This is there to prepare the controler if needed, for the activation switch and to have a parent to layer the sim with animation"""
    master_needs_preparation = False
    if master and not "springActivation" in pm.listAttr(ctrl):
        pm.addAttr(ctrl, longName="springActivation", attributeType="enum", enumName="Off:On", keyable=False,
                   defaultValue=1)
        ctrl.springActivation.set(channelBox=True)
        pm.addAttr(ctrl, longName="dynamicEnvelope", attributeType="float", keyable=True, defaultValue=1, min=0)
        pm.addAttr(ctrl, longName="startFrame", attributeType="float", keyable=False, defaultValue=1)
        pm.addAttr(ctrl, longName="timeScale", attributeType="float", keyable=True, defaultValue=1, min=0)
        pm.addAttr(ctrl, longName="motionDrag", attributeType="float", keyable=True, defaultValue=0, min=0)
        pm.addAttr(ctrl, longName="springSampling", attributeType="float", keyable=True, defaultValue=12, min=1)
        ctrl.startFrame.set(channelBox=True)
    zeroOut(ctrl, suffix="_DynamicParent")
    zeroOut(ctrl, suffix="_DynamicAnimation")


def get_bind_pose(target):  # todo check if this is still in use somewhere
    children = target.getChildren()
    for ev in children:
        if "BindPose" in ev.name():
            return ev
    return None


def zeroOut(transform, suffix="_ZERO"):
    if isinstance(transform, pm.PyNode):
        m1 = transform.getMatrix(worldSpace=True)
        group = pm.group(empty=True, n=transform.name().replace("_Ctrl", "") + suffix)
        group.setMatrix(m1)
        if transform.getParent(): pm.parent(group, transform.getParent())
        pm.parent(transform, group)

    return group


def create_curve(ctrl_selection, setup_name=None):
    """part one of the spring creation. Creates a curve and sets the attr on the master ctrl. Also gives a new parent to the ctrl."""
    curve_name = "{}_curve".format(setup_name)
    data_point = []
    for each in ctrl_selection:
        if len(data_point) == 0:
            prepare_ctrl(each, master=True)
        else:
            prepare_ctrl(each)
        point_data = pm.xform(each, q=1, t=1, ws=1)
        data_point.append(point_data)
    if curve_name == None:
        curve = pm.curve(points=data_point, degree=1)
    else:
        curve = pm.curve(point=data_point, name=curve_name, degree=1)
    new_curve = pm.rebuildCurve(curve, degree=1, keepControlPoints=True, constructionHistory=False, keepRange=0)[
        0].getShape()  # I need to rebuild the dam thing so it has a range between 0-1
    return new_curve


def make_dynamic_setup(curve, ctrl_master, setup_name="test", rig_high_point=None):
    """creates the default setup for maya dynamics. It affects as little as it can the nucleus because it is re used for all springs
    instead it clamps the value directly in the hairSystem node. It also make the connection to shut the dynamic without
    completly shutting down the follicle. static vs off in the hairSystem node"""
    time = pm.PyNode("time1")
    nucleus = create_utility_node("nucleus",
                                  name="{ctrl_name}_spring_nucleus".format(
                                      ctrl_name=ctrl_master.name().replace("_Ctrl", "")),
                                  currentTime=time.outTime,
                                  enable=ctrl_master.springActivation,
                                  subSteps=ctrl_master.springSampling,
                                  timeScale=ctrl_master.timeScale)

    follicle = create_utility_node("follicle",
                                   degree=1,
                                   startDirection=1,
                                   restPose=1,
                                   startPosition=curve.local,
                                   startPositionMatrix=curve.getParent().worldMatrix[0])

    pm.rename(follicle.getParent(), "{}_follicle".format(setup_name))
    pm.parent(curve.getParent(), follicle.getParent())
    follicle.getParent().setParent(rig_high_point)

    dynamic_curve = create_utility_node("nurbsCurve",
                                        create=follicle.outCurve)

    pm.rename(dynamic_curve.getParent(), "{}_DynamicCurve".format(setup_name))

    nHair = create_utility_node("hairSystem",
                                active=True,
                                collide=False,
                                nextState=nucleus.outputObjects[0],
                                startFrame=ctrl_master.startFrame,
                                currentTime=time.outTime,
                                motionDrag=ctrl_master.motionDrag)
    nHair.startState.connect(nucleus.inputActiveStart[0])
    nHair.currentState.connect(nucleus.inputActive[0])

    pm.rename(nHair.getParent(), "{}_nHair".format(setup_name))
    follicle.outHair.connect(nHair.inputHair[0])  # It should in fact always only have on curve per hairSystem.
    nHair.outputHair[0].connect(follicle.currentPosition)
    nHair_condition_node = create_utility_node("condition",
                                         secondTerm=1,
                                         firstTerm=ctrl_master.springActivation)  # firstTerm=ctrl_master.springActivation

    nHair_condition_node.colorIfFalseR.set(1)
    nHair_condition_node.colorIfTrueR.set(3)
    nHair_condition_node.outColorR.connect(nHair.simulationMethod)  # cannot connect via utility node.

    follicle_condition_node = create_utility_node("condition",
                                         secondTerm=1,
                                         firstTerm=ctrl_master.springActivation)  # firstTerm=ctrl_master.springActivation

    follicle_condition_node.colorIfFalseR.set(0)
    follicle_condition_node.colorIfTrueR.set(2)
    follicle_condition_node.outColorR.connect(follicle.simulationMethod)  # cannot connect via utility node.


    return dynamic_curve  # this curve should be a functionnal dynamic curve


def make_aim_connection_setup(dynamic_nurbsCurve, ctrl_list, ctrl_master, setup_name="spring", FK=True, aim=[0, 1, 0],
                              upVector=[1, 0, 0], rig_high_point=None):
    """Third part of the spring setup. This will create locator on curve points, linked them to the curve position data
    and aim each of them to the previous. It also makes a small matrix multiplication setup to localize the world data to
     the local fk chain of ctrl or to the rig itself. It creates a setup of switch to shut down the data collected or to
      scale it up or down when in need."""
    temp_nearestPointC = pm.createNode("nearestPointOnCurve")
    dynamic_nurbsCurve.worldSpace[0].connect(temp_nearestPointC.inputCurve)
    sim_locator_list = []
    # part one is setting up the sim locators with the point on curve info
    for x, (coordinates, current_ctrl) in enumerate(zip(dynamic_nurbsCurve.getCVs(), ctrl_list)):
        pointInfo = pm.createNode("pointOnCurveInfo")
        dynamic_nurbsCurve.worldSpace[0].connect(
            pointInfo.inputCurve)  # note that to myself. Using the wolrdSpace[0] of the curve instead of the local, better. Just localize your data after.
        temp_nearestPointC.inPosition.set(coordinates)
        parameter_fetched = temp_nearestPointC.parameter.get()
        pointInfo.parameter.set(parameter_fetched)

        # look at line below, zfill makes a padding of 0 for (x) being the minimal length to a string
        sim_loc = pm.createNode("locator").getParent()
        pm.rename(sim_loc, "{}_{}_Loc".format(setup_name, str(x).zfill(2)))
        sim_loc.setMatrix(current_ctrl.getMatrix(worldSpace=True))
        pointInfo.position.connect(sim_loc.translate)
        sim_locator_list.append(sim_loc)  # stocking only locator transform for efficiency gain

    # second part is to set up the dummy locators and the orient on the sim locators

    holdMatrix_list = []
    for x, (sim_loc, current_ctrl) in enumerate(zip(sim_locator_list, ctrl_list)):
        # try and match controller parent, it is a kind of bind pose and not a true matching setup
        ctrl_parent = get_zero_grp(current_ctrl)
        grp_m = ctrl_parent.matrix.get()

        holdMatrix = pm.createNode("holdMatrix", name="Dummy_{}_holdMatrix".format(ctrl_parent.name()))
        holdMatrix.inMatrix.set(
            grp_m)
        holdMatrix_list.append(holdMatrix)

        if x == 0:
            pm.aimConstraint(sim_locator_list[x + 1],
                             sim_locator_list[x],
                             aim=aim,
                             maintainOffset=True,
                             upVector=upVector,
                             wut="objectrotation",
                             worldUpObject=rig_high_point,
                             worldUpVector=upVector)

        elif not x == len(ctrl_list) - 1:
            # the last locator won't be able to react to the others in the same way
            pm.aimConstraint(sim_locator_list[x + 1],
                             sim_locator_list[x],
                             aim=aim, maintainOffset=True,
                             upVector=upVector,
                             wut="objectrotation",
                             worldUpObject=sim_locator_list[x - 1],
                             worldUpVector=upVector)

        # part three. I try to plug everything together.formula example for matrices multiplication: dummy_bind_loc2(local) * sim_loc1 *-loc2_sim
        # I do a small feet of matrices multiplication here to localize the result for the fk chain
        if not x == 0:
            decompose_node = localize_matrice_value(sim_loc, holdMatrix, previous_influence=sim_locator_list[x - 1])
        else:
            decompose_node = localize_matrice_value(sim_loc, holdMatrix, previous_influence=rig_high_point)

        multiply_scaling_t = pm.createNode("multiplyDivide",
                                           name="mult_{mult_name}{padding}_trans_scale".format(mult_name=setup_name,
                                                                                               padding=str(x).zfill(2)))
        multiply_scaling_r = pm.createNode("multiplyDivide",
                                           name="mult_{mult_name}{padding}_rot_scale".format(mult_name=setup_name,
                                                                                             padding=str(x).zfill(2)))

        for input2_plug1, input2_plug2 in zip(multiply_scaling_t.input2.getChildren(),
                                              multiply_scaling_r.input2.getChildren()):  # this is connect only one value into a triple value
            ctrl_master.dynamicEnvelope.connect(input2_plug1)
            ctrl_master.dynamicEnvelope.connect(input2_plug2)

        decompose_node.outputTranslate.connect(multiply_scaling_t.input1)
        multiply_scaling_t.output.connect(get_dynamic_parent(current_ctrl).translate)

        decompose_node.outputRotate.connect(multiply_scaling_r.input1)
        multiply_scaling_r.output.connect(get_dynamic_parent(current_ctrl).rotate)

    sim_loc_grp = pm.createNode("transform", name="SimLoc_{}_Grp".format(setup_name))
    pm.parent(sim_locator_list, sim_loc_grp)
    pm.delete(temp_nearestPointC)


def do_it(aim_direction=[0, 1, 0], upVector_direction=[1, 0, 0]):
    selection = pm.selected()
    setup_name = selection[0].name().replace("_Ctrl", "")
    master_ctrl = selection[0]
    rig_high_point = master_ctrl.getParent()

    curve = create_curve(selection,
                         setup_name=setup_name)

    dynamic_curve = make_dynamic_setup(curve,
                                       master_ctrl,
                                       setup_name=setup_name,
                                       rig_high_point=rig_high_point)

    make_aim_connection_setup(dynamic_curve,
                              selection,
                              master_ctrl,
                              setup_name=setup_name,
                              aim=aim_direction,
                              upVector=upVector_direction,
                              rig_high_point=rig_high_point)


"""made a bake like feature. I need to test it out once the setup is finished. I need to add a second group
to the setup so I can layer the anim without affecting the rig."""

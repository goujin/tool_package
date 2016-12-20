import pymel.core as pm
import pymel.core as pm
import maya.mel as mel
from omtk.libs import libRigging


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
        attr_local_tm = libRigging.create_utility_node(
            'multMatrix',
            matrixIn=(holdMatrix.outMatrix,  # this must be holding the local matrix
                      previous_influence.worldMatrix,
                      world_source.worldInverseMatrix
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


def get_bind_pose(target):
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


def create_curve(ctrl_selection, curve_name=None):
    """part one of the spring creation. Creates a curve and sets the attr on the master ctrl. Also gives a new parent to the ctrl."""
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


def make_dynamic_setup(curve, ctrl_master, curve_name="dynamicCurve"):
    """creates the default setup for maya dynamics. It affects as little as it can the nucleus because it is re used for all springs
    instead it clamps the value directly in the hairSystem node. It also make the connection to shut the dynamic without
    completly shutting down the follicle. static vs off in the hairSystem node"""

    nHair = pm.createNode("hairSystem")
    follicle = pm.createNode("follicle")
    dynamic_curve = pm.createNode("nurbsCurve", name=curve_name + "Shape")

    follicle.degree.set(1)
    follicle.startDirection.set(1)
    follicle.restPose.set(1)
    follicle.getParent().setParent(ctrl_master.getParent().getParent())
    pm.rename(dynamic_curve.getParent(), curve_name)

    nHair.active.set(
        True)  # here is some info on the active attr. Active means it will use the nucleus. aka use nucleus solver
    nHair.collide.set(False)

    nucleus = pm.createNode("nucleus",
                            n="{ctrl_name}_spring_nucleus".format(ctrl_name=ctrl_master.name().replace("_Ctrl", "")))

    curve.getParent().worldMatrix[0].connect(follicle.startPositionMatrix)
    curve.local.connect(follicle.startPosition)
    pm.parent(curve.getParent(), follicle.getParent())

    follicle.outCurve.connect(dynamic_curve.create)

    follicle.outHair.connect(nHair.inputHair[0])  # It should in fact always only have on curve per hairSystem.
    nHair.outputHair[0].connect(follicle.currentPosition)

    nHair.currentState.connect(nucleus.inputActive[0])
    nHair.startState.connect(nucleus.inputActiveStart[0], f=True)
    nucleus.outputObjects[0].connect(nHair.nextState, f=True)
    ctrl_master.startFrame.connect(nHair.startFrame)
    if not nucleus.currentTime.isConnected():
        pm.PyNode("time1").outTime.connect(nucleus.currentTime)
    pm.PyNode("time1").outTime.connect(nHair.currentTime)

    condition_node = pm.createNode("condition")
    ctrl_master.springActivation.connect(nucleus.enable)
    ctrl_master.timeScale.connect(nucleus.timeScale)
    ctrl_master.springSampling.connect(nucleus.subSteps)
    ctrl_master.motionDrag.connect(nHair.motionDrag)
    ctrl_master.springActivation.connect(condition_node.firstTerm)
    condition_node.secondTerm.set(1)
    condition_node.colorIfFalseR.set(1)
    condition_node.colorIfTrueR.set(3)
    condition_node.outColorR.connect(nHair.simulationMethod)

    return dynamic_curve  # this curve should be a functionnal dynamic curve


def make_aim_connection_setup(dynamic_nurbsCurve, ctrl_list, ctrl_master, naming="spring", FK=True, aim=[0, 1, 0],
                              upVector=[1, 0, 0]):
    """Third part of the spring setup. This will create locator on curve points, linked them to the curve position data
    and aim each of them to the previous. It also makes a small matrix multiplication setup to localize the world data to
     the local fk chain of ctrl or to the rig itself. It creates a setup of switch to shut down the data collected or to
      scale it up or down when in need."""
    rig_high_point = ctrl_master.getParent().getParent()
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
        sim_loc = pm.createNode("locator", name="{}_{}_Loc".format(naming, str(x).zfill(2))).getParent()
        sim_loc.setMatrix(current_ctrl.getMatrix(worldSpace=True))
        pointInfo.position.connect(sim_loc.translate)
        sim_locator_list.append(sim_loc)  # stocking only locator transform for efficiency gain
        # stocking bind pose zero grp in locator
        bp = pm.createNode("transform", name="{}_{}_BindPose".format(naming, str(x).zfill(2)))
        temp_m = current_ctrl.getMatrix(worldSpace=True)
        bp.setMatrix(temp_m)
        bp.setParent(sim_loc)

    # second part is to set up the dummy locators and the orient on the sim locators
    dummy_grp_list = []
    holdMatrix_list = []
    for x, (sim_loc, current_ctrl) in enumerate(zip(sim_locator_list, ctrl_list)):

        # Making a dummy matching locator. For safety only match with ctrl position and not curve position.
        # Even when they are suppose to be exactly the same
        loc_m = current_ctrl.getMatrix(worldSpace=True)
        dummy_loc = pm.createNode("locator").getParent()
        dummy_loc.rename("dummy_{}_{}_Loc".format(naming, str(x).zfill(2)))
        dummy_loc.setMatrix(loc_m)
        # try and match controller parent, it is a kind of bind pose and not a true matching setup
        ctrl_parent = current_ctrl.getParent().getParent()
        dummy_grp = pm.createNode("transform", n="Dummy_{}".format(ctrl_parent.name()))
        grp_m = ctrl_parent.matrix.get()
        dummy_grp.setMatrix(grp_m)

        holdMatrix = pm.createNode("holdMatrix", name="Dummy_{}_holdMatrix".format(ctrl_parent.name()))
        holdMatrix.inMatrix.set(
            grp_m)  # TODO, verify this approach works. Will hold important matrix instead of recreating a dummy chain
        holdMatrix_list.append(holdMatrix)

        dummy_grp_list.append(dummy_grp)
        dummy_loc.setParent(dummy_grp)

        if FK:
            if len(dummy_grp_list) >= 2:
                pm.parent(dummy_grp, dummy_grp_list[-2].getChildren()[0])

        if x == 0:
            pm.aimConstraint(sim_locator_list[x + 1],
                             sim_locator_list[x],
                             aim=aim,
                             maintainOffset=True,
                             upVector=upVector,
                             wut="objectrotation",
                             worldUpObject=current_ctrl.getParent().getParent(),
                             worldUpVector=upVector)

        elif not x == len(ctrl_list) - 1:
            # the last locator won't be able to react to the others in the same way  #TODO fix the orient flip problem
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
                                           name="mult_{mult_name}{padding}_trans_scale".format(mult_name=naming,
                                                                                               padding=str(x).zfill(2)))
        multiply_scaling_r = pm.createNode("multiplyDivide",
                                           name="mult_{mult_name}{padding}_rot_scale".format(mult_name=naming,
                                                                                             padding=str(x).zfill(2)))

        for input2_plug1, input2_plug2 in zip(multiply_scaling_t.input2.getChildren(),
                                              multiply_scaling_r.input2.getChildren()):  # this is connect only one value into a triple value
            ctrl_master.dynamicEnvelope.connect(input2_plug1)
            ctrl_master.dynamicEnvelope.connect(input2_plug2)

        decompose_node.outputTranslate.connect(current_ctrl.getParent().translate)
        decompose_node.outputRotate.connect(current_ctrl.getParent().rotate)

    if not FK:
        dummy_loc_data = pm.createNode("transform", name="DummyLoc_{}_Grp".format(naming))
        pm.parent(dummy_grp_list, dummy_loc_data)

    else:
        dummy_loc_data = pm.createNode("transform", name="DummyLoc_{}_Grp".format(naming))
        pm.parent(dummy_grp_list[0], dummy_loc_data)
    sim_loc_grp = pm.createNode("transform", name="SimLoc_{}_Grp".format(naming))
    pm.parent(sim_locator_list, sim_loc_grp)
    pm.delete(temp_nearestPointC)


def do_it(aim_direction=[0, 1, 0], upVector_direction=[1, 0, 0]):
    selection = pm.selected()
    setup_name = selection[0].name().replace("_Ctrl", "")
    master_ctrl = selection[0]
    curve = create_curve(selection, curve_name="{}_curve".format(setup_name))
    dynamic_curve = make_dynamic_setup(curve, master_ctrl, curve_name="holder_{}_dynamicCurve".format(setup_name))
    make_aim_connection_setup(dynamic_curve, selection, master_ctrl, naming=setup_name, aim=aim_direction,
                              upVector=upVector_direction)


"""made a bake like feature. I need to test it out once the setup is finished. I need to add a second group
to the setup so I can layer the anim without affecting the rig."""

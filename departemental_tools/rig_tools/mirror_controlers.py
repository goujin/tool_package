import pymel.core as pm


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


def controller_matcher_on_selection(selection=pm.selected(),flip=True):
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
    pm.makeIdentity(tmp, t=True)#this brings everything puts translate and rotate values at 0 before scale freezing
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

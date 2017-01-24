"""source= dynamic curve. Because every ctrl is being driven from this source
 ctrl= the animators ctrl, the one they will animate
 dynamic_layer= the layer where the animators will bake their dynamic data too."""
import pymel.core as pymel


def bake(elements,
         targets=None, sources=None,
         startFrame=None, endFrame=None,
         worldSpace=False):
    """by default will bake from a source to a target. It takes the matrice of one and set's it to the target.
    It is not supporting for now ANY other behavior. Elements must be a list of tuple or at least one tuple (dynamic_layer, animation_layer)
    (elements,
     startFrame=None, endFrame=None,
      worldSpace=False)"""
    # todo make it support inbetween frames. See the problem with range not accepting float and no other mesures are taken
    if not startFrame: startFrame = pymel.playbackOptions(q=True, minTime=True)
    if not endFrame: endFrame = pymel.playbackOptions(q=True, maxTime=True) + 2.0
    if not isinstance(elements, list): targets = [elements]

    pymel.currentTime(startFrame)
    for x in range(int(startFrame), int(endFrame)):
        pymel.currentTime(x, update=True)
        for each_dynamic_layer, each_animation_layer in elements:
            value = each_dynamic_layer.getMatrix()
            each_animation_layer.setMatrix(value)
            pymel.setKeyframe(each_animation_layer)


def unbake(elements):
    """Will remove all keyed animation connected to animation_layer.
    Elements must be a list of tuple or at least one tuple (dynamic_layer, animation_layer)
    """
    for _, animation_layer in elements:
        anim_nodes = animation_layer.listHistory(type="animCurve")
        pymel.delete(anim_nodes)
        pymel.makeIdentity(animation_layer, translate=True, rotate=True)


def get_nucleus_from_controller(ctrls):
    """
    This function will go get the nucleus of all the ctrls spring selected.
    :param ctrls: It needs valid controller from where to start looking for the nucleus.
    :return: It returns a purged list of doubles. ex: list(set(nucleus_list))
    """
    nucleus_list = []
    for ctrl in ctrls:
        dynamic_layer = ctrl.getParent().getParent()
        nucleus = dynamic_layer.listHistory(ac=True, type="nucleus")
        if nucleus: nucleus_list.extend(nucleus)

    return list(set(nucleus_list))


def get_animation_layer_from_nucleus(nucleus_list):
    """
    Function is needed to fetch (target,source) information from the nucleus to all the spring controller assosiated with it.
    :param nucleus: it needs the nucleus to get a start point from where to search
    :return: layer_list=[(target,source),...]
    """
    layer_list = []
    for nucleus in nucleus_list:
        history = nucleus.listHistory(ac=True, future=True, type="multiplyDivide")
        for ev in history:
            if "_trans_" in ev.name():
                animation_layer = ev.output.outputs()[0].getChildren()[0]
                dynamic_layer = ev.output.outputs()[0]
                layer_list.append((dynamic_layer, animation_layer))
    return layer_list


def test_selection(selection):
    """Function's purpose is to validate all the ctrls selected. It will check if they come from a proper dynamic spring
    workflow. test_selection will skip unexpected ctrls and therefore not return them to the main script.
    :param selection: user's selection
    :return: a valid list of accepted controllers
    """

    def test(singular_ctrl, animation_mathers=False):
        error_occured = "Error.Check script editor to verify your data.\n"
        this_ctrl = "This {} controller won't be used as it".format(singular_ctrl.name())
        skip = False
        if not "_Ctrl" in singular_ctrl.name():
            pymel.warning(
                "{}Controller naming safety check failed. {} isn't following proper naming rule '_Ctrl'. ".format(
                    error_occured, this_ctrl))
            skip = True
        elif not "_DynamicAnimation" in singular_ctrl.getParent().name():
            pymel.warning(
                "{}Controller spring entity check Failed. {} is not part of a spring.".format(
                    error_occured, this_ctrl))
            skip = True
        elif True in [attr.isConnected() for attr in singular_ctrl.getParent().listAttr(k=True)] and animation_mathers:
            # force unbake?
            pymel.warning(
                "{}Controller animation already present check Failed. {} is already baked.".format(
                    error_occured, this_ctrl))
            skip = False
        if not skip:
            return singular_ctrl

    valid_selection = []
    for each in selection:
        result = test(each)
        if result: valid_selection.append(result)

    return valid_selection


def animator_bake(ctrls):
    """ The assembled script an animator would use to perform a bake animation on a spring.
    :param ctrls: user's selection
    """
    valid_feedback = test_selection(ctrls)
    nucleus_list = get_nucleus_from_controller(valid_feedback)
    layer_list = get_animation_layer_from_nucleus(nucleus_list)

    bake(layer_list)
    # because the bake spams the script editor with keyframe results re run valid feedback to give the user feedback
    test_selection(ctrls)


def animator_unbake(ctrls):
    """ The assembled script an animator would use to remove animation on from a spring.
    Basically it finds animation node and deletes them.
    :param ctrls: user's selection
    """
    valid_feedback = test_selection(ctrls)
    nucleus_list = get_nucleus_from_controller(valid_feedback)
    layer_list = get_animation_layer_from_nucleus(nucleus_list)

    unbake(layer_list)

    test_selection(ctrls)

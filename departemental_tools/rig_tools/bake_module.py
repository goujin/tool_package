import pymel.core as pm


def bake( target,source=None, transfer_bake=True,
         startFrame=None, endFrame=None):
    """by default will bake from a source to a target. It takes the matrice of one and set's it to the target.
    It is not supporting for now ANY other behavior. """
    # Todo make it so, it support baking on itself and support transfer bake with custom attr
    if not startFrame: startFrame = pm.playbackOptions(q=True, minTime=True)
    if not endFrame: endFrame = pm.playbackOptions(q=True, maxTime=True)

    old_prefs_state=pm.autoKeyframe(q=True,state=True)
    old_prefs_characterOption=pm.autoKeyframe(q=True,characterOption=True)

    if transfer_bake:
        pm.autoKeyframe(state=True, characterOption=True)
        pm.currentTime(startFrame)
        pm.setKeyframe(target)
        for x in range(startFrame, endFrame):
            pm.currentTime(x, update=True)
            value = source.getMatrix()
            target.setMatrix(value)
        pm.autoKeyframe(state=old_prefs_state,characterOption=old_prefs_characterOption)

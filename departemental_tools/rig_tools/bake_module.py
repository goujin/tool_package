import pymel.core as pm


def bake(targets=None, sources=None,
         transfer_bake=True,
         startFrame=None, endFrame=None,
         worldSpace=False, source_list=[],
         target_list=[], multiBake=True):
    """by default will bake from a source to a target. It takes the matrice of one and set's it to the target.
    It is not supporting for now ANY other behavior.
    (target=None,source=None, transfer_bake=True,
         startFrame=None, endFrame=None,
          worldSpace=False,source_list=[],target_list=[],
          multiBake=True)"""
    # Todo make it so, it support baking on itself and support transfer bake with custom attr
    if not startFrame: startFrame = pm.playbackOptions(q=True, minTime=True)
    if not endFrame: endFrame = pm.playbackOptions(q=True, maxTime=True)

    old_prefs_state=pm.autoKeyframe(q=True,state=True)
    old_prefs_characterOption=pm.autoKeyframe(q=True,characterOption=True)

    if transfer_bake:
        pm.autoKeyframe(state=True, characterOption=True)
        pm.currentTime(startFrame)

        if multiBake:
            for each_target in targets:
                pm.setKeyframe(each_target)
            for x in range(startFrame, endFrame):
                pm.currentTime(x, update=True)
                for each_target,each_source in zip(targets,sources):
                    value = each_source.getMatrix(worldSpace=worldSpace)
                    each_target.setMatrix(value,worldSpace=worldSpace)
        else:
            pm.setKeyframe(targets)
            for x in range(startFrame, endFrame):
                pm.currentTime(x, update=True)
                pm.setKeyframe(targets)
                value = sources.getMatrix(worldSpace=worldSpace)
                targets.setMatrix(value, worldSpace=worldSpace)

    pm.autoKeyframe(state=old_prefs_state,characterOption=old_prefs_characterOption)

def get_targets_source():

    pass
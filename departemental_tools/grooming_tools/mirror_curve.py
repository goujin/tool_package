import pymel.core as pm

def mirror_curve(selection=pm.selected(), mirror_side='left'):
    """this will mirror the curves on the axis given"""
    _flipX_matrix = pm.datatypes.Matrix[
        [-1.0, -0.0, -0.0, -0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
    _flipY_matrix = pm.datatypes.Matrix[
        [1.0, 0.0, 0.0, 0.0], [0.0, -1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
    _flipZ_matrix = pm.datatypes.Matrix[
        [1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, -1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
    for ev in selection:
        if not (isinstance(ev, pm.nodetypes.Transform) and 1 == len(ev.getShapes())):
            pass
        else:
            new_curve = pm.createNode("nurbsCurve", n=ev.name() + "_mirrored")
            ev.getShape().worldSpace[0].connect(new_curve.create)
            pm.delete(new_curve, ch=True)

            source_matrix = ev.getMatrix(worldSpace=True)
            new_curve.getParent().setMatrix(source_matrix * _flipX_matrix, worldSpace=True)
            pm.makeIdentity(new_curve, apply=True, rotate=True)
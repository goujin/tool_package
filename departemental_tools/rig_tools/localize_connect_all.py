import pymel.core as pm
import maya.cmds as mc


def duplicate(object):
    prefix = 'driven_'

    #############

    pm.select(object, hi=True)
    selection_list = pm.ls(selection=True, type='transform')
    name_driven_selection_list = mc.ls(selection=True, type='transform', shortNames=True)

    dirty_duplicate_selection_list = pm.duplicate(selection_list, renameChildren=True)

    duplicate_selection_list = pm.ls(dirty_duplicate_selection_list, type='transform')

    results_dict = {}
    # renamming
    for ev in selection_list:
        pm.rename(ev, prefix + ev.name())
    for x, ev in enumerate(duplicate_selection_list):
        pm.rename(ev, name_driven_selection_list[x])
        results_dict[ev] = selection_list[x]

    return results_dict


def is_connected_operation(driven_attribute, driver_attribute):
    """connect source_attr to target_attribute"""
    if driver_attribute.isLocked():
        was_locked = True
    else:
        was_locked = False

    if driven_attribute.isLocked():
        attribute_was_locked = True
    else:
        attribute_was_locked = False

    if is_parentAttr_lock(driven_attribute):
        driverParentAttr_was_lock = True
    else:
        driverParentAttr_was_lock = True

    if is_parentAttr_lock(driven_attribute):
        drivenParentAttr_was_lock = True
    else:
        drivenParentAttr_was_lock = False

    driver_attribute.unlock()
    driven_attribute.unlock()
    parentAttr_lock_mangement(driven_attribute, False)
    parentAttr_lock_mangement(driver_attribute, False)

    pm.connectAttr(driven_attribute, driver_attribute)

    if was_locked: driver_attribute.lock()
    if attribute_was_locked: driven_attribute.lock()
    if drivenParentAttr_was_lock: parentAttr_lock_mangement(driven_attribute, True)
    if driverParentAttr_was_lock: parentAttr_lock_mangement(driver_attribute, True)


def is_not_connected_operation(driver_attribute, driven_attribute):  # todo make sure this part is safe and clean
    """connect source to target_attribute"""
    if driver_attribute.isLocked():
        sourceAttr_was_locked = True
    else:
        sourceAttr_was_locked = False

    if driven_attribute.isLocked():
        drivenAttr_was_locked = True
    else:
        drivenAttr_was_locked = False

    if is_parentAttr_lock(driven_attribute):
        driverParentAttr_was_lock = True
    else:
        driverParentAttr_was_lock = False

    if is_parentAttr_lock(driven_attribute):
        drivenParentAttr_was_lock = True
    else:
        drivenParentAttr_was_lock = False

    driver_attribute.unlock()
    driven_attribute.unlock()
    parentAttr_lock_mangement(driven_attribute, False)
    parentAttr_lock_mangement(driver_attribute, False)

    pm.connectAttr(driver_attribute, driven_attribute)

    if sourceAttr_was_locked: driver_attribute.lock()
    if drivenAttr_was_locked: driven_attribute.lock()
    if drivenParentAttr_was_lock: parentAttr_lock_mangement(driven_attribute, True)
    if driverParentAttr_was_lock: parentAttr_lock_mangement(driver_attribute, True)


def is_exact_destination(pymel_attribute):
    result = pm.connectionInfo(pymel_attribute, isExactDestination=True)
    return result


def is_parentAttr_lock(attribute):
    try:
        return attribute.getParent().isLocked()
    except:
        return False


def parentAttr_lock_mangement(attribute, decision):
    try:
        if decision:
            attribute.getParent().lock()
        else:
            attribute.getParent().unlock()
    except:
        pass


def bruteforceLocalize(selection=None):
    """duplicate all and reconnect driven connections to driver and driver to empty connectable driven attributes"""
    if selection==None: selection=pm.selected()
    duplicate_dict = duplicate(selection)

    for new_object in duplicate_dict:

        if isinstance(new_object, pm.nodetypes.Constraint):
            pass
            # pm.delete(new_object)

        else:
            list_attributes = pm.listAttr(duplicate_dict[new_object], keyable=True)
            object_list_attributes = []
            driven_list_attributes = []
            for attribute_holder in list_attributes:
                driven_list_attributes.append(duplicate_dict[new_object].attr(attribute_holder))
                object_list_attributes.append(new_object.attr(attribute_holder))

            ####################################
            # Making sure if any parent attribute is
            # Adding this part
            attribute_connected = duplicate_dict[new_object].connections(plugs=True,
                                                                         connections=True)
            for ev, _ in attribute_connected:  # unpacking both values from attribute connected. First value is always the one from teh same object
                if ev in driven_list_attributes and is_exact_destination(ev):
                    x = driven_list_attributes.index(ev)
                    is_connected_operation(ev, object_list_attributes[x])
                    # remove connected from list
                    driven_list_attributes.remove(ev)
                    object_list_attributes.pop(x)

                try:
                    ev.children()
                    check_children = True

                except:
                    check_children = False

                if check_children and is_exact_destination(ev):
                    if True in [test in driven_list_attributes for test in ev.children()]:
                        # make it so you can only make the connection if one of the children is at least in the keyable list
                        driver_attr = new_object.attr(ev.attrName(longName=True))
                        is_connected_operation(ev, driver_attr)
                        # remove children from attribute list because their parent was connected instead
                        for child_attr in ev.children():
                            if child_attr in driven_list_attributes:
                                x = driven_list_attributes.index(child_attr)
                                driven_list_attributes.remove(child_attr)
                                object_list_attributes.pop(x)

                                #####################################################

            for x, attribute in enumerate(driven_list_attributes):

                '''if is_exact_destination(attribute):
                    # this spot checks if an attribute is connected and if so it will transfer the connection from
                    # the driven object to the driver object
                    is_connected_operation(attribute, object_list_attributes[x])'''

                if attribute.isConnectable() and not is_exact_destination(attribute):
                    # This spot checks if the attribute is connectable to transfer the connection
                    # from the driver node to the driven node
                    is_not_connected_operation(object_list_attributes[x], attribute)


def do_matrix_offseter(mesh_transform_list):
    def create_offset(mesh_transform,locator=None):
        mesh = mesh_transform.getShape()
        skinCluster = mesh.inMesh.connections(plugs=True)[0]
        transform_geo = pm.createNode("transformGeometry")

        locator.worldMatrix[0].connect(transform_geo.transform)
        skinCluster.connect(transform_geo.inputGeometry)
        transform_geo.outputGeometry.connect(mesh.inMesh, f=True)

    if isinstance(mesh_transform_list, list) and not len(mesh_transform_list) == 0:
        locator = pm.createNode("locator").getParent()
        for mesh_transform in mesh_transform_list:
            if isinstance(mesh_transform.getShape(),pm.nodetypes.Mesh):
                create_offset(mesh_transform,locator=locator)

import pymel.core as pm
import sys
sys.path.append("/home/jgoulet/dev/tool_package/custom_lib/utils_lib")
import maya_utils.attribute_utils


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
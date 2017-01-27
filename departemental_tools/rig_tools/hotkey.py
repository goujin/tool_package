import pymel.core as pm
import sys
sys.path.append("/home/jgoulet/dev/tool_package/custom_lib/utils_lib/")
import rig_utils
import maya_utils.attribute_utils
import maya_utils.selection_utils



# position snaping
def position_snaping():
	selection=pm.selected()
	if len(selection)==2:
	    snap(selection[0],selection[1],ko=False)
	else:
	    pm.error("Need to have two elements in the selection.")

#displayoverrideOn
def displayoverrideOn():
	selection=pm.selected()
	if len(selection)==0:
	    pm.error("select maya DAG nodes that you want to affect")
	display_override(selection)

#displayoverrideAll On
def displayoverrideAll_On():
	pm.select(hi=True)
	selection=pm.selected()
	if len(selection)==0:
		pm.error("select maya DAG nodes that you want to affect")
	display_override(selection)

#displayoverrideOff
def displayoverrideOff():
	selection=pm.selected()
	if len(selection)==0:
	    pm.error("select maya DAG nodes that you want to affect")
	display_override(selection,False,"normal")

#displayoverrideAllOff
def displayoverrideAll_Off():
	pm.select(hi=True)
	selection=pm.selected()
	if len(selection)==0:
	    pm.error("select maya DAG nodes that you want to affect")
	display_override(selection,False,"normal")

# quick lock
def quick_lock():
	attr=getSel_channelBox(return_pynode=True)
	attr_lock(attr)

#all lock
def all_lock():
	selection=pm.selected()
	pymel_attributes=[]
	for each in selection:
	    temp_holding_list=[]

	    attributes_k=pm.listAttr(each,keyable=True)
	    temp_holding_list.extend(attributes_k)

	    attributes_nk=pm.listAttr(each,cb=True)
	    temp_holding_list.extend(attributes_nk)

	    for attribute in temp_holding_list:
	        pymel_attributes.append(each.attr(attribute))

	attr_lock(pymel_attributes)
    
#quick unlock
def quick_unlock():
	attr=getSel_channelBox(return_pynode=True)
	attr_lock(attr)

#unlock all
def unlock_all():
	selection=pm.selected()
	pymel_attributes=[]
	for each in selection:
	    temp_holding_list=[]

	    attributes_k=pm.listAttr(each,keyable=True)
	    temp_holding_list.extend(attributes_k)

	    attributes_nk=pm.listAttr(each,cb=True)
	    temp_holding_list.extend(attributes_nk)

	    for attribute in temp_holding_list:
	        pymel_attributes.append(each.attr(attribute))
	attr_unlock(pymel_attributes)

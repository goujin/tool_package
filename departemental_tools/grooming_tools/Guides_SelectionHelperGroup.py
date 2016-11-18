import pymel.core as pm

#select nurbs curve in same grp, Antoine wants a tool a to help him out with this process:
'''Select a curve, get the parent, isolate the parent, then mass select everything visible. 
Used to pick every object in the same group from selection   '''

selection= pm.selected()
safety_list= []
for selected in selection:
    if selected.getParent():
        selected_parent=selected.getParent()
        
        if selected_parent in safety_list:
            print 'for this selected object '+selected.name()+' . Parent already taken and processed. Skipping'
            pass            
        else:
            safety_list.append(selected_parent)
            pm.select(selected_parent.getChildren())
            
    else:
        pm.warning('selected has no parent: '+selected.name() )



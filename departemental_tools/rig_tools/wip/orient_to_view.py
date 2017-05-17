import pymel.core as pm
import omtk
from omtk.libs import libRigging
libRigging.align_joints_to_view(pm.selected(),pm.PyNode("persp"),affect_pos=False)
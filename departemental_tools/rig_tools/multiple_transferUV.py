import maya.cmds as mc
import pymel.core as pm
import maya.OpenMaya as om
from pymel.core import datatypes as dt

'''
USAGE: To use this script:
1. OPEN the scene you want to transfer UVs to.
2. REFERENCE the scene with correct UVs.
3. Copy/paste your namespace into line 108
4. Run the script. Double check manually. If hierarchy has changed, this script won't perform magic!
'''

#TODO: Add a more robust way of matching geo. Now it is using centers. But can we use vertices or bounding boxes, or a weighted score of multiple matches?

# Possible conditions:
# source and target have same name and same geometry (no problem)
# source and target have different  names, same position and same geometry (detect with vtx count and .bbox)
# source and target have different names, different position and same geometry (detect with vtx count, and...?)
# source and target have different names, different positions and different geometry (WTF?!?)


def transfer_uvs(source, target):
	# TODO: Is there a way to detect which search methods to use in the command?
	# eg. sample random vertices to see if vtx numbering matches. If not, use world space.
	pm.transferAttributes (
		source, target,
		transferPositions=0,
		transferNormals=0,
		transferUVs=2,
		transferColors=0,
		sampleSpace=4, # 0 is world, 4 is component. 4 is best if topology hasn't changed
		sourceUvSpace='map1', targetUvSpace='map1',
		searchMethod=0, # 0 is closest along normal, 3 is closest to point
		flipUVs=0,
		colorBorders=1
	)


def do_uv_sanity_check(namespace):
	# Compare SOURCE and TARGET to make sure that they have the same amount of geometry.
	# TODO: Make this more generalized, so it doesn't rely on "model" group.
	meshes = [mesh.getParent() for mesh in pm.PyNode('model').getChildren(ad=True, type='mesh')]
	meshes2 = [mesh.getParent() for mesh in pm.PyNode(namespace + 'model').getChildren(ad=True, type='mesh')]

	tally1 = set([str(x.name()) for x in meshes])
	tally2 = set([str(x.name().split(x.namespace())[-1]) for x in meshes2])

	final1 = list(tally2 - tally1)
	final2 = list(tally1 - tally2)
	if final1: mc.warning('missing from RIG: {0}'.format(final1))
	if final2: mc.warning('missing from MODEL: {0}'.format(final2))


def multiple_transfer_uvs(meshes, namespace):
	errors = [] # a list of objects which failed for some reason or other.
	noIntermediate = [] # a list of objects which had no intermediate objects

	for geo in meshes:
		try:
			uvGeo = pm.PyNode(namespace + geo.name())
			uvGeoName = uvGeo.name()
		except:	
			errors.append(geo)
			continue
		
		skin = []
		bShapes = []
		
		# Find the intermediate object
		# TODO: If there isn't one, we can assume there are no deformers (TEST TEST TEST)
		oInters = [shape for shape in geo.getShapes() if shape.intermediateObject.get() == True]
							
		reverseOrder = False #TODO: Sometimes you need to copy from geo to pasted__geo
		try:
			if oInters:
				oInter = oInters[0]
				oInter.intermediateObject.set(False)
				if reverseOrder:
					transfer_uvs(oInter, uvGeo.getShape())
				else:
					transfer_uvs(uvGeo.getShape(), oInter)
				pm.select(None) # for safety. Don't want to delete history on errant objects.
				pm.delete(oInter, ch=True) # delete history on intermediate object
				oInter.intermediateObject.set(True)
			else:
				#print('{0} did not appear to have an intermediate node!'.format(geo))
				if reverseOrder:
					transfer_uvs(geo, uvGeo.getShape())
				else:
					transfer_uvs(uvGeo.getShape(), geo)
				noIntermediate.append(geo)
				pm.select(None) # for safety. Don't want to delete history on errant objects.
				pm.delete(geo, ch=True)
		except:
			errors.append(geo)

	if errors:
		print('\n\nErrors:\n{0}'.format(errors))
		mc.warning ('there were {0} objects with new/invalid names'.format(len(errors)))
		pm.select(errors)


# get all the geometry under "model"
meshes = [mesh.getParent() for mesh in pm.PyNode('model').getChildren(ad=True, type='mesh') if mesh.getParent().isVisible() == True]

# Copy/Paste your namespace here. Include the semi-colon OR pasted__ if you copy/pasted the scene in.
namespace = 'tlp_pr_avt_cart_a_1_moh_1:'
multiple_transfer_uvs(meshes, namespace)
print('done')


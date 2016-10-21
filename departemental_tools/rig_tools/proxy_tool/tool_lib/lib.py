import pymel.core as pymel
import maya as maya
class Proxy_making():
    def __init__(self):
        self.edges_per_geo_dict={}


    def add_loop(self,selection):
        """it adds to memory the selected edges only and returns a warning for other types.
    The stored edges are in a dictionairy which stores the mesh info of the edges in a global variable edges_per_geo_dict"""

        for meshEdge in selection:

            if type(meshEdge)==pymel.general.MeshEdge:
                mesh_transform=meshEdge.node().getParent()

                if self.edges_per_geo_dict.has_key(mesh_transform):
                    self.edges_per_geo_dict[mesh_transform] = self.edges_per_geo_dict[mesh_transform].union(meshEdge)
                    print "Added:"+str(meshEdge)
                else:
                    self.edges_per_geo_dict[mesh_transform]=set([meshEdge])

            else:
                pymel.warning('this is an error in selection:'+str(meshEdge)+'.Object must be of edge type')


    def soft_reset_loop_list(self):
        """give the user back his selection wipes the stored edges from memory"""
        pymel.select(clear=True)

        for edges in self.edges_per_geo_dict.itervalues():

            pymel.select(list(edges),add=True)

        self.edges_per_geo_dict={}
        print "Made a selection from loop list. Loop list is also wiped."

    def scinder_mesh(self):
        """ separate mesh into pieces, renames them also"""

        for edges_set in self.edges_per_geo_dict.itervalues():
            pymel.select(list(edges_set))
            maya.mel.eval("DetachComponent;performDetachComponents")


        for geometry in self.edges_per_geo_dict.iterkeys():

            pymel.select(geometry)
            pymel.delete(geometry,ch=True)

            pymel.polySeparate(geometry)
            pymel.delete(geometry.getChildren(),ch=True)

            geo_name=geometry.name().replace('_geo','')
            pymel.refresh(f=True)

            for number,new_geometry in enumerate(geometry.getChildren()):

                new_geometry.exists()
                new_geometry.rename(geo_name+'_'+str(number)+'_proxy')

            print "Mesh scindered."

    def empty_dict(self):
        self.edges_per_geo_dict={}
        print "Emptied list mermory"

    def view_wip(self):
        """select the edges that was stored"""
        pymel.select(clear=True)

        for edges_set in self.edges_per_geo_dict.itervalues():
            pymel.select(list(edges_set),add=True)

        print "Made selection from current loop list."

    def rename_from_parent_selection(self,selection):
        for parent in selection:
            if (len(parent.getChildren())>=1):                                                
                parent_name = str(parent.name()).replace('_geo','')
                for number,mesh in enumerate(parent.getChildren()):
                        if (type(mesh)==pymel.nodetypes.Transform):                            
                            mesh.rename(parent_name+'_'+str(number)+'_proxy')
                            
                        else:
                            pymel.warning(r"This shape is isn't a mesh shape."+mesh.name()+r'/type/ '+str(type(mesh)))
                
                print "All mesh are renamed."
            
            else:
                pymel.warning("This must be a mistake. Selected needs children: "+parent.name())





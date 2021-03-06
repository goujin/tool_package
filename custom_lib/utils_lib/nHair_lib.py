"""Librairy that gives info on object and also that can do operations that are not yet supported in vanilla maya for nHairShape operations"""
import pymel.core as pymel
import sys
sys.path.append('/home/jgoulet/maya/2016/scripts/custom_lib/utils_lib/')
import attribute_utils as maya_utils


def getNucleus_from_nHairShape(nHairShape):
    """Give nHairShape and it will return nucleus associated"""
    nHairShape=pymel.PyNode(nHairShape)
    nucleus=nHairShape.currentState.connections(shapes=True)[0]
    return nucleus   


def getFollicles_from_nHairShape(nHairShape):         
    """Give nHairShape and function will return output [follicles] related."""
    pymel_nHairShape=pymel.PyNode(nHairShape)
    follicles=[x for x in pymel_nHairShape.outputHair.connections(shapes=True)]
    return follicles


#def getFollicles_from_output(outputCurves): TODO   
#    return follicles   


#def  getInputCurves_from_outputCurves(output):  TODO        
#    return curves_shape_input


def getInputCurves_from_nHairShape(nHairShape):         
    """Give hairSystemShape and it will return [input curves]"""
    nHairShape=pymel.PyNode(nHairShape)
    curves_shape_input=[x.getShape().startPosition.connections(shapes=True)[0] for x in nHairShape.inputHair.connections()]
    return curves_shape_input


def getOutputCurves_from_nHairShape(nHairShape):     
     """Give hairSystemShape and it will return [output curves]"""
     nHairShape=pymel.PyNode(nHairShape)
     curves_shape_output=[x.getShape().outCurve.connections(shapes=True)[0] for x in nHairShape.outputHair.connections()]
     return curves_shape_output


def give_construction_dict(nHairShape):
    """
The function will build the construction dictionnairy with all the functions : getFollicles_from_nHairShape
                                                                               getInputCurves_from_nHairShape
                                                                               getOutputCurves_from_nHairShape
With this kind of form: {follicle:(input,ouput),...}"""
    nHairShape=pymel.PyNode(nHairShape)
    follicles=getFollicles_from_nHairShape(nHairShape)
    curves_shape_input=getInputCurves_from_nHairShape(nHairShape)
    curves_shape_output=getOutputCurves_from_nHairShape(nHairShape)
    construction_hist_dict={x:(b,a) for x,b,a in zip(follicles,curves_shape_input,curves_shape_output)}
    return construction_hist_dict


def solver_change(nHairShape,new_nucleus):
        """(nHairShape,new_nucleus), it will switch nHairShape connections with the new nucleus"""
        new_nucleus=pymel.PyNode(nHairShape)
        nHairShape.currentState.disconnectAttr() 
        nHairShape.startState.disconnectAttr()
        (source,index)=zip(maya_utils.next_available(new_nucleus.outputObjects)[0])
        source.connectAttr(nHairShape.nextState,force=True)
        pymel.PyNode(nHairShape.name()+'.currentState['+str(index)+']').connectAttr(nucleus.inputActive,nextAvailable=True,force=True)


def change_nHairShape(folliclesShape_list,new_nHairShape):
    """(follicle_list,new_nHairShape), take note that you need to give the array of follicles shape as pymel objects"""
    nHairShape=pymel.PyNode(new_nHairShape)
    for follicle in folliclesShape_list:
        (destination,index)=maya_utils.next_available(nHairShape.inputHair)
        follicle.outHair.connect(destination,force=True)
        #index=follicle.outHair.listConnections(destination=True,plugs=True)[0].index()
        pymel.PyNode(nHairShape.name()+'.outputHair['+str(index)+']').connect(follicle.currentPosition,force=True) 


import pymel.core as pm
import pymel.core as pymel
#this class is made for test purpose only

"""
class Dynamics_nHair(object):
    if not len(pymel.ls(type='hairSystem')) == 1:
        pymel.error('One nHair at the time!')
    def __init__(self):
        self.nHair = pymel.ls(type='hairSystem')[0]        
        self.follicle = self.nHair.outputHair.connections()
        self.curve_shape_input  = [x.outCurve.connections()[0] for x in self.follicle]      #getting output curve from all follicle more explicit? [x.getShape().startPosition.connections()[0] for x in nHair.outputHair.connections()]
        self.curve_shape_output = [x.startPosition.connections()[0] for x in self.follicle] #getting input  curve from all follicle more explicit? [x.getShape().outCurve.connections()[0] for x in nHair.outputHair.connections()]
        self.nucleus=self.nHair.currentState.connections()[0]       
        self.construction_hist_dict={x:(b,a) for x,b,a in zip(self.follicle,self.curve_shape_input,self.curve_shape_output)}
        
    
    def getFollicle(self):         
         return self.follicle
    def  getInputCurve(self):
        return self.curve_shape_input
    def getOutputCurve(self):
         return self.curve_shape_output
    def give_construction_dict(self):
        return self.construction_hist_dict
test=Dynamics_nHair()
test.follicle
test.getFollicle()
test.getInputCurve()
test.getOutputCurve()
test.give_construction_dict()
test.__doc__

##################################################################################################################################################################    
    
    def solver_change(self,nHair,nucleus):
        pass
    def change_nHair(self,follicle,nucleus,new_nucleus):
        for follicle in follicle_list:            
            follicle.currentState.disconnectAttr() 
            follicle.startState.disconnectAttr()
            new_nucleus.outputObjects.connectAttr(nHair.nextState,na=True)#I'm sure to have a mistake here, next available flag work for connecting not to get the connected
            nHair.currentState.connectAttr()
            
        dir(follicle[0].currentState)
        nucleus=new_nucleus
        


class Dynamic_nHair_manager(object):
    nHair
    
"""
    


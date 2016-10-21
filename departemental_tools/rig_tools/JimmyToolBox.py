
'''###############SANDBOX###########################'''
#######################################################
#############################INFO#############################################
''' this script is made to connect the scaling of the node into multiple bones.
Select the top of the hierachy then run the script to connect the scaling grp'''
##############################################################################
##############################################################################
'''           connect scalling of 'ScaleData' in bones                      '''                      
##############################################################################
##############################################################################
'''this is to set up if the bone is already link in the x axis.
Just like a Ik spline series of bones would if they streched'''
##############################################################################

def scaleBone():
    

    #select
    mc.select ( hi=1)
    my_selection = mc.ls(sl=1, type="joint")
    mc.select (my_selection)

    #do operation 
           
    for bones in (my_selection):
        
        mc.connectAttr ( 'world.scaleX',  bones + ".scaleZ",f=1)
        mc.connectAttr ( 'world.scaleX',  bones + ".scaleY",f=1)
        mc.connectAttr ( 'world.scaleX',  bones + ".scaleX",f=1)
            
            
            
    mc.warning('Job is done')

####################################################################################
'''############DELETE UNWANTED NODES IN THE SCENE################################'''
#####################################################################################
def uNode():       
    listN=mc.ls(type='unknown')
    for n in listN:
        mc.lockNode(n,l=0)
        mc.delete(n)
        print n
###################################################################################################################################################
'''easy constrainer'''
'''this is an inverted parenting system'''
###################################################################################################################################################
def InvCons():
    ls=mc.ls(sl=1)
    ls.reverse()
    mc.parentConstraint(ls,mo=1)
    mc.warning('DONE XD')

####################################################################################################################################################
'''DELETE CONSTRAINT OUT OF A GROUP'''
###################################################################################################################################################
def delCons():
    grp=mc.ls(sl=1)
    mc.select(grp, hi=1)
    grp=mc.ls(sl=1,type='constraint')
    mc.delete(grp)
    mc.select(cl=1)
    mc.warning('done')

###################################################################################################################################################
'''hide fol'''
###################################################################################################################################################
def Hfol():
    visibility=True
    
    mc.select(hi=1)
    fol = mc.ls(typ='follicle', sl=1)
    mc.select (fol)
    
    for ev in fol:
        if (visibility==True):
            mc.setAttr(ev+'.visibility',0,l=1)


    else:
        #erreur possible
        mc.setAttr ("_l_folJoint15.visibility",0)
        mc.setAttr ( "_l_folJoint15.v",l=True) 


#######################################################################################################################################################
'''QUICK SNAP'''
###################################################################################################################################################
    
def qSnap():    
    list=mc.ls(sl=1)
    l1=list[0]
    l2=list[1]

    #l1=move object
    #l2= object target

    mc.select(l2,l1)
    cons=mel.eval('''doCreatePointConstraintArgList 1 { "0","0","0","0","0","0","0","1","","1" };
    pointConstraint -offset 0 0 0 -weight 1;''')
    mc.delete(cons)
    mc.select(l1)


#################################################################################################################################################
'''create joints on selection'''
#################################################################################################################################################
def jSel():
    ls=mc.ls(sl=1,fl=1)
    j=[]
    jo=[]
    for ev in ls:
        object=pm.PyNode(ev)
        object=object.name().split('.')[-1]
        if object.startswith('vtx[') or object.startswith('cv[')  or object.startswith('pt[') :
            print type(object)      
            mc.select(cl=1)
            pos=mc.xform(ev,q=1,t=1,ws=1) 
            jo=mc.joint(rad=0.2)
            mc.xform(jo,t=pos,ws=1)
            j.append(jo)   
            
        else:
            try:
                child=object.getChildren()[0]
                print child                           
                if pm.objectType(child)=='locator':
                    mc.select(cl=1)
                    pos=mc.xform(ev,q=1,sp=1,ws=1) 
                    jo=mc.joint(rad=0.2)
                    mc.xform(jo,t=pos,ws=1)
                    j.append(jo)       
                else:
                    mc.error('blabla')
                
            except:  
                mc.select(cl=1)
                pos=mc.xform(ev,q=1,rp=1,ws=1) 
                jo=mc.joint(rad=0.2)
                mc.xform(jo,t=pos,ws=1)
                j.append(jo)
    
    mc.group(j)
    
#################################################################################################################################################
'''create ctrls on selection'''
#################################################################################################################################################

def CTRLsel():
    

    ls=mc.ls(sl=1,fl=1)
    
    for ev in ls:
        if mc.objectType(ev)=='joint':
            child='none'        
        else:
            child=mc.listRelatives(ev,c=True)[0]
        if child=='none':
            dup=mc.duplicate('ctrl')[0]
            mc.select(cl=1)
            pos=mc.xform(ev,q=1,t=1,ws=1)
            mc.xform(dup,t=pos,ws=1)
            print 'bone: '+str(pos)
        elif mc.objectType(child)=='locator':
            dup=mc.duplicate('ctrl')[0]
            mc.select(cl=1)
            pos=mc.xform(ev,q=1,sp=1,ws=1)
            mc.xform(dup,t=pos,ws=1)
            print 'locator: '+str(pos)
        else:
            dup=mc.duplicate('ctrl')[0]
            mc.select(cl=1)
            pos=mc.xform(ev,q=1,t=1,ws=1)
            mc.xform(dup,t=pos,ws=1)
            print 'other: '+str(pos)
#################################################################################################################################################        
'''rename the grp of selected for selected name + ZERO'''
#################################################################################################################################################

def renameCGsel():

    l=mc.ls(sl=1)
    for ev in l:
        name=ev+'_ZERO'
        renamed=mc.listRelatives(ev,p=1)
        mc.rename(renamed,name)
    

#################################################################################################################################################    
'''connect a driven rig to anim ccc'''
#################################################################################################################################################

def ConDRitAnim():
    #############
    '''paramateters'''
    prefix='driven_'

    #############

    pm.select(hi=True)
    list=pm.ls(sl=True,type='transform')
    nameD=mc.ls(sl=True,type='transform',sn=True)


    Dup=pm.duplicate(list,rc=True)[0]

    pm.select(Dup,hi=True)
    listDup=pm.ls(sl=True,type='transform')

    #renamming
    for ev in list:
        pm.rename(ev,'driven_'+ev.name())
    for x, ev in enumerate(listDup):
        pm.rename(ev,nameD[x])
        
    print('Procedure started')

    for x, ev in enumerate(list):
        
        if x==0:
            pass
        else:
            #find extraAttr
            
            overalList=pm.listAttr(ev,k=True)
            
        #connect controls    
            
            for att in overalList:                
                buildAttr=pm.PyNode(ev.name()+'.'+att)
                buildDupAttr=pm.PyNode(listDup[x]+'.'+att)
                if not buildAttr.isDestination():
                    connection=pm.connectionInfo(buildAttr,sfd=True)
                    pm.connectAttr(connection,buildDupAttr)
            
        #check for connection update
            print overalList 
            for att in overalList:
                buildAttr=pm.PyNode(ev.name()+'.'+att)
                buildDupAttr=pm.PyNode(listDup[x]+'.'+att)
                print "buildAttr:"+ buildAttr
                print "buildDupAttr"+buildDupAttr
                if not (buildAttr.isLocked() or buildAttr.isDestination()):
                    pm.connectAttr(buildAttr,buildDupAttr)
            

    #hide driven_
    list[0].hide()
    (list[0].visibility).lock()
#################################################################################################################################################    
'''quick connectT'''
#################################################################################################################################################
def qCT():
    targ1=pm.selected()[0]
    targ2=pm.selected()[1]
    if targ2.isLocked():
        targ2.set(l=False)
        targ1.translate.connect(targ2.translate)
        targ2.set(l=True)
    else:
        targ1.translate.connect(targ2.translate)
#################################################################################################################################################    
'''quick connectR'''
#################################################################################################################################################        
def qCR():
    targ1=pm.selected()[0]
    targ2=pm.selected()[1]
    if targ2.isLocked():
        targ2.set(l=False)
        targ1.rotate.connect(targ2.rotate)
        targ2.set(l=True)
    else:
        targ1.rotate.connect(targ2.rotate)        
#################################################################################################################################################    
'''quick connectS'''
#################################################################################################################################################                

def qCS():
    targ1=pm.selected()[0]
    targ2=pm.selected()[1]
    if targ2.isLocked():
        targ2.set(l=False)
        targ1.scale.connect(targ2.scale)
        targ2.set(l=True)
    else:
        targ1.scale.connect(targ2.scale)

#################################################################################################################################################    
'''boneSel'''
#################################################################################################################################################

def boneSel():    
    mc.select(hi=1)
    bones = mc.ls(typ='joint', sl=1)
    mc.select (bones)

#################################################################################################################################################    
'''locSel'''
#################################################################################################################################################
def locSel():
    boneChesk=[]
    '''for ev in list:
        if mc.nodeType(ev):
            boneCheck.append(ev)'''
    mel.eval('''
       

    {     
            PolySelectConvert 3;
    string $edgeCluster[] = `newCluster " -envelope 1"`;
    $clustPos = `xform -query -sp  $edgeCluster`;
    string $jPosLoc[] = `spaceLocator -p $clustPos[0] $clustPos[1] $clustPos[2]`;
    xform -cp $jPosLoc;
    delete $edgeCluster;
    toggle -sh $jPosLoc;   
      
      
    string $shapes[] = `listRelatives -s -path $jPosLoc`;

    setAttr ($shapes[0] + ".localScaleZ") .3;
    setAttr ($shapes[0] + ".localScaleX") .3;
    setAttr ($shapes[0] + ".localScaleY") .3;


    }''')

#################################################################################################################################################    
'''locOrient'''
#################################################################################################################################################
def locOrient():
    mel.eval('''
             global proc fs_posLoc()

    {     
        PolySelectConvert 3;
        string $edgeCluster[] = `newCluster " -envelope 1"`;
        $clustPos = `xform -query -sp  $edgeCluster`;
        string $jPosLoc[] = `spaceLocator -n loc_Ce -p $clustPos[0] $clustPos[1] $clustPos[2]`;
        xform -cp $jPosLoc;
        delete $edgeCluster;
        toggle -sh $jPosLoc;   
          
          
        string $shapes[] = `listRelatives -s -path $jPosLoc`;

        setAttr ($shapes[0] + ".localScaleZ") .3;
        setAttr ($shapes[0] + ".localScaleX") .3;
        setAttr ($shapes[0] + ".localScaleY") .3;

    }


             ''')

    #step1
    sel=mc.ls(sl=1,fl=1)
    #step2
    mc.pickWalk(d='up',type='edgeloop')
    mel.eval('fs_posLoc ;')
    #step3
    mc.select(sel)
    mel.eval('fs_posLoc ;')
    loc=mc.ls('loc_Ce*',type='transform')
    #step4
    cons=mc.aimConstraint(loc[0],loc[1])
    mc.delete(cons,loc[0])

    gen=mc.ls('loc_*_gen')
    if (len(gen)==0):
        var='00'
    elif (len(gen)>0):
        gen.sort()
        var=((gen[-1].split('_')[1]))
        var ='0'+str(int(var)+1)
    mc.rename(loc[1],'loc_'+var+'_gen')
###########################################################
'''sel_ccc'''
###########################################################
def Sel_ccc():
    mc.select(hi=True)
    list=mc.ls(sl=True,type='transform')         
    ccc=[]
    for ev in list:
        if '_ccc' in ev[-4:10**10]:
          ccc.append(ev)  
    mc.select(ccc)

###########################################################
'''scale'''
###########################################################
def Scale():
    list=mc.ls(sl=1)
    if not mc.objExists('world'):
        mc.createNode('transform',n='world')
    for ev in list:
        mc.connectAttr('world.scale',ev+'.scale')

###########################################################
''' matrix local script '''
###########################################################
def do_matrix():


    mesh=mc.ls(sl=1)


    for ev in mesh:
        geoShape=mc.listRelatives(ev,c=1)[0]
        
        if not (mc.nodeType(geoShape)=='mesh' or 'nurbsSurface'):
            mc.error('Detected shape is not a mesh or NURBS!')
        
        skin=mc.connectionInfo(geoShape+'.inMesh',sfd=True)
        #matrix creation
        matrix= mc.spaceLocator(n='matrix')[0]
        #checking if wrap or skinCluster or blendShape
        
        if mc.nodeType(skin)=='skinCluster' or 'blendShape' or 'wrap':
            TG=mc.createNode('transformGeometry')

            mc.connectAttr(skin,TG+'.inputGeometry')
            mc.connectAttr(matrix+'.worldMatrix[0]',TG+'.transform')
            mc.connectAttr(TG+'.outputGeometry',geoShape+'.inMesh',f=1)
        
        else:
            print str(mc.nodeType(skin))
            mc.error('the node type is not useable!')

    if 'matrixNomade_00':
        NonNamed=mc.ls('matrixNomade_*',type='transform')    
    if NonNamed:
        num=int(NonNamed[-1].split('_')[-1])
        if num>=10:        
            name='matrixNomade_'+str(num+1)
        if num<10:
            name='matrixNomade_'+str(num+1)
    else:
        name='matrixNonNamed_00'
    mc.rename(matrix,name)
    
    
 ###   This Script is made for using the sandbox without running the
 ###   Code manually. 
 ###
 ###
 ###
########
#######
######
 ###
  #
############################################################################################################################################
import maya.OpenMaya as om
import maya.cmds as mc
import maya.mel as mel
import pymel.core as pm
import math as math
class window:
    def UI(self, *args):
        #checkwindow
        if mc.window('toolboxUI',exists=True):
            mc.deleteUI('toolboxUI')
        
        #create UI        
        windowTool=mc.window('toolboxUI',t= 'Tool Box', w=300, h=600,mnb=False, sizeable=False,rtf=False,bgc=(0.361,0.281,0.404))
        
        
        #Create main layout
        mainLayout93=mc.columnLayout(w=300,h=300)    
                    
       
        
        
        #True Window
        #selection help
        geoLayout93=mc.frameLayout(l='selection thingy',w=300,cl=False,cll=True,bgc=(0.361,0.2,0.404))
        
        geoMainLayout93=mc.rowColumnLayout(w=300,h=85,nc=3)    
        
        mc.button(l='hi',c='mc.select(hi=1)',w=100,h=40)
        mc.button(l='bonesSel',c='boneSel()',w=100,h=40)
        mc.button(l='model',c='mc.select("model")',w=100,h=40)
        mc.button(l='Sel_ccc',c='Sel_ccc()',w=100,h=40)
        
        mc.setParent("..")
        mc.setParent("..")
        
        #geo and others Thingy
        #####################################################################################
        geoLayout93=mc.frameLayout(l='Geo and others thingy',w=300,cl=False,cll=True,bgc=(0.361,0.2,0.404))
        
        geoMainLayout93=mc.rowColumnLayout(w=300,h=85,nc=3)    
        
        mc.button(l='uNode',c='uNode()',w=100,h=40)
        mc.button(l='locSel',c='locSel()',w=100,h=40)
        mc.button(l='locOrient',c='locOrient()',w=100,h=40)
        mc.button(l='do_matrix',c='do_matrix()',w=100,h=40)
        mc.setParent("..")
        mc.setParent("..")
        
        #connection and ccc thingy
        ##############################################################################################
        connnectLayout93=mc.frameLayout(l='Cons and ccc thingy',w=300,cl=False,cll=True,bgc=(0.361,0.2,0.404))
        mc.button(l='qConnectT',c='qCT()',w=100,h=40)
        mc.button(l='qConnectR',c='qCR()',w=100,h=40)
        mc.button(l='qConnectS',c='qCS()',w=100,h=40)
        mc.button(l='ConDRItAnim',c='ConDRitAnim()',w=100,h=40)
        
        mc.setParent("..")
        mc.setParent("..")
        #constraint and ccc thingy
        ##############################################################################################
        consLayout93=mc.frameLayout(l='Cons and ccc thingy',w=300,cl=False,cll=True,bgc=(0.361,0.2,0.404))
        
        consMainLayout93=mc.rowColumnLayout(w=300,h=85,nc=3)    
        mc.button(l='InvCons',c='InvCons()',w=100,h=40)
        mc.button(l='delCons',c='delCons()',w=100,h=40)
        mc.button(l='qSnap',c='qSnap()',w=100,h=40)
        mc.button(l='CTRLsel',c='CTRLsel()',w=100,h=40)

        mc.setParent("..")
        mc.setParent("..")
        
        #bones and fol thingy
        #############################################################################################
        bonesLayout93=mc.frameLayout(l='Bones and fol thingy',w=300,cl=False,cll=True,bgc=(0.361,0.2,0.404))
        
        bonesMainLayout93=mc.rowColumnLayout(w=300,h=85,nc=3)    
        mc.button(l='scaleBone',w=100,h=40)
        mc.button(l='jSel',c='jSel()',w=100,h=40)
        mc.button(l='Hfol',c='Hfol()',w=100,h=40)
        mc.button(l='Scale',c='Scale()',w=100,h=40)
        
        mc.setParent("..")
        mc.setParent("..")
        


        #Closing window
        #############################################################3
        mc.rowLayout(w=300,bgc=(0.361,0.2,0.404))
        
           
        mc.button(l='close',c='mc.deleteUI("toolboxUI")',w=300,h=100)
        

        mc.setParent("..")
        mc.setParent("..")
        
        

        #show window
        mc.showWindow(windowTool)
       
        


ConDRitAnim()        
#superWindow = window()
#superWindow.UI()
import pymel.core as pm

#first step select Nucleus, second select Controller or not

### SCRIPT ###

controlData=[(1.0, 0.0, -9.9579925010295987e-17),
 (-1.0, 0.0, 9.9579925010295987e-17),
 (2.2111185107375417e-32, -1.0, 2.2204460492503131e-16),
 (-1.0, 0.0, 9.9579925010295987e-17),
 (-2.2111185107375417e-32, 1.0, -2.2204460492503131e-16)]

#take user selection
nucleusName=pm.selected()

#is there a controller selected?
if 'transform'==pm.objectType(nucleusName[-1]):
    controller=nucleusName[-1]
    nucleusName.remove(controller)
    #yes
else:
    controller=None
    #no

#defining connection procedure    
def Connecting(nucleus,controller):
    nuc=str(nucleus.name())
    ctrl=controller.name()
    pm.expression(s=' $planarAngle=deg_to_rad('+ctrl+'''.rotateY);
                    $raisingAngle=deg_to_rad('''+ctrl+'''.rotateX);
                    $valueResize=cos($raisingAngle);
                    $valueResize=cos($raisingAngle);
                    
                    '''+ nuc+'''.windDirectionX=sin($planarAngle)*$valueResize;
                    '''+ nuc+'''.windDirectionZ=cos($planarAngle)*$valueResize;
                    '''+ nuc+'.windDirectionY=-sin($raisingAngle);')

#cleanup for nucleus expression
for ev in nucleusName:
    try:
        result=pm.connectionInfo(ev.windDirectionX, sfd=True)
        delete=pm.PyNode(result.split('.')[0])
        pm.delete(delete)
    except:
        pass    

#Look for a batch connection or single connection
try:
    for x, ev in enumerate(nucleusName):
        
        result=pm.objectType(ev)
                     
        if result=='nucleus':
            pass
        else:
            pm.error("This ain't a nucleus!")
    
except:
        pm.error('Error!')    

if controller:
    for ev in nucleusName:
            Connecting(ev,controller)
            
elif not controller:
    controller=pm.curve(n='windController', p=controlData,d=1)
    controller.rotateY.set(90)
    pm.makeIdentity(controller,a=True,r=True)
    controller.visibility.lock()
    controller.rotateZ.lock()
    

    for ev in nucleusName:
        Connecting(ev,controller)
    
else:
    pm.error('Something very wrong happened...DEBUG, last update:5/02/2015')
###adding wind speed ctrl
#checking if attr
try:
    isAttrPresent=controller.wind_Speed.exists()
except:
    isAttrPresent=None
#the rest of the procedure
try:
    if isAttrPresent:
        pass
    else:        
        controller.addAttr('wind_Speed',k=True)
        controller.addAttr('wind_Density',k=True,dv=1)
        controller.addAttr('wind_Noise',k=True)
except:
    pm.warning('new Attr were not created!')
for ev in nucleusName:
    try:
        controller.wind_Speed.connect(ev.windSpeed)
        controller.wind_Density.connect(ev.airDensity)
        controller.wind_Noise.connect(ev.windNoise)
 
    except:
        pm.warning('new Attr were not connected!')




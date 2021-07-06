#!/usr/bin/env python
# coding: utf-8

# ## Simulating Frames on top of Omega ##

# ## Scripting the Omega-Frame Test

# In[2]:


import bifacial_radiance

import os
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'makeModTests')

if not os.path.exists(testfolder):
    os.makedirs(testfolder)
    
print ("Your simulation will be stored in %s" % testfolder)


# In[4]:


demo = bifacial_radiance.RadianceObj('Sim1', testfolder) 
#generating sky


x = 2
y = 1
xgap = 0.02
ygap = 0.15
zgap = 0.3
numpanels = 2
offsetfromaxis = True

module_type = 'TEST'
frameParams = {'frame_material' : 'Metal_Grey', 
               'frame_thickness' : 0.05,
               'frame_z' : 0.06,
               'nSides_frame' : 4,
               'frame_width' : 0.08}


omegaParams = {'omega_material': 'litesoil',
                'x_omega1' : 0.4,
                'mod_overlap' : 0.25,
                'y_omega' : 1.5,
                'x_omega3' : 0.25,
                'omega_thickness' : 0.05,
                'inverted' : False}

mymod = demo.makeModule(name=module_type,x=x, y=y, xgap = xgap, ygap = ygap, zgap = zgap, 
                torquetube = True, diameter = 0.3, axisofrotationTorqueTube=False,
                numpanels = numpanels, 
                frameParams=frameParams, omegaParams=omegaParams)
                



# In[5]:


demo.setGround(0.2)
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)
metdata = demo.readWeatherFile(epwfile, coerce_year = 2021)
demo.gendaylit(4020)

nMods = 1
nRows = 1
sceneDict = {'tilt':0, 'pitch':3, 'clearance_height':3,'azimuth':90, 'nMods': nMods, 'nRows': nRows} 
scene = demo.makeScene(module_type,sceneDict)
demo.makeOct()


# # rvu -vp -7 0 3 -vd 1 0 0 Sim1.oct
# 
# # rvu -vp 0 -5 3 -vd 0 1 0 Sim1.oct

# In[ ]:





# # OLD CODE

# In[1]:


import os
from pathlib import Path

testfolder = r'C:\Users\sarefeen\Documents\RadianceScenes\Omega'  

print ("Your simulation will be stored in %s" % testfolder)


# In[2]:


import bifacial_radiance


# In[3]:


demo = bifacial_radiance.RadianceObj('bifacial_example_omegatest',str(testfolder)) 


# In[4]:


albedo = 0.62
demo.setGround(albedo)


# In[5]:


epwfile = demo.getEPW(lat = 37.5, lon = -77.6)


# In[6]:


metdata = demo.readWeatherFile(epwfile, coerce_year = 2021)


# In[7]:


#generating sky
demo.gendaylit(4020)


# The possible workflow:
# 
# before making the module we need to know:
# - whether the the module is framed or not
# - if the frame is 2-sided or all-sided (if 2-sided, along x or y)
# - The other frameParams (frame thickness, height, leg length, leg height)
# - if there is an omega or not
# - if there is, what are the omegaParams (might also include the omega type...A or n OR V or u)
# - How the presence/absence of Frames/omega matters the other parameters or variables like offsetfromaxis etc.
# - how to handle the dependencies of the variables those were being used only during the makemodule function (numpanels)?

# In[8]:


frameParams = {}
frameParams['frame_material'] = 'Metal_Grey'
frameParams['frame_thickness'] = 0.05
frameParams['frame_height'] = 0.06
frameParams['nSides_frame'] = 4
frameParams['frame_width'] = 0.08


# In[9]:


frameParams


# In[10]:


x = 2
y = 1
xgap = 0.02
ygap = 0.05
zgap = 0.5
numpanels = 2
offsetfromaxis = True
Ny = numpanels


# In[11]:


#the subfunction that makes the frames
def _makeFrames (frameParams, x,y, ygap, numpanels, rotframe = False):
            
    if frameParams['frame_material']:
        frame_material = frameParams['frame_material'] 
    else:
        frame_material = 'Metal_Grey'
    if frameParams['frame_thickness']:
        f_thickness = frameParams['frame_thickness'] 
    else:
        f_thickness = 0.05
    if frameParams['frame_height']:
        f_height = frameParams['frame_height'] 
    else:
        f_height = 0.06
    if frameParams['nSides_frame']:
        n_frame = frameParams['nSides_frame']  
    else:
        n_frame = 4
    if frameParams['frame_width']:
        fl_x = frameParams['frame_width']-f_thickness
    else:
        fl_x = 0.05
    if x>y and n_frame==2:
        x_temp,y_temp = y,x
        rotframe = True
        frame_y = x
    else:
        x_temp,y_temp = x,y
        frame_y = y


    Ny = numpanels
    ygap = 0.05
    y_half = (y*Ny/2)+(ygap*(Ny-1)/2)

    #nameframes
    nameframe1 = 'frameside'
    nameframe2 = 'frameleg'
    
    # taking care of lengths and translation points
    # The pieces are same and symmetrical for west and east


    #frame sides
    few_x = f_thickness
    few_y = frame_y
    few_z = f_height

    fw_xt = -x_temp/2
    fe_xt = x_temp/2-f_thickness
    few_yt = -y_half
    few_zt = -f_height

    #frame legs for east-west 

    flw_xt = -x_temp/2 + f_thickness
    fle_xt = x_temp/2 - f_thickness-fl_x
    flew_yt = -y_half
    flew_zt = -f_height


    #pieces for the shorter side (north-south in this case)

    #filler

    fns_x = x_temp-2*f_thickness
    fns_y = f_thickness
    fns_z = f_height-f_thickness

    fns_xt = -x_temp/2+f_thickness
    fn_yt = -y_half+y-f_thickness
    fs_yt = -y_half
    fns_zt = -f_height+f_thickness

    # the filler legs

    filleg_x = x_temp-2*f_thickness-2*fl_x
    filleg_y = f_thickness + fl_x
    filleg_z = f_thickness

    filleg_xt = -x_temp/2+f_thickness+fl_x
    fillegn_yt = -y_half+y-f_thickness-fl_x
    fillegs_yt = -y_half
    filleg_zt = -f_height


    # making frames: west side

    frame_text = '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(frame_material, nameframe1, few_x, few_y, few_z, fw_xt, few_yt, few_zt) 
    frame_text += ' -a {} -t 0 {} 0'.format(Ny, y_temp+ygap)
    if rotframe:
        frame_text +='| xform -rz 90'


    frame_text += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(frame_material, nameframe2, fl_x, frame_y, f_thickness, flw_xt, flew_yt, flew_zt)
    frame_text += ' -a {} -t 0 {} 0'.format(Ny, y_temp+ygap)
    if rotframe:
        frame_text +='| xform -rz 90'

    # making frames: east side

    frame_text += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(frame_material, nameframe1, few_x, few_y, few_z, fe_xt, few_yt, few_zt) 
    frame_text += ' -a {} -t 0 {} 0'.format(Ny, y_temp+ygap)
    if rotframe:
        frame_text +='| xform -rz 90'

    frame_text += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(frame_material, nameframe2, fl_x, frame_y, f_thickness, fle_xt, flew_yt, flew_zt)
    frame_text += ' -a {} -t 0 {} 0'.format(Ny, y_temp+ygap)
    if rotframe:
        frame_text +='| xform -rz 90'

    if n_frame == 4:
        #making frames: north side

        frame_text += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(frame_material, nameframe1, fns_x, fns_y, fns_z, fns_xt, fn_yt, fns_zt) 
        frame_text += ' -a {} -t 0 {} 0'.format(Ny, y+ygap)


        frame_text += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(frame_material, nameframe2, filleg_x, filleg_y, filleg_z, filleg_xt, fillegn_yt, filleg_zt)
        frame_text += ' -a {} -t 0 {} 0'.format(Ny, y+ygap)

        #making frames: south side

        frame_text += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(frame_material, nameframe1, fns_x, fns_y, fns_z, fns_xt, fs_yt, fns_zt) 
        frame_text += ' -a {} -t 0 {} 0'.format(Ny, y+ygap)

        frame_text += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(frame_material, nameframe2, filleg_x, filleg_y, filleg_z, filleg_xt, fillegs_yt, filleg_zt)
        frame_text += ' -a {} -t 0 {} 0'.format(Ny, y+ygap)


    return frame_text


# In[12]:


frametext = _makeFrames(frameParams, x,y, ygap, numpanels, rotframe = False)


# In[13]:


frametext


# In[14]:


if frametext != '':
    frame = True


# In[15]:


frame


# In[16]:


omegaParams = {}
omegaParams['omega_material'] = 'litesoil'
omegaParams['x_omega1'] = 0.4
omegaParams['z_omega1'] = 0.05
omegaParams['mod_overlap'] = 0.25
omegaParams['y_omega'] = 1.5
omegaParams['x_omega2'] = 0.05
omegaParams['z_omega2'] = 0.5
omegaParams['x_omega3'] = 0.25
omegaParams['z_omega3'] = 0.05
omegaParams['inverted'] = False

#names
name1 = 'mod_adj'
name2 = 'verti'
name3 = 'tt_adj'


# In[17]:


omegaParams


# In[20]:


def _makeOmega(omegaParams, x, y, xgap, zgap):
        
    if omegaParams['omega_material']:
        omega_material = omegaParams['omega_material'] 
    else:
        omega_material = 'Metal_Grey'
    if omegaParams['x_omega1']:
        x_omega1 = omegaParams['x_omega1'] 
    else:
        x_omega1 = xgap*0.5*0.6
    if omegaParams['y_omega']:
        y_omega = omegaParams['y_omega'] 
    else:
        y_omega = y/2
    if omegaParams['mod_overlap']:
        mod_overlap = omegaParams['mod_overlap'] 
    else:
        mod_overlap = x_omega1*0.6
    if omegaParams['z_omega1']:
        z_omega1 = omegaParams['z_omega1']  
    else:
        z_omega1 = zgap*0.1 
    if omegaParams['x_omega2']:
        x_omega2 = omegaParams['x_omega2']
    else:
        x_omega2 = xgap*0.5*0.1
    z_omega2 = zgap
    if omegaParams['x_omega3']:
        x_omega3 = omegaParams['x_omega3'] 
    else:
        x_omega3 = xgap*0.5*0.3
    if omegaParams['z_omega3']:
        z_omega3 = omegaParams['z_omega3']
    else:
        z_omega3 = zgap*0.1  
    if omegaParams['inverted']:
        inverted = omegaParams['inverted']
    else:
        inverted = False

    #naming the omega pieces

    name1 = 'mod_adj'
    name2 = 'verti'
    name3 = 'tt_adj'


    # defining the module adjacent member of omega
    x_translate1 = -x/2 - x_omega1 + mod_overlap
    y_translate = -y_omega/2 #common for all the pieces
    z_translate1 = -z_omega1

    #defining the vertical (zgap) member of the omega
    x_translate2 = x_translate1
    z_translate2 = -z_omega2

    #defining the torquetube adjacent member of omega
    x_translate3 = x_translate1-x_omega3
    z_translate3 = z_translate2
    
    # In presence of frame, the z-translates have to shift
    
    if frame == True:
        frame_height = frameParams['frame_height']
        z_translate1 += -frame_height
        z_translate2 += -frame_height
        z_translate3 += -frame_height

    # for this code, only the translations need to be shifted for the inverted omega

    if inverted == True:
        # shifting the non-inv omega shape of west as inv omega shape of east
        x_translate1_inv_east = x/2-mod_overlap
        x_shift_east = x_translate1_inv_east - x_translate1

        # shifting the non-inv omega shape of west as inv omega shape of east
        x_translate1_inv_west = -x_translate1_inv_east - x_omega1
        x_shift_west = -x_translate1_inv_west + (-x_translate1-x_omega1)

        #customizing the East side of the module for omega_inverted

        custom_text = '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name1, x_omega1, y_omega, z_omega1, x_translate1_inv_east, y_translate, z_translate1) 
        custom_text += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name2, x_omega2, y_omega, z_omega2, x_translate2 + x_shift_east, y_translate, z_translate2)
        custom_text += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name3, x_omega3, y_omega, z_omega3, x_translate3 + x_shift_east, y_translate, z_translate3)

        #customizing the West side of the module for omega_inverted

        custom_text += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name1, x_omega1, y_omega, z_omega1, x_translate1_inv_west, y_translate, z_translate1) 
        custom_text += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name2, x_omega2, y_omega, z_omega2, -x_translate2-x_omega2 -x_shift_west, y_translate, z_translate2)
        custom_text += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name3, x_omega3, y_omega, z_omega3, -x_translate3-x_omega3 - x_shift_west, y_translate, z_translate3)

        omega2omega_x = -x_translate1_inv_east*2

    else:

        #customizing the West side of the module for omega

        omegatext = '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name1, x_omega1, y_omega, z_omega1, x_translate1, y_translate, z_translate1) 
        omegatext += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name2, x_omega2, y_omega, z_omega2, x_translate2, y_translate, z_translate2)
        omegatext += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name3, x_omega3, y_omega, z_omega3, x_translate3, y_translate, z_translate3)

        #customizing the East side of the module for omega

        omegatext += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name1, x_omega1, y_omega, z_omega1, -x_translate1-x_omega1, y_translate, z_translate1) 
        omegatext += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name2, x_omega2, y_omega, z_omega2, -x_translate2-x_omega2, y_translate, z_translate2)
        omegatext += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name3, x_omega3, y_omega, z_omega3, -x_translate3-x_omega3, y_translate, z_translate3)

        omega2omega_x = -x_translate3*2
        
    return omega2omega_x,omegatext


# In[21]:


scene_x, omegatext = _makeOmega(omegaParams, x, y, xgap, zgap)


# In[22]:


omegatext


# In[23]:


customtext = frametext+omegatext


# In[24]:


module_type = 'Prism Solar Bi60 landscape' 
demo.makeModule(name=module_type,x=x, y=y, torquetube = True, diameter = 0.3, xgap = xgap, ygap = ygap, zgap = zgap, numpanels = Ny, customtext = customtext, axisofrotationTorqueTube=False)


# In[25]:


nMods = 1
nRows = 1
sceneDict = {'tilt':0, 'pitch':3, 'clearance_height':3,'azimuth':90, 'nMods': nMods, 'nRows': nRows} 


# In[26]:


scene = demo.makeScene(module_type,sceneDict)


# In[27]:


octfile = demo.makeOct()


# #rvu command from tutorial 1
# rvu -vf views\front.vp -e .01 bifacial_example_omegatest.oct
# 
# rvu -vp 2.5 0 3 -vd -1 0 0 bifacial_example_omegatest.oct
# 
# rvu -vp 2.5 0 3 -vd 0 1 0 bifacial_example_omegatest.oct
# 

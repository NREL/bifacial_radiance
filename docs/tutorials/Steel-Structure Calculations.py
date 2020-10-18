#!/usr/bin/env python
# coding: utf-8

# # Steel Structure Calculations
# 
# 
# Calculate amount of steel needed for torquetube and posts, for various types of racking. 
# 

# In[1]:


import numpy as np
np.pi


# In[2]:


# Constants
density_steel = 7850 # kg/m³
cost_per_kg_steel = 2314 # US$/ton, Global Composite Steel Price and Index 
                        # April-2020 Stainless Steel https://worldsteelprices.com/


# In[3]:


perlin_table = {'perlin1' : {'b' : 2,
                             'b_units': 'in',
                             'h' : 4,
                             'h_units': 'in',
                             'l' : 6,
                             'l_units': 'm',
                             't' : 0.8,
                            't_units': 'mm'},
    
                'perlin2' : {'b' : 2,
                             'b_units': 'in',
                             'h' : 3,
                             'h_units': 'in',
                             'l' : 6,
                             'l_units': 'm',
                             't' : 1.1,
                             't_units': 'mm'},
                            
                'perlin3' : {'b' : 2,
                             'b_units': 'in',
                             'h' : 6,
                             'h_units': 'in',
                             'l' : 6,
                             'l_units': 'm',
                             't' : 1.15,
                             't_units': 'mm'},
                            
                'perlin4' : {'b' : 2,
                             'b_units': 'in',
                             'h' : 7,
                             'h_units': 'in',
                             'l' : 7,
                             'l_units': 'm',
                             't' : 1.15,
                             't_units': 'mm'},
                            
                'perlin5' : {'b' : 2,
                             'b_units': 'in',
                             'h' : 7,
                             'h_units': 'in',
                             'l' : 6,
                             'l_units': 'm',
                             't' : 1.30,
                             't_units': 'mm'},
                            
                'perlin6' : {'b' : 2,
                             'b_units': 'in',
                             'h' : 7,
                             'h_units': 'in',
                             'l' : 6,
                             'l_units': 'm',
                             't' : 1.35, 
                             't_units': 'mm'},
                            
                'perlin7' : {'b' : 2,
                             'b_units': 'in',
                             'h' : 6,
                             'h_units': 'in',
                             'l' : 6,
                             'l_units': 'm',
                             't' : 1.5, 
                             't_units': 'mm'},
                            
                'perlin8' : {'b' : 2,
                             'b_units': 'in',
                             'h' : 6,
                             'h_units': 'in',
                             'l' : 6,
                             'l_units': 'm',
                             't' : 1.8, 
                             't_units': 'mm'},
                            
                'perlin9' : {'b' : 2,
                             'b_units': 'in',
                             'h' : 6,
                             'h_units': 'in',
                             'l' : 7,
                             'l_units': 'm',
                             't' : 1.8,
                             't_units': 'mm'}}        


tube_table = {'tube1' : {'name': 'Smooth-Bore Seamless Steel Tubing',
                         'code': '9220K521',
                         'seller': 'McMaster',
                         'cost': 36.04,
                         'date': '10/18/20',
                         'url': 'https://www.mcmaster.com/steel-tubing/smooth-bore-seamless-steel-tubing/',
                         'OD': 1, 
                         'OD_units': 'in',
                         'ID': 0.834,
                         'ID_units': 'in',
                         'l': 6,
                         'l_units': 'ft',
                         'profile': 'round'},
              'tube2' : {'name': 'Low-Carbon Steel Rectangular Tubes',
                         'code': '6527K644',
                         'seller': 'McMaster',
                         'cost': 182.5,
                         'date': '10/18/20',
                         'url': r'https://www.mcmaster.com/steel-tubing/smooth-bore-seamless-steel-tubing/',
                         'OD': 6, 
                         'OD_units': 'in' ,
                         'ID': 5.5,
                         'ID_units': 'in',
                         'l': 6,
                         'l_units': 'ft',
                         'profile': 'rectangular'}}


# ### PARAMETERS

# In[4]:


# PARAMETERS

# From bifacial_radiance
numpanels = 2  # 1 UP, 2 UP, 3 UP.
x = 0.95   #   moduleDict['x']
y = 1.95   #   moduleDict['y']
xgap = 0.1 #   moduleDict['xgap'].   Leaving 10 centimeters between modules on x direction
numMods = 20     
numRows = 7
hub_height = 2.3

## New Parameters

# TorqueTube
tubetype = 'perlin4'  # other options examples: 'tube2'. If custom, add to the dictionaries above.
numtorquetubes = 1

#POSTS:
postsseparation = 5 # every 5 modules
diameterPosts = 0.20 #m.  
thickness = 0.005 #m 

# Others:
weightpermodule = 60 # kg


# ## Calculations
# 
# (This to become a function in bifacial_radiance once we define if this parameters / process is enough for initial optimization)

# In[5]:


# Mass per M2 TorqueTube
if 'perlin' in tubetype:
    perlsizes = perlin_table[tubetype]
    b = perlsizes['b']
    h = perlsizes['h']
    l = perlsizes['l']
    t = perlsizes['t']
    torquetubeweightperm2 = (b*2+h) * 0.0254 * t/1000 * 1 * density_steel 

if 'tube' in tubetype:
    tube_size = tube_table[tubetype]
    OD = tube_size['OD']
    ID = tube_size['OD']
    torquetubeweightperm2 = (np.pi * (OD * 0.0254/2)**2 - np.pi * (ID * 0.0254/2)**2) * 1 * density_steel

# Mass per M2 Posts
postweightperm2 = (np.pi * (diameterPosts/2)**2 - np.pi * ((diameterPosts-thickness*2)/2)**2) * 1 * density_steel

## 

# Meters of Torquetube and Post needed
torquetubelength = x*numMods+(numMods-1)*xgap            # moduleDict['scenex'] can be used instead of x and xgap-1.
torquetube_needed = torquetubelength*numtorquetubes*numRows

# Meters of Posts needed
numposts_perRow = np.floor(numMods / postsseparation)+1
posts_needed = numposts_perRow*hub_height*numRows

## 

# Mass of Material Needed:
mass_steel = torquetube_needed*torquetubeweightperm2 + posts_needed*postweightperm2
cost = mass_steel/1000 * cost_per_kg_steel

print('This project needs {} Kg of Steel'.format(mass_steel))
print( 'Which would cost ${} at ${} USD/tonne'.format(round(cost,2), cost_per_kg_steel))


# ### BEAM STRESS AND DEFLECTION CALCULATIONS
# 
# 
# To be added. And torsion for wind to calculate needed ballasting ~~

# In[ ]:





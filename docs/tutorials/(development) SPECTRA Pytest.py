#!/usr/bin/env python
# coding: utf-8

# In[ ]:


testfolder = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\bifacial_radiance\TEMP'
weatherfile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\USA_CO_Boulder.724699_TMY2.epw' 
spectrafolder = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\tests\spectra'


# # 1 ) Generate Spectra for 1 timestamp
# 

# In[16]:


idx = 4020


# In[1]:


import bifacial_radiance as br
rad_obj = br.RadianceObj('TEMP', testfolder)
metdata = rad_obj.readWeatherFile(weatherfile)
br.spectral_utils.gen_spectra(idx, rad_obj.metdata, material='Grass', spectra_folder=spectrafolder)


# In[3]:


# Improvements: 
# Create new SPECTRA Folder on the Radiance Scene Folder to save spectras in automatically
# Search for metdata internally if not passed
# Start using timestamps instead of indexes
# generate spectras and save values internally as part of the rad_obj ~ 
# generate spectras for all indexes in metdata automatically (might take a while for the year if readWeatherFile is not restricted)
# pySMARTS: interactive folder selectro to choose where Smarts executable is at, in case it doesn't find it in the Environment Variables


# # 2) Call spectra for that timestamp

# In[14]:


wavelength = 700


# In[ ]:


# spectral_utils generates files with this suffix
suffix = f'_{idx:04}.txt'

# Load albedo
alb_file = Path(spectra_folder, "alb"+suffix)
spectral_alb = br.spectral_utils.spectral_property.load_file(alb_file)

# Generate/Load dni and dhi
dni_file = os.path.join(spectra_folder, "dni"+suffix)
dhi_file = os.path.join(spectra_folder, "dhi"+suffix)
ghi_file = os.path.join(spectra_folder, "ghi"+suffix)
spectral_dni = br.spectral_utils.spectral_property.load_file(dni_file)
spectral_dhi = br.spectral_utils.spectral_property.load_file(dhi_file)
spectral_ghi = br.spectral_utils.spectral_property.load_file(ghi_file)

alb = spectral_alb[wavelength]
dni = spectral_dni[wavelength]
dhi = spectral_dhi[wavelength]
ghi = spectral_ghi[wavelength]

rad_obj.setGround(alb) # this option is for spectral-albedo
solpos = rad_obj.metdata.solpos.iloc[idx]
zen = float(solpos.zenith)
azm = float(solpos.azimuth) - 180
rad_obj.gendaylit2manual(dni, dhi, 90 - zen, azm)

sceneDict = {'tilt':tilt, 'pitch':0.0001, 'clearance_height':2.0,
                     'azimuth':180, 'nMods':1, 'nRows':1}
sceneObj = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict) 

# Build oct file            
octfile = rad_obj.makeOct(octname=f'Oct_{idx:04}')
analysis = br.AnalysisObj(octfile, rad_obj.basename)  
frontscan, backscan = analysis.moduleAnalysis(sceneObj, sensorsy=3)
res_name = f'CenterRow_Center_{idx:04}'
frontdict, backdict = analysis.analysis(octfile, res_name, frontscan, backscan)


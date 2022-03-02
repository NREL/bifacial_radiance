# -*- coding: utf-8 -*-
"""
# P2
# COMPILE THE MODULE's IRRADIANCE 

"""


import os
import pandas as pd
import numpy as np

# Folders where results are and will be saved
savefolder=r'/scratch/sayala/JORDAN/RESULTS_PR_NEW'
posSampled = 50 #!! Modify to the number of positions sampled

ft2m = 0.3048

xgaps = np.round(np.array([3, 4, 6, 9, 12, 15, 18, 21]) * ft2m,1)
numpanelss = [3, 4]
sensorsxs = np.array(list(range(0, 41)))   


errors_all_numpanels = []
errors_all_xgap = []
errors_all_posx = []

for ii in range(0, len(numpanelss)):
    numpanels = numpanelss[ii]
    for jj in range(0, len(xgaps)):
        xgap = xgaps[jj]

        
        x_all = []
        y_all = []
        z_all = []
        mattype_all = []
        rearZ_all = []
        mattype_all = []
        rearMat_all = []
        Wm2Front_all = []
        Wm2Back_all = []

        numpanels_all = []
        xgap_all = []
        posx_all = []
        
        for posx in sensorsxs:
            xgap = xgaps[jj]

            #/scratch/sayala/JORDAN/PUERTO_RICO_NEW_P2/numpanels_3_xgap_1.2_Posx_001/results/irr_xloc_1_Front.csv 
            zero_filled_posx = str(posx).zfill(3)
            filename = '/scratch/sayala/JORDAN/PUERTO_RICO_NEW_P2/numpanels_{}_xgap_{}_Posx_{}/results/irr_xloc_{}.csv'.format(numpanels, xgap, zero_filled_posx, posx)
            print("Working on entry numpanels_{}_xgap_{}_Posx_{}".format(numpanels, xgap, posx))

            try:
                data = pd.read_csv(filename)
                
                # Save all the values
                x_all.append(list(data['x']))
                y_all.append(list(data['y']))
                z_all.append(list(data['z']))
                rearZ_all.append(list(data['rearZ']))
                mattype_all.append(list(data['mattype']))
                rearMat_all.append(list(data['rearMat']))
                Wm2Front_all.append(list(data['Wm2Front']))
                Wm2Back_all.append(list(data['Wm2Back']))

                # Saving position and parameters for indexing
                numpanels_all.append(numpanels)
                xgap_all.append(xgap)
                posx_all.append(posx)

            except:
                print('*** Missing entry numpanels_{}_xgap_{}_Posx_{}'.format(numpanels, xgap, posx))
                errors_all_numpanels.append(numpanels)
                errors_all_xgap.append(xgap)
                errors_all_posx.append(posx)
                

        savefilename = 'Results_p2_numpanels_{}_xgap_{}_Posx_{}.csv'.format(numpanels, xgap, posx)
        df = pd.DataFrame(list(zip(numpanels_all,xgap_all, posx_all,
                                    x_all,y_all,z_all,rearZ_all,
                               mattype_all,rearMat_all,Wm2Front_all,Wm2Back_all)),
                                    columns=['numpanels', 'xgap', 'posx', 'x','y','z','rearZ',
                                       'mattype','rearMat','Wm2Front','Wm2Back'])

        df.to_csv(os.path.join(savefolder,savefilename))

errorfile = pd.DataFrame(list(zip(errors_all_numpanels,errors_all_xgap, errors_all_posx)),
                                columns=['numpanels', 'xgap', 'posx'])

errorfile.to_csv(os.path.join(savefolder, 'ERRORS_05Sep21_PRNew2.csv'))

print("FINISHED")

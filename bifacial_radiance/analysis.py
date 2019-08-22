# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 20:16:47 2019

@author: sayala
"""

#from load import * 


    
def analysisIrradianceandPowerMismatcheEUPVSEC(testfolder, writefiletitle, sensorsy, portraitorlandscape, bififactor, numcells=72):
    r'''
    Use this when sensorsy calculated with bifacial_radiance > cellsy
    
    Reads and calculates power output and mismatch for each file in the 
    testfolder where all the bifacial_radiance irradiance results .csv are saved.
    First load each file, cleans it and resamples it to the numsensors set in this function,
    and then calculates irradiance mismatch and PVMismatch power output for averaged, minimum,
    or detailed irradiances on each cell for the cases of A) only 12 or 8 downsmaples values are
    considered (at the center of each cell), and B) 12 or 8 values are obtained from averaging
    all the irradiances falling in the area of the cell (No edges or inter-cell spacing are considered
    at this moment). Then it saves all the A and B irradiances, as well as the cleaned/resampled
    front and rear irradiances.
    
    Ideally sensorsy in the read data is >> 12 to give results for the irradiance mismatch in the cell.
    
    Also ideally n
     
    Parameters
    ----------
    testfolder:   folder containing output .csv files for bifacial_radiance
    writefiletitle:   .csv title where the output results will be saved. 
    portraitorlandscape: 'portrait' or 'landscape', for PVMismatch input
                      which defines the electrical interconnects inside the module. 
    sensorsy : number of sensors. Ideally this number is >> 12 and 
               is also similar to the number of sensors (points) in the .csv result files.
               We want more than 12 sensors to be able to calculate mismatch of 
               irradiance in the cell.
    bififactor: bifaciality factor of the module. Max 1.0. ALL Rear irradiance values saved include the bifi-factor.
    
    Example:
        
    # User information.
    import bifacial_radiance
    testfolder=r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\HPC Tracking Results\RICHMOND\Bifacial_Radiance Results\PVPMC_0\results'
    writefiletitle= r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\HPC Tracking Results\RICHMOND\Bifacial_Radiance Results\PVPMC_0\test_df.csv'
    sensorsy=100
    portraitorlandscape = 'portrait'
    analysis.analysisIrradianceandPowerMismatch(testfolder, writefiletitle, sensorsy, portraitorlandscape, bififactor=1.0, numcells=72)

    '''
    from bifacial_radiance import load
    import os
    import pandas as pd
        
    # Default variables 
    numpanels=1 # 1 at the moment, necessary for the cleaning routine.
    automatic=True
    
    # Setup PVMismatch parameters
    stdpl, cellsx, cellsy = setupforPVMismatch(portraitorlandscape=portraitorlandscape, sensorsy=sensorsy, numcells=numcells)

    #loadandclean
    filelist = sorted(os.listdir(testfolder))
    print('{} files in the directory'.format(filelist.__len__()))

    F=pd.DataFrame()
    B=pd.DataFrame()
    for z in range(0, filelist.__len__()):
            data=load.read1Result(os.path.join(testfolder,filelist[z]))
            [frontres, backres] = load.deepcleanResult(data, sensorsy=sensorsy, numpanels=numpanels, automatic=automatic)
            F[filelist[z]]=frontres
            B[filelist[z]]=backres          

    B = B*bififactor
    # Downsample routines:
    if sensorsy > cellsy:
        F_cellcenter = sensorsdownsampletocellbyCenter(F, cellsy)
        B_cellcenter = sensorsdownsampletocellbyCenter(B, cellsy)
        F_cellaverage = sensorsdownsampletocellsbyAverage(F, cellsy)
        B_cellaverage = sensorsdownsampletocellsbyAverage(B, cellsy)
    elif sensorsy < cellsy:
        # 2DO IMPORTANT:
        # This section is not ready because I don't think the empty dataframe
        # will absolve me from all the mathematical following equations to 
        # non existing F_cellaverage adn B_cellaverage
        # ... have ot restructure all of this 
        # nicerly!!!! ugh.
        F_cellcenter = sensorupsampletocellsbyInterpolation(F, cellsy)
        B_cellcenter = sensorupsampletocellsbyInterpolation(B, cellsy)
        F_cellaverage = pd.DataFrame() # Fix
        B_cellaverage = pd.DataFrame() # Fix
    elif sensorsy == cellsy:
        # Same as sensorsy < cellsy note.
        F_cellcenter = F
        B_cellcenter = B
        F_cellaverage = pd.DataFrame() # Fix 
        B_cellaverage = pd.DataFrame() # Fix
        return


    # Calculate POATs
    Poat_cellcenter = F_cellcenter+B_cellcenter
    Poat_cellaverage = F_cellaverage+B_cellaverage
    Poat_clean = F+B  # this is ALL the sensorsy.
            
    # Define arrays to fill in:
    Pavg_cellcenter_all=[]; Pdet_cellcenter_all=[]
    Pavg_cellaverage_all=[]; Pdet_cellaverage_all=[]
    Pavg_front_cellaverage_all=[]; Pdet_front_cellaverage_all=[]
    colkeys = F_cellcenter.keys()
    
    # Calculate powers for each hour:
    for i in range(0,len(colkeys)):        
        Pavg_cellcenter, Pdet_cellcenter = calculateVFPVMismatch(stdpl=stdpl, cellsx=cellsx, cellsy=cellsy, Gpoat=list(Poat_cellcenter[colkeys[i]]/1000))
        Pavg_cellaverage, Pdet_cellaverage = calculateVFPVMismatch(stdpl, cellsx, cellsy,Gpoat= list(Poat_cellaverage[colkeys[i]]/1000))
        Pavg_front_cellaverage, Pdet_front_cellaverage = calculateVFPVMismatch(stdpl, cellsx, cellsy, Gpoat= list(F_cellaverage[colkeys[i]]/1000))
        Pavg_cellcenter_all.append(Pavg_cellcenter)
        Pdet_cellcenter_all.append(Pdet_cellcenter)
        Pavg_cellaverage_all.append(Pavg_cellaverage) 
        Pdet_cellaverage_all.append(Pdet_cellaverage)
        Pavg_front_cellaverage_all.append(Pavg_front_cellaverage) 
        Pdet_front_cellaverage_all.append(Pdet_front_cellaverage)
    
    
    ## Rename Rows and save dataframe and outputs.
    F.index='All_Front_'+F.index.astype(str)
    B.index='All_Back_'+B.index.astype(str)
    F_cellcenter.index='CellCenter_FrontIrradiance_cell_'+F_cellcenter.index.astype(str)
    B_cellcenter.index='CellCenter_BackIrradiance_cell_'+B_cellcenter.index.astype(str)
    F_cellaverage.index='CellAverage_FrontIrradiance_cell_'+F_cellaverage.index.astype(str)
    B_cellaverage.index='CellAverage_BackIrradiance_cell_'+B_cellaverage.index.astype(str)
    Poat_cellcenter.index='CellCenter_POATIrradiance_cell_'+Poat_cellcenter.index.astype(str)
    Poat_cellaverage.index='CellAverage_POATIrradiance_cell_'+Poat_cellaverage.index.astype(str)

    ## Transpose
    F = F.T
    B = B.T
    F_cellcenter = F_cellcenter.T
    B_cellcenter = B_cellcenter.T
    F_cellaverage = F_cellaverage.T
    B_cellaverage = B_cellaverage.T
    Poat_cellcenter = Poat_cellcenter.T
    Poat_cellaverage = Poat_cellaverage.T
    Poat_clean = Poat_clean.T
    
    # Statistics Calculatoins
    dfst=pd.DataFrame()
    dfst['CellCenter_MAD/G_Total'] = Poat_cellcenter.apply(mad_fn,axis=1)
    dfst['CellAverage_MAD/G_Total'] = Poat_cellaverage.apply(mad_fn,axis=1)
    dfst['FrontCellAverage_MAD/G_Total'] = F_cellaverage.apply(mad_fn,axis=1)
    dfst['All_MAD/G_Total'] = Poat_clean.apply(mad_fn,axis=1)

    dfst['CellCenter_MAD/G_Total**2'] = dfst['CellCenter_MAD/G_Total']**2
    dfst['CellAverage_MAD/G_Total**2'] = dfst['CellAverage_MAD/G_Total']**2
    dfst['FrontCellAverage_MAD/G_Total**2'] = dfst['FrontCellAverage_MAD/G_Total']**2
    dfst['All_MAD/G_Total**2'] = dfst['All_MAD/G_Total']**2

    dfst['CellCenter_poat'] = Poat_cellcenter.mean(axis=1)
    dfst['CellAverage_poat'] = Poat_cellaverage.mean(axis=1)
    dfst['All_poat'] = Poat_clean.mean(axis=1)

    dfst['CellCenter_gfront'] = F_cellcenter.mean(axis=1)
    dfst['CellAverage_gfront'] = F_cellaverage.mean(axis=1)
    dfst['All_gfront'] = F.mean(axis=1)

    dfst['CellCenter_grear'] = B_cellcenter.mean(axis=1)
    dfst['CellAverage_grear'] = B_cellaverage.mean(axis=1)
    dfst['All_grear'] = B.mean(axis=1)

    dfst['CellCenter_bifi_ratio'] =  dfst['CellCenter_grear']/dfst['CellCenter_gfront']
    dfst['CellAverage_bifi_ratio'] =  dfst['CellAverage_grear']/dfst['CellAverage_gfront']
    dfst['All_bifi_ratio'] =  dfst['All_grear']/dfst['All_gfront']

    dfst['CellCenter_stdev'] = Poat_cellcenter.std(axis=1)/ dfst['CellCenter_poat']
    dfst['CellAverage_stdev'] = Poat_cellaverage.std(axis=1)/ dfst['CellAverage_poat']
    dfst['All_stdev'] = Poat_clean.std(axis=1)/ dfst['All_poat']

    dfst.index=Poat_cellaverage.index.astype(str)

    # Power Calculations/Saving
    Pout=pd.DataFrame()
    Pout['CellCenter_Pavg']=Pavg_cellcenter_all
    Pout['CellCenter_Pdet']=Pdet_cellcenter_all
    Pout['CellAverage_Pavg']=Pavg_cellaverage_all
    Pout['CellAverage_Pdet']=Pdet_cellaverage_all
    Pout['FrontCellAverage_Pavg']=Pavg_front_cellaverage_all
    Pout['FrontCellAverage_Pdet']=Pdet_front_cellaverage_all
    
    Pout['CellCenter_Mismatch_rel'] = 100-(Pout['CellCenter_Pdet']*100/Pout['CellCenter_Pavg'])
    Pout['CellAverage_Mismatch_rel'] = 100-(Pout['CellAverage_Pdet']*100/Pout['CellAverage_Pavg'])
    Pout['FrontCellAverage_Mismatch_rel'] = 100-(Pout['FrontCellAverage_Pdet']*100/Pout['FrontCellAverage_Pavg'])   
    Pout.index=Poat_cellaverage.index.astype(str)

    ## Save CSV
    df_all = pd.concat([Pout,dfst,Poat_cellcenter,Poat_cellaverage,F_cellcenter,B_cellcenter,F_cellaverage,B_cellaverage, F,B],axis=1)
    df_all.to_csv(writefiletitle)
    print("Saved Results to ", writefiletitle)

def sensorupsampletocellsbyInterpolation(df, cellsy):
    '''
        
    Function for when sensorsy in the results are less than cellsy desired.
    Interpolates the dataframe.
    
    #2DO: improve interpolation with pandas. right onw it's row by row.
    
    sensorupsampletocellsbyInterpolation(df, cellsy)
    '''
    
    import pandas as pd
    import numpy as np
    
    sensorsy = len(df)
    
    #2DO: Update this section to match bifacialvf
    cellCenterPVM=[]                                    
    for i in range (0, cellsy):
        cellCenterPVM.append((i*sensorsy/cellsy+(i+1)*sensorsy/cellsy)/2)
    
    df2 = pd.DataFrame()
    for j in range (0, len(df.keys())):
        A = list(df[df.keys()[j]])
        B= np.interp(cellCenterPVM, list(range(0,sensorsy)), A)
        df2[df.keys()[j]]=B
    
    return df2
    
def sensorsdownsampletocellsbyAverage(df, cellsy):
    '''
    df = dataframe with rows indexed by number (i.e. 0 to sensorsy) where sensorsy > cellsy
    cellsy = int. usually 8 or 12.

    example:
    F_centeraverages = sensorsdownsampletocellsbyAverage(F, cellsy)
    '''
    import numpy as np
    import pandas as pd

    edges=len(df)-np.floor(len(df)/(cellsy))*(cellsy)
    edge1=int(np.floor(edges/2))
    edge2=int(edges-edge1)
    A = list(range(df.index[0]+edge1, df.index[-1]-edge2+2, int(np.floor(len(df)/(cellsy)))))
    B = range(0,len(A)-1,1)
    C = [df.iloc[A[x]:A[x+1]].mean(axis=0) for x in B]
    df_centeraverages=pd.DataFrame(C)
    
    return df_centeraverages

def sensorsdownsampletocellbyCenter(df, cellsy):
    '''
    df = dataframe with rows indexed by number (i.e. 0 to sensorsy) where sensorsy > cellsy
    cellsy = int. usually 8 or 12.

    example:
    F_centervalues = sensorsdownsampletocellbyCenter(F, cellsy)
    '''

    import numpy as np

    
    edges=len(df)-np.floor(len(df)/(cellsy))*(cellsy)
    edge1=int(np.floor(edges/2))
    edge2=int(edges-edge1)
    A = list(range(df.index[0]+edge1, df.index[-1]-edge2+2, int(np.floor(len(df)/(cellsy)))))
    A = [int(x+(A[1]-A[0])*0.5) for x in A]
    A = A[:-1]
    df_centervalues=df.loc[A]
    df_centervalues=df_centervalues.reset_index(drop=True)
    
    return df_centervalues
    
def setupforPVMismatch(portraitorlandscape, sensorsy, numcells=72):
    r''' Sets values for calling PVMismatch, for ladscape or portrait modes and 
    
    Example:
    stdpl, cellsx, cellsy = setupforPVMismatch(portraitorlandscape='portrait', sensorsy=100):
    '''

    import numpy as np

        # cell placement for 'portrait'.
    if numcells == 72:
        stdpl=np.array([[0,	23,	24,	47,	48,	71],
        [1,	22,	25,	46,	49,	70],
        [2,	21,	26,	45,	50,	69],
        [3,	20,	27,	44,	51,	68],
        [4,	19,	28,	43,	52,	67],
        [5,	18,	29,	42,	53,	66],
        [6,	17,	30,	41,	54,	65],
        [7,	16,	31,	40,	55,	64],
        [8,	15,	32,	39,	56,	63],
        [9,	14,	33,	38,	57,	62],
        [10,	13,	34,	37,	58,	61],
        [11,	12,	35,	36,	59,	60]])
    
    elif numcells == 96:
        stdpl=np.array([[0,	23,	24,	47,	48,	71,	72,	95],
            [1,	22,	25,	46,	49,	70,	73,	94],
            [2,	21,	26,	45,	50,	69,	74,	93],
            [3,	20,	27,	44,	51,	68,	75,	92],
            [4,	19,	28,	43,	52,	67,	76,	91],
            [5,	18,	29,	42,	53,	66,	77,	90],
            [6,	17,	30,	41,	54,	65,	78,	89],
            [7,	16,	31,	40,	55,	64,	79,	88],
            [8,	15,	32,	39,	56,	63,	80,	87],
            [9,	14,	33,	38,	57,	62,	81,	86],
            [10,	13,	34,	37,	58,	61,	82,	85],
            [11,	12,	35,	36,	59,	60,	83,	84]])
    else:
        print("Error. Only 72 and 96 cells modules supported at the moment. Change numcells to either of this options!")
        return
    
    if portraitorlandscape == 'landscape':
        stdpl = stdpl.transpose()
    elif portraitorlandscape != 'portrait':
        print("Error. portraitorlandscape variable must either be 'landscape' or 'portrait'")
        return
    
    cellsx = len(stdpl[1]); cellsy = len(stdpl)
    
    return stdpl, cellsx, cellsy


def calculateVFPVMismatch(stdpl, cellsx, cellsy, Gpoat):
    r''' calls PVMismatch with all the pre-generated values on bifacial_radiance
    
    Example:
    PowerAveraged, PowerDetailed = def calculateVFPVMismatch(stdpl, cellsx, cellsy, Gpoat)

    '''

    import pvmismatch  # this imports everything we need
    import numpy as np
    
    if np.mean(Gpoat) < 0.001:
        PowerAveraged = 0
        PowerDetailed = 0
    else:                   
        
        if cellsx*cellsy == 72:
            cell_pos = pvmismatch.pvmismatch_lib.pvmodule.STD72
        elif cellsx*cellsy == 96:
            cell_pos = pvmismatch.pvmismatch_lib.pvmodule.STD96
        else:
            print("Error. Only 72 and 96 cells modules supported at the moment. Change numcells to either of this options!")
            return
        
        pvmod=pvmismatch.pvmismatch_lib.pvmodule.PVmodule(cell_pos=cell_pos)
        # makes the system  # 1 module, in portrait mode. 
        pvsys = pvmismatch.pvsystem.PVsystem(numberStrs=1, numberMods=1, pvmods=pvmod)  
        
        G=np.array([Gpoat]).transpose()
        H = np.ones([1,cellsx]) 
        array_det = np.dot(G,H) 
        array_avg = np.ones([cellsy,cellsx])*np.mean(Gpoat)        
                                
        # ACtually do calculations
        pvsys.setSuns({0: {0: [array_avg, stdpl]}})
        PowerAveraged=pvsys.Pmp
        
        pvsys.setSuns({0: {0: [array_det, stdpl]}})
        PowerDetailed=pvsys.Pmp

    return PowerAveraged, PowerDetailed

def mad_fn(data):
    # EUPVSEC 2019 Chris Version
    # return MAD / Average for a 1D array
    import numpy as np
    
    return (np.abs(np.subtract.outer(data,data)).sum()/data.__len__()**2 / np.mean(data))*100



def analysisIrradianceandPowerMismatch(testfolder, writefiletitle, portraitorlandscape, bififactor, numcells=72, downsamplingmethod='byCenter'):
    r'''
    Use this when sensorsy calculated with bifacial_radiance > cellsy
    
    Reads and calculates power output and mismatch for each file in the 
    testfolder where all the bifacial_radiance irradiance results .csv are saved.
    First load each file, cleans it and resamples it to the numsensors set in this function,
    and then calculates irradiance mismatch and PVMismatch power output for averaged, minimum,
    or detailed irradiances on each cell for the cases of A) only 12 or 8 downsmaples values are
    considered (at the center of each cell), and B) 12 or 8 values are obtained from averaging
    all the irradiances falling in the area of the cell (No edges or inter-cell spacing are considered
    at this moment). Then it saves all the A and B irradiances, as well as the cleaned/resampled
    front and rear irradiances.
    
    Ideally sensorsy in the read data is >> 12 to give results for the irradiance mismatch in the cell.
    
    Also ideally n
     
    Parameters
    ----------
    testfolder:   folder containing output .csv files for bifacial_radiance
    writefiletitle:   .csv title where the output results will be saved. 
    portraitorlandscape: 'portrait' or 'landscape', for PVMismatch input
                      which defines the electrical interconnects inside the module. 
    sensorsy : number of sensors. Ideally this number is >> 12 and 
               is also similar to the number of sensors (points) in the .csv result files.
               We want more than 12 sensors to be able to calculate mismatch of 
               irradiance in the cell.
    bififactor: bifaciality factor of the module. Max 1.0. ALL Rear irradiance values saved include the bifi-factor.
    downsampling method: 1 - 'byCenter' - 2 - 'byAverage'
    
    Example:
        
    # User information.
    import bifacial_radiance
    testfolder=r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\HPC Tracking Results\RICHMOND\Bifacial_Radiance Results\PVPMC_0\results'
    writefiletitle= r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\HPC Tracking Results\RICHMOND\Bifacial_Radiance Results\PVPMC_0\test_df.csv'
    sensorsy=100
    portraitorlandscape = 'portrait'
    analysis.analysisIrradianceandPowerMismatch(testfolder, writefiletitle, sensorsy, portraitorlandscape, bififactor=1.0, numcells=72)

    '''
    from bifacial_radiance import load
    import os
    import pandas as pd
        
    # Default variables 
    numpanels=1 # 1 at the moment, necessary for the cleaning routine.
    automatic=True
    
    #loadandclean
    # testfolder = r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\PinPV_Bifacial_Radiance_Runs\HPCResults\df4_FixedTilt\FixedTilt_Cairo_C_0.15\results'
    filelist = sorted(os.listdir(testfolder))
    print('{} files in the directory'.format(filelist.__len__()))

    # Check number of sensors on data.
    temp = load.read1Result(os.path.join(testfolder,filelist[0]))
    sensorsy = len(temp)

    # Setup PVMismatch parameters
    stdpl, cellsx, cellsy = setupforPVMismatch(portraitorlandscape=portraitorlandscape, sensorsy=sensorsy, numcells=numcells)

    F=pd.DataFrame()
    B=pd.DataFrame()
    for z in range(0, filelist.__len__()):
            data=load.read1Result(os.path.join(testfolder,filelist[z]))
            [frontres, backres] = load.deepcleanResult(data, sensorsy=sensorsy, numpanels=numpanels, automatic=automatic)
            F[filelist[z]]=frontres
            B[filelist[z]]=backres          

    B = B*bififactor
    # Downsample routines:
    if sensorsy > cellsy:
        if downsamplingmethod == 'byCenter':
            print("Sensors y > cellsy; Downsampling data by finding CellCenter method")
            F = sensorsdownsampletocellbyCenter(F, cellsy)
            B = sensorsdownsampletocellbyCenter(B, cellsy)
        elif downsamplingmethod == 'byAverage':
            print("Sensors y > cellsy; Downsampling data by Averaging data into Cells method")
            F = sensorsdownsampletocellsbyAverage(F, cellsy)
            B = sensorsdownsampletocellsbyAverage(B, cellsy)
        else:
            print ("Sensors y > cellsy for your module. Select a proper downsampling method ('byCenter', or 'byAverage')")
            return
    elif sensorsy < cellsy:
        print("Sensors y < cellsy; Upsampling data by Interpolation")
        F = sensorupsampletocellsbyInterpolation(F, cellsy)
        B = sensorupsampletocellsbyInterpolation(B, cellsy)
    elif sensorsy == cellsy:
        print ("Same number of sensorsy and cellsy for your module.")
        F = F
        B = B
        return

    # Calculate POATs
    Poat = F+B
            
    # Define arrays to fill in:
    Pavg_all=[]; Pdet_all=[]
    Pavg_front_all=[]; Pdet_front_all=[]
    colkeys = F.keys()
    
    # Calculate powers for each hour:
    for i in range(0,len(colkeys)):        
        Pavg, Pdet = calculateVFPVMismatch(stdpl=stdpl, cellsx=cellsx, cellsy=cellsy, Gpoat=list(Poat[colkeys[i]]/1000))
        Pavg_front, Pdet_front = calculateVFPVMismatch(stdpl, cellsx, cellsy, Gpoat= list(F[colkeys[i]]/1000))
        Pavg_all.append(Pavg)
        Pdet_all.append(Pdet)
        Pavg_front_all.append(Pavg_front) 
        Pdet_front_all.append(Pdet_front)
    
    ## Rename Rows and save dataframe and outputs.
    F.index='FrontIrradiance_cell_'+F.index.astype(str)
    B.index='BackIrradiance_cell_'+B.index.astype(str)
    Poat.index='POAT_Irradiance_cell_'+Poat.index.astype(str)
    
    ## Transpose
    F = F.T
    B = B.T
    Poat = Poat.T
    
    # Statistics Calculatoins
    dfst=pd.DataFrame()
    dfst['MAD/G_Total'] = Poat.apply(mad_fn,axis=1)
    dfst['Front_MAD/G_Total'] = F.apply(mad_fn,axis=1)
    dfst['MAD/G_Total**2'] = dfst['MAD/G_Total']**2
    dfst['Front_MAD/G_Total**2'] = dfst['Front_MAD/G_Total']**2
    dfst['poat'] = Poat.mean(axis=1)
    dfst['gfront'] = F.mean(axis=1)
    dfst['grear'] = B.mean(axis=1)
    dfst['bifi_ratio'] =  dfst['grear']/dfst['gfront']
    dfst['stdev'] = Poat.std(axis=1)/ dfst['poat']
    dfst.index=Poat.index.astype(str)

    # Power Calculations/Saving
    Pout=pd.DataFrame()
    Pout['Pavg']=Pavg_all
    Pout['Pdet']=Pdet_all
    Pout['Front_Pavg']=Pavg_front_all
    Pout['Front_Pdet']=Pdet_front_all
    Pout['Mismatch_rel'] = 100-(Pout['Pdet']*100/Pout['Pavg'])
    Pout['Front_Mismatch_rel'] = 100-(Pout['Front_Pdet']*100/Pout['Front_Pavg'])   
    Pout.index=Poat.index.astype(str)

    ## Save CSV
    df_all = pd.concat([Pout,dfst,Poat,F,B],axis=1)
    df_all.to_csv(writefiletitle)
    print("Saved Results to ", writefiletitle)
    

def updatelegacynames(testfolder, downsamplingmethod='byAverage'):

    import os
    import pandas as pd

    if downsamplingmethod == 'byCenter':
        initstr = 'CellCenter_'
    if downsamplingmethod == 'byAverage':
        initstr = 'CellAverage_'

 #   testfolder = r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\PinPV_Bifacial_Radiance_Runs\HPCResults\df4_FixedTilt'
    filelist = sorted(os.listdir(testfolder))
    filelist = [s for s in filelist if "BifRad" in s]    
    print('{} files in the directory'.format(filelist.__len__()))

    try:
        
        for i in range (1, filelist.__len__()):
            df = pd.read_csv(os.path.join(testfolder,filelist[i]))
    
            #I think this are the columns that get the most used?            
            df.rename(columns = {'MAD/G_Total':initstr+'MAD/G_Total'}, inplace = True)
            df.rename(columns = {'Mismatch_rel':initstr+'Mismatch_rel'}, inplace = True)
            df.rename(columns = {'bifi_ratio':initstr+'bifi_ratio'}, inplace = True)
            df.rename(columns = {'stdev':initstr+'stdev'}, inplace = True)
    
            df.to_csv(os.path.join(testfolder,filelist[i]), index=False)
        
    except:
        print("File already on right header format it seems")
        return
    
        
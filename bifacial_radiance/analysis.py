# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 20:16:47 2019

@author: sayala
"""

#from load import * 
import load
import os
from pvmismatch import *  # this imports everything we need
import numpy as np
import csv
from statsmodels import robust


def analysisIrradianceandPowerMismatch(testfolder, writefiletitle, numpanels, sensorsy, portraitorlandscape='landscape'):
    '''
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
    numpanels:   1 or 2 only at hte moment, necessary for the cleaning routine.
    portraitorlandscape: 'portrait' or 'landscape', for PVMismatch input
                      which defines the electrical interconnects inside the module. 
    sensorsy : number of sensors. Ideally this number is >> 12 and 
               is also similar to the number of sensors (points) in the .csv result files.
               We want more than 12 sensors to be able to calculate mismatch of 
               irradiance in the cell.
    
    '''

    
    
    #INPUT VARIABLES NECESSARY:
    #\\nrel.gov\shared\5J00\Staff\CDeline\Bifacial mismatch data\Tracker mismatch data\3_26_19 Cairo_mismatch_1up tube
    #testfolder = r'C:\Users\sayala\Documents\RadianceScenes\Demo3\results'
    #testfolder = r'\\nrel.gov\shared\5J00\Staff\CDeline\Bifacial mismatch data\Tracker mismatch data\3_26_19 Cairo_mismatch_1up tube\results_noTorqueTube'
    #writefiletitle = r'C:\Users\sayala\Documents\RadianceScenes\results_Cairo_mismatch_1up_noTorqueTube.csv'
    #numpanels= 1
    #portraitorlandscape = 'portrait' # portrait has 12 cells, landscape has 8
    #sensorsy = 120  # deepclean will clean and resample to this number of sensors.
    #ideally close nubmer to the original number of sample points.
    # Also, if it's just 12 or 8 (for landscape or portrait), all the averagd values and cell mismatch
    # become a mooth point
    
    # User information.
    filelist = sorted(os.listdir(testfolder))
    print('{} files in the directory'.format(filelist.__len__()))
    
    # PVMISMATCH Initialization of System
    pvsys = pvsystem.PVsystem(numberStrs=1, numberMods=1)  # makes the system  # 1 module, in portrait mode. 
    pmp_ideal=pvsys.Pmp   # Panel ideal. Monofacial.        
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
    
    
    if portraitorlandscape == 'portrait':
        samplecells=12
        repeatedcells=8
    
    if portraitorlandscape == 'landscape':
        samplecells=8
        repeatedcells=12
        stdpl = stdpl.transpose()
    
    # SAMPLE POINT AND HEADER DEFINITION
    cellCenterPVM=[]          # This grabs just the value at the 'center' of the cell.        
    cellFrontandBackMismatch_Header = []
    cellBackMismatch_Header = []
    cellCenterFrontValue_Header = []
    cellCenterBackValue_Header = []
    cellFrontAveragedValue_Header = []
    cellBackAveragedValue_Header = []
    frontres_header = []
    backres_header = []
    
    for i in range (0, samplecells):
        cellCenterPVM.append((i*sensorsy/(samplecells*1.0)+(i+1)*sensorsy/(samplecells*1.0)/2))
        cellFrontandBackMismatch_Header.append('FrontplusBack_Mismatch_cell_'+str(i))
        cellBackMismatch_Header.append('Back_Mismatch_cell_'+str(i))
        cellCenterFrontValue_Header.append('CellCenterFrontValue_cell'+str(i))
        cellCenterBackValue_Header.append('CellCenterBackValue_cell'+str(i))
        cellBackAveragedValue_Header.append('CellBack_AveragedValue_cell_'+str(i))
        cellFrontAveragedValue_Header.append('CellFront_AveragedValue_cell_'+str(i))
    
    for i in range (0, sensorsy):
        frontres_header.append('Clean_Front_cell'+str(i))
        backres_header.append('Clean_Back_cell'+str(i))
    
    # HEADERS:
    outputheaders = ['Timestamp', 'PowerAveraged_CellCenter', 'PowerMin_CellCenter', 'PowerDetailed_CellCenter', 'PowerAveraged_AverageValues', 'PowerMin_AverageValues', 'PowerDetailed_AverageValues',
                    'MAD_cellCenterVal', 'MAD_cellAverage', 'MAD_frontplusback_clean', 'Cell Front Min', 'Cell Back Min', 'Irradiance Mismatch Front+Back Max', 
                    'Irradiance Mismatch Back Max']
    outputheaders += cellFrontandBackMismatch_Header
    outputheaders += cellBackMismatch_Header
    outputheaders += cellCenterFrontValue_Header
    outputheaders += cellCenterBackValue_Header
    outputheaders += cellBackAveragedValue_Header
    outputheaders += cellFrontAveragedValue_Header
    outputheaders += frontres_header
    outputheaders += backres_header
    
    with open (writefiletitle,'w') as csvfile:
    
        sw = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    
        sw.writerow(outputheaders)
        # LOOP OVER FILES HERE
        for z in range(0, filelist.__len__()):
        #for z in range(0, 1):
        
            data=load.read1Result(os.path.join(testfolder,filelist[z]))
            #sensorsy = len(data)  # 210 for this case. deepclean resamples to value given.
            
            [frontres, backres] = load.deepcleanResult(data, sensorsy, numpanels, automatic=True)
            cellAverageValues_FrontPlusBack=[]
            cellFrontAverage=[]       # This averages the number of sensors.
            cellBackAverage=[]
            cellFrontandBackMismatch=[]
            cellBackMismatch=[]
            cellFrontMin=[]
            cellBackMin=[]
            cellFrontPlusBackMin=[]
            frontandbackres = frontres+ backres
            cellRows=len(frontres)  # this is the same as sensorsy.... maybe replace? #TODO
            
            if cellRows != samplecells:
                for i in range (0, samplecells):
                    istart = int(i*cellRows/samplecells)
                    iend = int((i+1)*cellRows/samplecells)
                    cellFrontAverage.append(np.average(frontres[istart:iend]))
                    cellBackAverage.append(np.average(backres[istart:iend]))                
                    cellAverageValues_FrontPlusBack.append(np.average(frontres[istart:iend])+np.average(backres[istart:iend]))
                    cellFrontandBackMismatch.append((max(frontandbackres[istart:iend])-min(frontandbackres[istart:iend]))*100/(max(frontandbackres[istart:iend])+min(frontandbackres[istart:iend])))
                    cellBackMismatch.append((max(backres[istart:iend])-min(backres[istart:iend]))*100/(max(backres[istart:iend])+min(backres[istart:iend])))
                    cellFrontMin.append(min(frontres[istart:iend]))
                    cellBackMin.append(min(backres[istart:iend]))
                    cellFrontPlusBackMin.append(min(frontandbackres[istart:iend]))
                cellCenterValFront= np.interp(cellCenterPVM, list(range(0,cellRows)), frontres)
                cellCenterValBack= np.interp(cellCenterPVM, list(range(0,cellRows)), backres)
            else:
                cellCenterValFront = frontres
                cellCenterValBack = backres
                
                
            sunmatDetailed_CellCenter=[]
            sunmatAveraged_CellCenter=[]
            sunmatMin_CellCenter=[]
            sunmatDetailed_AverageValues=[]
            sunmatAveraged_AverageValues=[]
            sunmatMin_AverageValues=[]
            
            # Center of Cell only
            cellCenterValues_FrontPlusBack = cellCenterValFront+cellCenterValBack
            AveFront_CellCenter=cellCenterValFront.mean()                
            AveBack_CellCenter=cellCenterValBack.mean()
                     
            # Average of Cell
            #cellAverageValues_FrontPlusBack = sum(cellFrontAverage,cellBackAverage)
            AveFront_AverageValues = np.mean(cellFrontAverage)
            AveBack_AverageValues = np.mean(cellBackAverage)
            
            # Repeat to create a matrix to pass matrix.
            for j in range (0, len(cellCenterValues_FrontPlusBack)):
                sunmatDetailed_CellCenter.append([cellCenterValues_FrontPlusBack[j]/1000]*repeatedcells)
                sunmatDetailed_AverageValues.append([cellAverageValues_FrontPlusBack[j]/1000]*repeatedcells)
                
            for j in range (0, len(cellCenterValFront)):
                sunmatAveraged_CellCenter.append([(AveFront_CellCenter+AveBack_CellCenter)/1000]*repeatedcells)
                sunmatAveraged_AverageValues.append([(AveFront_AverageValues+AveBack_AverageValues)/1000]*repeatedcells)
    
            for j in range (0, len(cellCenterValFront)):
                sunmatMin_CellCenter.append([min(cellCenterValues_FrontPlusBack)/1000]*repeatedcells)
                sunmatMin_AverageValues.append([min(cellFrontPlusBackMin)/1000]*repeatedcells)
                            
            # ACtually do calculations
            pvsys.setSuns({0: {0: [sunmatAveraged_CellCenter, stdpl]}})
            PowerAveraged_CellCenter=pvsys.Pmp
            
            pvsys.setSuns({0: {0: [sunmatDetailed_CellCenter, stdpl]}})
            PowerDetailed_CellCenter=pvsys.Pmp
    
            pvsys.setSuns({0: {0: [sunmatMin_CellCenter, stdpl]}})
            PowerMinimum_CellCenter=pvsys.Pmp
            
            # ACtually do calculations
            pvsys.setSuns({0: {0: [sunmatAveraged_AverageValues, stdpl]}})
            PowerAveraged_AverageValues=pvsys.Pmp
            
            pvsys.setSuns({0: {0: [sunmatDetailed_AverageValues, stdpl]}})
            PowerDetailed_AverageValues=pvsys.Pmp
    
            pvsys.setSuns({0: {0: [sunmatMin_AverageValues, stdpl]}})
            PowerMinimum_AverageValues=pvsys.Pmp
    
            
            #flattened = [val for sublist in dictvalues for val in sublist]
    
            
            # Append Values
            # Append Values
            #cellCenterValFrontFlat = [val for sublist in cellCenterValFront for val in sublist]
            outputvalues = [filelist[z],PowerAveraged_CellCenter, PowerMinimum_CellCenter, PowerDetailed_CellCenter, PowerAveraged_AverageValues, PowerMinimum_AverageValues, PowerDetailed_AverageValues,
                            robust.mad(cellCenterValues_FrontPlusBack), robust.mad(cellAverageValues_FrontPlusBack), robust.mad(frontandbackres), 
                            min(cellFrontMin), min(cellBackMin), 
                            max(cellFrontandBackMismatch), max(cellBackMismatch)]
            outputvalues+=cellFrontandBackMismatch # 12 
            outputvalues+=cellBackMismatch   #   12   
            outputvalues+=list(cellCenterValFront) # 12
            outputvalues+=list(cellCenterValBack) # 12
            outputvalues+=list(cellFrontAverage) # 12
            outputvalues+=list(cellBackAverage) # 12
            outputvalues+=list(frontres) #   sensorsy   # 210
            outputvalues+=list(backres) # sensorsy 210
                                 
            sw.writerow(outputvalues)
            
            
def analysisIrradianceandPowerMismatch2(testfolder, writefiletitle, numpanels, sensorsy, portraitorlandscape='landscape'):
    '''
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
    numpanels:   1 or 2 only at hte moment, necessary for the cleaning routine.
    portraitorlandscape: 'portrait' or 'landscape', for PVMismatch input
                      which defines the electrical interconnects inside the module. 
    sensorsy : number of sensors. Ideally this number is >> 12 and 
               is also similar to the number of sensors (points) in the .csv result files.
               We want more than 12 sensors to be able to calculate mismatch of 
               irradiance in the cell.
    
    '''

    
    
    #INPUT VARIABLES NECESSARY:
    #\\nrel.gov\shared\5J00\Staff\CDeline\Bifacial mismatch data\Tracker mismatch data\3_26_19 Cairo_mismatch_1up tube
    #testfolder = r'C:\Users\sayala\Documents\RadianceScenes\Demo3\results'
    #testfolder = r'\\nrel.gov\shared\5J00\Staff\CDeline\Bifacial mismatch data\Tracker mismatch data\3_26_19 Cairo_mismatch_1up tube\results_noTorqueTube'
    #writefiletitle = r'C:\Users\sayala\Documents\RadianceScenes\results_Cairo_mismatch_1up_noTorqueTube.csv'
    #numpanels= 1
    #portraitorlandscape = 'portrait' # portrait has 12 cells, landscape has 8
    #sensorsy = 120  # deepclean will clean and resample to this number of sensors.
    #ideally close nubmer to the original number of sample points.
    # Also, if it's just 12 or 8 (for landscape or portrait), all the averagd values and cell mismatch
    # become a mooth point
    
    # User information.
    filelist = sorted(os.listdir(testfolder))
    print('{} files in the directory'.format(filelist.__len__()))
    
    # PVMISMATCH Initialization of System
    pvsys = pvsystem.PVsystem(numberStrs=1, numberMods=1)  # makes the system  # 1 module, in portrait mode. 
    pmp_ideal=pvsys.Pmp   # Panel ideal. Monofacial.        
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
    
    
    if portraitorlandscape == 'portrait':
        samplecells=12
        repeatedcells=8
    
    if portraitorlandscape == 'landscape':
        samplecells=8
        repeatedcells=12
        stdpl = stdpl.transpose()
    
    # SAMPLE POINT AND HEADER DEFINITION
    cellCenterPVM=[]          # This grabs just the value at the 'center' of the cell.        
    cellFrontandBackMismatch_Header = []
    cellBackMismatch_Header = []
    cellCenterFrontValue_Header = []
    cellCenterBackValue_Header = []
    cellFrontAveragedValue_Header = []
    cellBackAveragedValue_Header = []
    frontres_header = []
    backres_header = []
    
    for i in range (0, samplecells):
        cellCenterPVM.append((i*sensorsy/(samplecells*1.0)+(i+1)*sensorsy/(samplecells*1.0)/2))
        cellFrontandBackMismatch_Header.append('FrontplusBack_Mismatch_cell_'+str(i))
        cellBackMismatch_Header.append('Back_Mismatch_cell_'+str(i))
        cellCenterFrontValue_Header.append('CellCenterFrontValue_cell'+str(i))
        cellCenterBackValue_Header.append('CellCenterBackValue_cell'+str(i))
        cellBackAveragedValue_Header.append('CellBack_AveragedValue_cell_'+str(i))
        cellFrontAveragedValue_Header.append('CellFront_AveragedValue_cell_'+str(i))
    
    for i in range (0, sensorsy):
        frontres_header.append('Clean_Front_cell'+str(i))
        backres_header.append('Clean_Back_cell'+str(i))
    
    # HEADERS:
    outputheaders = ['Timestamp', 'PowerAveraged_CellCenter', 'PowerMin_CellCenter', 'PowerDetailed_CellCenter', 'PowerAveraged_AverageValues', 'PowerMin_AverageValues', 'PowerDetailed_AverageValues',
                    'PowerFRONT_Averaged', 'PowerFRONT_Detailed',
                     'MAD_cellCenterVal', 'MAD_cellAverage', 'MAD_frontplusback_clean', 'Cell Front Min', 'Cell Back Min', 'Irradiance Mismatch Front+Back Max', 
                    'Irradiance Mismatch Back Max']
    outputheaders += cellFrontandBackMismatch_Header
    outputheaders += cellBackMismatch_Header
    outputheaders += cellCenterFrontValue_Header
    outputheaders += cellCenterBackValue_Header
    outputheaders += cellBackAveragedValue_Header
    outputheaders += cellFrontAveragedValue_Header
    outputheaders += frontres_header
    outputheaders += backres_header
    
    with open (writefiletitle,'w') as csvfile:
    
        sw = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    
        sw.writerow(outputheaders)
        # LOOP OVER FILES HERE
        for z in range(0, filelist.__len__()):
        #for z in range(0, 1):
        
            data=load.read1Result(os.path.join(testfolder,filelist[z]))
            #sensorsy = len(data)  # 210 for this case. deepclean resamples to value given.
            
            [frontres, backres] = load.deepcleanResult(data, sensorsy, numpanels, automatic=True)
            cellAverageValues_FrontPlusBack=[]
            cellFrontAverage=[]       # This averages the number of sensors.
            cellBackAverage=[]
            cellFrontandBackMismatch=[]
            cellBackMismatch=[]
            cellFrontMin=[]
            cellBackMin=[]
            cellFrontPlusBackMin=[]
            frontandbackres = frontres+ backres
            cellRows=len(frontres)  # this is the same as sensorsy.... maybe replace? #TODO
            
            if cellRows != samplecells:
                for i in range (0, samplecells):
                    istart = int(i*cellRows/samplecells)
                    iend = int((i+1)*cellRows/samplecells)
                    cellFrontAverage.append(np.average(frontres[istart:iend]))
                    cellBackAverage.append(np.average(backres[istart:iend]))                
                    cellAverageValues_FrontPlusBack.append(np.average(frontres[istart:iend])+np.average(backres[istart:iend]))
                    cellFrontandBackMismatch.append((max(frontandbackres[istart:iend])-min(frontandbackres[istart:iend]))*100/(max(frontandbackres[istart:iend])+min(frontandbackres[istart:iend])))
                    cellBackMismatch.append((max(backres[istart:iend])-min(backres[istart:iend]))*100/(max(backres[istart:iend])+min(backres[istart:iend])))
                    cellFrontMin.append(min(frontres[istart:iend]))
                    cellBackMin.append(min(backres[istart:iend]))
                    cellFrontPlusBackMin.append(min(frontandbackres[istart:iend]))
                cellCenterValFront= np.interp(cellCenterPVM, list(range(0,cellRows)), frontres)
                cellCenterValBack= np.interp(cellCenterPVM, list(range(0,cellRows)), backres)
            else:
                cellCenterValFront = frontres
                cellCenterValBack = backres
                
                
            sunmatDetailed_CellCenter=[]
            sunmatAveraged_CellCenter=[]
            sunmatMin_CellCenter=[]
            sunmatDetailed_AverageValues=[]
            sunmatAveraged_AverageValues=[]
            sunmatMin_AverageValues=[]
            sunmatFrontOnly_Averaged=[]
            sunmatFrontOnly_Detailed=[]
            
            # Center of Cell only
            cellCenterValues_FrontPlusBack = cellCenterValFront+cellCenterValBack
            AveFront_CellCenter=cellCenterValFront.mean()                
            AveBack_CellCenter=cellCenterValBack.mean()
                     
            # Average of Cell
            #cellAverageValues_FrontPlusBack = sum(cellFrontAverage,cellBackAverage)
            AveFront_AverageValues = np.mean(cellFrontAverage)
            AveBack_AverageValues = np.mean(cellBackAverage)
            
            # Repeat to create a matrix to pass matrix.
            for j in range (0, len(cellCenterValues_FrontPlusBack)):
                sunmatDetailed_CellCenter.append([cellCenterValues_FrontPlusBack[j]/1000]*repeatedcells)
                sunmatDetailed_AverageValues.append([cellAverageValues_FrontPlusBack[j]/1000]*repeatedcells)
                
            for j in range (0, len(cellCenterValFront)):
                sunmatAveraged_CellCenter.append([(AveFront_CellCenter+AveBack_CellCenter)/1000]*repeatedcells)
                sunmatAveraged_AverageValues.append([(AveFront_AverageValues+AveBack_AverageValues)/1000]*repeatedcells)
    
            for j in range (0, len(cellCenterValFront)):
                sunmatMin_CellCenter.append([min(cellCenterValues_FrontPlusBack)/1000]*repeatedcells)
                sunmatMin_AverageValues.append([min(cellFrontPlusBackMin)/1000]*repeatedcells)

            # FRONT MISMATCH
            for j in range (0, len(cellCenterValFront)):
                sunmatFrontOnly_Averaged.append([cellFrontAverage[j]/1000]*repeatedcells)
                sunmatFrontOnly_Detailed.append([cellCenterValFront[j]/1000]*repeatedcells)
                            

            # ACtually do calculations
            pvsys.setSuns({0: {0: [sunmatAveraged_CellCenter, stdpl]}})
            PowerAveraged_CellCenter=pvsys.Pmp
            
            pvsys.setSuns({0: {0: [sunmatDetailed_CellCenter, stdpl]}})
            PowerDetailed_CellCenter=pvsys.Pmp
    
            pvsys.setSuns({0: {0: [sunmatMin_CellCenter, stdpl]}})
            PowerMinimum_CellCenter=pvsys.Pmp
            
            # ACtually do calculations
            pvsys.setSuns({0: {0: [sunmatAveraged_AverageValues, stdpl]}})
            PowerAveraged_AverageValues=pvsys.Pmp
            
            pvsys.setSuns({0: {0: [sunmatDetailed_AverageValues, stdpl]}})
            PowerDetailed_AverageValues=pvsys.Pmp
    
            pvsys.setSuns({0: {0: [sunmatMin_AverageValues, stdpl]}})
            PowerMinimum_AverageValues=pvsys.Pmp
    
            # ACtually do calculations
            pvsys.setSuns({0: {0: [sunmatFrontOnly_Averaged, stdpl]}})
            PowerFRONT_Averaged=pvsys.Pmp
            
            pvsys.setSuns({0: {0: [sunmatFrontOnly_Detailed, stdpl]}})
            PowerFRONT_Detailed=pvsys.Pmp
                
            #flattened = [val for sublist in dictvalues for val in sublist]
    
            
            # Append Values
            # Append Values
            #cellCenterValFrontFlat = [val for sublist in cellCenterValFront for val in sublist]
            outputvalues = [filelist[z],PowerAveraged_CellCenter, 
                            PowerMinimum_CellCenter, PowerDetailed_CellCenter, 
                            PowerAveraged_AverageValues, PowerMinimum_AverageValues, 
                            PowerDetailed_AverageValues, PowerFRONT_Averaged, PowerFRONT_Detailed,
                            robust.mad(cellCenterValues_FrontPlusBack), robust.mad(cellAverageValues_FrontPlusBack), robust.mad(frontandbackres), 
                            min(cellFrontMin), min(cellBackMin), 
                            max(cellFrontandBackMismatch), max(cellBackMismatch)]
            outputvalues+=cellFrontandBackMismatch # 12 
            outputvalues+=cellBackMismatch   #   12   
            outputvalues+=list(cellCenterValFront) # 12
            outputvalues+=list(cellCenterValBack) # 12
            outputvalues+=list(cellFrontAverage) # 12
            outputvalues+=list(cellBackAverage) # 12
            outputvalues+=list(frontres) #   sensorsy   # 210
            outputvalues+=list(backres) # sensorsy 210
                                 
            sw.writerow(outputvalues)
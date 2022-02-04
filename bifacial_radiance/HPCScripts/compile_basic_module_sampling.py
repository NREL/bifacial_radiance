import os
import pandas as pd
import numpy as np

# Folders where results are and will be saved
savefolder=r'/scratch/sayala/RadianceScenes/BasicSimulations/'
posSampled = 50 #!! Modify to the number of positions sampled



for jj in range(0, 2):
    # 0 - With
    # 1 - Without
    
    if jj == 0:
        testfolder=r'/scratch/sayala/RadianceScenes/BasicSimulations/Gendaylit1axis/WithResults'
        savefilename = 'COMPILED_Results_WITH_19AUG.csv'
        withopt = 'WITH'
    if jj == 1:
        testfolder=r'/scratch/sayala/RadianceScenes/BasicSimulations/Gendaylit1axis/WithoutResults'
        savefilename = 'COMPILED_Results_WITHOUT_19AUG.csv'   
        withopt = 'WITHOUT'
    
    filelist = sorted(os.listdir(testfolder))
    #daylist = [x[4:] for x in filelist]
    # timestamplist = []
    # for i in range(len(daylist)):
    #     timestamplist[i] = sorted(os.listdir(testfolder+r'\'+f'{day for day in daylist}'))
    print('{} files in the directory'.format(filelist.__len__()))
    #print(filelist[1].partition('_Module_')[0])
    #!! Make sures this matches the folder names pattern or adjust accordingly.
    # This assumes the folders are named "Day_01_01_01_08" (y m d h)
    
    
    
    x_all = []
    y_all = []
    z_all = []
    rearZ_all = []
    mattype_all = []
    rearMat_all = []
    Wm2Front_all = []
    Wm2Back_all = []
    pos_all = []
    timestamp_all = []
    errors_all = []

    timestamplist = [x[4:15] for x in filelist]
#    positionlist = [x[21:] for x in filelist] 

   
    timestamplist = ['21_04_29_11']
    
    for i in range(0, len(timestamplist)):
        
        print("Working on entry "+str(i)+" timestamp "+timestamplist[i])

        posSampled = 200
    
        for ii in range (0, posSampled):
            resfolder = os.path.join(testfolder, 'Day_'+timestamplist[i]+'_Posx_'+str(ii))
            resfolder = os.path.join(resfolder, 'results/')
            print(resfolder)
        
            #!! Make sure this matches the format being used to save results or
            # modify accordingly.
            # example filename: 'irr_20_01_01_08_pos_0.csv' 
            filename = 'irr_1axis_'+timestamplist[i]+'_00_'+withopt+'_pos_'+str(ii)+'.csv'
            try:
                data = pd.read_csv(os.path.join(resfolder,filename))
                
                # Save all the values
                x_all.append(list(data['x']))
                y_all.append(list(data['y']))
                z_all.append(list(data['z']))
                rearZ_all.append(list(data['rearZ']))
                mattype_all.append(list(data['mattype']))
                rearMat_all.append(list(data['rearMat']))
                Wm2Front_all.append(list(data['Wm2Front']))
                Wm2Back_all.append(list(data['Wm2Back']))
    
                # Saving position and timestamp for indexing
                pos_all.append(ii)
                timestamp_all.append(timestamplist[i])
    
            except:
                print('*** Missing positions ', ii)
                errors_all.append(ii)
                

    df = pd.DataFrame(list(zip(timestamp_all,pos_all,x_all,y_all,z_all,rearZ_all,
                               mattype_all,rearMat_all,Wm2Front_all,Wm2Back_all)),
                              columns=['Timestamp', 'Position', 'x','y','z','rearZ',
                                       'mattype','rearMat','Wm2Front','Wm2Back'])

    df.to_csv(os.path.join(savefolder,savefilename))
    
    errorfile = os.path.join(savefolder, 'ERRORS'+withopt+'.txt')
    with open(errorfile, 'w') as f:
        for s in errors_all:
            f.write(str(s) + '\n')
print("FINISHED")
    
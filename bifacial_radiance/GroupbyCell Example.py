# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 10:58:15 2019

@author: sayala
"""

    #ResultFile='C:\Users\sayala\Documents\RadianceScenes\\asdf2\\results\irr_PRISM_2UP_4234_WITHTorqueTube_Round_black_Diam_0.1_tubeZgap_0.15_GAP_0.05.csv'
    ResultFile=r'C:\Users\sayala\Documents\JPV-3\GenCum vs Gendaylit w TorqueTube Results\results\irr_Torque_tube_hex_test.csv'
    #This reads the file
    test = read1Result(ResultFile)
    numberofsensors=200
    numpanels = 2
    azimuth_angle = 270
    automatic = True
    
    #This cleans it.
    Front4243, Back4243 = deepcleanResult(test, numberofsensors, numpanels, azimuth_angle, automatic)
    
    ResultFile2=r'C:\Users\sayala\Documents\RadianceScenes\GenCumSkyTest\results\irr_Torque_tube_hex_test.csv'
    test = read1Result(ResultFile2)
    FrontJan, BackJan = deepcleanResult(test, numberofsensors, numpanels, azimuth_angle, automatic)

    plt.plot(Back4243/Back4243.max(), label='Yearly')
    plt.plot(BackJan/BackJan.max(), label='January')
    plt.ylabel('Back Irradiance W/m2')
    plt.xlabel('Position on the two panels (gap not plotted), panel 1 0 to 100, panel 2 101 to 200')
    plt.legend()
    plt.show()


    # Option 1:
    # Cellsize given.
    slope = 1.944 # m
    bottomedge = 0.05
    topedge = 0.10
    numcells = 12
    cellsize = 0.12
    gapbetweencells = (slope-bottomedge-topedge-numcells*cellsize)/(numcells-1)
    if gapbetweencells < 0:
        print "Error on dimensions"
    
    # 1 MAP SENSORS
    if numpanels == 2:
        a=np.arange(0,numberofsensors/2-1)
        b=a*slope/100
        
        df = ({'Front B': Front4243 [0:numberofsensors/2-1], 'Back B': Back4243 [0:numberofsensors/2-1], 
               'Front A': Front4243 [numberofsensors/2:-1], 'Back A': Back4243 [numberofsensors/2:-1], 'Physical Position': b})
        
        df = pd.DataFrame.from_records(df)
        
    df['color'] = 'w'
    df['a'] = a
        
    cellstart = bottomedge
    cellsita=[]
    for i in range (0, numcells):
        cellend = cellstart+cellsize
        cellval = df[(df['Physical Position'] >= cellstart) & (df['Physical Position'] <= cellend)]
        print "MAD:", cellval['Back A'].mad()
        print "w_g:", (cellval['Back A'].max()-cellval['Back A'].min())*100/(cellval['Back A'].max()+cellval['Back A'].min())
        df.loc[(df['Physical Position'] <= cellend) & (df['Physical Position'] >= cellstart), ['color']] = 'r'
        cellstart=cellend+gapbetweencells
        cellsita.append(cellval)
        

    
    f, (ax0, ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9, ax10, ax11) = plt.subplots(1, 12, sharey=True)
    ax0.plot(cellsita[0]['Back A']/Back4243.max())
    ax1.plot(cellsita[1]['Back A']/Back4243.max())
    ax1.set_title('Sharing X axis')
    ax2.plot(cellsita[2]['Back A']/Back4243.max())
    ax3.plot(cellsita[3]['Back A']/Back4243.max())
    ax4.plot(cellsita[4]['Back A']/Back4243.max())
    ax5.plot(cellsita[5]['Back A']/Back4243.max())
    ax6.plot(cellsita[6]['Back A']/Back4243.max())
    ax7.plot(cellsita[7]['Back A']/Back4243.max())
    ax8.plot(cellsita[8]['Back A']/Back4243.max())
    ax9.plot(cellsita[9]['Back A']/Back4243.max())
    ax10.plot(cellsita[10]['Back A']/Back4243.max())
    ax11.plot(cellsita[11]['Back A']/Back4243.max())
    plt.ylim([0.8,1.0])
    
    f, (ax0, ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9, ax10, ax11) = plt.subplots(1, 12, sharey=True)
    ax0.plot(cellsita[0]['Back B']/Back4243.max())
    ax1.plot(cellsita[1]['Back B']/Back4243.max())
    ax1.set_title('Sharing X axis')
    ax2.plot(cellsita[2]['Back B']/Back4243.max())
    ax3.plot(cellsita[3]['Back B']/Back4243.max())
    ax4.plot(cellsita[4]['Back B']/Back4243.max())
    ax5.plot(cellsita[5]['Back B']/Back4243.max())
    ax6.plot(cellsita[6]['Back B']/Back4243.max())
    ax7.plot(cellsita[7]['Back B']/Back4243.max())
    ax8.plot(cellsita[8]['Back B']/Back4243.max())
    ax9.plot(cellsita[9]['Back B']/Back4243.max())
    ax10.plot(cellsita[10]['Back B']/Back4243.max())
    ax11.plot(cellsita[11]['Back B']/Back4243.max())
    ax12.plot(cellsita[12]['Back B']/Back4243.max())
    plt.ylim([0.8,1.0])
    
    
    sns.relplot(x='a', y='Front A', hue='color', data=df, palette=dict(w='w', r='r'))
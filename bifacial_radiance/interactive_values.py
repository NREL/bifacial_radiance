# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 10:22:50 2019

@author: sayala
"""
from tkinter import *

    
def interactive_values():
    # Tkinter directory picker.  Now Py3.6 compliant!

    def read_inputfile():
        clearAllValues()
        
        import read_file as ibf
        entry_albedo.insert(0,ibf.albedo)        
        entry_angledelta.insert(0,ibf.angledelta)
        entry_axis_azimuth.insert(0,ibf.axis_azimuth)
        entry_azimuth.insert(0,ibf.azimuth)
        entry_bifi.insert(0,ibf.bifi)
        entry_clearanceheight.insert(0,ibf.clearanceheight)
        entry_enddate_day.insert(0,ibf.enddate_day)
        entry_enddate_hour.insert(0,ibf.enddate_hour)
        entry_enddate_month.insert(0,ibf.enddate_month)
        entry_epwfile.insert(0,ibf.epwfile)
        entry_gcr.insert(0,ibf.gcr)
        entry_getepwfileLat.insert(0,ibf.lat)
        entry_getepwfileLong.insert(0,ibf.lon)
        entry_hubheight.insert(0,ibf.hubheight)
        entry_inputvariablefile.insert(0,ibf.inputvariablefile)
        entry_limitangle.insert(0,ibf.limitangle)
        entry_moduletype.insert(0,ibf.moduletype)
        entry_modWanted.insert(0,ibf.modWanted)
        entry_nMods.insert(0,ibf.nMods)
        entry_nRows.insert(0,ibf.nRows)
        entry_numberofPanels.insert(0,ibf.numberofPanels)
        entry_numcellsx.insert(0,ibf.numcellsx)
        entry_numcellsy.insert(0,ibf.numcellsy)
        entry_pitch.insert(0,ibf.pitch)
        entry_rowWanted.insert(0,ibf.rowWanted)
        entry_sensorsy.insert(0,ibf.sensorsy)
        entry_simulation.insert(0,ibf.simulation)
        entry_startdate_day.insert(0,ibf.startdate_day)
        entry_startdate_hour.insert(0,ibf.startdate_hour)
        entry_startdate_month.insert(0,ibf.startdate_month)
        entry_testfolder.insert(0,ibf.testfolder)
        entry_tilt.insert(0,ibf.tilt)
        entry_timestampend.insert(0, ibf.timestampend) #FIX
        entry_timestampstart.insert(0, ibf.timestampstart) #FIX
        entry_x.insert(0,ibf.x)
        entry_xcell.insert(0,ibf.xcell)
        entry_xcellgap.insert(0,ibf.xcellgap)
        entry_y.insert(0,ibf.y)
        entry_ycell.insert(0,ibf.ycell)
        entry_ycellgap.insert(0,ibf.ycellgap)
        entry_xgap.insert(0,ibf.xgap)
        entry_ygap.insert(0,ibf.ygap)
        entry_zgap.insert(0,ibf.zgap)
        
        
        
    def save_inputfile():

        # example of ow to validate for a number
        try:
            albedo = float(entry_albedo.get())
        except:
            print("ALBEDO: Please type in a number!")

        angledelta = float(entry_angledelta.get())
        axis_azimuth =  float(entry_axis_azimuth.get())
        azimuth =  float(entry_azimuth.get())
        bifi = float( entry_bifi.get())
        clearanceheight =  float(entry_clearanceheight.get())
        diameter = float( entry_diameter.get())
        enddate_day =  int(entry_enddate_day.get())
        enddate_hour = int( entry_enddate_hour.get())
        enddate_month = int( entry_enddate_month.get())
        epwfile = entry_epwfile.get()
        gcr = float(entry_gcr.get())
        lat = float(entry_getepwfileLat.get())
        lon = float(entry_getepwfileLong.get())
        hubheight = float(entry_hubheight.get())
        inputvariablefile = entry_inputvariablefile.get()
        limitangle = float(entry_limitangle.get())
        moduletype = entry_moduletype.get()
        modWanted = int(entry_modWanted.get())
        nMods = int(entry_nMods.get())
        nRows = int(entry_nRows.get())
        numberofPanels = int(entry_numberofPanels.get())
        numcellsx = int(entry_numcellsx.get())
        numcellsy = int(entry_numcellsy.get())
        pitch = float(entry_pitch.get())
        rowWanted = int(entry_rowWanted.get())
        sensorsy = int(entry_sensorsy.get())
        simulation = entry_simulation.get()
        startdate_day = int(entry_startdate_day.get())
        startdate_hour = int(entry_startdate_hour.get())
        startdate_month = int(entry_startdate_month.get())
        testfolder = entry_testfolder.get()
        tilt = float(entry_tilt.get())
        #timestampend = int(entry_timestampend.get())
        #timestampstart = int(entry_timestampstart.get())
        x = float(entry_x.get())
        xcell = float(entry_xcell.get())
        xcellgap = float(entry_xcellgap.get())
        y = float(entry_y.get())
        ycell = float(entry_ycell.get())
        ycellgap = float(entry_ycellgap.get())
        xgap = float(entry_xgap.get())
        ygap = float(entry_ygap.get())
        zgap = float(entry_zgap.get())

        if rb_axisofrotation.get() == 0: axisofrotationTorqueTube=True
        if rb_axisofrotation.get() == 1: axisofrotationTorqueTube=False

        if rb_backtrack.get() == 0: backtrack=True
        if rb_backtrack.get() == 1: backtrack=False

        if rb_cellLevelModule.get() == 0: cellLevelModule=True
        if rb_cellLevelModule.get() == 1: cellLevelModule=False

        if rb_cumulativesky.get() == 0: cumulativesky=True
        if rb_cumulativesky.get() == 1: cumulativesky=True

        if rb_cumulativesky.get() == 0: cumulativesky=True
        if rb_cumulativesky.get() == 1: cumulativesky=True
        
        if rb_fixedortracking.get() == 0: fixedortracking='fixed'
        if rb_fixedortracking.get() == 1: fixedortracking='tracking'
        
        if rb_GCRorPitch.get() == 0: GCRorPitch='GCR'
        if rb_GCRorPitch.get() == 1: GCRorPitch='Pitch'

        if rb_rewriteModule.get() == 0: rewriteModule=True
        if rb_rewriteModule.get() == 1: rewriteModule=False
        
        if rb_roundtrackerangle.get() == 0: roundtrackerangle=True
        if rb_roundtrackerangle.get() == 1: roundtrackerangle=False
    
        if rb_timecontrol.get() == 0: timecontrol='AllYear'
        if rb_timecontrol.get() == 1: timecontrol='StartEndDate'
        if rb_timecontrol.get() == 2: timecontrol='DayDate'
        if rb_timecontrol.get() == 3: timecontrol='Timestamps'
        
        if rb_torqueTube.get() == 0: torqueTube=True
        if rb_torqueTube.get() == 1: torqueTube=False
        
        if rb_torqueTubeMaterial.get() == 0: torqueTubeMaterial='Metal_Grey'
        if rb_torqueTubeMaterial.get() == 1: torqueTubeMaterial='black'

        if rb_tubeType.get() == 0: tubeType='round'
        if rb_tubeType.get() == 1: tubeType='square'  
        if rb_tubeType.get() == 2: tubeType='hex'
        if rb_tubeType.get() == 3: tubeType='oct'
      
        if rb_weatherinputModule.get() == 0: weatherinputMode='getEPW'
        if rb_weatherinputModule.get() == 1: weatherinputMode='readEPWorTMY'
        
        inputvariablefile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\bifacial_radiance\write_file.py'
        file1 = open(inputvariablefile,"w")
        file1.write("#Version 0.2.5a\n")
        file1.write("\n")
        file1.write("#Control Variables\n")
        file1.write("axisofrotationTorqueTube = %s\n" % axisofrotationTorqueTube)
        file1.write("backtrack = %s\n" % backtrack)
        file1.write("cellLevelModule = %s\n" % cellLevelModule)
        file1.write("cumulativesky = %s\n" % cumulativesky)
        file1.write("fixedortracking = '%s'\n" % fixedortracking)
        file1.write("GCRorPitch = '%s'\n" % GCRorPitch)
        file1.write("rewriteModule = %s\n" % rewriteModule)
        file1.write("roundtrackerangle = %s\n" % roundtrackerangle)
        file1.write("torqueTube = %s\n" % torqueTube)
        file1.write("timecontrol = '%s'\n" % timecontrol)
        file1.write("torqueTubeMaterial = '%s'\n" % torqueTubeMaterial)
        file1.write("tubeType = '%s'\n" % tubeType)
        file1.write("weatherinputMode = '%s'\n" % weatherinputMode)
        file1.write("\n")
        file1.write("#Variables and Values\n")        
        file1.write("albedo = %0.2f\n" % albedo)
        file1.write("angledelta = %0.1f\n" % angledelta)
        file1.write("axis_azimuth =  %0.1f\n" % axis_azimuth)
        file1.write("azimuth =  %0.1f\n" % azimuth)
        file1.write("bifi = %0.2f\n" % bifi)
        file1.write("clearanceheight =  %0.3f\n" % clearanceheight)
        file1.write("diameter = %0.3f\n" % diameter)
        file1.write("enddate_day =  %i\n" % enddate_day)
        file1.write("enddate_hour = %i\n" % enddate_hour)
        file1.write("enddate_month = %i\n" % enddate_month)
        file1.write("epwfile =r'%s'\n" % epwfile)
        file1.write("gcr = %0.3f\n" % gcr)
        file1.write("lat = %0.6f\n" % lat)
        file1.write("lon = %0.6f\n" % lon)
        file1.write("hubheight = %0.3f\n" %  hubheight)
        file1.write("inputvariablefile = r'%s'\n" %  inputvariablefile)
        file1.write("limitangle = %i\n" % limitangle)
        file1.write("moduletype = '%s'\n" % moduletype)
        file1.write("modWanted = %i\n" % modWanted)
        file1.write("nMods = %i\n" % nMods)
        file1.write("nRows = %i\n" % nRows)
        file1.write("numberofPanels = %i\n" %  numberofPanels)
        file1.write("numcellsx = %i\n" % numcellsx)
        file1.write("numcellsy = %i\n" % numcellsy)
        file1.write("pitch = %0.3f\n" % pitch)
        file1.write("rowWanted = %i\n" % rowWanted)
        file1.write("sensorsy = %i\n" % sensorsy)
        file1.write("simulation = '%s'\n" % simulation)
        file1.write("startdate_day = %i\n" % startdate_day)
        file1.write("startdate_hour = %i\n" % startdate_hour)
        file1.write("startdate_month = %i\n" %  startdate_month)
        file1.write("testfolder = r'%s'\n" % testfolder)
        file1.write("tilt = %0.2f\n" % tilt)
        file1.write("timestampend = %i\n" % 4020)    #FIX
        file1.write("timestampstart = %i\n" % 4024) #FIX
        file1.write("x = %0.3f\n" % x)
        file1.write("xcell = %0.3f\n" % xcell)
        file1.write("xcellgap = %0.4f\n" % xcellgap)
        file1.write("y = %0.3f\n" %  y)
        file1.write("ycell = %0.3f\n" %  ycell)
        file1.write("ycellgap =%0.4f\n" % ycellgap)
        file1.write("xgap = %0.3f\n" % xgap)
        file1.write("ygap = %0.3f\n" % ygap)
        file1.write("zgap = %0.3f\n" % zgap)
        
        file1.close() 
        
        

        
    def setDefaultValues():
        entry_albedo.insert(0,"0.62")
        entry_angledelta.insert(0,"5")
        entry_axis_azimuth.insert(0,"180")
        entry_azimuth.insert(0,"180")
        entry_bifi.insert(0,"0.9")
        entry_clearanceheight.insert(0,"0.8")
        entry_diameter.insert(0,"0.1")
        entry_enddate_day.insert(0,"30")
        entry_enddate_hour.insert(0,"20")
        entry_enddate_month.insert(0,"6")
        entry_epwfile.insert(0, "AA") #FIX
        entry_gcr.insert(0,"0.35")
        entry_getepwfileLat.insert(0,"33")
        entry_getepwfileLong.insert(0,"-110")
        entry_hubheight.insert(0,"0.9")
        entry_inputvariablefile.insert(0, "BB") #FIX
        entry_limitangle.insert(0,"60")
        entry_moduletype.insert(0,"Prism Solar Bix60")
        entry_modWanted.insert(0,"10")
        entry_nMods.insert(0,"20")
        entry_nRows.insert(0,"7")
        entry_numberofPanels.insert(0,"2")
        entry_numcellsx.insert(0,"12")
        entry_numcellsy.insert(0,"6")
        entry_pitch.insert(0,"10")
        entry_rowWanted.insert(0,"3")
        entry_sensorsy.insert(0,"9")
        entry_simulation.insert(0,"Demo1")
        entry_startdate_day.insert(0,"21")
        entry_startdate_hour.insert(0,"5")
        entry_startdate_month.insert(0,"6")
        entry_testfolder.insert(0, "CC") #FIX
        entry_tilt.insert(0,"10")
        entry_timestampend.insert(0,"4024")
        entry_timestampstart.insert(0,"4020")
        entry_x.insert(0,"0.98")
        entry_xcell.insert(0,"0.15")
        entry_xcellgap.insert(0,"0.01")
        entry_y.insert(0,"1.98")
        entry_ycell.insert(0,"0.15")
        entry_ycellgap.insert(0,"0.01")
        entry_xgap.insert(0,"0.05")
        entry_ygap.insert(0,"0.15")
        entry_zgap.insert(0,"0.10")

    def clearAllValues():
        entry_albedo.delete(0,END)
        entry_angledelta.delete(0,END)
        entry_axis_azimuth.delete(0,END)
        entry_azimuth.delete(0,END)
        entry_bifi.delete(0,END)
        entry_clearanceheight.delete(0,END)
        entry_diameter.delete(0,END)
        entry_enddate_day.delete(0,END)
        entry_enddate_hour.delete(0,END)
        entry_enddate_month.delete(0,END)
        entry_epwfile.delete(0,END)
        entry_gcr.delete(0,END)
        entry_getepwfileLat.delete(0,END)
        entry_getepwfileLong.delete(0,END)
        entry_hubheight.delete(0,END)
        entry_inputvariablefile.delete(0,END)
        entry_limitangle.delete(0,END)
        entry_moduletype.delete(0,END)
        entry_modWanted.delete(0,END)
        entry_nMods.delete(0,END)
        entry_nRows.delete(0,END)
        entry_numberofPanels.delete(0,END)
        entry_numcellsx.delete(0,END)
        entry_numcellsy.delete(0,END)
        entry_pitch.delete(0,END)
        entry_rowWanted.delete(0,END)
        entry_sensorsy.delete(0,END)
        entry_simulation.delete(0,END)
        entry_startdate_day.delete(0,END)
        entry_startdate_hour.delete(0,END)
        entry_startdate_month.delete(0,END)
        entry_testfolder.delete(0,END)
        entry_tilt.delete(0,END)
        entry_timestampend.delete(0,END)
        entry_timestampstart.delete(0,END)
        entry_x.delete(0,END)
        entry_xcell.delete(0,END)
        entry_xcellgap.delete(0,END)
        entry_y.delete(0,END)
        entry_ycell.delete(0,END)
        entry_ycellgap.delete(0,END)
        entry_xgap.delete(0,END)
        entry_ygap.delete(0,END)
        entry_zgap.delete(0,END)
        
        
    def setDefaults():
        clearAllValues()
        setDefaultValues()
        
        
        # RB Values 
        '''
        rb_axisofrotation
        rb_backtrack
        rb_cellLevelModule
        rb_cumulativesky
        rb_fixedortracking
        rb_GCRorPitch
        rb_rewriteModule
        rb_roundtrackerangle
        rb_timecontrol
        rb_torqueTube
        rb_torqueTubeMaterial
        rb_tubeType
        rb_weatherinputModule
        '''
        
        #Labels that should be inactive
        epwfile_label.config(state='disable')
        epwfile_button.config(state='disable')
        startdate_label.config(state='disabled')
        enddate_label.config(state='disabled')
        timestampend_label.config(state='disabled')
        timestampstart_label.config(state='disabled')
        backtrack_label.config(state='disabled')
        limitangle_label.config(state='disabled')
        roundtrackerangle_label.config(state='disabled')
        angledelta_label.config(state='disabled')
        axisofrotation_label.config(state='disabled')
        numcellsx_label.config(state='disabled')
        numcellsy_label.config(state='disabled')
        xcell_label.config(state='disabled')
        ycell_label.config(state='disabled')
        xcellgap_label.config(state='disabled')
        ycellgap_label.config(state='disabled')
        pitch_label.config(state='disabled')
        axis_azimuth_label.config(state='disabled')
        hubheight_label.config(state='disabled')

        #Labels that should be active
        getepwfile_label.config(state='normal')
        azimuth_label.config(state='normal')
        clearanceheight_label.config(state='normal')
        x_label.config(state='normal')
        y_label.config(state='normal')
        gcr_label.config(state='normal')
        tubeType_label.config(state='normal')
        torqueTubeMaterial_label.config(state='normal')

        #Entries that should be inactive
        entry_epwfile.config(state='disabled')
        entry_limitangle.config(state='disabled')
        entry_angledelta.config(state='disabled')
        entry_numcellsx.config(state='disabled')
        entry_numcellsy.config(state='disabled')
        entry_xcell.config(state='disabled')
        entry_ycell.config(state='disabled')
        entry_xcellgap.config(state='disabled')
        entry_ycellgap.config(state='disabled')
        entry_pitch.config(state='disabled')
        entry_axis_azimuth.config(state='disabled')
        entry_hubheight.config(state='disabled')
        
        #buttons that should be inactive
        epwfile_button.config(state='disabled')
        
        #Radiobuttons that should be disabled
        rad1_axisofrotation.config(state='disabled')
        rad1_backtrack.config(state='disabled')
        rad1_roundtrackerangle.config(state='disabled')
        rad2_roundtrackerangle.config(state='disabled')
        rad3_timecontrol.config(state='disabled')
        rad4_timecontrol.config(state='disabled')

        #Radiobuttons that should be enabled
        rad1_tubeType.config(state='normal')
        rad2_tubeType.config(state='normal')
        rad3_tubeType.config(state='normal')
        rad4_tubeType.config(state='normal')
        rad1_torqueTubeMaterial.config(state='normal')
        rad2_torqueTubeMaterial.config(state='normal')
        rad1_timecontrol.config(state='normal')
        rad2_timecontrol.config(state='normal')
                
        #Radio button Selected
        rad1_weatherinputModule.config(state='active')
        rad1_tubeType.config(state='active')
        rad1_torqueTubeMaterial.config(state='active')
        rad1_torqueTube.config(state='active')
        rad1_timecontrol.config(state='active')
        rad1_rewriteModule.config(state='active')
        rad1_GCRorPitch.config(state='active')
        rad1_fixedortracking.config(state='active')
        rad1_cumulativesky.config(state='active')
        rad1_cellLevelModule.config(state='active')
        rad1_backtrack.config(state='active')

        # Unselected
        '''
        rad2_weatherinputModulE
        rad2_tubeType
        rad3_tubeType
        rad4_tubeType
        rad2_torqueTubeMaterial
        rad2_torqueTube
        rad2_timecontrol
        rad3_timecontrol
        rad4_timecontrol
        rad2_rewriteModule
        rad2_GCRorPitch
        rad2_fixedortracking        
        rad2_cumulativesky
        rad2_cellLevelModule
        rad2_backtrack
        '''
        
    global fixedortracking
    fixedortracking='fixed'

    root = Tk()
    root.geometry('870x900')  # width x height of window

    # Create all of the main containers
    #Col1
    maincontrol_frame = Frame(root, bg='lavender', width=230, height=60, pady=10, padx=20)
    simulationcontrol_frame = Frame(root, width=180, height=30, pady=3, padx=20)
    trackingparams_frame = Frame(root, width=180, height=60, pady=3, padx=20)
    torquetubeparams_frame = Frame(root, width=230, height=60, pady=3, padx=20)
    
    #Col2
    imagevariables_frame = Frame(root, width=230, height=60, pady=3, padx=30)
    moduleparams_frame = Frame(root, width=230, height=60, pady=3, padx=30)
    sceneparams_frame = Frame(root, width=230, height=60, pady=3, padx=30)
    analysisparams_frame = Frame(root, width=230, height=60, pady=3, padx=30)
    
    # layout all of the main containers
    root.grid_rowconfigure(6, weight=1)
    root.grid_columnconfigure(2, weight=1)
    
    maincontrol_frame.grid(row=0, column=0, sticky="ew")
    simulationcontrol_frame.grid(row=1, column=0, sticky="ew")
    trackingparams_frame.grid(row=2, column=0, sticky="ew")
    torquetubeparams_frame.grid(row=3, column=0, sticky="ew")
    
    imagevariables_frame.grid(row=0, column=1, sticky="ew")
    moduleparams_frame.grid(row=1, column=1, sticky="ew")
    sceneparams_frame.grid(row=2, column=1, sticky="ew")
    analysisparams_frame.grid(row=3, column=1, sticky="ew")
    
    # MAIN CONTROL
    ###################
    # Create teh widgets for the maincontrol_frame
    def selGetEPW():
        getepwfile_label.config(state='normal')
        entry_getepwfileLat.config(state='normal')
        entry_getepwfileLong.config(state='normal')
        epwfile_label.config(state='disabled')
        entry_epwfile.config(state='disabled')
        epwfile_button.config(state='disabled')
    def selReadEPW():
        getepwfile_label.config(state='disabled')
        entry_getepwfileLat.config(state='disabled')
        entry_getepwfileLong.config(state='disabled')
        epwfile_label.config(state='normal')
        entry_epwfile.config(state='normal')
        epwfile_button.config(state='normal')
        
    maincontrol_label = Label(maincontrol_frame, bg='lavender', text='Main Control', font=("Arial Bold", 15))
    maincontrol_label.grid(row = 0)
    inputvariablefile_label = Label(maincontrol_frame, bg='orange', text='Input Variables File:')
    inputvariablefile_label.grid(row = 1, sticky=W)
    entry_inputvariablefile = Entry(maincontrol_frame, background="orange")
    entry_inputvariablefile.grid(row=1, column=1)
    inputfileRead_button = Button(maincontrol_frame, text="READ", command=read_inputfile)
    inputfileRead_button.grid(column=0, row=2)   
    inputfileSave_button = Button(maincontrol_frame, text="SAVE", command=save_inputfile)
    inputfileSave_button.grid(column=1, row=2) 
    testfolder_label = Label(maincontrol_frame, bg='lavender', text='TestFolder:')
    testfolder_label.grid(row = 3, sticky = W)
    entry_testfolder = Entry(maincontrol_frame, background="pink")
    entry_testfolder.grid(row=3, column=1)    
    testfolder_button = Button(maincontrol_frame, width=10, text="Search")
    testfolder_button.grid(column=2, row=3, sticky= W) 
    
    
    rb_weatherinputModule=IntVar()
    rad1_weatherinputModule = Label(maincontrol_frame, bg='lavender', text='WeatherFile Input:')
    rad1_weatherinputModule.grid(row = 4, sticky=W)
    rad1_weatherinputModule = Radiobutton(maincontrol_frame,bg='lavender', variable=rb_weatherinputModule, text='GetEPW', value=0, command=selGetEPW)
    rad2_weatherinputModule = Radiobutton(maincontrol_frame,bg='lavender', variable=rb_weatherinputModule, text='ReadEPW / TMY', value=1, command=selReadEPW)
    rad1_weatherinputModule.grid(column=1, row=4)
    rad2_weatherinputModule.grid(column=2, row=4)
    getepwfile_label = Label(maincontrol_frame, bg='lavender', text='Get EPW (Lat/Lon):')
    getepwfile_label.grid(row = 5, sticky=W)
    entry_getepwfileLat = Entry(maincontrol_frame, background="white")
    entry_getepwfileLat.grid(row=5, column=1)
    #entry_getepwfileLat.insert(5,"33")
    entry_getepwfileLong = Entry(maincontrol_frame, background="white")
    entry_getepwfileLong.grid(row=5, column=2)
    epwfile_label = Label(maincontrol_frame, bg='lavender', text='EPW / TMY File:', state='disabled')
    epwfile_label.grid(row = 6, sticky=W)
    entry_epwfile = Entry(maincontrol_frame, background="white", state='disabled')
    entry_epwfile.grid(row=6, column=1)
    epwfile_button = Button(maincontrol_frame, state='disabled', width=10, text="Search")
    epwfile_button.grid(column=2, row=6, sticky= W) 
    
    simulation_label = Label(maincontrol_frame, bg='lavender', text='Simulation Name:')
    simulation_label.grid(row = 7, sticky=W)
    entry_simulation = Entry(maincontrol_frame, background="white")
    entry_simulation.grid(row=7, column=1)
    moduletype_label = Label(maincontrol_frame, bg='lavender', text='Module Type:')
    moduletype_label.grid(row = 8, sticky=W)
    entry_moduletype = Entry(maincontrol_frame, background="white")
    entry_moduletype.grid(row=8, column=1)
    rewriteModule_label = Label(maincontrol_frame, bg='lavender', text='Rewrite Module:')
    rewriteModule_label.grid(row = 9, sticky=W)
    rb_rewriteModule=IntVar()
    rad1_rewriteModule = Radiobutton(maincontrol_frame,bg='lavender', variable=rb_rewriteModule, text='True', value=0)
    rad2_rewriteModule = Radiobutton(maincontrol_frame,bg='lavender', variable=rb_rewriteModule, text='False', value=1)
    rad1_rewriteModule.grid(column=1, row=9)
    rad2_rewriteModule.grid(column=2, row=9)

    # Simulation CONTROL
    ###################

    def selfixed():
        global fixedortracking
        fixedortracking='fixed'
        
        buttonImage.configure(image=image_fixed)
        
        azimuth_label.config(state='normal')
        entry_azimuth.config(state='normal')
        clearanceheight_label.config(state='normal') 
        entry_clearanceheight.config(state='normal')
        tilt_label.config(state='normal')
        entry_tilt.config(state='normal')
    
        axis_azimuth_label.config(state='disabled')
        entry_axis_azimuth.config(state='disabled')
        hubheight_label.config(state='disabled')
        entry_hubheight.config(state='disabled')
        
        backtrack_label.config(state='disabled')
        rad1_backtrack.config(state='disabled') 
        rad2_backtrack.config(state='disabled')
        limitangle_label.config(state='disabled')
        entry_limitangle.config(state='disabled')
        roundtrackerangle_label.config(state='disabled') 
        rad1_roundtrackerangle.config(state='disabled')
        rad2_roundtrackerangle.config(state='disabled')
        angledelta_label.config(state='disabled')
        entry_angledelta.config(state='disabled')
        
        axisofrotation_label.config(state='disabled')
        rad1_axisofrotation.config(state='disabled')
        rad2_axisofrotation.config(state='disabled')
        selcumulativeSky()
        selGendaylitSky()


    def selHSAT():
        global fixedortracking
        fixedortracking='tracking'       
        buttonImage.configure(image=image_tracked)        
        azimuth_label.config(state='disabled')
        entry_azimuth.config(state='disabled')
        clearanceheight_label.config(state='disabled')  
        entry_clearanceheight.config(state='disabled') 
        tilt_label.config(state='disabled')
        entry_tilt.config(state='disabled')
        
        axis_azimuth_label.config(state='normal')
        entry_axis_azimuth.config(state='normal')
        hubheight_label.config(state='normal')
        entry_hubheight.config(state='normal')
        
        backtrack_label.config(state='normal')
        rad1_backtrack.config(state='normal') 
        rad2_backtrack.config(state='normal')
        limitangle_label.config(state='normal')
        entry_limitangle.config(state='normal')
        roundtrackerangle_label.config(state='normal') 
        rad1_roundtrackerangle.config(state='normal')
        rad2_roundtrackerangle.config(state='normal')
        angledelta_label.config(state='normal')
        entry_angledelta.config(state='normal')
         
        axisofrotation_label.config(state='normal')
        rad1_axisofrotation.config(state='normal')
        rad2_axisofrotation.config(state='normal')
        selcumulativeSky()
        selGendaylitSky()

    def selcumulativeSky():
        rad1_timecontrol.config(state='normal')
        rad2_timecontrol.config(state='normal')
        rad3_timecontrol.config(state='disabled')
        rad4_timecontrol.config(state='disabled')
        rad1_timecontrol.config(state='normal')
        rad2_timecontrol.config(state='disabled')
        rad3_timecontrol.config(state='disabled')
        rad4_timecontrol.config(state='disabled')
            
        #2DO: How to make sure one of the gendaylit options is not selected when doing gencumsky?
        #if self.rb_timecontrol == 3 or self.rb_timecontrol == 4:
         #   self.rb_timecontrol = 1
        
    def selGendaylitSky():
        
#        if fixedortracking == 'fixed':
        rad1_timecontrol.config(state='normal')
        rad2_timecontrol.config(state='normal')
        rad3_timecontrol.config(state='disabled')
        rad4_timecontrol.config(state='normal')
 #     else:
        rad1_timecontrol.config(state='normal')
        rad2_timecontrol.config(state='normal')
        rad3_timecontrol.config(state='normal')
        rad4_timecontrol.config(state='disabled')     
        
    def tcAll():
        startdate_label.config(state='disabled')
        enddate_label.config(state='disabled')
        timestampstart_label.config(state='disabled')
        timestampend_label.config(state='disabled')
        entry_startdate_month.config(state='disabled')
        entry_startdate_day.config(state='disabled')        
        entry_startdate_hour.config(state='disabled')
        entry_enddate_month.config(state='disabled')
        entry_enddate_day.config(state='disabled')        
        entry_enddate_hour.config(state='disabled')
        entry_timestampstart.config(state='disabled')
        entry_timestampend.config(state='disabled')


    def tcStartEndDate():
        startdate_label.config(state='normal')
        enddate_label.config(state='normal')
        timestampstart_label.config(state='disabled')
        timestampend_label.config(state='disabled')
        entry_startdate_month.config(state='normal')
        entry_startdate_day.config(state='normal')        
        entry_startdate_hour.config(state='normal')
        entry_enddate_month.config(state='normal')
        entry_enddate_day.config(state='normal')        
        entry_enddate_hour.config(state='normal')
        entry_timestampstart.config(state='disabled')
        entry_timestampend.config(state='disabled')
        
    def tcDayDate():
        startdate_label.config(state='normal')
        enddate_label.config(state='disabled')
        timestampstart_label.config(state='disabled')
        timestampend_label.config(state='disabled')
        entry_startdate_month.config(state='normal')
        entry_startdate_day.config(state='normal')     
        entry_startdate_hour.config(state='disabled')
        entry_enddate_month.config(state='disabled')
        entry_enddate_day.config(state='disabled')
        entry_enddate_hour.config(state='disabled')
        entry_timestampstart.config(state='disabled') 
        entry_timestampend.config(state='disabled')
        
    def tcTimestamps():
        startdate_label.config(state='disabled')
        enddate_label.config(state='disabled')
        timestampstart_label.config(state='normal')
        timestampend_label.config(state='normal')
        entry_startdate_month.config(state='disabled')
        entry_startdate_day.config(state='disabled')        
        entry_startdate_hour.config(state='disabled')
        entry_enddate_month.config(state='disabled')
        entry_enddate_day.config(state='disabled')        
        entry_enddate_hour.config(state='disabled')
        entry_timestampstart.config(state='normal')
        entry_timestampend.config(state='normal')
        
        #2DO:
        # disable if Fixed:
        # rad3_timecontrol.config(state='normal')   # FullDay 
        
        # disable if HSAT:
        # rad4_timecontrol.config(state='disable')   # Timestamp 
        # timestampstart_label.config(state='disable')
        # timestampend_label.config(state='disable')
        # entry_timestampstart.config(state='disable')
        # entry_timestampend.config(state='disable')


    simulationcontrol_label = Label(simulationcontrol_frame, text='Simulation Control', font=("Arial Bold", 15))
    simulationcontrol_label.grid(row = 0, columnspan=2, sticky=W)
    rb_fixedortracking=IntVar()
    rad1_fixedortracking = Radiobutton(simulationcontrol_frame, variable=rb_fixedortracking, indicatoron = 0, width = 15, pady=12, text='Fixed', value=0, command=selfixed)
    rad2_fixedortracking = Radiobutton(simulationcontrol_frame, variable=rb_fixedortracking, indicatoron = 0, width = 15, pady=12, text='HSAT', value=1, command=selHSAT)
    rad1_fixedortracking.grid(column=0, row=1, columnspan=2)
    rad2_fixedortracking.grid(column=2, row=1, columnspan=2)
    rb_cumulativesky=IntVar()
    rad1_cumulativesky = Radiobutton(simulationcontrol_frame, variable=rb_cumulativesky, indicatoron = 0, width = 15, text='Cumulative Sky', value=0, command=selcumulativeSky)
    rad2_cumulativesky = Radiobutton(simulationcontrol_frame, variable=rb_cumulativesky, indicatoron = 0, width = 15, text='Gendaylit Sky', value=1, command=selGendaylitSky)
    rad1_cumulativesky.grid(column=0, row=2, pady=10, columnspan=2)
    rad2_cumulativesky.grid(column=2, row=2, pady=10, columnspan=2)
    
    #timecontrol_label = Label(simulationcontrol_frame, bg='cyan', text='Time Options', font=("Arial Bold", 10))
    #timecontrol_label.grid(row = 3, columnspan=2, sticky=W, pady=20)

    rb_timecontrol=IntVar()
    rad1_timecontrol = Radiobutton(simulationcontrol_frame, bg='cyan', variable=rb_timecontrol, indicatoron = 0, width = 15, text='ALL Year', value=0, command=tcAll)
    rad2_timecontrol = Radiobutton(simulationcontrol_frame, bg='cyan', variable=rb_timecontrol, indicatoron = 0, width = 15, text='Start-End date', value=1, command=tcStartEndDate)
    rad3_timecontrol = Radiobutton(simulationcontrol_frame, bg='cyan', variable=rb_timecontrol, indicatoron = 0, width = 15, state='disabled', text='Full Day', value=2, command=tcDayDate)
    rad4_timecontrol = Radiobutton(simulationcontrol_frame, bg='cyan', variable=rb_timecontrol, indicatoron = 0, width = 15, state='disabled', text='By Timestamps', value=3, command=tcTimestamps)
    rad1_timecontrol.grid(column=0, row=4, padx=20)
    rad2_timecontrol.grid(column=1, row=4)
    rad3_timecontrol.grid(column=0, row=5, padx=20)
    rad4_timecontrol.grid(column=1, row=5)


    # Time CONTROL
    ###################


    startdate_label = Label(simulationcontrol_frame, state='disabled',  text='StartDate ( MM | DD | HH ):')
    startdate_label.grid(row = 6, column=0)
    entry_startdate_month = Entry(simulationcontrol_frame, width = 4, state='disabled', background="white")
    entry_startdate_month.grid(row=6, column=1)
    entry_startdate_day = Entry(simulationcontrol_frame, width = 4, state='disabled', background="white")
    entry_startdate_day.grid(row=6, column=2)
    entry_startdate_hour = Entry(simulationcontrol_frame, width = 4, state='disabled', background="white")
    entry_startdate_hour.grid(row=6, column=3)

    enddate_label = Label(simulationcontrol_frame, state='disabled',   text='Enddate ( MM | DD | HH ):')
    enddate_label.grid(row= 7, column=0)
    entry_enddate_month = Entry(simulationcontrol_frame, width = 4, state='disabled', background="white")
    entry_enddate_month.grid(row=7, column=1)
    entry_enddate_day = Entry(simulationcontrol_frame, width = 4, state='disabled', background="white")
    entry_enddate_day.grid(row=7, column=2)
    entry_enddate_hour = Entry(simulationcontrol_frame, width = 4, state='disabled', background="white")
    entry_enddate_hour.grid(row=7, column=3)        

    timestampstart_label = Label(simulationcontrol_frame, state='disabled',  text='Timestamp Start:')
    timestampstart_label.grid(row=8, column=0)
    entry_timestampstart = Entry(simulationcontrol_frame, state='disabled', background="white")
    entry_timestampstart.grid(row=8, column=1, columnspan=3)
    
    timestampend_label = Label(simulationcontrol_frame, state='disabled',  text='Timestamp End:')
    timestampend_label.grid(row= 9, column=0)
    entry_timestampend = Entry(simulationcontrol_frame, state='disabled',  background="white")
    entry_timestampend.grid(row=9, column=1, columnspan=3)

    # Tracking Parameters
    ###################
    trackingcontrol_label = Label(trackingparams_frame, text='Tracking Parameters', font=("Arial Bold", 15))
    trackingcontrol_label.grid(row = 0, columnspan=2, sticky=W)
    backtrack_label = Label(trackingparams_frame, state='disabled',  text='Backtrack:')
    backtrack_label.grid(row=1, column=0,  sticky = W)
    rb_backtrack=IntVar()
    rad1_backtrack = Radiobutton(trackingparams_frame, state='disabled', variable=rb_backtrack, text='True', value=0)
    rad2_backtrack = Radiobutton(trackingparams_frame, state='disabled', variable=rb_backtrack, text='False', value=1)
    rad1_backtrack.grid(column=1, row=1,  sticky = W)
    rad2_backtrack.grid(column=2, row=1,  sticky = W)
    limitangle_label = Label(trackingparams_frame, state='disabled',  text='Limit Angle (deg):')
    limitangle_label.grid(row=2, column=0, sticky = W)
    entry_limitangle = Entry(trackingparams_frame, state='disabled', background="white")
    entry_limitangle.grid(row=2, column=1, columnspan=2, sticky = W)
    roundtrackerangle_label = Label(trackingparams_frame, state='disabled',  text='Round Tracker Angle:')
    roundtrackerangle_label.grid(row=3, column=0,  sticky = W)
    rb_roundtrackerangle=IntVar()
    rad1_roundtrackerangle = Radiobutton(trackingparams_frame, state='disabled', variable=rb_roundtrackerangle, text='True', value=0)
    rad2_roundtrackerangle = Radiobutton(trackingparams_frame, state='disabled', variable=rb_roundtrackerangle, text='False', value=1)
    rad1_roundtrackerangle.grid(column=1, row=3,  sticky = W)
    rad2_roundtrackerangle.grid(column=2, row=3,  sticky = W)    
    angledelta_label = Label(trackingparams_frame, state='disabled',  text='Angle delta (deg):')
    angledelta_label.grid(row=4, column=0,  sticky = W)
    entry_angledelta = Entry(trackingparams_frame, state='disabled', background="white")
    entry_angledelta.grid(row=4, column=1, columnspan=2)
    
    axisofrotation_label = Label(trackingparams_frame, state='disabled', text='Axis of Rotation:')
    axisofrotation_label.grid(row=5, column=0, sticky = W)
    rb_axisofrotation=IntVar()
    rad1_axisofrotation = Radiobutton(trackingparams_frame, variable=rb_axisofrotation, state='disabled', text='Torque Tube', value=0)
    rad2_axisofrotation = Radiobutton(trackingparams_frame, width = 8, variable=rb_axisofrotation, state='disabled', text='Panels', value=1)
    rad1_axisofrotation.grid(row=5, column=1, sticky = W)
    rad2_axisofrotation.grid(row=5, column=2, sticky = W)
    
    
    # TorqueTube Parameters
    ###################
    
    def torquetubeTrue():
        tubeType_label.config(state='normal')
        rad1_tubeType.config(state='normal')
        rad2_tubeType.config(state='normal')
        rad3_tubeType.config(state='normal')
        rad4_tubeType.config(state='normal')
        torqueTubeMaterial_label.config(state='normal') 
        rad1_torqueTubeMaterial.config(state='normal')
        rad2_torqueTubeMaterial.config(state='normal')

    
    def torquetubeFalse():
        tubeType_label.config(state='disabled')
        rad1_tubeType.config(state='disabled')
        rad2_tubeType.config(state='disabled')
        rad3_tubeType.config(state='disabled')
        rad4_tubeType.config(state='disabled')
        torqueTubeMaterial_label.config(state='disabled')
        rad1_torqueTubeMaterial.config(state='disabled')
        rad2_torqueTubeMaterial.config(state='disabled')
    
    
    torquetubecontrol_label = Label(torquetubeparams_frame, text='TorqueTube Parameters', font=("Arial Bold", 15))
    torquetubecontrol_label.grid(row = 0, columnspan=3, sticky=W)
    torqueTube_label = Label(torquetubeparams_frame,   text='TorqueTube:')
    torqueTube_label.grid(row=1, column=0,  sticky = W)
    rb_torqueTube=IntVar()
    rad1_torqueTube = Radiobutton(torquetubeparams_frame, indicatoron = 0, width = 10,  variable=rb_torqueTube, text='True', value=0, command=torquetubeTrue)
    rad2_torqueTube = Radiobutton(torquetubeparams_frame, indicatoron = 0, width = 10,  variable=rb_torqueTube, text='False', value=1, command=torquetubeFalse)
    rad1_torqueTube.grid(column=1, row=1,  sticky = W)
    rad2_torqueTube.grid(column=2, row=1,  sticky = W)
    diameter_label = Label(torquetubeparams_frame,  text='Diameter:')
    diameter_label.grid(row=2, column=0, sticky = W)
    entry_diameter = Entry(torquetubeparams_frame,  width = 12,  background="white")
    entry_diameter.grid(row=2, column=1,  sticky = W)
    tubeType_label = Label(torquetubeparams_frame,  text='Tube type:')
    tubeType_label.grid(row=3, column=0,  sticky = W)
    rb_tubeType=IntVar()
    rad1_tubeType = Radiobutton(torquetubeparams_frame,  variable=rb_tubeType, text='Round', value=0)
    rad2_tubeType = Radiobutton(torquetubeparams_frame,   variable=rb_tubeType, text='Square', value=1)
    rad3_tubeType = Radiobutton(torquetubeparams_frame, width = 5,   variable=rb_tubeType, text='Hex', value=2)
    rad4_tubeType = Radiobutton(torquetubeparams_frame, width = 5,  variable=rb_tubeType, text='Oct', value=3)
    rad1_tubeType.grid(column=1, row=3,  sticky = W)
    rad2_tubeType.grid(column=2, row=3,  sticky = W)
    rad3_tubeType.grid(column=3, row=3,  sticky = W)    
    rad4_tubeType.grid(column=4, row=3,  sticky = W)
    rb_torqueTubeMaterial=IntVar()
    torqueTubeMaterial_label = Label(torquetubeparams_frame, text='TorqueTube Material:')
    torqueTubeMaterial_label.grid(column=0, row=4,  sticky = W)
    rad1_torqueTubeMaterial = Radiobutton(torquetubeparams_frame,  variable=rb_torqueTubeMaterial, text='Metal_Grey', value=0)
    rad2_torqueTubeMaterial = Radiobutton(torquetubeparams_frame,  variable=rb_torqueTubeMaterial, text='Black', value=1)
    rad1_torqueTubeMaterial.grid(column=1, row = 4, sticky = W)
    rad2_torqueTubeMaterial.grid(column=2, row = 4, sticky = W)


    # MODULE PARAMETERS Parameters
    ###################
    
    def cellLevelModuleOn():        
        numcellsx_label.config(state='normal')
        entry_numcellsx.config(state='normal')
        numcellsy_label.config(state='normal')
        entry_numcellsy.config(state='normal')
        xcell_label.config(state='normal')
        entry_xcell.config(state='normal')
        ycell_label.config(state='normal')
        entry_ycell.config(state='normal')
        xcellgap_label.config(state='normal')
        entry_xcellgap.config(state='normal')
        ycellgap_label.config(state='normal') 
        entry_ycellgap.config(state='normal') 
        x_label.config(state='disabled')
        y_label.config(state='disabled')
        entry_x.config(state='disabled')
        entry_y.config(state='disabled')
        
    def cellLevelModuleOff():    
        numcellsx_label.config(state='disabled')
        entry_numcellsx.config(state='disabled') 
        numcellsy_label.config(state='disabled') 
        entry_numcellsy.config(state='disabled')
        xcell_label.config(state='disabled')
        entry_xcell.config(state='disabled')
        ycell_label.config(state='disabled')
        entry_ycell.config(state='disabled')
        xcellgap_label.config(state='disabled')
        entry_xcellgap.config(state='disabled')
        ycellgap_label.config(state='disabled')
        entry_ycellgap.config(state='disabled')
        x_label.config(state='normal')
        y_label.config(state='normal')
        entry_x.config(state='normal')
        entry_y.config(state='normal')
        
    moduleparams_label = Label(moduleparams_frame, text='Module Parameters', font=("Arial Bold", 15))
    moduleparams_label.grid(row = 0, columnspan=3, sticky=W)
    numberofPanels_label = Label(moduleparams_frame, text='Number of Panels')
    numberofPanels_label.grid(row=1, column=0, sticky = W)
    entry_numberofPanels = Entry(moduleparams_frame, width = 4)
    entry_numberofPanels.grid(row=1, column=1, sticky = W)
    cellLevelModule_label = Label(moduleparams_frame, text='Cell Level Module', pady=10)
    cellLevelModule_label.grid(row=2, column=0, sticky = W)
    rb_cellLevelModule=IntVar()
    rad1_cellLevelModule = Radiobutton(moduleparams_frame, indicatoron = 0, width = 8, variable=rb_cellLevelModule, text='False', value=0, command=cellLevelModuleOff)
    rad2_cellLevelModule = Radiobutton(moduleparams_frame, indicatoron = 0, width = 8, variable=rb_cellLevelModule, text='True', value=1, command=cellLevelModuleOn)
    rad1_cellLevelModule.grid(column=1, row=2,  sticky = W)
    rad2_cellLevelModule.grid(column=2, row=2,  sticky = W)  
    
    numcellsx_label = Label(moduleparams_frame, state='disabled', text='numcells x:')
    numcellsx_label.grid(row=3, column=0, sticky = W)
    entry_numcellsx = Entry(moduleparams_frame, state='disabled', width = 6)
    entry_numcellsx.grid(row=3, column=1, sticky = W)
    numcellsy_label = Label(moduleparams_frame, state='disabled', text='numcells y:')
    numcellsy_label.grid(row=3, column=2, sticky = W)
    entry_numcellsy = Entry(moduleparams_frame, state='disabled', width = 6)
    entry_numcellsy.grid(row=3, column=3, sticky = W)
    
    xcell_label = Label(moduleparams_frame, state='disabled', text='Size Xcell:')
    xcell_label.grid(row=4, column=0, sticky = W)
    entry_xcell = Entry(moduleparams_frame, state='disabled', width = 6)
    entry_xcell.grid(row=4, column=1, sticky = W)
    ycell_label = Label(moduleparams_frame, state='disabled', text='Size Ycell:')
    ycell_label.grid(row=4, column=2, sticky = W)
    entry_ycell = Entry(moduleparams_frame, state='disabled', width = 6)
    entry_ycell.grid(row=4, column=3, sticky = W)

    xcellgap_label = Label(moduleparams_frame, state='disabled', text='Xcell gap:')
    xcellgap_label.grid(row=5, column=0, sticky = W)
    entry_xcellgap = Entry(moduleparams_frame, state='disabled', width = 6)
    entry_xcellgap.grid(row=5, column=1, sticky = W)
    ycellgap_label = Label(moduleparams_frame, state='disabled', text='Ycell gap:')
    ycellgap_label.grid(row=5, column=2, sticky = W)
    entry_ycellgap = Entry(moduleparams_frame, state='disabled', width = 6)
    entry_ycellgap.grid(row=5, column=3, sticky = W)
        
    x_label = Label(moduleparams_frame,  text='Module size   x:', pady=10)
    x_label.grid(row=6, column=0, sticky = W)
    entry_x = Entry(moduleparams_frame, width = 6)
    entry_x.grid(row=6, column=1, sticky = W)
    y_label = Label(moduleparams_frame, width = 4, text='y:')
    y_label.grid(row=6, column=2, sticky = W)
    entry_y = Entry(moduleparams_frame, width = 6)
    entry_y.grid(row=6, column=3, sticky = W)
    xgap_label = Label(moduleparams_frame,  text='Xgap | Ygap | Zgap :')
    xgap_label.grid(row=7, column=0, sticky = W)
    entry_xgap = Entry(moduleparams_frame, width = 6)
    entry_xgap.grid(row=7, column=1, sticky = W)
    entry_ygap = Entry(moduleparams_frame, width = 6)
    entry_ygap.grid(row=7, column=2, sticky = W)
    entry_zgap = Entry(moduleparams_frame, width = 6)
    entry_zgap.grid(row=7, column=3, sticky = W)
    bifi_label = Label(moduleparams_frame,  text='Bifacial Factor (i.e. 0.9):')
    bifi_label.grid(row=8, column=0, sticky = W)
    entry_bifi = Entry(moduleparams_frame, width = 6)
    entry_bifi.grid(row=8, column=1, sticky = W)


    # SCENE PARAMETERS 
    ###################
    def definebyGCR():        
        gcr_label.config(state='normal')
        entry_gcr.config(state='normal')
        pitch_label.config(state='disabled')
        entry_pitch.config(state='disabled')
    
    def definebyPitch():
        gcr_label.config(state='disabled')
        entry_gcr.config(state='disabled')
        pitch_label.config(state='normal')
        entry_pitch.config(state='normal')
        
    sceneparams_label = Label(sceneparams_frame, text='Scene Parameters', font=("Arial Bold", 15))
    sceneparams_label.grid(row = 0, columnspan=3, sticky=W)
    GCRorPitch_label = Label(sceneparams_frame, text='Row spacing by:')
    GCRorPitch_label.grid(row=1, column=0, sticky = W)
    rb_GCRorPitch=IntVar()
    rad1_GCRorPitch = Radiobutton(sceneparams_frame, width = 8, variable=rb_GCRorPitch, text='GCR', value=0, command=definebyGCR)
    rad2_GCRorPitch = Radiobutton(sceneparams_frame, width = 8, variable=rb_GCRorPitch, text='Pitch', value=1, command=definebyPitch)
    rad1_GCRorPitch.grid(column=1, row=1,  sticky = W)
    rad2_GCRorPitch.grid(column=2, row=1,  sticky = W)  
    gcr_label  = Label(sceneparams_frame, text='GCR:')
    gcr_label.grid(row=2, column=0, sticky = W)
    entry_gcr = Entry(sceneparams_frame, width = 6)
    entry_gcr.grid(row=2, column=1, sticky = W)
    pitch_label = Label(sceneparams_frame, state='disabled', text='Pitch:')
    pitch_label.grid(row=2, column=2, sticky = W)
    entry_pitch = Entry(sceneparams_frame, state='disabled', width = 6)
    entry_pitch.grid(row=2, column=3, sticky = W)
    albedo_label  = Label(sceneparams_frame, text='Albedo:')
    albedo_label.grid(row=3, column=0, sticky = W)
    entry_albedo = Entry(sceneparams_frame, width = 6)
    entry_albedo.grid(row=3, column=1, sticky = W)
    nMods_label  = Label(sceneparams_frame, text='# Mods:')
    nMods_label.grid(row=4, column=0, sticky = W)
    entry_nMods = Entry(sceneparams_frame, width = 6)
    entry_nMods.grid(row=4, column=1, sticky = W)
    nRows_label = Label(sceneparams_frame, text='# Rows:')
    nRows_label.grid(row=4, column=2, sticky = W)
    entry_nRows = Entry(sceneparams_frame, width = 6)
    entry_nRows.grid(row=4, column=3, sticky = W)   
    
    azimuth_label  = Label(sceneparams_frame, text='Azimuth Angle (i.e. 180 for South):')
    azimuth_label.grid(row=5, column=0, sticky = W, columnspan=2)
    entry_azimuth = Entry(sceneparams_frame, width = 6)
    entry_azimuth.grid(row=5, column=2, sticky = W)
    
    clearanceheight_label  = Label(sceneparams_frame, text='Clearance height: ')
    clearanceheight_label.grid(row=6, column=0, sticky = W, columnspan=2)
    entry_clearanceheight = Entry(sceneparams_frame, width = 6)
    entry_clearanceheight.grid(row=6, column=1, sticky = W)

    tilt_label  = Label(sceneparams_frame, text='Tilt: ')
    tilt_label.grid(row=6, column=2, sticky = W, columnspan=2)
    entry_tilt = Entry(sceneparams_frame, width = 6)
    entry_tilt.grid(row=6, column=3, sticky = W)
    
    axis_azimuth_label = Label(sceneparams_frame, state='disabled', text='Axis Azimuth (i.e. 180 for EW HSATtrackers):')
    axis_azimuth_label.grid(row=7, column=0, sticky = W, columnspan=3)
    entry_axis_azimuth = Entry(sceneparams_frame,  state='disabled',  width = 6)
    entry_axis_azimuth.grid(row=7, column=3, sticky = W)
    
    hubheight_label  = Label(sceneparams_frame,  state='disabled', text='Hub height: ')
    hubheight_label.grid(row=8, column=0, sticky = W, columnspan=2)
    entry_hubheight = Entry(sceneparams_frame,  state='disabled', width = 6)
    entry_hubheight.grid(row=8, column=1, sticky = W)


    # Analysis PARAMETERS 
    ###################
    analysisparams_label = Label(analysisparams_frame, text='Analysis Parameters', font=("Arial Bold", 15))
    analysisparams_label.grid(row = 0, columnspan=3, sticky=W)
    sensorsy_label  = Label(analysisparams_frame, text='# Sensors: ')
    sensorsy_label.grid(row=1, column=0, sticky = W)
    entry_sensorsy = Entry(analysisparams_frame, width = 6)
    entry_sensorsy.grid(row=1, column=1, sticky = W)
    modWanted_label  = Label(analysisparams_frame, text='Mod Wanted: ')
    modWanted_label.grid(row=2, column=0, sticky = W)
    entry_modWanted = Entry(analysisparams_frame, width = 6)
    entry_modWanted.grid(row=2, column=1, sticky = W)
    rowWanted_label  = Label(analysisparams_frame, text='Row Wanted: ')
    rowWanted_label.grid(row=2, column=2, sticky = W)
    entry_rowWanted = Entry(analysisparams_frame, width = 6)
    entry_rowWanted.grid(row=2, column=3, sticky = W)
    emptyspace = Label(analysisparams_frame, text='', font=("Arial Bold", 5))
    emptyspace.grid(row = 3, columnspan=3, sticky=W)
    Clear_button = Button(analysisparams_frame, pady=8, text="CLEAR", command=clearAllValues)
    Clear_button.grid(column=0, row=4)
    DEFAULT_button = Button(analysisparams_frame, pady=8, text="DEFAULT", command=setDefaults)
    DEFAULT_button.grid(column=1, row=4)
    RUN_button = Button(analysisparams_frame, bg='lavender', width = 25, pady=15, text="RUN", command=save_inputfile)
    RUN_button.grid(column=2, row=4, columnspan=3) 
    
    ## IMAGE STUFF
    #imagevariables_frame
    image_fixed = PhotoImage(file='fig1_fixed_small.gif')
    image_tracked = PhotoImage(file='fig2_tracked_small.gif')
    buttonImage = Button(imagevariables_frame, image=image_fixed)
    buttonImage.grid(row=0, columnspan=4, sticky=W)
        
    #setDefaultValues()
    setDefaultValues()
    root.title("Bifacial_Radiance | v. 0_2_5")
    root.mainloop()
    
if __name__ == "__main__":
    '''
    Example of how to run a Radiance routine for a simple rooftop bifacial system

    '''

    interactive_values()
        
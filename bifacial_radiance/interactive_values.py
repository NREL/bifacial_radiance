# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 10:22:50 2019

@author: sayala
"""
from tkinter import *

def btn_clear():
    global expression
    expression = ""
    input_text.set("")

def btn_click(item):
    global expression
    expression = expression + str(item)
    input_text.set(expression)
    
def interactive_values():
    # Tkinter directory picker.  Now Py3.6 compliant!

    root = Tk()
    root.geometry('700x800')  # width x height of window
    
    # Create all of the main containers
    maincontrol_frame = Frame(root, bg='lavender', width=230, height=60, pady=3)
    simulationcontrol_frame = Frame(root, width=180, height=30, pady=3)
    timecontrol_frame = Frame(root, width=180, height=60, pady=3)
    trackingparams_frame = Frame(root, width=180, height=60, pady=3)
    torquetubeparams_frame = Frame(root, width=230, height=60, pady=3)
    moduleparams_frame = Frame(root, width=230, height=60, pady=3)
    cellLevelModule_frame = Frame(root, width=230, height=60, pady=3)
    sceneparams_frame = Frame(root, width=230, height=60, pady=3)
    analysisparams_frame = Frame(root, width=230, height=60, pady=3)

    # layout all of the main containers
    root.grid_rowconfigure(6, weight=1)
    root.grid_columnconfigure(2, weight=1)
    
    maincontrol_frame.grid(row=0, column=0, sticky="ew")
    simulationcontrol_frame.grid(row=1, column=0, sticky="ew")
    timecontrol_frame.grid(row=2, column=0, sticky="ew")
    trackingparams_frame.grid(row=3, column=0, sticky="ew")
    torquetubeparams_frame.grid(row=4, column=0, sticky="ew")
    
    moduleparams_frame.grid(row=0, column=1, sticky="ew")
    cellLevelModule_frame.grid(row=1, column=1, sticky="nsew")
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
    def selReadEPW():
        getepwfile_label.config(state='disabled')
        entry_getepwfileLat.config(state='disabled')
        entry_getepwfileLong.config(state='disabled')
        epwfile_label.config(state='normal')
        entry_epwfile.config(state='normal')
        
    maincontrol_label = Label(maincontrol_frame, bg='lavender', text='Main Control', font=("Arial Bold", 15))
    maincontrol_label.grid(row = 0)
    inputvariablefile_label = Label(maincontrol_frame, bg='orange', text='Input Variables File:')
    inputvariablefile_label.grid(row = 1, sticky=W)
    entry_inputvariablefile = Entry(maincontrol_frame, background="orange")
    entry_inputvariablefile.grid(row=1, column=1)
    inputfileRead_button = Button(maincontrol_frame, text="READ")
    inputfileRead_button.grid(column=0, row=2)   
    inputfileSave_button = Button(maincontrol_frame, text="SAVE")
    inputfileSave_button.grid(column=1, row=2) 
    testfolder_label = Label(maincontrol_frame, bg='lavender', text='TestFolder:')
    testfolder_label.grid(row = 3, sticky = W)
    entry_testfolder = Entry(maincontrol_frame, background="pink").grid(row=3, column=1)
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
    entry_getepwfileLat.insert(5,"33")
    entry_getepwfileLong = Entry(maincontrol_frame, background="white")
    entry_getepwfileLong.grid(row=5, column=2)
    epwfile_label = Label(maincontrol_frame, bg='lavender', text='EPW / TMY File:', state='disabled')
    epwfile_label.grid(row = 6, sticky=W)
    entry_epwfile = Entry(maincontrol_frame, background="white", state='disabled')
    entry_epwfile.grid(row=6, column=1)
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
        a=2
        
    def selHSAT():
        a=2

    def selcumulativeSky():
        rad1_timecontrol.config(state='normal')
        rad2_timecontrol.config(state='normal')
        rad3_timecontrol.config(state='disabled')
        rad4_timecontrol.config(state='disabled')

        #2DO: How to make sure one of the gendaylit options is not selected when doing gencumsky?
        #if self.rb_timecontrol == 3 or self.rb_timecontrol == 4:
         #   self.rb_timecontrol = 1
        
    def selGendaylitSky():
        rad1_timecontrol.config(state='normal')
        rad2_timecontrol.config(state='normal')
        rad3_timecontrol.config(state='normal')
        rad4_timecontrol.config(state='normal')

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
    rad1_fixedortracking = Radiobutton(simulationcontrol_frame,bg='lavender', variable=rb_fixedortracking, indicatoron = 0, width = 15 , text='Fixed', value=0, command=selfixed)
    rad2_fixedortracking = Radiobutton(simulationcontrol_frame,bg='lavender', variable=rb_fixedortracking, indicatoron = 0, width = 15, text='HSAT', value=1, command=selHSAT)
    rad1_fixedortracking.grid(column=0, row=1, columnspan=2)
    rad2_fixedortracking.grid(column=2, row=1, columnspan=2)
    rb_cumulativesky=IntVar()
    rad1_cumulativesky = Radiobutton(simulationcontrol_frame,bg='lavender', variable=rb_cumulativesky, indicatoron = 0, width = 15, text='Cumulative Sky', value=0, command=selcumulativeSky)
    rad2_cumulativesky = Radiobutton(simulationcontrol_frame,bg='lavender', variable=rb_cumulativesky, indicatoron = 0, width = 15, text='Gendaylit Sky', value=1, command=selGendaylitSky)
    rad1_cumulativesky.grid(column=0, row=2, pady=10, columnspan=2)
    rad2_cumulativesky.grid(column=2, row=2, pady=10, columnspan=2)
    
    rb_timecontrol=IntVar()
    rad1_timecontrol = Radiobutton(simulationcontrol_frame,bg='lavender', variable=rb_timecontrol, indicatoron = 0, width = 15, text='ALL Year', value=0, command=tcAll)
    rad2_timecontrol = Radiobutton(simulationcontrol_frame,bg='lavender', variable=rb_timecontrol, indicatoron = 0, width = 15, text='Start-End date', value=1, command=tcStartEndDate)
    rad3_timecontrol = Radiobutton(simulationcontrol_frame,bg='lavender', variable=rb_timecontrol, indicatoron = 0, width = 15, state='disabled', text='Full Day', value=2, command=tcDayDate)
    rad4_timecontrol = Radiobutton(simulationcontrol_frame,bg='lavender', variable=rb_timecontrol, indicatoron = 0, width = 15, state='disabled', text='By Timestamps', value=3, command=tcTimestamps)
    rad1_timecontrol.grid(column=0, row=3)
    rad2_timecontrol.grid(column=1, row=3)
    rad3_timecontrol.grid(column=2, row=3)
    rad4_timecontrol.grid(column=4, row=3)

    # Time CONTROL
    ###################

    timecontrol_label = Label(timecontrol_frame, text='Time Control', font=("Arial Bold", 15))
    timecontrol_label.grid(row = 0, columnspan=2, sticky=W)
    startdate_label = Label(timecontrol_frame, state='disabled', bg='lavender', text='StartDate ( MM | DD | HH ):')
    startdate_label.grid(row = 1, column=0)
    entry_startdate_month = Entry(timecontrol_frame, width = 4, state='disabled', background="white")
    entry_startdate_month.grid(row=1, column=1)
    entry_startdate_day = Entry(timecontrol_frame, width = 4, state='disabled', background="white")
    entry_startdate_day.grid(row=1, column=2)
    entry_startdate_hour = Entry(timecontrol_frame, width = 4, state='disabled', background="white")
    entry_startdate_hour.grid(row=1, column=3)

    enddate_label = Label(timecontrol_frame, state='disabled',  bg='lavender', text='Enddate ( MM | DD | HH ):')
    enddate_label.grid(row= 2, column=0)
    entry_enddate_month = Entry(timecontrol_frame, width = 4, state='disabled', background="white")
    entry_enddate_month.grid(row=2, column=1)
    entry_enddate_day = Entry(timecontrol_frame, width = 4, state='disabled', background="white")
    entry_enddate_day.grid(row=2, column=2)
    entry_enddate_hour = Entry(timecontrol_frame, width = 4, state='disabled', background="white")
    entry_enddate_hour.grid(row=2, column=3)        

    timestampstart_label = Label(timecontrol_frame, state='disabled', bg='lavender', text='Timestamp Start:')
    timestampstart_label.grid(row=3, column=0)
    entry_timestampstart = Entry(timecontrol_frame, state='disabled', background="white")
    entry_timestampstart.grid(row=3, column=1, columnspan=3)
    
    timestampend_label = Label(timecontrol_frame, state='disabled', bg='lavender', text='Timestamp End:')
    timestampend_label.grid(row= 4, column=0)
    entry_timestampend = Entry(timecontrol_frame, state='disabled',  background="white")
    entry_timestampend.grid(row=4, column=1, columnspan=3)

    # Tracking Parameters
    ###################
    trackingcontrol_label = Label(trackingparams_frame, text='Tracking Parameters', font=("Arial Bold", 15))
    trackingcontrol_label.grid(row = 0, columnspan=2, sticky=W)
    backtrack_label = Label(trackingparams_frame, state='disabled', bg='lavender', text='Backtrack:')
    backtrack_label.grid(row=1, column=0,  sticky = W)
    rb_backtrack=IntVar()
    rad1_backtrack = Radiobutton(trackingparams_frame,bg='lavender', variable=rb_backtrack, text='True', value=0)
    rad2_backtrack = Radiobutton(trackingparams_frame,bg='lavender', variable=rb_backtrack, text='False', value=1)
    rad1_backtrack.grid(column=1, row=1,  sticky = W)
    rad2_backtrack.grid(column=2, row=1,  sticky = W)
    limitangle_label = Label(trackingparams_frame, state='disabled', bg='lavender', text='Limit Angle (deg):')
    limitangle_label.grid(row=2, column=0, sticky = W)
    entry_limitangle = Entry(trackingparams_frame, state='disabled', background="white")
    entry_limitangle.grid(row=2, column=1, columnspan=2, sticky = W)
    roundtrackerangle_label = Label(trackingparams_frame, state='disabled', bg='lavender', text='Round Tracker Angle:')
    roundtrackerangle_label.grid(row=3, column=0,  sticky = W)
    rb_roundtrackerangle=IntVar()
    rad1_roundtrackerangle = Radiobutton(trackingparams_frame,bg='lavender', variable=rb_roundtrackerangle, text='True', value=0)
    rad2_roundtrackerangle = Radiobutton(trackingparams_frame,bg='lavender', variable=rb_roundtrackerangle, text='False', value=1)
    rad1_roundtrackerangle.grid(column=1, row=3,  sticky = W)
    rad2_roundtrackerangle.grid(column=2, row=3,  sticky = W)    
    angledelta_label = Label(trackingparams_frame, state='disabled', bg='lavender', text='Angle delta (deg):')
    angledelta_label.grid(row=4, column=0,  sticky = W)
    entry_angledelta = Entry(trackingparams_frame, state='disabled', background="white")
    entry_angledelta.grid(row=4, column=1, columnspan=2)
    
    # TorqueTube Parameters
    ###################
    torquetubecontrol_label = Label(torquetubeparams_frame, text='TorqueTube Parameters', font=("Arial Bold", 15))
    torquetubecontrol_label.grid(row = 0, columnspan=3, sticky=W)
    torqueTube_label = Label(torquetubeparams_frame, state='disabled', bg='lavender', text='TorqueTube:')
    torqueTube_label.grid(row=1, column=0,  sticky = W)
    rb_torqueTube=IntVar()
    rad1_torqueTube = Radiobutton(torquetubeparams_frame,bg='lavender', indicatoron = 0, width = 10,  variable=rb_torqueTube, text='True', value=0)
    rad2_torqueTube = Radiobutton(torquetubeparams_frame,bg='lavender', indicatoron = 0, width = 10,  variable=rb_torqueTube, text='False', value=1)
    rad1_torqueTube.grid(column=1, row=1,  sticky = W)
    rad2_torqueTube.grid(column=2, row=1,  sticky = W)
    diameter_label = Label(torquetubeparams_frame, state='disabled', bg='lavender', text='Diameter:')
    diameter_label.grid(row=2, column=0, sticky = W)
    entry_diameter = Entry(torquetubeparams_frame,  width = 12, state='disabled', background="white")
    entry_diameter.grid(row=2, column=1,  sticky = W)
    tubeType_label = Label(torquetubeparams_frame, state='disabled', bg='lavender', text='Tube type:')
    tubeType_label.grid(row=3, column=0,  sticky = W)
    rb_tubeType=IntVar()
    rad1_tubeType = Radiobutton(torquetubeparams_frame,bg='lavender',  variable=rb_tubeType, text='Round', value=0)
    rad2_tubeType = Radiobutton(torquetubeparams_frame,bg='lavender',   variable=rb_tubeType, text='Square', value=1)
    rad3_tubeType = Radiobutton(torquetubeparams_frame,bg='lavender', width = 5,   variable=rb_tubeType, text='Hex', value=2)
    rad4_tubeType = Radiobutton(torquetubeparams_frame,bg='lavender', width = 5,  variable=rb_tubeType, text='Oct', value=3)
    rad1_tubeType.grid(column=1, row=3,  sticky = W)
    rad2_tubeType.grid(column=2, row=3,  sticky = W)
    rad3_tubeType.grid(column=3, row=3,  sticky = W)    
    rad4_tubeType.grid(column=4, row=3,  sticky = W)
    rb_torqueTubeMaterial=IntVar()
    torqueTubeMaterial_label = Label(torquetubeparams_frame, state='disabled', bg='lavender', text='TorqueTube Material:')
    torqueTubeMaterial_label.grid(column=0, row=4,  sticky = W)
    rad1_torqueTubeMaterial = Radiobutton(torquetubeparams_frame,bg='lavender',  variable=rb_torqueTubeMaterial, text='Metal_Grey', value=0)
    rad2_torqueTubeMaterial = Radiobutton(torquetubeparams_frame,bg='lavender',  variable=rb_torqueTubeMaterial, text='Black', value=1)
    rad1_torqueTubeMaterial.grid(column=1, row = 4, sticky = W)
    rad2_torqueTubeMaterial.grid(column=2, row = 4, sticky = W)

    
    mainloop()
            
if __name__ == "__main__":
    '''
    Example of how to run a Radiance routine for a simple rooftop bifacial system

    '''

    interactive_values()
        
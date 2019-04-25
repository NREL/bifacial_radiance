# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 14:56:38 2019

@author: sayala
"""



demo = demo



import ConfigParser

config = ConfigParser.ConfigParser()
config.read("config.ini")
testfolder = config.get("simulationParamsDict", "testfolder")
moduletype = config.get("simulationParamsDict", "moduletype")
hpc = boolean(config.get("simulationParamsDict", "hpc"))

# Check for basic sections or break.
config.has_section("simulationParamsDict") 
config.has_section("timeControlParamsDict")

if config.has_option("simulationParamsDict", "custommodule"):
    if config.has_section("moduleParams"):
        try: 
            testfolder = config.get("simulationParamsDict", "testfolder"), 
        except: print ("Missing x in moduleParams")
    else:
        print ("No Module Parameters and Custom Module OPtion chosen.")
        print ("Set custom module to False and use a type of module in Json")
        readmodule (name=None) # print availablem odule types.
        
testfolder = config.get("simulationParamsDict", "testfolder")
config.has_section("timeControlParamsDict") 

if c
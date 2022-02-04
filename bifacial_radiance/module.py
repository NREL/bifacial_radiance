# -*- coding: utf-8 -*-
"""
@author: cdeline

ModuleObj class for defining module geometry

"""
import os
import numpy as np

from bifacial_radiance.main import _missingKeyWarning, _popen, DATA_PATH
 
class SuperClass:
    def __repr__(self):
        return str(self.getDataDict())
    def getDataDict(self):
        """
        return dictionary values from self.  Originally stored as self.data
        """
        return dict(zip(self.keys,[getattr(self,k) for k in self.keys]))   

class ModuleObj(SuperClass):
    """
    Module object to store module & torque tube details.  
    Does the heavy lifting of demo.makeModule()
    Module details are passed in and stored in module.json.
    Pass this object into makeScene or makeScene1axis.
    """

    
    def __init__(self, name=None, x=None, y=None, z=None, bifi=1, modulefile=None, 
                 text=None, customtext='', xgap=0.01, ygap=0.0, zgap=0.1,
                 numpanels=1, rewriteModulefile=True, cellModule=None,  
                 glass=False, modulematerial='black', tubeParams=None,
                 frameParams=None, omegaParams=None, hpc=False):
        """
        Add module details to the .JSON module config file module.json

        Module definitions assume that the module .rad file is defined
        with zero tilt, centered along the x-axis and y-axis for the center
        of rotation of the module (+X/2, -X/2, +Y/2, -Y/2 on each side).
        Tip: to define a module that is in 'portrait' mode, y > x. 

        Parameters
        ------------
        name : str
            Input to name the module type
        x : numeric
            Width of module along the axis of the torque tube or rack. (meters)
        y : numeric
            Length of module (meters)
        bifi : numeric
            Bifaciality of the panel (not currently used). Between 0 (monofacial) 
            and 1, default 1.
        modulefile : str
            Existing radfile location in \objects.  Otherwise a default value is used
        text : str
            Text used in the radfile to generate the module
        customtext : str
            Added-text used in the radfile to generate any
            extra details in the racking/module. Does not overwrite
            generated module (unlike "text"), but adds to it at the end.
        rewriteModulefile : bool
            Default True. Will rewrite module file each time makeModule is run.

        numpanels : int
            Number of modules arrayed in the Y-direction. e.g.
            1-up or 2-up, etc. (supports any number for carport/Mesa simulations)
        xgap : float
            Panel space in X direction. Separation between modules in a row.
        ygap : float
            Gap between modules arrayed in the Y-direction if any.
        zgap : float
            Distance behind the modules in the z-direction to the edge of the tube (m)
        cellModule : dict
            Dictionary with input parameters for creating a cell-level module.
            Shortcut for ModuleObj.addCellModule()
        tubeParams : dict
            Dictionary with input parameters for creating a torque tube as part of the 
            module. Shortcut for ModuleObj.addTorquetube()
        frameParams : dict
            Dictionary with input parameters for creating a frame as part of the module.
            Shortcut for ModuleObj.addFrame()
        omegaParams : dict
            Dictionary with input parameters for creating a omega or module support 
            structure. Shortcut for ModuleObj.addOmega()
        hpc         : bool (default False)
            Set up module in HPC mode.  Namely turn off read/write to module.json
            and just pass along the details in the module object. Note that 
            calling e.g. addTorquetube() after this will tend to write to the
            module.json so pass all geometry parameters at once in to makeModule
            for best response.
        
        
        '"""
        self.keys = ['x', 'y', 'z', 'modulematerial', 'scenex','sceney',
            'scenez','numpanels','bifi','text','modulefile', 'glass',
            'offsetfromaxis','xgap','ygap','zgap' ] 
        
        #replace whitespace with underlines. what about \n and other weird characters?
        # TODO: Address above comment?        
        self.name = str(name).strip().replace(' ', '_') 
        self.customtext = customtext
        
        # are we writing to JSON with passed data or just reading existing?
        if (x is None) & (y is None) & (cellModule is None):
            #just read in file. If .rad file doesn't exist, make it.
            self.readModule(name=name)
            if name is not None:
                self._saveModule(savedata=None, json=False, 
                                 rewriteModulefile=False)

        else:
            # set initial variables that aren't passed in 
            scenex = sceney = scenez = offsetfromaxis = 0
            """
            # TODO: this is kind of confusing and should probably be changed
            # set torque tube internal dictionary
            tubeBool = torquetube
            torquetube = {'bool':tubeBool,
                          'diameter':tubeParams['diameter'],
                          'tubetype':tubeParams['tubetype'],
                          'material':tubeParams['material']
                          }   
            try:
                self.axisofrotationTorqueTube = tubeParams['axisofrotation']
            except AttributeError:
                self.axisofrotationTorqueTube = False
            """
            if tubeParams:
                if 'bool' in tubeParams:  # backward compatible with pre-0.4
                    tubeParams['visible'] = tubeParams.pop('bool')
                if 'torqueTubeMaterial' in tubeParams:  #  pre-0.4
                    tubeParams['material'] = tubeParams.pop('torqueTubeMaterial')
                self.addTorquetube(**tubeParams, recompile=False)
            if omegaParams:
                self.addOmega(**omegaParams, recompile=False)
                
            if frameParams:
                self.addFrame(**frameParams, recompile=False)
                
            if cellModule:
                self.addCellModule(**cellModule, recompile=False)
            
            # set data object attributes from datakey list. 
            for key in self.keys:
                setattr(self, key, eval(key))      
            
            if self.modulefile is None:
                self.modulefile = os.path.join('objects',
                                                       self.name + '.rad')
                print("\nModule Name:", self.name)
                  
            if hpc:
                self.compileText(rewriteModulefile, json=False)
            else:
                self.compileText(rewriteModulefile)
            
    def compileText(self, rewriteModulefile=True, json=True):
        """
        Generate the text for the module .rad file based on ModuleObj attributes.
        Optionally save details to the module.json and module.rad files.

        Parameters
        ------------
        rewriteModulefile : bool (default True)
            Overwrite the .rad file for the module
        json : bool  (default True)
            Update the module.json file with ModuleObj attributes
        """
        saveDict = self.getDataDict()

        if hasattr(self,'cellModule'):
            saveDict = {**saveDict, 'cellModule':self.cellModule.getDataDict()}
        if hasattr(self,'torquetube'):
            saveDict = {**saveDict, 'torquetube':self.torquetube.getDataDict()}
        if hasattr(self,'omega'):
            saveDict = {**saveDict, 'omegaParams':self.omega.getDataDict()}
        if hasattr(self,'frame'):
            saveDict = {**saveDict, 'frameParams':self.frame.getDataDict()}            
        self._makeModuleFromDict(**saveDict)  

        #write JSON data out and write radfile if it doesn't exist
        self._saveModule({**saveDict, **self.getDataDict()}, json=json, 
                         rewriteModulefile=rewriteModulefile)

            
    def readModule(self, name=None):
        """
        Read in available modules in module.json.  If a specific module name is
        passed, return those details into the SceneObj. Otherwise 
        return available module list.

        Parameters:  name (str)  Name of module to be read

        Returns:  moduleDict dictionary or list of modulenames if name is not passed in.

        """
        import json
        filedir = os.path.join(DATA_PATH,'module.json')
        with open( filedir ) as configfile:
            data = json.load(configfile)

        modulenames = data.keys()
        if name is None:
            return list(modulenames)

        if name in modulenames:
            moduleDict = data[name]
            self.name = name
            # BACKWARDS COMPATIBILITY - look for missing keys
            if not 'scenex' in moduleDict:
                moduleDict['scenex'] = moduleDict['x']
            if not 'sceney' in moduleDict:
                moduleDict['sceney'] = moduleDict['y']
            if not 'offsetfromaxis' in moduleDict:
                moduleDict['offsetfromaxis'] = 0
            if not 'modulematerial' in moduleDict:
                moduleDict['modulematerial'] = 'black'
            if not 'glass' in moduleDict:
                moduleDict['glass'] = False    
            if not 'z' in moduleDict:
                moduleDict['z'] = 0.02
            # set ModuleObj attributes from moduleDict
            #self.data = moduleDict
            for keys in moduleDict:
                setattr(self, keys, moduleDict[keys])
            
            # Run torquetube, frame, omega, cellmodule
            if moduleDict.get('torquetube'):
                tubeParams = moduleDict['torquetube']
                if 'bool' in tubeParams:  # backward compatible with pre-0.4
                    tubeParams['visible'] = tubeParams.pop('bool')
                if 'torqueTubeMaterial' in tubeParams:  #  pre-0.4
                    tubeParams['material'] = tubeParams.pop('torqueTubeMaterial')
                self.addTorquetube(**tubeParams, recompile=False)
            if moduleDict.get('cellModule'):
                self.addCellModule(**moduleDict['cellModule'], recompile=False)
            if moduleDict.get('omegaParams'):
                self.addOmega(**moduleDict['omegaParams'], recompile=False) 
            if moduleDict.get('frameParams'):
                self.addFrame(**moduleDict['frameParams'], recompile=False) 
            
            
            return moduleDict
        else:
            print('Error: module name {} doesnt exist'.format(name))
            return {}


    def _saveModule(self, savedata, json=True, rewriteModulefile=True):
        """
        write out changes to module.json and make radfile if it doesn't
        exist.  if rewriteModulefile is true, always overwrite Radfile.

        Parameters
        ----------
        json : bool, default is True.  Save JSON
        rewriteModulefile : bool, default is True.

        """
        import json as jsonmodule
        
        if json:
            filedir = os.path.join(DATA_PATH, 'module.json') 
            with open(filedir) as configfile:
                data = jsonmodule.load(configfile)
    
            data.update({self.name:savedata})
            with open(os.path.join(DATA_PATH, 'module.json') ,'w') as configfile:
                jsonmodule.dump(data, configfile, indent=4, sort_keys=True, 
                                cls=MyEncoder)
    
            print('Module {} updated in module.json'.format(self.name))
        
        if rewriteModulefile & os.path.isfile(self.modulefile):
            print(f"Pre-existing .rad file {self.modulefile} "
                  "will be overwritten\n")
            os.remove(self.modulefile)
            
        if not os.path.isfile(self.modulefile):
            # py2 and 3 compatible: binary write, encode text first
            with open(self.modulefile, 'wb') as f:
                f.write(self.text.encode('ascii'))
            
    def showModule(self):
        """ 
        Method to call objview and render the module object 
        (visualize it).
        
        Parameters: None

        """
       
        cmd = 'objview %s %s' % (os.path.join('materials', 'ground.rad'),
                                         self.modulefile)
        _,err = _popen(cmd,None)
        if err is not None:
            print('Error: {}'.format(err))
            print('possible solution: install radwinexe binary package from '
                  'http://www.jaloxa.eu/resources/radiance/radwinexe.shtml'
                  ' into your RADIANCE binaries path')
            return 

    def addTorquetube(self, diameter=0.1, tubetype='Round', material='Metal_Grey', 
                      axisofrotation=True, visible=True,  recompile=True):
        """
        For adding torque tubes to the module simulation. 
        
        Parameters
        ----------
        diameter : float   Tube diameter in meters. For square, diameter means 
                           the length of one of the square-tube side.  For Hex, 
                           diameter is the distance between two vertices 
                           (diameter of the circumscribing circle). Default 0.1
        tubetype : str     Options: 'Square', 'Round' (default), 'Hex' or 'Oct'
                           Tube cross section
        material : str     Options: 'Metal_Grey' or 'black'. Material for the 
                           torque tube.
        axisofrotation     (bool) :  Default True. IF true, creates geometry
                           so center of rotation is at the center of the 
                           torquetube, with an offsetfromaxis equal to half the
                           torquetube diameter + the zgap. If there is no 
                           torquetube (visible=False), offsetformaxis will 
                           equal the zgap.
        visible            (bool) :  Default True. If false, geometry is set
                           as if the torque tube were present (e.g. zgap, 
                           axisofrotation) but no geometry for the tube is made
        recompile : Bool          Rewrite .rad file and module.json file (default True)

        """
        self.torquetube = Tube(diameter=diameter, tubetype=tubetype,
                           material=material, axisofrotation=axisofrotation,
                           visible=visible)
        if recompile:
            self.compileText()


    def addOmega(self, omega_material='Metal_Grey', omega_thickness=0.004,
                 inverted=False, x_omega1=None, x_omega3=None, y_omega=None,
                 mod_overlap=None, recompile=True):
        """
        Add the racking structure element `omega`, which connects 
        the frame to the torque tube. 


        Parameters
        ----------

        omega_material : str      The material the omega structure is made of.
                                  Default: 'Metal_Grey'
        x_omega1  : float         The length of the module-adjacent arm of the 
                                  omega parallel to the x-axis of the module
        mod_overlap : float       The length of the overlap between omega and 
                                  module surface on the x-direction
        y_omega  : float          Length of omega (Y-direction)
        omega_thickness : float   Omega thickness. Default 0.004
        x_omega3  : float         X-direction length of the torquetube adjacent 
                                  arm of omega
        inverted : Bool           Modifies the way the Omega is set on the Torquetbue
                                  Looks like False: u  vs True: n  (default False)
                                  NOTE: The part that bridges the x-gap for a False
                                  regular orientation omega (inverted = False),
                                  is the x_omega3;
                                  and for inverted omegas (inverted=True) it is
                                  x_omega1.
        recompile : Bool          Rewrite .rad file and module.json file (default True)

        """
        self.omega = Omega(self, omega_material=omega_material,
                           omega_thickness=omega_thickness,
                           inverted=inverted, x_omega1=x_omega1,
                           x_omega3=x_omega3, y_omega=y_omega, 
                           mod_overlap=mod_overlap)
        if recompile:
            self.compileText()

    def addFrame(self, frame_material='Metal_Grey', frame_thickness=0.05, 
                 frame_z=0.3, nSides_frame=4, frame_width=0.05, recompile=True):
        """
        Add a metal frame geometry around the module.
        
        Parameters
        ------------

        frame_material : str    The material the frame structure is made of
        frame_thickness : float The profile thickness of the frame 
        frame_z : float         The Z-direction length of the frame that extends 
                                below the module plane
        frame_width : float     The length of the bottom frame that is bolted 
                                with the omega
        nSides_frame : int      The number of sides of the module that are framed.
                                4 (default) or 2

        """
        
        self.frame = Frame(frame_material=frame_material,
                   frame_thickness=frame_thickness,
                   frame_z=frame_z, nSides_frame=nSides_frame,
                   frame_width=frame_width)
        if recompile:
            self.compileText()
            
    def addCellModule(self, numcellsx, numcellsy ,xcell, ycell,
                      xcellgap=0.02, ycellgap=0.02, centerJB=None, recompile=True):
        """
        Create a cell-level module, with individually defined cells and gaps
        
        Parameters
        ------------
        numcellsx : int    Number of cells in the X-direction within the module
        numcellsy : int    Number of cells in the Y-direction within the module
        xcell : float      Width of each cell (X-direction) in the module
        ycell : float      Length of each cell (Y-direction) in the module
        xcellgap : float   Spacing between cells in the X-direction. 0.02 default
        ycellgap : float   Spacing between cells in the Y-direction. 0.02 default
        centerJB : float   (optional) Distance betwen both sides of cell arrays 
                           in a center-JB half-cell module. If 0 or not provided,
                           module will not have the center JB spacing. 
                           Only implemented for 'portrait' mode at the moment.
                           (numcellsy > numcellsx). 
        

        """
        import warnings
        if centerJB:
            warnings.warn(
                'centerJB functionality is currently experimental and subject '
                'to change in future releases. ' )
            
        
        self.cellModule = CellModule(numcellsx=numcellsx, numcellsy=numcellsy,
                                     xcell=xcell, ycell=ycell, xcellgap=xcellgap,
                                     ycellgap=ycellgap, centerJB=centerJB)
                                     
        if recompile:
            self.compileText()
    

    
    def _makeModuleFromDict(self,  x=None, y=None, z=None, xgap=None, ygap=None, 
                    zgap=None, numpanels=None, modulefile=None,
                    modulematerial=None, **kwargs):

        """
        go through and generate the text required to make a module
        """

        #aliases for equations below
        Ny = numpanels
        _cc = 0  # cc is an offset given to the module when cells are used
                  # so that the sensors don't fall in air when numcells is even.
                  # For non cell-level modules default is 0.
        # Update values for rotating system around torque tube.  
        diam=0
        if hasattr(self, 'torquetube'):
            diam = self.torquetube.diameter
            if self.torquetube.axisofrotation is True:
                self.offsetfromaxis = np.round(zgap + diam/2.0,8)
            if hasattr(self, 'frame'):
                self.offsetfromaxis = self.offsetfromaxis + self.frame.frame_z
        # TODO: make sure the above is consistent with old version below
        """
        if torquetube:
            diam = torquetube['diameter']
            torquetube_bool = torquetube['bool']
        else:
            diam=0
            torquetube_bool = False
        if self.axisofrotationTorqueTube == True:
            if torquetube_bool == True:
                self.offsetfromaxis = np.round(zgap + diam/2.0,8)
            else:
                self.offsetfromaxis = zgap
            if hasattr(self, 'frame'):
                self.offsetfromaxis = self.offsetfromaxis + self.frame.frame_z
        """
        # Adding the option to replace the module thickess
        if self.glass:
            zglass = 0.01
        else:
            zglass = 0.0
            
        if z is None:
            if self.glass:
                z = 0.001
            else:
                z = 0.020
                
        self.z = z
        self.zglass = zglass

            
        if modulematerial is None:
            modulematerial = 'black'
            self.modulematerial = 'black'
            
        if hasattr(self, 'cellModule'):
            (text, x, y, _cc) = self.cellModule._makeCellLevelModule(self, z, Ny, ygap, 
                                   modulematerial) 
        else:
            try:
                text = '! genbox {} {} {} {} {} '.format(modulematerial, 
                                                          self.name, x, y, z)
                text +='| xform -t {} {} {} '.format(-x/2.0,
                                        (-y*Ny/2.0)-(ygap*(Ny-1)/2.0),
                                        self.offsetfromaxis)
                text += '-a {} -t 0 {} 0'.format(Ny, y+ygap)
                packagingfactor = 100.0

            except Exception as err: # probably because no x or y passed
                raise Exception('makeModule variable {}'.format(err.args[0])+
                                ' and cellModule is None.  '+
                                'One or the other must be specified.')
 
            
        self.scenex = x + xgap
        self.sceney = np.round(y*numpanels + ygap*(numpanels-1), 8)
        self.scenez = np.round(zgap + diam / 2.0, 8)
        

        if hasattr(self, 'frame'):
            _zinc, frametext = self.frame._makeFrames( 
                                    x=x,y=y, ygap=ygap,numpanels=Ny, 
                                    offsetfromaxis=self.offsetfromaxis- 0.5*zglass)
        else:
            frametext = ''
            _zinc = 0  # z increment from frame thickness 
        _zinc = _zinc + 0.5 * zglass
            
        if hasattr(self, 'omega'):
            # This also defines scenex for length of the torquetube.
            omega2omega_x, omegatext = self.omega._makeOmega(x=x,y=y, xgap=xgap,  
                                            zgap=zgap, z_inc=_zinc, 
                                            offsetfromaxis=self.offsetfromaxis)
            if omega2omega_x > self.scenex:
                self.scenex =  omega2omega_x
            
            # TODO: is the above line better than below?
            #       I think this causes it's own set of problems, need to check.
            """
            if self.scenex <x:
                scenex = x+xgap #overwriting scenex to maintain torquetube continuity
        
                print ('Warning: Omega values have been provided, but' +
                       'the distance between modules with the omega'+
                       'does not match the x-gap provided.'+
                       'Setting x-gap to be the space between modules'+
                       'from the omega.')
            else:
                print ('Warning: Using omega-to-omega distance to define'+
                       'gap between modules'
                       +'xgap value not being used')
            """
        else:
            omegatext = ''
        
        # Defining scenex if it was not defined by the Omegas, 
        # after the module has been created in case it is a 
        # cell-level Module, in which the "x" gets calculated internally.
        # Also sanity check in case omega-to-omega distance is smaller
        # than module.

        #if torquetube_bool is True:
        if hasattr(self,'torquetube'):
            if self.torquetube.visible:
                text += self.torquetube._makeTorqueTube(cc=_cc, zgap=zgap,   
                                         z_inc=_zinc, scenex=self.scenex)

        # TODO:  should there be anything updated here like scenez?
        #        YES.
        if self.glass: 
                edge = 0.01                     
                text = text+'\r\n! genbox stock_glass {} {} {} {} '.format(self.name+'_Glass',x+edge, y+edge, zglass)
                text +='| xform -t {} {} {} '.format(-x/2.0-0.5*edge + _cc,
                                        (-y*Ny/2.0)-(ygap*(Ny-1)/2.0)-0.5*edge,
                                        self.offsetfromaxis - 0.5*zglass)
                text += '-a {} -t 0 {} 0'.format(Ny, y+ygap)
            

        text += frametext
        if hasattr(self, 'omega'):
            text += self.omega.text    
        text += self.customtext  # For adding any other racking details at the module level that the user might want.

        self.text = text
        return text
    #End of makeModuleFromDict()
  
# end of ModuleObj



class Omega(SuperClass):

    def __init__(self, module, omega_material='Metal_Grey', omega_thickness=0.004,
                 inverted=False, x_omega1=None, x_omega3=None, y_omega=None,
                 mod_overlap=None):
        """
        ====================    ===============================================
        Keys : type             Description
        ================        =============================================== 
        module : ModuleObj      Parent object with details related to geometry
        omega_material : str    The material the omega structure is made of
        omega_thickness : float Omega thickness
        inverted : Bool         Modifies the way the Omega is set on the Torquetbue
                                Looks like False: u  vs True: n  (default False)
        x_omega1  : float       The length of the module-adjacent arm of the 
                                omega parallel to the x-axis of the module
        y_omega  : float         Length of omega (Y-direction)
        x_omega3  : float       X-direction length of the torquetube adjacent 
                                arm of omega
        mod_overlap : float     The length of the overlap between omega and 
                                module surface on the x-direction

        =====================   ===============================================

        """
        self.keys = ['omega_material', 'x_omega1', 'mod_overlap', 'y_omega', 
            'omega_thickness','x_omega3','inverted']

        if x_omega1 is None:
            if inverted:
                x_omega1 = module.xgap*0.5
            else:
                x_omega1 = module.xgap*0.5*0.6
            _missingKeyWarning('Omega', 'x_omega1', x_omega1)
                
        if x_omega3 is None:
            if inverted:
                x_omega3 = module.xgap*0.5*0.3
            else:
                x_omega3 = module.xgap*0.5
            _missingKeyWarning('Omega', 'x_omega3', x_omega3)
            
        if y_omega is None:
            y_omega = module.y/2
            _missingKeyWarning('Omega', 'y_omega', y_omega)
        
        if mod_overlap is None:
           mod_overlap = x_omega1*0.6
           _missingKeyWarning('Omega', 'mod_overlap', mod_overlap)

        # set data object attributes from datakey list. 
        for key in self.keys:
            setattr(self, key, eval(key))        

        
        
    def _makeOmega(self, x, y, xgap, zgap, offsetfromaxis, z_inc = 0, **kwargs):
        """
        Helper function for creating a module that includes the racking 
        structure element `omega`.  

        TODO: remove some or all of this documentation since this is an internal function    
        
        Parameters
        ------------
        x : numeric
            Width of module along the axis of the torque tube or racking structure. (meters).
        y : numeric
            Length of module (meters)
        xgap : float
            Panel space in X direction. Separation between modules in a row.
        zgap : float
            Distance behind the modules in the z-direction to the edge of the tube (m)
        offsetfromaxis : float
            Internally defined variable in makeModule that specifies how much
            the module is offset from the Axis of Rotation due to zgap and or 
            frame thickness.
        z_inc : dict
            Internally defined variable in makeModule that specifies how much
            the module is offseted by the Frame.
        
        """
        
        # set local variables
        omega_material = self.omega_material
        x_omega1 = self.x_omega1
        mod_overlap = self.mod_overlap
        y_omega = self.y_omega
        omega_thickness = self.omega_thickness
        x_omega3 = self.x_omega3

        
        z_omega2 = zgap
        x_omega2 = omega_thickness 
        z_omega1 = omega_thickness
        z_omega3 = omega_thickness
        
        #naming the omega pieces
        name1 = 'mod_adj'
        name2 = 'verti'
        name3 = 'tt_adj'
        
        
        # defining the module adjacent member of omega
        x_translate1 = -x/2 - x_omega1 + mod_overlap
        y_translate = -y_omega/2 #common for all the pieces
        z_translate1 = offsetfromaxis-z_omega1
        
        #defining the vertical (zgap) member of the omega
        x_translate2 = x_translate1
        z_translate2 = offsetfromaxis-z_omega2
            
        #defining the torquetube adjacent member of omega
        x_translate3 = x_translate1-x_omega3
        z_translate3 = z_translate2
        
        if z_inc != 0: 
            z_translate1 += -z_inc
            z_translate2 += -z_inc
            z_translate3 += -z_inc
        
        # for this code, only the translations need to be shifted for the inverted omega
        
        if self.inverted == True:
            # shifting the non-inv omega shape of west as inv omega shape of east
            x_translate1_inv_east = x/2-mod_overlap
            x_shift_east = x_translate1_inv_east - x_translate1

            # shifting the non-inv omega shape of west as inv omega shape of east
            x_translate1_inv_west = -x_translate1_inv_east - x_omega1
            x_shift_west = -x_translate1_inv_west + (-x_translate1-x_omega1)
            
            #customizing the East side of the module for omega_inverted

            omegatext = '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name1, x_omega1, y_omega, z_omega1, x_translate1_inv_east, y_translate, z_translate1) 
            omegatext += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name2, x_omega2, y_omega, z_omega2, x_translate2 + x_shift_east, y_translate, z_translate2)
            omegatext += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name3, x_omega3, y_omega, z_omega3, x_translate3 + x_shift_east, y_translate, z_translate3)

            #customizing the West side of the module for omega_inverted

            omegatext += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name1, x_omega1, y_omega, z_omega1, x_translate1_inv_west, y_translate, z_translate1) 
            omegatext += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name2, x_omega2, y_omega, z_omega2, -x_translate2-x_omega2 -x_shift_west, y_translate, z_translate2)
            omegatext += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name3, x_omega3, y_omega, z_omega3, -x_translate3-x_omega3 - x_shift_west, y_translate, z_translate3)
            
            omega2omega_x = -x_translate1_inv_east*2
        
        else:
            
            #customizing the West side of the module for omega
            
            omegatext = '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name1, x_omega1, y_omega, z_omega1, x_translate1, y_translate, z_translate1) 
            omegatext += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name2, x_omega2, y_omega, z_omega2, x_translate2, y_translate, z_translate2)
            omegatext += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name3, x_omega3, y_omega, z_omega3, x_translate3, y_translate, z_translate3)
                
            #customizing the East side of the module for omega
                
            omegatext += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name1, x_omega1, y_omega, z_omega1, -x_translate1-x_omega1, y_translate, z_translate1) 
            omegatext += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name2, x_omega2, y_omega, z_omega2, -x_translate2-x_omega2, y_translate, z_translate2)
            omegatext += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(omega_material, name3, x_omega3, y_omega, z_omega3, -x_translate3-x_omega3, y_translate, z_translate3)
        
            omega2omega_x = -x_translate3*2
        self.text = omegatext
        self.omega2omega_x = omega2omega_x
        return omega2omega_x,omegatext
    
class Frame(SuperClass):

    def __init__(self, frame_material='Metal_Grey', frame_thickness=0.05, 
                 frame_z=None, nSides_frame=4, frame_width=0.05):
        """
        Parameters
        ------------

        frame_material : str    The material the frame structure is made of
        frame_thickness : float The profile thickness of the frame 
        frame_z : float         The Z-direction length of the frame that extends 
                                below the module plane
        frame_width : float     The length of the bottom frame that is bolted 
                                with the omega
        nSides_frame : int      The number of sides of the module that are framed.
                                4 (default) or 2


        """
        self.keys = ['frame_material', 'frame_thickness', 'frame_z', 'frame_width',
            'nSides_frame']
        
        if frame_z is None:
            frame_z = 0.03
            _missingKeyWarning('Frame', 'frame_z', frame_z)
        
        # set data object attributes from datakey list. 
        for key in self.keys:
            setattr(self, key, eval(key))  
        
    def _makeFrames(self,  x, y, ygap, numpanels, offsetfromaxis):
        """
        Helper function for creating a module that includes the frames attached to the module, 

            
        Parameters
        ------------
        frameParams : dict
            Dictionary with input parameters for creating a frame as part of the module.
            See details below for keys needed.
        x : numeric
            Width of module along the axis of the torque tube or racking structure. (meters).
        y : numeric
            Length of module (meters)
        ygap : float
            Gap between modules arrayed in the Y-direction if any.
        numpanels : int
            Number of modules arrayed in the Y-direction. e.g.
            1-up or 2-up, etc. (supports any number for carport/Mesa simulations)
        offsetfromaxis : float
            Internally defined variable in makeModule that specifies how much
            the module is offset from the Axis of Rotation due to zgap and or 
            frame thickness.


        """
        
        # 
        if self.nSides_frame == 2 and x>y:
            print("Development Warning: Frames has only 2 sides and module is"+
                  "in ladscape. This functionality is not working properly yet"+
                  "for this release. We are overwriting nSide_frame = 4 to continue."+
                  "If this functionality is pivotal to you we can prioritize adding it but"+
                  "please comunicate with the development team. Thank you.")
            self.nSides_frame = 4
        
        #Defining internal names
        frame_material = self.frame_material 
        f_thickness = self.frame_thickness 
        f_height = self.frame_z
        n_frame = self.nSides_frame  
        fl_x = self.frame_width

        y_trans_shift = 0 #pertinent to the case of x>y with 2-sided frame
                

        # Recalculating width ignoring the thickness of the aluminum
        # for internal positioining and sizing of hte pieces
        fl_x = fl_x-f_thickness
        
        if x>y and n_frame==2:
            x_temp,y_temp = y,x
            rotframe = 90
            frame_y = x
            y_trans_shift = x/2-y/2
        else:
            x_temp,y_temp = x,y
            frame_y = y
            rotframe = 0
    
        Ny = numpanels
        y_half = (y*Ny/2)+(ygap*(Ny-1)/2)
    
        # taking care of lengths and translation points
        # The pieces are same and symmetrical for west and east
    
        # naming the frame pieces
        nameframe1 = 'frameside'
        nameframe2 = 'frameleg'
        
        #frame sides
        few_x = f_thickness
        few_y = frame_y
        few_z = f_height
    
        fw_xt = -x_temp/2 # in case of x_temp = y this doesn't reach panel edge
        fe_xt = x_temp/2-f_thickness 
        few_yt = -y_half-y_trans_shift
        few_zt = offsetfromaxis-f_height
    
        #frame legs for east-west 
    
        flw_xt = -x_temp/2 + f_thickness
        fle_xt = x_temp/2 - f_thickness-fl_x
        flew_yt = -y_half-y_trans_shift
        flew_zt = offsetfromaxis-f_height
    
    
        #pieces for the shorter side (north-south in this case)
    
        #filler
    
        fns_x = x_temp-2*f_thickness
        fns_y = f_thickness
        fns_z = f_height-f_thickness
    
        fns_xt = -x_temp/2+f_thickness
        fn_yt = -y_half+y-f_thickness
        fs_yt = -y_half
        fns_zt = offsetfromaxis-f_height+f_thickness
    
        # the filler legs
    
        filleg_x = x_temp-2*f_thickness-2*fl_x
        filleg_y = f_thickness + fl_x
        filleg_z = f_thickness
    
        filleg_xt = -x_temp/2+f_thickness+fl_x
        fillegn_yt = -y_half+y-f_thickness-fl_x
        fillegs_yt = -y_half
        filleg_zt = offsetfromaxis-f_height
    
    
        # making frames: west side
        
        
        frame_text = '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(frame_material, nameframe1, few_x, few_y, few_z, fw_xt, few_yt, few_zt) 
        frame_text += ' -a {} -t 0 {} 0 | xform -rz {}'.format(Ny, y_temp+ygap, rotframe)
    
        frame_text += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(frame_material, nameframe2, fl_x, frame_y, f_thickness, flw_xt, flew_yt, flew_zt)
        frame_text += ' -a {} -t 0 {} 0 | xform -rz {}'.format(Ny, y_temp+ygap, rotframe)
                
        # making frames: east side
    
        frame_text += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(frame_material, nameframe1, few_x, few_y, few_z, fe_xt, few_yt, few_zt) 
        frame_text += ' -a {} -t 0 {} 0 | xform -rz {}'.format(Ny, y_temp+ygap, rotframe)
    
        frame_text += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(frame_material, nameframe2, fl_x, frame_y, f_thickness, fle_xt, flew_yt, flew_zt)
        frame_text += ' -a {} -t 0 {} 0 | xform -rz {}'.format(Ny, y_temp+ygap, rotframe)

    
        if n_frame == 4:
            #making frames: north side
    
            frame_text += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(frame_material, nameframe1, fns_x, fns_y, fns_z, fns_xt, fn_yt, fns_zt) 
            frame_text += ' -a {} -t 0 {} 0'.format(Ny, y+ygap)
    
    
            frame_text += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(frame_material, nameframe2, filleg_x, filleg_y, filleg_z, filleg_xt, fillegn_yt, filleg_zt)
            frame_text += ' -a {} -t 0 {} 0'.format(Ny, y+ygap)
    
            #making frames: south side
    
            frame_text += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(frame_material, nameframe1, fns_x, fns_y, fns_z, fns_xt, fs_yt, fns_zt) 
            frame_text += ' -a {} -t 0 {} 0'.format(Ny, y+ygap)
    
            frame_text += '\r\n! genbox {} {} {} {} {} | xform -t {} {} {}'.format(frame_material, nameframe2, filleg_x, filleg_y, filleg_z, filleg_xt, fillegs_yt, filleg_zt)
            frame_text += ' -a {} -t 0 {} 0'.format(Ny, y+ygap)

        z_inc = f_height

        return z_inc, frame_text

class Tube(SuperClass):

    def __init__(self, diameter=0.1, tubetype='Round', material='Metal_Grey', 
                      axisofrotation=True, visible=True):
        """
        ================   ====================================================
        Keys : type        Description
        ================   ====================================================  
        diameter : float   Tube diameter in meters. For square, diameter means 
                           the length of one of the square-tube side.  For Hex, 
                           diameter is the distance between two vertices 
                           (diameter of the circumscribing circle). Default 0.1
        tubetype : str     Options: 'Square', 'Round' (default), 'Hex' or 'Oct'
                           Tube cross section
        material : str     Options: 'Metal_Grey' or 'black'. Material for the 
                           torque tube.
        axisofrotation     (bool) :  Default True. IF true, creates geometry
                           so center of rotation is at the center of the 
                           torquetube, with an offsetfromaxis equal to half the
                           torquetube diameter + the zgap. If there is no 
                           torquetube (visible=False), offsetformaxis will 
                           equal the zgap.
        visible            (bool) :  Default True. If false, geometry is set
                           as if the torque tube were present (e.g. zgap, 
                           axisofrotation) but no geometry for the tube is made
        ================   ==================================================== 
        """
        
        self.keys = ['diameter', 'tubetype', 'material', 'visible']   # what about axisofrotation?
        
        self.axisofrotation = axisofrotation
        # set data object attributes from datakey list. 
        for key in self.keys:
            setattr(self, key, eval(key))    
            
    def _makeTorqueTube(self, cc,  z_inc, zgap, scenex):
        """  
        Return text string for generating the torque tube geometry
        
        Parameters
        
        cc = module._cc #horizontal offset to center of a cell
        """
        import math
        
        
        text = ''
        tto = 0  # Torquetube Offset. Default = 0 if axisofrotationTT == True
        diam = self.diameter  #alias
        material = self.material #alias
        
        if self.tubetype.lower() == 'square':
            if self.axisofrotation == False:
                tto = -z_inc-zgap-diam/2.0
            text += '\r\n! genbox {} tube1 {} {} {} '.format(material,
                                  scenex, diam, diam)
            text += '| xform -t {} {} {}'.format(-(scenex)/2.0+cc,
                                -diam/2.0, -diam/2.0+tto)

        elif self.tubetype.lower() == 'round':
            if self.axisofrotation == False:
                tto = -z_inc-zgap-diam/2.0
            text += '\r\n! genrev {} tube1 t*{} {} '.format(material, scenex, diam/2.0)
            text += '32 | xform -ry 90 -t {} {} {}'.format(-(scenex)/2.0+cc, 0, tto)

        elif self.tubetype.lower() == 'hex':
            radius = 0.5*diam

            if self.axisofrotation == False:
                tto = -z_inc-radius*math.sqrt(3.0)/2.0-zgap

            text += '\r\n! genbox {} hextube1a {} {} {} | xform -t {} {} {}'.format(
                    material, scenex, radius, radius*math.sqrt(3),
                    -(scenex)/2.0+cc, -radius/2.0, -radius*math.sqrt(3.0)/2.0+tto) #ztran -radius*math.sqrt(3.0)-tto


            # Create, translate to center, rotate, translate back to prev. position and translate to overal module position.
            text = text+'\r\n! genbox {} hextube1b {} {} {} | xform -t {} {} {} -rx 60 -t 0 0 {}'.format(
                    material, scenex, radius, radius*math.sqrt(3), -(scenex)/2.0+cc, -radius/2.0, -radius*math.sqrt(3.0)/2.0, tto) #ztran (radius*math.sqrt(3.0)/2.0)-radius*math.sqrt(3.0)-tto)
            
            text = text+'\r\n! genbox {} hextube1c {} {} {} | xform -t {} {} {} -rx -60 -t 0 0 {}'.format(
                    material, scenex, radius, radius*math.sqrt(3), -(scenex)/2.0+cc, -radius/2.0, -radius*math.sqrt(3.0)/2.0, tto) #ztran (radius*math.sqrt(3.0)/2.0)-radius*math.sqrt(3.0)-tto)

        elif self.tubetype.lower()=='oct':
            radius = 0.5*diam
            s = diam / (1+math.sqrt(2.0))   # 

            if self.axisofrotation == False:
                tto = -z_inc-radius-zgap

            text = text+'\r\n! genbox {} octtube1a {} {} {} | xform -t {} {} {}'.format(
                    material, scenex, s, diam, -(scenex)/2.0, -s/2.0, -radius+tto)

            # Create, translate to center, rotate, translate back to prev. position and translate to overal module position.
            text = text+'\r\n! genbox {} octtube1b {} {} {} | xform -t {} {} {} -rx 45 -t 0 0 {}'.format(
                    material, scenex, s, diam, -(scenex)/2.0+cc, -s/2.0, -radius, tto)

            text = text+'\r\n! genbox {} octtube1c {} {} {} | xform -t {} {} {} -rx 90 -t 0 0 {}'.format(
                    material, scenex, s, diam, -(scenex)/2.0+cc, -s/2.0, -radius, tto)

            text = text+'\r\n! genbox {} octtube1d {} {} {} | xform -t {} {} {} -rx 135 -t 0 0 {} '.format(
                    material, scenex, s, diam, -(scenex)/2.0+cc, -s/2.0, -radius, tto)


        else:
            raise Exception("Incorrect torque tube type.  "+
                            "Available options: 'square' 'oct' 'hex' or 'round'."+
                            "  Value entered: {}".format(self.tubetype))    
        self.text = text
        return text
    
class CellModule(SuperClass):

    def __init__(self, numcellsx, numcellsy,
                 xcell, ycell, xcellgap=0.02, ycellgap=0.02, centerJB=None):
        """
        For creating a cell-level module, the following input parameters should 
        be in ``cellModule``:
        
        ================   ====================================================
        Keys : type        Description
        ================   ====================================================  
        numcellsx : int    Number of cells in the X-direction within the module
        numcellsy : int    Number of cells in the Y-direction within the module
        xcell : float      Width of each cell (X-direction) in the module
        ycell : float      Length of each cell (Y-direction) in the module
        xcellgap : float   Spacing between cells in the X-direction. 0.02 default
        ycellgap : float   Spacing between cells in the Y-direction. 0.02 default
        centerJB : float   (optional) Distance betwen both sides of cell arrays 
                           in a center-JB half-cell module. If 0 or not provided,
                           module will not have the center JB spacing. 
                           Only implemented for 'portrait' mode at the moment.
                           (numcellsy > numcellsx). 
        cc : float         center cell offset from x so scan is not at a gap 
                           between cells
        ================   ==================================================== 

        """
        self.keys = ['numcellsx', 'numcellsy', 'xcell', 'ycell', 'xcellgap',
            'ycellgap','centerJB'] 
        
        # set data object attributes from datakey list. 
        for key in self.keys:
            setattr(self, key, eval(key))    
        
    
    def _makeCellLevelModule(self, module, z, Ny, ygap, 
                         modulematerial):
        """  Calculate the .radfile generation text for a cell-level module.
        """
        offsetfromaxis = module.offsetfromaxis
        c = self.getDataDict()

        # For half cell modules with the JB on the center:
        if c['centerJB'] is not None:
            centerJB = c['centerJB']
            y = c['numcellsy']*c['ycell'] + (c['numcellsy']-2)*c['ycellgap'] + centerJB            
        else:
            centerJB = 0
            y = c['numcellsy']*c['ycell'] + (c['numcellsy']-1)*c['ycellgap']

        x = c['numcellsx']*c['xcell'] + (c['numcellsx']-1)*c['xcellgap']

        #center cell -
        if c['numcellsx'] % 2 == 0:
            _cc = c['xcell']/2.0
            print("Module was shifted by {} in X to avoid sensors on air".format(_cc))
        else:
            _cc = 0

        text = '! genbox {} cellPVmodule {} {} {} | '.format(modulematerial,
                                               c['xcell'], c['ycell'], z)
        text +='xform -t {} {} {} '.format(-x/2.0 + _cc,
                         (-y*Ny / 2.0)-(ygap*(Ny-1) / 2.0)-centerJB/2.0,
                         offsetfromaxis)
        
        text += '-a {} -t {} 0 0 '.format(c['numcellsx'], c['xcell'] + c['xcellgap'])
        
        if centerJB != 0:
            trans0 = c['ycell'] + c['ycellgap']
            text += '-a {} -t 0 {} 0 '.format(c['numcellsy']/2, trans0)
            #TODO: Continue playing with the y translation of the array in the next two lines
                 # Until it matches. Close but not there.
            # This is 0 spacing
            #ytrans1 = y/2.0-c['ycell']/2.0-c['ycellgap']+centerJB/2.0   # Creating the 2nd array with the right Jbox distance
            ytrans1 = y/2.0-c['ycell']/2.0-c['ycellgap']+centerJB/2.0 + centerJB
            ytrans2= c['ycell'] - centerJB/2.0 + c['ycellgap']/2.0
            text += '-a {} -t 0 {} 0 '.format(2, ytrans1)  
            text += '| xform -t 0 {} 0 '.format(ytrans2)   

        else:
            text += '-a {} -t 0 {} 0 '.format(c['numcellsy'], c['ycell'] + c['ycellgap'])
            
        text += '-a {} -t 0 {} 0'.format(Ny, y+ygap)

        # OPACITY CALCULATION
        packagingfactor = np.round((c['xcell']*c['ycell']*c['numcellsx']*c['numcellsy'])/(x*y), 2)
        print("This is a Cell-Level detailed module with Packaging "+
              "Factor of {} %".format(packagingfactor)) 
        
        module.x = x
        module.y = y
        self.text = text
        
        return(text, x, y, _cc)    

# deal with Int32 JSON incompatibility
# https://www.programmerall.com/article/57461489186/
import json
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)
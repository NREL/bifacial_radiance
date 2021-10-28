import bifacial_radiance

rad_obj = bifacial_radiance.RadianceObj('makemod', 'TEMP')

moduletype='Prism Solar Bi60 landscape'
numpanels = 1  # This site have 1 module in Y-direction
x = 2
y = 1
zgap = 0.10 # gap to torquetube.
torquetube = True
axisofrotationTorqueTube = True
diameter = 0.15  # 15 cm diameter for the torquetube
tubetype = 'square'    # Put the right keyword upon reading the document
material = 'black'   # Torque tube of this material (0% reflectivity)
xgap = 0.02

rad_obj.makeModule(name=moduletype, x=x, y=y,
            torquetube=torquetube, diameter=diameter, tubetype=tubetype, material=material,
                xgap = 0.02, zgap=zgap, numpanels=numpanels,
                axisofrotationTorqueTube=axisofrotationTorqueTube,
                orientation=None, glass=False, torqueTubeMaterial=None)
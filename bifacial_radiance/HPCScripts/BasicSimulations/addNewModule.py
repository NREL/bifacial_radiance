import bifacial_radiance
import os

testfolder = 'TEMP'

if not os.path.exists(testfolder):
    os.makedirs(testfolder)

rad_obj = bifacial_radiance.RadianceObj('makemod', testfolder)

moduletype='tutorial-module'
x = 2
y = 1

rad_obj.makeModule(name=moduletype, x=x, y=y)

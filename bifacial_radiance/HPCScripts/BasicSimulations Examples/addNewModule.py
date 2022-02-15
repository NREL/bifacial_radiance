import bifacial_radiance

rad_obj = bifacial_radiance.RadianceObj('makemod', 'TEMP')

rad_obj.getEPW(37.42, -110)

moduletype='tutorial-module'
x = 2
y = 1

rad_obj.makeModule(name=moduletype, x=x, y=y)

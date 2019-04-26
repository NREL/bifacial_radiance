#Version 0.2.5b

simulationParamsDict = {'testfolder': r'C:\Users\sayala\Documents\RadianceScenes\Demo',
	'EPWorTMY': 'EPW',
	'tmyfile': r'EPWs\USA_VA_Richmond.Intl.AP.724010_TMY.epw',
	'epwfile': r'EPWs\USA_VA_Richmond.Intl.AP.724010_TMY.epw',
	'getEPW': True,
	'simulationname': 'Demo1',
	'custommodule': True,
	'moduletype': 'Prism Solar Bix60',
	'rewriteModule': True,
	'cellLevelModule': True,
	'axisofrotationTorqueTube': True,
	'torqueTube': True,
	'hpc': False,
	'tracking': False,
	'cumulativeSky': True,
	'timestampRangeSimulation': False,
	'daydateSimulation': False,
	'latitude': 33.0,
	'longitude': -110.0}

timeControlParamsDict = {'HourStart': 5,
	'HourEnd': 20,
	'DayStart': 21,
	'DayEnd': 30,
	'MonthStart': 6,
	'MonthEnd': 6,
	'timeindexstart': 4020,
	'timeindexend': 4024}

moduleParamsDict = {'numpanels': 2,
	'x': 0.98,
	'y': 1.98,
	'bifi': 0.9,
	'xgap': 0.05,
	'ygap': 0.15,
	'zgap': 0.1}

sceneParamsDict = {'gcrorpitch': 'gcr',
	'gcr': 0.35,
	'pitch': 10.0,
	'albedo': 0.62,
	'nMods': 20,
	'nRows': 7,
	'azimuth_ang': 180.0,
	'tilt': 10.0,
	'clearance_height': 0.8,
	'hub_height': 0.9,
	'axis_azimuth': 180.0}

trackingParamsDict = {'backtrack': True,
	'limit_angle': 60.0,
	'angle_delta': 5.0}

torquetubeParamsDict = {'diameter': 0.1,
	'tubetype': 'round',
	'torqueTubeMaterial': 'Metal_Grey'}

analysisParamsDict = {'sensorsy': 9,
	'modWanted': 10,
	'rowWanted': 3}

cellLevelModuleParamsDict = {'numcellsx': 12,
	'numcellsy': 6,
	'xcell': 0.15,
	'ycell': 0.15,
	'xcellgap': 0.01,
	'ycellgap': 0.01}
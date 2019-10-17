#include "cPerezSkyModel.h"
#include "climateFile.h"

/////////////////////////////////////////////
// Check to see if cSkyVault has already been declared
#if (!defined(CSKYVAULT_H))
#define CSKYVAULT_H

class cSkyVault
{
public:
	enum eSunType { NO_SUN, CUMULATIVE_SUN, MANY_SUNS };

	cSkyVault(double latitude=51.7, double longitude=0);
	~cSkyVault(void);

	inline int GetNumberOfPatches() { return m_NumPatches; }

	// updates PREDEFINED array pointed to by PatchDat with locations of sky patches and their sizes
	// length m_NumPatches, 1st element altitude, 2nd azimuth (in rads), 2nd = deltaAlt, 3rd= deltaAz
	void GetPatchDetails(double (*ptPatchDat)[5]);

	// Calculate the sky radiance distribution for the whole year
	void CalculateSky(eSunType Suns=NO_SUN, bool DoDiffuse=true, bool DoIlluminance=false, double hourshift=0);

	bool LoadClimateFile(char *filename, cClimateFile::eClimateFileFormat ClimateFileFormat,double StartTime, double EndTime, int StartDay, int EndDay, int StartMonth, int EndMonth);



	bool SetLatitude(double latitude);
	bool SetLongitude(double longitude);
	bool SetMeridian(double meridian);

	// Temporary function to return the cumulative sky
	double* GetCumulativeSky();

	// start time and date; end time and date
	double StartTime;
	double EndTime;
	int StartDay;
	int EndDay;
	int StartMonth;
	int EndMonth;


private:
	// number of patches in sky
	int m_NumPatches;

	// data for each sky patch
	double *m_ptPatchAlt;
	double *m_ptPatchAz;
	double *m_ptPatchDeltaAlt;
	double *m_ptPatchDeltaAz;
	double *m_ptPatchLuminance;
	double *m_ptPatchSolidAngle;

	// Sky radiances (last element is mean annual radiance)
	// define as float to improve run time (with minimal loss of accuracy)
	float (*m_ptRadiance)[145];

	// The sky luminance model to be used
	cPerezSkyModel m_SkyModel;

	// Climate file containing irradiation data
	cClimateFile m_ClimateFile;

	// Sun object (to handle solar geometry
	cSun m_Sun;

	// Remember whether or not we've already processed the sky
	bool m_SkyCalculated;

	// Cumulative sky
	double *m_CumSky;

	// radians
	double m_latitude;
	double m_longitude;
	double m_meridian;


};

#endif
//////////////////////////////////////////

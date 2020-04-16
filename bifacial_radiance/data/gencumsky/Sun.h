#define _USE_MATH_DEFINES
#include <math.h>
class cSun
{
public:
	cSun (double latitude=54*2*M_PI/360, int day=1, double _hourangle=M_PI/2, double _meridian=0.0); // latitude in radians, day is integer 1-365
	~cSun(void);

	bool SetDay(int day);
	int GetDay() { return int((_day*365/(2*M_PI)) + 1); }

	bool SetLatitude(double latitude);
	double GetLatitude() { return _latitude; }
  
	void SetMeridian(double meridian) { _meridian=meridian; }
	double GetMeridian() { return _meridian; }

	bool SetHourAngle(double hourangle);
	double GetHourAngle() { return _hourangle; }

	void GetPosition (double &Alt, double &Az);  
	double GetSunrise () { return _sunrise; }

	// Difference between solar and clock time (add result to clock time to get solar)
	// return value in hours, longitude in degrees(?)
	double TimeDiff (double Longitude,double Meridian);

private:
// all of these angles stored in radians
	double _altitude;
	double _azimuth;
	double _latitude;
	double _hourangle;
	double _declination;
	double _sunrise;

	double _meridian;

	double _day;

	void calculateAltitude();
	void calculateAzimuth();
	void CalculateSunrise();

};

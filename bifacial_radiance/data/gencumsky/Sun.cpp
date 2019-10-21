#include "Sun.h"

#define _USE_MATH_DEFINES
#include <math.h>
#include <stdio.h>

cSun::cSun (double latitude, int day, double hourangle, double meridian)
{
  _latitude=latitude;
  if (!this->SetDay(day))
      this->SetDay(0);

  if (!this->SetHourAngle(hourangle))
      this->SetHourAngle(M_PI/2);
}

cSun::~cSun(void)
{
}

bool cSun::SetDay(int day)
{
  if (day >=1 && day <=365)
  {
    _day=2.0*M_PI*(day-1.0)/365.0;
    _declination = 0.006918 - 0.399912*cos(_day) + 0.070257*sin(_day) 
               - 0.006758*cos(2*_day) + 0.000907*sin(2*_day) - 0.002697*cos(3*_day) 
               + 0.00148*sin(3*_day);

    CalculateSunrise();
	return true;
  }
  else
    return false;
}


bool cSun::SetLatitude(double latitude)
{ 
  if (latitude >= -M_PI/2 && latitude <=M_PI/2)
  {
    _latitude = latitude; 
	CalculateSunrise();
    return true;
  }
  else
    return false;
}

bool cSun::SetHourAngle(double hourangle)
{
  _hourangle=hourangle;
  if (hourangle >= _sunrise && hourangle <= (2*M_PI - _sunrise))
  {
    return true;
  }
  else
    return false;
}

void cSun::calculateAltitude()
{
  _altitude=asin(sin(_latitude)*sin(_declination) - cos(_latitude)*cos(_declination)*cos(_hourangle));

}


void cSun::calculateAzimuth()
{
  double temp;

  temp = (-sin(_latitude)*sin(_altitude) + sin(_declination))/(cos(_latitude)*cos(_altitude));

  if (temp > 1)
	 _azimuth=0;
  else if (temp < -1)
	 _azimuth=M_PI;  
  else if (_hourangle < M_PI)
     _azimuth=acos(temp);
  else
     _azimuth=2*M_PI - acos(temp);



}

void cSun::GetPosition(double &Alt, double &Az)
{
  calculateAltitude();
  calculateAzimuth();

 

  
  Alt=_altitude;
  Az=_azimuth;
}

void cSun::CalculateSunrise()
{
	if (tan(_latitude)*tan(_declination)>=1)
		_sunrise=0;
	else if (tan(_latitude)*tan(_declination)<=-1)
		_sunrise=M_PI;
	else
		_sunrise=acos(tan(_latitude)*tan(_declination));

}

double cSun::TimeDiff(double Longitude,double Meridian )
{
	double Et;

	Et = 229.2 * (0.000075 + 0.001868*cos(_day) - 0.032077*sin(_day) - 0.014615*cos(2*_day) - 0.04089*sin(2*_day));
	return (-4*(Longitude-Meridian)*180./M_PI + Et)/60;


}

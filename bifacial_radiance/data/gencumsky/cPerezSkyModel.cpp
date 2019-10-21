#include "cPerezSkyModel.h"

#define _USE_MATH_DEFINES
#include <math.h>
#include <stdio.h>

// Perez all weather sky model coefficients
double cPerezSkyModel::m_a1[8]= {1.3525,-1.2219,-1.1000,-0.5484,-0.6000,-1.0156,-1.0000,-1.0500};
double cPerezSkyModel::m_a2[8]= {-0.2576,-0.7730,-0.2515,-0.6654,-0.3566,-0.3670,0.0211,0.0289};
double cPerezSkyModel::m_a3[8]= {-0.2690,1.4148,0.8952,-0.2672,-2.5000,1.0078,0.5025,0.4260};
double cPerezSkyModel::m_a4[8]= {-1.4366,1.1016,0.0156,0.7117,2.3250,1.4051,-0.5119,0.3590};
double cPerezSkyModel::m_b1[8]= {-0.7670,-0.2054,0.2782,0.7234,0.2937,0.2875,-0.3000,-0.3250};
double cPerezSkyModel::m_b2[8]= {0.0007,0.0367,-0.1812,-0.6219,0.0496,-0.5328,0.1922,0.1156};
double cPerezSkyModel::m_b3[8]= {1.2734,-3.9128,-4.5000,-5.6812,-5.6812,-3.8500,0.7023,0.7781};
double cPerezSkyModel::m_b4[8]= {-0.1233,0.9156,1.1766,2.6297,1.8415,3.3750,-1.6317,0.0025};
double cPerezSkyModel::m_c1[8]= {2.8000,6.9750,24.7219,33.3389,21.0000,14.0000,19.0000,31.0625};
double cPerezSkyModel::m_c2[8]= {0.6004,0.1774,-13.0812,-18.3000,-4.7656,-0.9999,-5.0000,-14.5000};
double cPerezSkyModel::m_c3[8]= {1.2375,6.4477,-37.7000,-62.2500,-21.5906,-7.1406,1.2438,-46.1148};
double cPerezSkyModel::m_c4[8]= {1.0000,-0.1239,34.8438,52.0781,7.2492,7.5469,-1.9094,55.3750};
double cPerezSkyModel::m_d1[8]= {1.8734,-1.5798,-5.0000,-3.5000,-3.5000,-3.4000,-4.0000,-7.2312};
double cPerezSkyModel::m_d2[8]= {0.6297,-0.5081,1.5218,0.0016,-0.1554,-0.1078,0.0250,0.4050};
double cPerezSkyModel::m_d3[8]= {0.9738,-1.7812,3.9229,1.1477,1.4062,-1.0750,0.3844,13.3500};
double cPerezSkyModel::m_d4[8]= {0.2809,0.1080,-2.6204,0.1062,0.3988,1.5702,0.2656,0.6234};
double cPerezSkyModel::m_e1[8]= {0.0356,0.2624,-0.0156,0.4659,0.0032,-0.0672,1.0468,1.5000};
double cPerezSkyModel::m_e2[8]= {-0.1246,0.0672,0.1597,-0.3296,0.0766,0.4016,-0.3788,-0.6426};
double cPerezSkyModel::m_e3[8]= {-0.5718,-0.2190,0.4199,-0.0876,-0.0656,0.3017,-2.4517,1.8564};
double cPerezSkyModel::m_e4[8]= {0.9938,-0.4285,-0.5562,-0.0329,-0.1294,-0.4844,1.4656,0.5636};
double cPerezSkyModel::m_PerezClearnessBin[8]={1.065,1.23,1.5,1.95,2.8,4.5,6.2,999999};

// Perez global luminous efficacy coefficients
double cPerezSkyModel::m_GlobLumEffya[8]={96.63,107.54,98.73,92.72,86.73,88.34,78.63,99.65};
double cPerezSkyModel::m_GlobLumEffyb[8]={-.47,.79,.7,.56,.98,1.39,1.47,1.86};
double cPerezSkyModel::m_GlobLumEffyc[8]={11.5,1.79,4.4,8.36,7.1,6.06,4.93,-4.46};
double cPerezSkyModel::m_GlobLumEffyd[8]={-9.16,-1.19,-6.95,-8.31,-10.94,-7.6,-11.37,-3.15};

// Perez diffuse luminous efficacy coefficients
double cPerezSkyModel::m_DiffLumEffya[8]={97.24,107.22,104.97,102.39,100.71,106.42,141.88,152.23};
double cPerezSkyModel::m_DiffLumEffyb[8]={-.46,1.15,2.96,5.59,5.94,3.83,1.90,.35};
double cPerezSkyModel::m_DiffLumEffyc[8]={12.0,.59,-5.53,-13.95,-22.75,-36.15,-53.24,-45.27};
double cPerezSkyModel::m_DiffLumEffyd[8]={-8.91,-3.95,-8.77,-13.9,-23.74,-28.83,-14.03,-7.98};

// Perez direct luminous efficacy coefficients
double cPerezSkyModel::m_BeamLumEffya[8]={57.2,98.99,109.83,110.34,106.36,107.19,105.75,101.18};
double cPerezSkyModel::m_BeamLumEffyb[8]={-4.55,-3.46,-4.90,-5.84,-3.97,-1.25,.77,1.58};
double cPerezSkyModel::m_BeamLumEffyc[8]={-2.98,-1.21,-1.71,-1.99,-1.75,-1.51,-1.26,-1.10};
double cPerezSkyModel::m_BeamLumEffyd[8]={117.12,12.38,-8.81,-4.56,-6.16,-26.73,-34.44,-8.29};

// TODO:  check sunrise/sunset

cPerezSkyModel::cPerezSkyModel(void)
{
	m_coefficientsset=false;
}

cPerezSkyModel::~cPerezSkyModel(void)
{
}

bool cPerezSkyModel::SetSkyConditions(double Idh, double Ibh, cSun *Sun)
{
	double SolarZenith;
	double Ibn;

	double PerezBrightness, PerezClearness;
	double E0,day_angle, AirMass;

	int i, intClearness;

	// if no sun, return no luminance
	if (Idh <= 0)
	{
		m_a=0;
		m_b=0;
		m_c=0;
		m_d=0;
		m_e=0;
		m_coefficientsset=true;
		return false;
	}

	Sun->GetPosition(m_SolarAlt,m_SolarAz);
	
	// store solar zenith
	SolarZenith = M_PI/2 - m_SolarAlt;

	// calculate clearness
	if (m_SolarAlt > 0)
		Ibn=Ibh/sin(m_SolarAlt);
	else if (m_SolarAlt <=0 && Ibh>0)
	{
		// if there's direct horizontal radiation specified but sun is below horizon,
		// lump it in with the diffuse
		Idh=Idh+Ibh;
		Ibn=0;
	}
	else
		Ibn=0;

	PerezClearness = ((Idh+Ibn)/Idh + 1.041*pow(SolarZenith,3))/(1+1.041*pow(SolarZenith,3));

	// calculate brightness
	// extra terrestrial radiation

	// TODO: check IextraT and AirMass eqns with task 3 microclimate modelling paper
	day_angle=Sun->GetDay()*2*M_PI/365;

    E0 = 1367 * (1.00011+0.034221*cos(day_angle)+0.00128*sin(day_angle)
								+0.000719*cos(2*day_angle)+0.000077*sin(2*day_angle));

	// air optical mass
	if (m_SolarAlt >= 10 * M_PI/180)
		AirMass=1/sin(m_SolarAlt);
	else
//		AirMass=1/(sin(m_SolarAlt) + 0.15*pow(m_SolarAlt*180/M_PI + 3.885,-1.253));
		AirMass=1/(sin(m_SolarAlt) + 0.50572*pow(180*m_SolarAlt/M_PI+6.07995,-1.6364));

	// fix in case a very negative solar altitude is input
//	if (m_SolarAlt*180/M_PI + 3.885 >=0)
	if (m_SolarAlt*180/M_PI + 6.07995 >=0)
		PerezBrightness=AirMass*Idh/E0;
	else
	{
		// Idh is not zero, but sun altitude < 6 degrees, if Idh is very small (<10) neglect it
        if (Idh <= 10)
		{
			m_a=0;
			m_b=0;
			m_c=0;
			m_d=0;
			m_e=0;
			m_coefficientsset=true;
			return false;
		}

		// Idh is > 10 and sun altitude v. low, flag up an error and blunder on anyway
		fprintf(stderr,"Error!  Solar altitude is %.0f < -6 degrees and Idh = %.0f > 10 W/m^2 on day %d !Ibn is %.0f.  Attempting to continue!\n",m_SolarAlt*180/M_PI,Idh,Sun->GetDay(),Ibn);
		PerezBrightness=0;
	}

	// TODO: Temporary bit!!!
	if (PerezBrightness < 0.2 && (PerezClearness > 1.065 && PerezClearness < 2.8)) PerezBrightness=0.2;

	// Now determine the model coefficients
	// TODO: Error checking
	if (PerezClearness <1)
	{
		//fprintf(stderr,"ERROR! CLEARNESS < 1\n");
		return false;
	}

	// find which 'clearness bin' to use (note intClearness is set to one lower than the
	// tradiational bin numbers (i.e. for clearness bin 1, intClearness=0)
	for (i=7; i>=0; i--)
		if (PerezClearness < m_PerezClearnessBin[i]) intClearness=i;

	m_a = m_a1[intClearness] + m_a2[intClearness]*SolarZenith
		+ PerezBrightness*(m_a3[intClearness] + m_a4[intClearness]*SolarZenith);
	m_b = m_b1[intClearness] + m_b2[intClearness]*SolarZenith
		+ PerezBrightness*(m_b3[intClearness] + m_b4[intClearness]*SolarZenith);
	m_e = m_e1[intClearness] + m_e2[intClearness]*SolarZenith
		+ PerezBrightness*(m_e3[intClearness] + m_e4[intClearness]*SolarZenith);

	if (intClearness > 0)
	{
		m_c = m_c1[intClearness] + m_c2[intClearness]*SolarZenith
			+ PerezBrightness*(m_c3[intClearness] + m_c4[intClearness]*SolarZenith);
		m_d = m_d1[intClearness] + m_d2[intClearness]*SolarZenith
			+ PerezBrightness*(m_d3[intClearness] + m_d4[intClearness]*SolarZenith);
	}
	else
	{
		// different equations for c & d in clearness bin no. 1
		m_c=exp(pow(PerezBrightness*(m_c1[intClearness] + m_c2[intClearness]*SolarZenith),m_c3[intClearness])) - 1;
		m_d=-exp(PerezBrightness*(m_d1[intClearness] + m_d2[intClearness]*SolarZenith)) + m_d3[intClearness] +   m_d4[intClearness]*PerezBrightness;
	}

	m_coefficientsset=true;
	m_PerezClearness=PerezClearness;
	m_IntPerezClearness=intClearness;
	m_PerezBrightness=PerezBrightness;
	return true;
}

double cPerezSkyModel::GetRelativeLuminance(double Alt, double Az)
{
	double cosSkySunAngle;
	double lv;

	if (!m_coefficientsset)
	{
		// trying to use model without setting it up
		printf("Attempt to use model before coefficients are set!\n");
		return -1;
	}

	cosSkySunAngle= sin(Alt)*sin(m_SolarAlt) + cos(m_SolarAlt)*cos(Alt)*cos(fabs(Az-m_SolarAz));

	lv=(1 + m_a*exp(m_b/sin(Alt))) * (1 + m_c*exp(m_d*acos(cosSkySunAngle)) + m_e*cosSkySunAngle*cosSkySunAngle);
	if (lv < 0) lv=0;
	return lv;
}

// TODO: Work out W properly!
// Td - three hourly surface dew point temp (degC)
double cPerezSkyModel::GetDiffuseLumEffy(double SolarAlt, double Td)
{
	double W = 2.0;

	return m_DiffLumEffya[m_IntPerezClearness] + m_DiffLumEffyb[m_IntPerezClearness]*W + m_DiffLumEffyc[m_IntPerezClearness]*sin(SolarAlt)
		+ m_DiffLumEffyd[m_IntPerezClearness]*log(m_PerezBrightness);
}

// Td - three hourly surface dew point temp (degC)
double cPerezSkyModel::GetBeamLumEffy(double SolarAlt, double Td)
{
	double W = 2.0;
	double BeamLumEffy=m_BeamLumEffya[m_IntPerezClearness] + m_BeamLumEffyb[m_IntPerezClearness]*W + m_BeamLumEffyc[m_IntPerezClearness]*exp(5.73*(M_PI/2-SolarAlt)-5)
		+ m_BeamLumEffyd[m_IntPerezClearness]*m_PerezBrightness;

	if (BeamLumEffy>0)
		return BeamLumEffy;
	else
		return 0;
}

// Td - three hourly surface dew point temp (degC)
double cPerezSkyModel::GetGlobalLumEffy(double SolarAlt, double Td)
{
	double W = 2.0;
	double GlobLumEffy=m_GlobLumEffya[m_IntPerezClearness] + m_GlobLumEffyb[m_IntPerezClearness]*W + m_GlobLumEffyc[m_IntPerezClearness]*sin(SolarAlt)
		+ m_GlobLumEffyd[m_IntPerezClearness]*log(m_PerezBrightness);
	// careful we don't return a negative efficacy!

	if (GlobLumEffy>0)
		return GlobLumEffy;
	else
		return 0;
}

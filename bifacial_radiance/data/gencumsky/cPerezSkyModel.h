#include "Sun.h"
class cPerezSkyModel 
{

public:
	cPerezSkyModel(void);
	virtual ~cPerezSkyModel(void);

	// return whether or not it was succesful
	// cSun object should be set up in the correct position before calling
	virtual bool SetSkyConditions(double Idh, double Ibh, cSun *Sun);
	virtual double GetRelativeLuminance(double Alt, double Az);
	virtual double GetDiffuseLumEffy(double SolarAlt, double Td);
	virtual double GetGlobalLumEffy(double SolarAlt, double Td);
	virtual double GetBeamLumEffy(double SolarAlt, double Td);

	double GetSkyClearness() { return m_PerezClearness; }

private:
	double m_SolarAlt, m_SolarAz; // in radians

	// used to make sure we don't return a luminance before model is set up
	bool m_coefficientsset;

	// model coefficients
	// TODO: probably shouldn't declare these as static, but need to find a way
	// to initialise them
	static double m_a1[8], m_a2[8], m_a3[8], m_a4[8];
	static double m_b1[8], m_b2[8], m_b3[8], m_b4[8];
	static double m_c1[8], m_c2[8], m_c3[8], m_c4[8];
	static double m_d1[8], m_d2[8], m_d3[8], m_d4[8];
	static double m_e1[8], m_e2[8], m_e3[8], m_e4[8];
	static double m_PerezClearnessBin[8];

	// Perez global luminous efficacy coefficients
	static double m_GlobLumEffya[8];
	static double m_GlobLumEffyb[8];
	static double m_GlobLumEffyc[8];
	static double m_GlobLumEffyd[8];

	// Perez diffuse luminous efficacy coefficients
	static double m_DiffLumEffya[8];
	static double m_DiffLumEffyb[8];
	static double m_DiffLumEffyc[8];
	static double m_DiffLumEffyd[8];

	// Perez direct luminous efficacy coefficients
	static double m_BeamLumEffya[8];
	static double m_BeamLumEffyb[8];
	static double m_BeamLumEffyc[8];
	static double m_BeamLumEffyd[8];

	double m_a,m_b,m_c,m_d,m_e;
	double m_PerezClearness;
	int m_IntPerezClearness;
	double m_PerezBrightness;
};

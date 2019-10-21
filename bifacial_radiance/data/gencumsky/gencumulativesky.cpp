// GenCumulativeSky was conceived, developed and validated by Darren Robinson and Andrew Stone for efficient solar irradiation modelling using RADIANCE
// When using GenCumulativeSky they would be pleased if you would ackowledge their work by referring to the following article: "Robinson, D., Stone, A.,
// Irradiation modeling made simple the cumulative sky approach and its applications, Proc. PLEA 2004, Eindhoven 2004."
//
// GenCumulativeSky.cpp : Defines the entry point for the console application.
//

#include "cSkyVault.h"


int main(int argc, char* argv[])
{
	cSkyVault sky;
	double (*patchData)[5] = new double[145][5];
	int i,j, counter;

	double *CumSky;
	double dx,dy,dz;
	double alt,az,deltaalt,deltaaz;
	double ScalingFactor=1.0;

	double rowdeltaaz[7]={12,12,15,15,20,30,60};
	//double rowdeltaaz[14]={6,6,6,6,7.5,7.5,7.5,7.5,10,10,15,15,30,30};
	int rowdeltaalt=12;

	char *filename=argv[argc-1];
	double hourshift=0;

	bool DoIlluminance=false;
	bool DoRadiance_179=false;

	cSkyVault::eSunType SunType;
	cClimateFile::eClimateFileFormat ClimateFileFormat;

	bool DoDiffuse;

	if (!(argc>1))
	{
		// User didn't give any command line arguments
		fprintf(stderr,"GenCumulativeSky: Error - invalid input parameters\n");
		goto USAGEERROR;
	}

	counter=1;
	sky.StartTime=0.0;
	sky.EndTime=24.0;
	sky.StartDay=1;
	sky.EndDay=31;
	sky.StartMonth=1;
	sky.EndMonth=12;

	// Set the default parameters
	SunType=cSkyVault::NO_SUN;
	DoDiffuse=true;
	sky.SetLatitude(51.7*M_PI/180);
	sky.SetLongitude(0*M_PI/180);
	ClimateFileFormat=cClimateFile::GLOBAL_DIFFUSE;

	while (counter<argc-1)
	{
		if (argv[counter][0]=='+' && argv[counter][1]=='s' && argv[counter][2]=='1')
		{
			SunType=cSkyVault::CUMULATIVE_SUN;
			counter++;
		}
		else if (argv[counter][0]=='+' && argv[counter][1]=='s' && argv[counter][2]=='2')
		{
			SunType=cSkyVault::MANY_SUNS;
			counter++;
		}
		else if (argv[counter][0]=='-' && argv[counter][1]=='d' && argv[counter][2]==' ' )
		{
			DoDiffuse=false;
			counter++;
		}
		else if (argv[counter][0]=='-' && argv[counter][1]=='G' )
		{
			ClimateFileFormat=cClimateFile::GLOBAL_DIFFUSE;
			counter++;
		}
		else if (argv[counter][0]=='-' && argv[counter][1]=='B' )
		{
			ClimateFileFormat=cClimateFile::DIRECTHORIZONTAL_DIFFUSE;
			counter++;
		}
		else if (argv[counter][0]=='-' && argv[counter][1]=='E' )
		{
			ClimateFileFormat=cClimateFile::GLOBAL_DIFFUSE_EPW;
			counter++;
		}
		else if (argv[counter][0]=='-' && argv[counter][1]=='l' )
		{
			DoIlluminance=true;
			counter++;
		}
		else if (argv[counter][0]=='-' && argv[counter][1]=='r' )
		{
			ScalingFactor=1.0/179000;;
			counter++;
		}
		else if (argv[counter][0]=='-' && argv[counter][1]=='p' )
		{
			ScalingFactor=1.0/1000;;
			counter++;
		}
		else if (argv[counter][0]=='-' && argv[counter][1]=='a')
		{
			if ((argc-counter)>2)
			{
				sky.SetLatitude(atof(argv[counter+1])*M_PI/180.);
				counter+=2;
			}
			else
			{
				goto USAGEERROR;
			}
		}
		else if (argv[counter][0]=='-' && argv[counter][1]=='h')
		{
			if ((argc-counter)>2)
			{
				// hourshift - used to alter the default time convention
				hourshift=atof(argv[counter+1]);
				counter+=2;
			}
			else
			{
				goto USAGEERROR;
			}
		}
		else if (argv[counter][0]=='-' && argv[counter][1]=='o' && (argc-counter)>2)
		{
			if ((argc-counter)>2)
			{
				sky.SetLongitude(atof(argv[counter+1])*M_PI/180.);
				counter+=2;
			}
			else
			{
				goto USAGEERROR;
			}
		}
		else if (argv[counter][0]=='-' && argv[counter][1]=='m' && (argc-counter)>2)
		{
			if ((argc-counter)>2)
			{
				sky.SetMeridian(atof(argv[counter+1])*M_PI/180.);
				counter+=2;
			}
			else
			{
				goto USAGEERROR;
			}
		}
		else if (argv[counter][0]=='-' && argv[counter][1]=='t' && argv[counter][2]=='i' && argv[counter][3]=='m' && argv[counter][4]=='e'  )
		{
			if ((argc-counter)>3 )
			{
				sky.StartTime=atof(argv[counter+1]);
				sky.EndTime=atof(argv[counter+2]);
				counter+=3;
				if(sky.StartTime<0 || sky.StartTime >24 || sky.EndTime<0 || sky.EndTime >24 || sky.EndTime <= sky.StartTime)
				{
					fprintf(stderr,"GenCumulativeSky: Error - invalid start time (%.3f) or end time (%.3f)\n",sky.StartTime,sky.EndTime );
					goto USAGEERROR;
				}
			}
			else
			{
				goto USAGEERROR;
			}

		}
		else if (argv[counter][0]=='-' && argv[counter][1]=='d' && argv[counter][2]=='a' && argv[counter][3]=='t' && argv[counter][4]=='e'  )
		{
			if ((argc-counter)>5 )
			{
				sky.StartMonth=atoi(argv[counter+1]);
				sky.StartDay=atoi(argv[counter+2]);
				sky.EndMonth=atoi(argv[counter+3]);
				sky.EndDay=atoi(argv[counter+4]);
				counter+=5;
				if(sky.StartDay<0 || sky.StartDay >31.0 ||sky.EndDay<0.0 || sky.EndDay >31.0 ||sky.StartMonth<0.0 || sky.StartMonth >12.0 ||sky.EndMonth<0.0 || sky.EndMonth >12.0)
				{
					fprintf(stderr,"GenCumulativeSky: Error - invalid start date (%2.0f//%2.0f) or end date (%2.0f//%2.0f)\n",(double)sky.StartMonth,(double)sky.StartDay,(double)sky.EndMonth,(double)sky.EndDay );
					goto USAGEERROR;
				}
			}
			else
			{
				goto USAGEERROR;
			}

		}
		else
		{
			fprintf(stderr,"GenCumulativeSky: Error - invalid input parameter '%s'\n\n",argv[counter]);
			goto USAGEERROR;
		}
	}


	
	if (!sky.LoadClimateFile(filename, ClimateFileFormat, sky.StartTime, sky.EndTime, sky.StartDay, sky.EndDay, sky.StartMonth, sky.EndMonth))
	{
		fprintf(stderr,"GenCumulativeSky: Error reading climate file %s\n\n",filename);
		goto USAGEERROR;
	}

	sky.CalculateSky(SunType, DoDiffuse, DoIlluminance, hourshift);

	CumSky=sky.GetCumulativeSky();
	sky.GetPatchDetails(patchData);



	printf("{ This .cal file was generated automatically by GenCumulativeSky }\n");
	printf("{ ");
	for (j=0; j<argc; j++)
		printf("%s ",argv[j]);
	printf(" }\n\n");
	printf("skybright=");
	for (j=0; j<7; j++)
	{
		printf("row%d+",j);
	}
	printf("row7;\n\n");

	counter=0;
	for (j=0; j<7; j++)
	{
		// note first patch split into two parts - first part (> 0 deg) and last patch (<360)
		printf("row%d=if(and(alt-%d, %d-alt),select(floor(0.5+az/%5.2f)+1,\n",j,j*rowdeltaalt,(j+1)*rowdeltaalt,rowdeltaaz[j]);
		for (i=0+counter; i<counter+360/int(rowdeltaaz[j]); i++)
		{
			printf("\t%f,\n",CumSky[i]*ScalingFactor);
		}
		printf("\t%f),0);\n\n",CumSky[counter]*ScalingFactor);
		counter+=(int)(360/rowdeltaaz[j]);
	}

	printf("row7=if(alt-84,%f,0);\n\n",CumSky[144]*ScalingFactor);

	printf("alt=asin(Dz)*180/PI;\n\n");

	printf("az=if(azi,azi,azi+360);\n");
	printf("azi=atan2(Dx,Dy)*180/PI;\n\n");

	return 0;

USAGEERROR:
	fprintf(stderr,"Usage: GenCumulativeSky [-d] [+s1|+s2] [-a latitude] [-o longitude] [-l] [-m standard meridian] [-h hourshift] [-G|-B|-E] <climate file>\n");
	fprintf(stderr,"(Note: longitude +ve East of Greenwich)\n\n");
	fprintf(stderr,"\t-d\tIgnore diffuse irradiance\n");
	fprintf(stderr,"\t+s1\tUse \"smeared sun\" approach (default)\n");
	fprintf(stderr,"\t+s2\tUse \"binned sun\" approach\n");
	fprintf(stderr,"\t-l\tOutput luminance instead of radiance\n");
	fprintf(stderr,"\t-r\tOutput radiance/179000 (ensures that units in the Radiance Image Viewer are in kWhm-2)\n");
	fprintf(stderr,"\t-p\tOutput radiance/1000 (ensures that units in the Radiance RGB data file  are in kWhm-2)\n");
	fprintf(stderr,"\t-G\tFile format is col1=global irradiance (W/m2), col2=diffuse irradiance (W/m2)\n");
	fprintf(stderr,"\t-B\tFile format is col1=direct horizontal irradiance (W/m2), col2=diffuse irradiance (W/m2)\n");
	fprintf(stderr,"\t-E\tFile format is an energyplus weather file (*.epw) The gprogram uses the global irradiance (W/m2) and diffuse irradiance (W/m2) data columns.\n");
	fprintf(stderr,"\t\tIn combination with \'-E' the considered time interval can be specified:\n");
	fprintf(stderr,"\t\t-time <start time of day> <end time of day>\n");
	fprintf(stderr,"\t\t-date mm_start dd_start mm_end dd_end (if start-date after end-date then the winter interval is considered)\n");
	fprintf(stderr,"\n");
	return -1;
}


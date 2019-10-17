#include "climateFile.h"
#include <stdio.h>
#include <iostream>


#include "paths.h"

cClimateFile::cClimateFile(void)
{
	// set pointers to point to zero initially
	m_ptIgh=0;
	m_ptIdh=0;
}

cClimateFile::~cClimateFile(void)
{
	delete[] m_ptIgh;
	delete[] m_ptIdh;
}

bool cClimateFile::ReadClimateFile(char *FileName, int HourConvention, eClimateFileFormat ClimateFileFormat,double StartTime, double EndTime, int StartDay, int EndDay, int StartMonth, int EndMonth)
{
	FILE *InputFile;
	char *Line = new char[1000];

	int hour,day;
	int i;
	float n1,n2,n3,n4,n5,n7,n8,n9,n10,n11,n12,n13,n14,n15,n16;
	char line_string[1000]="";
	char s7[1000]="";

	// open file (checking that you can...)
	if ((InputFile=LoadFile(FileName))==NULL)
	{
		fprintf(stderr,"Error opening: %s\n",FileName);
		return false;
	}
	rewind(InputFile);
	// TODO: Add error checking

	// get rid of old climate data
	delete[] m_ptIgh;
	delete[] m_ptIdh;

	//Assume we've got 8760 points
	m_NumPoints=8760;

	double *Col1 = new double[m_NumPoints];
	double *Col2 = new double[m_NumPoints];

	// read in points for each hour of each day
	// points are assumed to be at 0:30, 1:30, ... from 1st Jan to 3st Dec
	// The function assumes  a full hourly annual data file with 8760 lines.

	//if EPW file format
	if (ClimateFileFormat==GLOBAL_DIFFUSE_EPW)
	{
		//skip file header:
		for (i=0; i<8; i++)
		{
			fscanf(InputFile,"%*[^\n]");
			fscanf(InputFile,"%*[\n\r]");
		}
		for (day=0; day<365; day++)
		{
			for (hour=0; hour<24; hour++)
			{
				
				fscanf(InputFile,"%f,%f,%f,%f,%f,%s",&n1,&n2,&n3,&n4,&n5,&line_string[0]);
				//replace ',' with ' '
				for (i=0;i<1000;i++){
					if(line_string[i] == ',')
						line_string[i] = ' ';
				}
				if (sscanf(line_string,"%s %f %f %f %f %f %f %f %f %f  %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f",
					&s7[0],&n7,&n8,&n9,&n10,&n11,&n12,&n13,&n14,&n15,&n16,&n1,&n1,&n1,&n1,&n1,&n1,&n1,&n1,&n1,&n1,&n1,&n1,&n1,&n1,&n1)== EOF)
				{
					// ran out of file
					fprintf(stderr,"Error processing climate file %s\n",FileName);
					return false;
				}
				// StartDay, EndDay, StartMonth, EndMonth);
				if(hour>= (StartTime) && hour< (EndTime-1))
				{
					if(JulianDate(StartMonth, StartDay)<=JulianDate(EndMonth, EndDay))
					{
						if(day>=JulianDate(StartMonth, StartDay) && day<=JulianDate(EndMonth, EndDay))
						{
							Col1[day*24+hour]=n14;
							Col2[day*24+hour]=n16;
						}
					} else if(JulianDate(StartMonth, StartDay)>JulianDate(EndMonth, EndDay))
					{
						if(day>=JulianDate(StartMonth, StartDay) || day<=JulianDate(EndMonth, EndDay))
						{
							Col1[day*24+hour]=n14;
							Col2[day*24+hour]=n16;
						}
					}
				}
				//printf("%.0f %.0f %.0f %.0f %.0f\n",n2,n3,n4,Col1[day*24+hour],Col2[day*24+hour]);
			}
		}



	}else{
		for (day=0; day<365; day++)
		{
			for (hour=0; hour<24; hour++)
			{
				if (fgets(Line,100,InputFile)==NULL)
				{
					// ran out of file
					fprintf(stderr,"Error processing climate file %s\n",FileName);
					return false;
				}

				sscanf(Line,"%lf %lf\n",&Col1[day*24+hour],&Col2[day*24+hour]);


			}
		}
	}

	// Now convert data into appropriate form
	if (ClimateFileFormat==GLOBAL_DIFFUSE || ClimateFileFormat==GLOBAL_DIFFUSE_EPW)
	{
		m_ptIgh=Col1;
		m_ptIdh=Col2;

	}
	else if (ClimateFileFormat == DIRECTHORIZONTAL_DIFFUSE)
	{
		m_ptIdh=Col2;
		for (i=0; i<m_NumPoints; i++)
		{
			Col1[i]=Col1[i]+Col2[i];
		}
		m_ptIgh=Col1;
	}
	else
	{
		// ran out of file
		fprintf(stderr,"Unknown climate file format!\n");
		return false;
	}


	if (!ValidateData())
	{
		fprintf(stderr,"Invalid Data!\n");
		return false;
	}
	fclose(InputFile);
	return true;
}


bool cClimateFile::ValidateData()
{
	// TODO: Write this function!
	return true;
}

int cClimateFile::JulianDate(int month, int day)
{
	// calculate julian date
	int jd=0;
	if(month==1)
		jd=day;
	if(month==2)
		jd=31+day;
	if(month==3)
		jd=59+day;
	if(month==4)
		jd=90+day;
	if(month==5)
		jd=120+day;
	if(month==6)
		jd=151+day;
	if(month==7)
		jd=181+day;
	if(month==8)
		jd=212+day;
	if(month==9)
		jd=243+day;
	if(month==10)
		jd=273+day;
	if(month==11)
		jd=304+day;
	if(month==12)
		jd=334+day;
	return (jd-1);
}
double cClimateFile::GetDirectRad(double hour, int day)
{
	// interpolate linearly between two closest hours
	double hourdiff, hour1;
	int pointer;

	// find the half hour before current time (climate file has data for 0:30, 1:30,2:30, etc...)
	hour1=(int)hour;
	hourdiff=hour-hour1;
	if (hourdiff >= 0.5) hour1+= 0.5;
	else hour1-=0.5;

	pointer=(day-1)*24+(int)(hour1-0.5);

	// if pointer < 0, don't have data for specified day
	if (pointer < 0) return -9999;

	float ratio, diff;

	ratio=hour-hour1;
	// TODO: CHeck this (first/last hours of day)
	diff=(m_ptIgh[pointer+1]-m_ptIdh[pointer+1])-(m_ptIgh[pointer]-m_ptIdh[pointer]);

	return (m_ptIgh[pointer]-m_ptIdh[pointer]) + diff*ratio;
}

double cClimateFile::GetDiffuseRad(double hour, int day)
{
	// interpolate linearly between two closest hours
	float hour1, hourdiff;
	int pointer;

	// find the half hour before current time (climate file has data for 0:30, 1:30,2:30, etc...)
	hour1=int(hour);
	hourdiff=hour-hour1;
	if (hourdiff >= 0.5) hour1+= 0.5;
	else hour1-=0.5;

	pointer=(day-1)*24+(int)(hour1-0.5);

	// if pointer < 0, don't have data for specified day
	if (pointer < 0) return -9999;

	float ratio, diff;

	ratio=hour-hour1;
	diff=m_ptIdh[pointer+1]-m_ptIdh[pointer];

	return m_ptIdh[pointer] + diff*ratio;
}

double cClimateFile::GetGlobalRad(double hour, int day)
{
	// interpolate linearly between two closest hours
	float hour1, hourdiff;
	int pointer;

	// find the half hour before current time (climate file has data for 0:30, 1:30,2:30, etc...)
	hour1=int(hour);
	hourdiff=hour-hour1;
	if (hourdiff >= 0.5) hour1+= 0.5;
	else hour1-=0.5;

	pointer=(day-1)*24+(int)(hour1-0.5);

	// if pointer < 0, don't have data for specified day
	if (pointer < 0) return -9999;

	float ratio, diff;

	ratio=hour-hour1;
	diff=m_ptIgh[pointer+1]-m_ptIgh[pointer];
	return m_ptIgh[pointer] + diff*ratio;
}


// THIS ROUTINE 'BORROWED' FROM GENDAYLIT
//FILE* cClimateFile::LoadFile( char *fname)			/* find file and open for reading */
//{
//	FILE  *fp;
//	char  pname[MAXPATH];
//	char *libpath=NULL;
//	register char  *sp, *cp;

//	if (fname == NULL)
//		return(NULL);

//	if (ISDIRSEP(fname[0]) || fname[0] == '.')	/* absolute path */
//		return(fopen(fname, "r"));

//	if (libpath == NULL) {			/* get search path */
//		libpath = getenv(ULIBVAR);
//		if (libpath == NULL)
//			libpath = DEFPATH;
//	}
						/* check search path */
//	sp = libpath;
//	do {
//		cp = pname;
//		while (*sp && (*cp = *sp++) != PATHSEP)
//			cp++;
//		if (cp > pname && !ISDIRSEP(cp[-1]))
//			*cp++ = DIRSEP;
//		strcpy(cp, fname);
//		if ((fp = fopen(pname, "r")) != NULL)
//			return(fp);			/* got it! */
//	} while (*sp);
//						/* not found */
//	return(NULL);
//}

FILE* cClimateFile::LoadFile( char *fname)	/*open file for reading*/
{	FILE *Datei;
	Datei = fopen(fname, "r");
	if ( Datei == NULL) fprintf(stderr,		  "fatal warning FUNCTION LoadFile: open of %s for input failed.\n",fname);
	return Datei;}


SOLAR RADIATION MAPPING
========================
This is directory contains the source for the gencumulativesky program.  To compile it using gcc:

g++ -D_XOPEN_SOURCE *.cpp -lm -o gencumulativesky

(The _XOPEN_SOURCE definition is required so that M_PI is defined when math.h is included - this will need changing depending on your compiler)

bifacial_radiance update Oct 2019:  run python make_gencumskyexe.py from the command line to compile a platform-specific instance of gencumulativesky.exe
#include <iostream>
#include <fstream>
#include <string>

#include <blitz/array.h>
#include <nifti1.h>

using namespace std;
using namespace blitz;

#include <boost/program_options.hpp>
namespace po = boost::program_options;


/* GLOBAL variables */
#define DEBUG 0
string	TRK_filename, ROI_filename, MAP_filename, CMX_filename;

/* Other code */
#include "../common/lib_ui.cxx"
#include "../common/lib_nii.cxx"
#include "../common/lib_trk.cxx"
#include "fibers_stats.cxx"



/******************************/
/*----------  MAIN  ----------*/
/******************************/
int main(int argc, char** argv)
{
//    TRK_filename = "/home/ale/Documents/Projects/cmt/c++/build/DTB_scalar/data/streamline.trk";
//    MAP_filename = "/home/ale/Documents/Projects/cmt/c++/build/DTB_scalar/data/dsi_gfa__1x1x1.nii";
//    ROI_filename = "/home/ale/Documents/Projects/cmt/c++/build/DTB_scalar/data/ROI_HR_th.nii";
//    CMX_filename = "/home/ale/Documents/Projects/cmt/c++/build/DTB_scalar/data/mymap.dat";


	/***** PARSING of INPUT parameters (achieved with BOOST libraries) *****/
	po::variables_map vm;
    try {
    	po::arg = "ARG";
		po::options_description desc("Parameters syntax");
        desc.add_options()
            ("trk", 		po::value<string>(&TRK_filename), "TRK path/filename (e.g. \"data/myfibers.trk\")")
            ("map", 		po::value<string>(&MAP_filename), "SCALAR MAP path/filename (e.g. \"data/fa.nii\")")
            ("roi", 		po::value<string>(&ROI_filename), "GM ROI path/filename (e.g. \"data/ROI_HR_th.nii\")")
            ("out", 		po::value<string>(&CMX_filename), "OUT path/prefix  (e.g. \"data/mymat\")")
            ("help", "Print this help message")
        ;
        po::store(po::command_line_parser(argc, argv).options(desc).run(), vm);
        po::notify(vm);

        if ( argc<2 || vm.count("help") )
        {
			cout <<"\n"<<COLOR(33,40,0)<< desc <<COLOR_reset<<"\n\n";
			return 1;
		}
    }
    catch(exception& e) {
        cerr <<COLOR(30,41,0)<<"[ERROR]"<<COLOR(31,40,0)<< " "<<e.what() <<COLOR_reset<<"\n\n";
        return 1;
    }
    catch(...) {
        COLOR_error("Exception of unknown type!\n\n");
    }


	/* Check INOUT PARAMETERS */
	if ( !vm.count("trk") )
	{
		COLOR_error("'trk' parameter not set.\n\n");
		return 1;
	}
	if ( !vm.count("map") )
	{
		COLOR_error("'map' parameter not set.\n\n");
		return 1;
	}
	if ( !vm.count("roi") )
	{
		COLOR_error("'roi' parameter not set.\n\n");
		return 1;
	}
	if ( !vm.count("out") )
	{
		COLOR_error("'out' parameter not set.\n\n");
		return 1;
	}


	return main__fibers_stats();
}

#include <iostream>
#include <fstream>
#include <string>

#include <blitz/array.h>
#include <nifti1.h>

using namespace std;
using namespace blitz;

#include <boost/program_options.hpp>
namespace po = boost::program_options;

#include "../common/lib_ui.cxx"
#include "../common/lib_nii.cxx"
#include "../common/lib_trk.cxx"
#include "cmx_matrix.cxx"


string	TRK_filename, ROI_filename, CMX_basename, MEASURE;



/******************************/
/*----------  MAIN  ----------*/
/******************************/
int main(int argc, char** argv)
{
	/***** PARSING of INPUT parameters (achieved with BOOST libraries) *****/
	po::variables_map vm;
    try {
    	po::arg = "ARG";
		po::options_description desc("Parameters syntax");
        desc.add_options()
            ("trk", 		po::value<string>(&TRK_filename), "TRK path/filename (e.g. \"data/myfibers.trk\")")
            ("roi", 		po::value<string>(&ROI_filename), "Gray matter ROI path/filename (e.g. \"data/ROI_HR_th.nii\")")
            ("measure",		po::value<string>(&MEASURE), "connectivity measure to calculate {count, density, percentage}")
            ("out", 		po::value<string>(&CMX_basename), "OUT path/prefix  (e.g. \"data/mymat\")")
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
	if ( !vm.count("roi") )
	{
		COLOR_error("'roi' parameter not set.\n\n");
		return 1;
	}
	if ( !vm.count("measure") )
	{
		COLOR_error("'measure' parameter not set.\n\n");
		return 1;
	}
	if ( !vm.count("out") )
	{
		COLOR_error("'out' parameter not set.\n\n");
		return 1;
	}


	return main__cmx_matrix();
}

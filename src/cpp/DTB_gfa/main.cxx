#include <iostream>
#include <fstream>
#include <string>

#include <blitz/array.h>
#include <nifti1.h>

using namespace std;
using namespace blitz;

#include <boost/program_options.hpp>
namespace po = boost::program_options;

#include "lib_ui.cxx"
#include "lib_nii.cxx"


unsigned int moment;	// keep the moment (2,3,4...) to calculate


int main(int argc, char** argv)
{
	string	DSI_basename;


/*--------------------------*/
/*  Check INPUT parameters  */
/*--------------------------*/

	/* PARSING of INPUT parameters (achieved with BOOST libraries) */
	po::variables_map vm;
    try {
    	po::arg = "ARG";
		po::options_description desc("Parameters syntax");
        desc.add_options()
            ("dsi", 	po::value<string>(&DSI_basename), "DSI path/basename (e.g. \"data/dsi_\")")
            ("m", 		po::value<unsigned int>(&moment)->default_value(2), "Moment to calculate [2,3,4]")
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


	/* Check values */
	if ( !vm.count("dsi") )
	{
		COLOR_error("'dsi' parameter not set.\n\n");
		return 1;
	}

	string GFA_filename;
	switch (moment)
	{
		case 2:	GFA_filename = DSI_basename + "gfa.nii"; break;
		case 3:	GFA_filename = DSI_basename + "skewness.nii"; break;
		case 4:	GFA_filename = DSI_basename + "kurtosis.nii"; break;
		default:
			COLOR_error("'m' parameter is not in the {2,3,4} valid range.\n\n");
			return 1;
	}


/*---------------------*/
/*  CALCULATE GFA map  */
/*---------------------*/

	/* READING 'ODF' dataset */
	string ODF_filename = DSI_basename + "odf.nii";

	cout <<COLOR(37,40,1)<< "\n-> Reading 'ODF' dataset...\n" <<COLOR_reset;

	NII<FLOAT32>* niiODF = nifti_load<FLOAT32>( ODF_filename );
	if ( niiODF == NULL )
		{ cerr << "\n" <<COLOR_strERR<< "Unable to open file '"<< ODF_filename <<"'!\n\n"<< COLOR_reset; exit(1); }
	if ( niiODF->hdr.datatype != 16 )
		{ cerr << "\n" <<COLOR_strERR<< "File '"<< ODF_filename <<".nii' has a WRONG DATA TYPE! It should be FLOAT32!\n\n"<< COLOR_reset; exit(1); }

	cout <<"   [ OK ]\n\n";


	/* CALCULATE GFA map  */
	short nDIR = niiODF->hdr.dim[1];
	short dim[4] 	= {niiODF->hdr.dim[2],niiODF->hdr.dim[3],niiODF->hdr.dim[4],1};
	float pixdim[4] = {niiODF->hdr.pixdim[2],niiODF->hdr.pixdim[3],niiODF->hdr.pixdim[4],1};

	NII<FLOAT32>* niiGFA = nifti_make<FLOAT32>( dim, pixdim );
	niiGFA->img = niiGFA->img * 0;

	memcpy((void*)(&niiGFA->hdr), (void*)(&niiODF->hdr), sizeof(niiODF->hdr));
	niiGFA->hdr.dim[0] = 3;
	niiGFA->hdr.dim[1] = dim[0]; 		niiGFA->hdr.dim[2] = dim[1]; 		niiGFA->hdr.dim[3] = dim[2]; 		niiGFA->hdr.dim[4] = dim[3];
	niiGFA->hdr.pixdim[1] = pixdim[0];	niiGFA->hdr.pixdim[2] = pixdim[1];	niiGFA->hdr.pixdim[3] = pixdim[2];	niiGFA->hdr.pixdim[4] = pixdim[3];
	niiGFA->hdr.datatype 	= 16;	niiGFA->hdr.bitpix 		= 32;
	niiGFA->hdr.cal_min		= 0;	niiGFA->hdr.cal_max		= 1;
	niiGFA->hdr.xyzt_units  = 10;

	Array<float,1> ODF(nDIR);
	float STD, RMS, MEAN, SUM, SQRT, sign;
	MEAN = 1.0 / nDIR;
	SQRT = 1.0 / moment;

	cout <<COLOR(37,40,1)<< "-> Calculating GFA in each voxel...\n" <<COLOR_reset;
	for(int x=0; x<dim[0] ;x++)
		for(int y=0; y<dim[1] ;y++)
			for(int z=0; z<dim[2] ;z++)
			{
				ODF = niiODF->img(Range::all(),x,y,z);
				SUM = sum(ODF);
				if (SUM<=0) continue;

				ODF = ODF / SUM;
				STD = sum(pow(ODF-MEAN,(float)moment)) / (nDIR-1);
				RMS = sum(pow(ODF,(float)moment)) / nDIR;

				if (moment==3 && STD<0) sign = -1; else sign=1;

				if (RMS>0)
					niiGFA->img(x,y,z) = sign * pow( abs(STD / RMS), SQRT);
				else
					niiGFA->img(x,y,z) = -1;
			}


	/* SAVE it as .nii  */
	nifti_save(niiGFA, GFA_filename);
	cout <<"   [ '"<< GFA_filename <<"' written ]\n\n";

	return 0;
}

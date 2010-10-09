#include <random/uniform.h>
#include <time.h>


typedef Array<float,2> FIBER;


/* GLOBAL variables */
extern 	string 	BASE_filename, MASK_filename, BASE_outname, BASE_filename_2;
extern 	float	maxAngle, maxAngle_2;
extern 	int		CONFIG__seeds;

extern	int 	CONFIG__minLength;
extern	float	CONFIG__stepSize;
extern	int		CONFIG__maxSteps;

float	ANGLE_thr;
float	ANGLE_thr_2;


extern 	string	MEASURE, ROI_filename, CMX_basename;




/* It returns:
       0   -->  no compatible directions
     < 0   -->  negative direction (-idx-1 inside S)
     > 0   -->  positive direction ( idx+1 inside S)
*/
int bestDir(Array<float,1>* dir, Array<float,2>* S, float angle_thr)
{
	int idx = 0;
	float max = 0, DOT, DOTabs;

	for(int i=0; i<S->extent(0) ;i++)
	{
		DOT    = (*dir)(0) * (*S)(i,0) + (*dir)(1) * (*S)(i,1) + (*dir)(2) * (*S)(i,2);
		DOTabs = abs(DOT);
		if ( DOTabs > max && DOTabs > angle_thr )
		{
			max = DOTabs;
			idx = ( DOT>0 ? i+1: -(i+1) );
		}
	}
	return idx;
}


/*********************************/
/*  NORMALIZE a direction array  */
/*********************************/
void normalize( Array<float,1> A )
{
    float tmp = sqrt( sum( pow(A,2) ) );
    if ( tmp>0 ) A = A / tmp;
    return;
}



/************************************************************************************************/
/******                                    streamline()                                    ******/
/************************************************************************************************/
void streamline(Array<Array<float,2>,3>* STIX, Array<Array<float,2>,3>* STIX2, NII<INT16>* niiMAX, NII<UINT8>* niiMASK, NII<UINT8>* niiSEED)
{
	FIBER*			 	fiber = new FIBER(3,CONFIG__maxSteps);
	FIBER				tmp;
	Array<float,1> 		COORD(3), seed_COORD(3), dir(3);
	Array<int,1> 		VOXEL_stix(3), VOXEL_wm(3);
	int 				step, totDir, idx, is_complete, tot_fibers = 0, tot_connections = 0;
	short int			dim[3]    = {niiMASK->hdr.dim[1], niiMASK->hdr.dim[2], niiMASK->hdr.dim[3]};
	float				pixdim[3] = {niiMASK->hdr.pixdim[1], niiMASK->hdr.pixdim[2], niiMASK->hdr.pixdim[3]};
	float				ratio[3]  = {niiMASK->hdr.pixdim[1]/niiMAX->hdr.pixdim[2], niiMASK->hdr.pixdim[2]/niiMAX->hdr.pixdim[3], niiMASK->hdr.pixdim[3]/niiMAX->hdr.pixdim[4]};

    ranlib::Uniform<float> 	uniformGenerator;
    uniformGenerator.seed( (unsigned int)time(0) );



	/* cycle on each voxel = 1 of the SEED mask */
	int percent = 0, tot = dim[0]*dim[1]*dim[2];
	for(int z=0; z < dim[2] ;z++)
	for(int y=0; y < dim[1] ;y++)
	for(int x=0; x < dim[0] ;x++)
	{
		percent++;
		if ( niiSEED->img(x,y,z)==0 || niiMASK->img(x,y,z)==0 ) continue;

		float deltaSEED = 1.0 / ((float)(CONFIG__seeds+1.0));

		for(int seedX=1; seedX <= CONFIG__seeds ;seedX++)
		for(int seedY=1; seedY <= CONFIG__seeds ;seedY++)
		for(int seedZ=1; seedZ <= CONFIG__seeds ;seedZ++)
		//for(int seedNum=0; seedNum<CONFIG__seeds ;seedNum++)
		{
			// SETUP
 			//seed_COORD = (float)x+uniformGenerator.random()-0.5, (float)y+uniformGenerator.random()-0.5, (float)z+uniformGenerator.random()-0.5;
 			seed_COORD = (float)x + (seedX*deltaSEED) - 0.5, (float)y + (seedY*deltaSEED) - 0.5, (float)z + (seedZ*deltaSEED) - 0.5;

			VOXEL_stix = round(seed_COORD(0)*ratio[0]), round(seed_COORD(1)*ratio[1]), round(seed_COORD(2)*ratio[2]);

			totDir = (*STIX)( VOXEL_stix(0), VOXEL_stix(1), VOXEL_stix(2) ).extent(0);
			if ( totDir==0 ) continue;

			// perform tractography FOR EACH DIRECTION of the SEED VOXEL_stix STIX
			for(int seedDir=0; seedDir<totDir ;seedDir++)
			{
				(*fiber)(Range(0,2),0) = seed_COORD;

				VOXEL_stix = round(seed_COORD(0)*ratio[0]), round(seed_COORD(1)*ratio[1]), round(seed_COORD(2)*ratio[2]);

				dir = (*STIX)( VOXEL_stix(0), VOXEL_stix(1), VOXEL_stix(2) )(seedDir,Range(0,2));
				COORD = (*fiber)(Range(0,2),0) + CONFIG__stepSize*dir;
				(*fiber)(Range(0,2),1) = COORD;


				// STEPPING (starting from step=2)
				step = 2;
				is_complete = 1;
				for(int semi_step=0; semi_step<2 ;semi_step++)
				{
					dir = (*fiber)(Range(0,2),step-1) - (*fiber)(Range(0,2),step-2);
 					normalize(dir);

					while( step<CONFIG__maxSteps )
					{
						VOXEL_wm   = round(COORD(0)), round(COORD(1)), round(COORD(2));
						VOXEL_stix = round(COORD(0)*ratio[0]), round(COORD(1)*ratio[1]), round(COORD(2)*ratio[2]);

						// checking for STOPPING CRITERIA
						if ( VOXEL_wm(0) < 0 || VOXEL_wm(1) < 0 || VOXEL_wm(2) < 0 || VOXEL_wm(0) > dim[0]-1 || VOXEL_wm(1) > dim[1]-1 || VOXEL_wm(2) > dim[2]-1 ) break;
						if ( niiMASK->img(VOXEL_wm(0),VOXEL_wm(1),VOXEL_wm(2)) == 0 ) break;

						// find NEXT DIRECTION to follow
						idx = bestDir(&dir, &(*STIX)( VOXEL_stix(0), VOXEL_stix(1), VOXEL_stix(2) ), ANGLE_thr);
						if ( idx != 0 )
							dir = (*STIX)( VOXEL_stix(0), VOXEL_stix(1), VOXEL_stix(2) )( abs(idx)-1, Range(0,2) );
						else {
							// if NO OTHER ODF is provided...
							if ( STIX2 == NULL )
							{
								is_complete = 0;
								break;
							}

							// otherwise, use it!
							idx = bestDir(&dir, &(*STIX2)( VOXEL_stix(0), VOXEL_stix(1), VOXEL_stix(2) ), ANGLE_thr_2);
							if ( idx == 0 )	{
								is_complete = 0;
								break;
							}
							dir = (*STIX2)( VOXEL_stix(0), VOXEL_stix(1), VOXEL_stix(2) )( abs(idx)-1, Range(0,2) );
						}


						if ( idx<0 ) dir = -dir;
						COORD = COORD + CONFIG__stepSize*dir;
						(*fiber)(Range(0,2),step++) = COORD;
					}

					/* reverse the first part of the fiber and run the second part (opposite dir) */
					if (semi_step==0)
					{
						COORD = (*fiber)(Range(0,2),0);

						tmp.resize(3,step);
						tmp = (*fiber)(Range(0,2),Range(0,step-1));
						tmp.reverseSelf(1);
						(*fiber)(Range(0,2),Range(0,step-1)) = tmp;
					}
				}


				/* UPDATE matrix */
				if ( (step-1)*CONFIG__stepSize*pixdim[0] >= CONFIG__minLength )
				{
					if ( is_complete )
					{
						tot_fibers++;
						tot_connections += matrix_update( fiber, step );
					}
				}
			} // seedDir loop
		} // seedNum loop
		printf("\r   [ %5.1f%% ]", 100.0 * (double)percent / (double)tot);

	} // niiSEED loop
	printf("\r   [ %d/%d connections found ]\n", tot_connections, tot_fibers);

	CONNECTIONS.free();
	matrix_normalize();
	matrix_save();
}



/************************************************************************************************/
/******                                 main__tractography()                               ******/
/************************************************************************************************/
int main__tractography()
{
	ANGLE_thr   = cos(maxAngle/180.0*3.14159265);
	ANGLE_thr_2 = cos(maxAngle_2/180.0*3.14159265);

	/* READING 'ROI_HR_th' dataset */
 	printf("-> Reading 'GRAY MATTER' labels dataset...\n");

 	niiROI = nifti_load<INT16>( ROI_filename );
	if ( niiROI == NULL )
		{ cerr << "\n[ERROR] Unable to open file '"<< ROI_filename <<"'!\n\n"; exit(1); }
	if ( niiROI->hdr.datatype != 4 )
		{ cerr << "\n[ERROR] File '"<< ROI_filename <<"' has a WRONG DATA TYPE! It should be INT16!\n\n"; exit(1); }

	// Create the matrix of the right size
	if ( min( niiROI->img ) != 0 || max( niiROI->img ) != 83 )
		{ cerr << "\n[ERROR] datset contains labels values out of VALID RANGE (0..83)|\n\n"; exit(1); }

	printf("   [ max label = %d ]\n\n", 83);


	/* READING 'ROI_HR_th__forRoiSizeCalc' dataset */
	string ROI_prefix = ROI_filename.substr(0, ROI_filename.length()-4);
 	printf("-> Calculating ROIs volumes from '%s__forRoiSizeCalc.nii' dataset...\n", ROI_prefix.c_str());

 	niiVOL = nifti_load<INT16>( ROI_prefix+"__forRoiSizeCalc.nii" );
	if ( niiVOL == NULL )
		{ cerr << "\n[ERROR] Unable to open file '"<< ROI_prefix <<"__forRoiSizeCalc.nii'!\n\n"; exit(1); }
	if ( niiVOL->hdr.datatype != 4 )
		{ cerr << "\n[ERROR] File '"<< ROI_prefix <<"__forVolCalc.nii' has a WRONG DATA TYPE! It should be INT16!\n\n"; exit(1); }

	// calculate VOLUME of each region
	ROI_size = 0;
	for(int z=0; z<niiVOL->hdr.dim[3] ;z++)
	for(int y=0; y<niiVOL->hdr.dim[2] ;y++)
	for(int x=0; x<niiVOL->hdr.dim[1] ;x++)
	{
		int value = niiVOL->img(x,y,z);
		if (value<1 || value>83) continue;
		ROI_size(value-1)++;
	}

	printf("   [ OK ]\n\n");


	/* CREATING dataset for storing CONENCTIONS between ROIs */
 	printf("-> CREATING dataset for storing CONNECTIONS between ROIs ...\n");

	CONNECTIONS.resize( niiROI->hdr.dim[1], niiROI->hdr.dim[2], niiROI->hdr.dim[3], 83 );
	CONNECTIONS = 0;

	printf("   [ %dx%dx%dx%d dataset created ]\n\n", CONNECTIONS.extent(0),CONNECTIONS.extent(1),CONNECTIONS.extent(2),CONNECTIONS.extent(3));


	/* READING 'B0' dataset */
	string B0_filename = BASE_filename + "b0.nii";

	cout <<COLOR(37,40,1)<< "\n-> Reading 'B0' dataset...\n" <<COLOR_reset;

 	NII<INT16>* niiB0 = nifti_load<INT16>( B0_filename );
	if ( niiB0 == NULL )
		{ cerr << "\n"<<COLOR_strERR<<"Unable to open file '"<< B0_filename <<"'!\n\n"<<COLOR_reset; exit(1); }
	if ( niiB0->hdr.datatype != 4 )
		{ cerr << "\n"<<COLOR_strERR<<"File '"<< B0_filename <<".nii' has a WRONG DATA TYPE! It should be INT16!\n\n"<<COLOR_reset; exit(1); }

	cout <<"   [ OK ]\n\n";


	/* READING the gradients' directions file */
	string dirlistFilename = "./181_vecs.dat";

	cout <<COLOR(37,40,1)<< "-> Reading 'ODF DIRECTIONS' list...\n" <<COLOR_reset;

	Array<float,2> dirlist(181,3);

	FILE* fp = fopen(dirlistFilename.c_str(),"r");
	int tmp = fread((char*)dirlist.data(),1,4*3*181,fp);
	fclose(fp);

	cout <<"   [ OK ]\n\n";


	/* calculate QFORM matrix (needed for correct reorientation of gradient directions) */
	cout <<COLOR(37,40,1)<< "-> Reorienting GRADIENT DIRECTIONS...\n" <<COLOR_reset;

	float d = niiB0->hdr.quatern_d;
	float c = niiB0->hdr.quatern_c;
	float b = niiB0->hdr.quatern_b;
	float a = sqrt(1.0-(b*b+c*c+d*d));

	Array<float,2> QFORM(3,3);
	QFORM = a*a+b*b-c*c-d*d, 2*b*c-2*a*d, 2*b*d+2*a*c,
		2*b*c+2*a*d, a*a+c*c-b*b-d*d, 2*c*d-2*a*b,
		2*b*d-2*a*c, 2*c*d+2*a*b, a*a+d*d-c*c-b*b;

	// so far, I work only with (X-,Y-,Z+) orientation (as in MATLAB)
	if ( QFORM(0,0)!=-1 || QFORM(1,0)!=0  || QFORM(2,0)!=0 ||
	 	 QFORM(0,1)!=0  || QFORM(1,1)!=-1 || QFORM(2,1)!=0 ||
	     QFORM(0,2)!=0  || QFORM(1,2)!=0  || QFORM(2,2)!=1 )
	{
		cerr << "\n\n" <<COLOR_strERR<< "The 'qform' is not handled by this tractography software!\n"<< COLOR_reset;
		cerr << "\n   qform = "<< QFORM << "\n\n";
	}

	for(int i=0; i<181 ;i++) {
		Array<float,1> tmp( dirlist(i,Range(0,2)) );
 		dirlist(i,0) = tmp(0)*QFORM(0,0) + tmp(1)*QFORM(1,0) + tmp(2)*QFORM(2,0);
		dirlist(i,1) = tmp(0)*QFORM(0,1) + tmp(1)*QFORM(1,1) + tmp(2)*QFORM(2,1);
		dirlist(i,2) = tmp(0)*QFORM(0,2) + tmp(1)*QFORM(1,2) + tmp(2)*QFORM(2,2);
		dirlist(i,1) = -dirlist(i,1);		// [NOTE] don't know why
	}

	cout <<"   [ OK ]\n\n";


	/* READING 'MASK' dataset */
	cout <<COLOR(37,40,1)<< "-> Reading 'MASK' dataset...\n" <<COLOR_reset;

	NII<UINT8>* niiMASK = nifti_load<UINT8>( MASK_filename );
	if ( niiMASK == NULL )
		{ cerr << "\n" <<COLOR_strERR<< "Unable to open file '"<< MASK_filename <<"'!\n\n"<< COLOR_reset; exit(1); }
	if ( niiMASK->hdr.datatype != 2 )
		{ cerr << "\n" <<COLOR_strERR<< "File '"<< MASK_filename <<".nii' has a WRONG DATA TYPE! It should be UINT8!\n\n"<< COLOR_reset; exit(1); }

	printf("      dim   : %d x %d x %d\n", niiMASK->hdr.dim[1],niiMASK->hdr.dim[2],niiMASK->hdr.dim[3]);
	printf("      pixdim: %.4f x %.4f x %.4f\n", niiMASK->hdr.pixdim[1],niiMASK->hdr.pixdim[2],niiMASK->hdr.pixdim[3]);

	cout <<"   [ OK ]\n\n";



/*--------------*/
/*  FIRST STIX  */
/*--------------*/
	Array< Array<float,2>,3>* 	STIX;

	/* READING 'ODF' dataset */
	string ODF_filename = BASE_filename + "odf.nii";

	cout <<COLOR(37,40,1)<< "-> Reading 'ODF' dataset...\n" <<COLOR_reset;

	NII<FLOAT32>* niiODF = nifti_load<FLOAT32>( ODF_filename );
	if ( niiODF == NULL )
		{ cerr << "\n" <<COLOR_strERR<< "Unable to open file '"<< ODF_filename <<"'!\n\n"<< COLOR_reset; exit(1); }
	if ( niiODF->hdr.datatype != 16 )
		{ cerr << "\n" <<COLOR_strERR<< "File '"<< ODF_filename <<".nii' has a WRONG DATA TYPE! It should be FLOAT32!\n\n"<< COLOR_reset; exit(1); }

	printf("      dim   : %d x %d x %d\n", niiODF->hdr.dim[2],niiODF->hdr.dim[3],niiODF->hdr.dim[4]);
	printf("      pixdim: %.4f x %.4f x %.4f\n", niiODF->hdr.pixdim[2],niiODF->hdr.pixdim[3],niiODF->hdr.pixdim[4]);

	cout <<"   [ OK ]\n\n";


	// check for the FOV between wm mask and ODF
	if ( niiMASK->hdr.dim[1]*niiMASK->hdr.pixdim[1] != niiODF->hdr.dim[2]*niiODF->hdr.pixdim[2] ||
		 niiMASK->hdr.dim[2]*niiMASK->hdr.pixdim[2] != niiODF->hdr.dim[3]*niiODF->hdr.pixdim[3] ||
		 niiMASK->hdr.dim[3]*niiMASK->hdr.pixdim[3] != niiODF->hdr.dim[4]*niiODF->hdr.pixdim[4] )
	{
		cout <<"\n" <<COLOR_strWAR<< "The FOV doesn't match between WM MASK and ODF! The software could CRASH or give weird results!\n\n"<< COLOR_reset;
	}


	/* READING 'MAX' dataset */
	string MAX_filename = BASE_filename + "max.nii";

	cout <<COLOR(37,40,1)<< "-> Reading 'MAX' dataset...\n" <<COLOR_reset;

	NII<INT16>* niiMAX = nifti_load<INT16>( MAX_filename );
	if ( niiMAX == NULL )
		{ cerr << "\n" <<COLOR_strERR<< "Unable to open file '"<< MAX_filename <<"'!\n\n"<< COLOR_reset; exit(1); }
	if ( niiMAX->hdr.datatype != 4 )
		{ cerr << "\n" <<COLOR_strERR<< "File '"<< MAX_filename <<".nii' has a WRONG DATA TYPE! It should be INT16!\n\n"<< COLOR_reset; exit(1); }

	cout <<"   [ OK ]\n\n";


	/* CREATE STIX structure */
	cout <<COLOR(37,40,1)<< "-> Creating STIX structure...\n" <<COLOR_reset;

	STIX = new Array< Array<float,2>,3>( niiODF->hdr.dim[2], niiODF->hdr.dim[3], niiODF->hdr.dim[4] );
	Array<float,1> 				dir(3);
	int 						nMax;

	for(int x=0; x<niiODF->hdr.dim[2] ;x++)
		for(int y=0; y<niiODF->hdr.dim[3] ;y++)
			for(int z=0; z<niiODF->hdr.dim[4] ;z++)
			{
				nMax = count( niiMAX->img(Range::all(),x,y,z)==1 );
				(*STIX)(x,y,z).resize(nMax,3);

				for(int i=0,d=0; d<nMax ;i++)
					if ( niiMAX->img(i,x,y,z)==1 )
					{
						dir(0) = dirlist(i,0) * niiODF->img(i,x,y,z);
						dir(1) = dirlist(i,1) * niiODF->img(i,x,y,z);
						dir(2) = dirlist(i,2) * niiODF->img(i,x,y,z);
						normalize(dir);

						(*STIX)(x,y,z)(d++,Range(0,2)) = dir;
					}
			}

	niiODF->img.free();
	niiMAX->img.free();
	cout <<"   [ OK ]\n\n";



/*---------------*/
/*  SECOND STIX  */
/*---------------*/
	Array< Array<float,2>,3>* 	STIX2;


	/* READING 'ODF' dataset */
	ODF_filename = BASE_filename_2 + "odf.nii";

	if ( !BASE_filename_2.empty() )
	{
		cout <<COLOR(37,40,1)<< "-> Reading 'ODF/2' dataset...\n" <<COLOR_reset;

		niiODF = nifti_load<FLOAT32>( ODF_filename );
		if ( niiODF == NULL )
		{
			cout << "\n" <<COLOR_strERR<< "Unable to open auxiliary odf/max\n\n"<< COLOR_reset;
			exit(1);
		}
		else
		{
			if ( niiODF->hdr.datatype != 16 )
				{ cerr << "\n" <<COLOR_strERR<< "File '"<< ODF_filename <<".nii' has a WRONG DATA TYPE! It should be FLOAT32!\n\n"<< COLOR_reset; exit(1); }

			printf("      dim   : %d x %d x %d\n", niiODF->hdr.dim[2],niiODF->hdr.dim[3],niiODF->hdr.dim[4]);
			printf("      pixdim: %.4f x %.4f x %.4f\n", niiODF->hdr.pixdim[2],niiODF->hdr.pixdim[3],niiODF->hdr.pixdim[4]);

			printf("   [ OK ]\n\n");


			/* READING 'MAX' dataset */
			MAX_filename = BASE_filename_2 + "max.nii";

			cout <<COLOR(37,40,1)<< "-> Reading 'MAX/2' dataset...\n" <<COLOR_reset;

			niiMAX = nifti_load<INT16>( MAX_filename );
			if ( niiMAX == NULL )
				{ cerr << "\n" <<COLOR_strERR<< "Unable to open file '"<< MAX_filename <<"'!\n\n"<< COLOR_reset; exit(1); }
			if ( niiMAX->hdr.datatype != 4 )
				{ cerr << "\n" <<COLOR_strERR<< "File '"<< MAX_filename <<".nii' has a WRONG DATA TYPE! It should be INT16!\n\n"<< COLOR_reset; exit(1); }

			cout <<"   [ OK ]\n\n";


			/* CREATE STIX structure */
			cout <<COLOR(37,40,1)<< "-> Creating STIX/2 structure...\n" <<COLOR_reset;

			STIX2 = new Array< Array<float,2>,3>( niiODF->hdr.dim[2], niiODF->hdr.dim[3], niiODF->hdr.dim[4] );

			for(int x=0; x<niiODF->hdr.dim[2] ;x++)
				for(int y=0; y<niiODF->hdr.dim[3] ;y++)
					for(int z=0; z<niiODF->hdr.dim[4] ;z++)
					{
						nMax = count( niiMAX->img(Range::all(),x,y,z)==1 );
						(*STIX2)(x,y,z).resize(nMax,3);

						for(int i=0,d=0; d<nMax ;i++)
							if ( niiMAX->img(i,x,y,z)==1 )
							{
								dir(0) = dirlist(i,0) * niiODF->img(i,x,y,z);
								dir(1) = dirlist(i,1) * niiODF->img(i,x,y,z);
								dir(2) = dirlist(i,2) * niiODF->img(i,x,y,z);
								normalize(dir);

								(*STIX2)(x,y,z)(d++,Range(0,2)) = dir;
							}
					}

			niiODF->img.free();
			niiMAX->img.free();
			cout <<"   [ OK ]\n\n";
		}
	}
	else
	{
		STIX2 = NULL;
	}


/*------------------------*/
/*  Perform TRACTOGRAPHY  */
/*------------------------*/

	/* Run TRACTOGRAPHY */
	cout <<COLOR(37,40,1)<< "-> Performing TRACTOGRAPHY...\n" <<COLOR_reset;

	clock_t start_time = time(NULL);

 	streamline(STIX, STIX2, niiMAX, niiMASK, niiMASK);

	double elapsed_time = (time(NULL)-start_time);
	printf("   Time elapsed: %dh %d' %d''\n", int(elapsed_time/3600.0), (int)(elapsed_time/60.0), (int)fmod(elapsed_time,60.0));

	cout <<"\n";
}

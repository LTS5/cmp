#include <random/uniform.h>
#include <time.h>


typedef Array<float,2> FIBER;


/* GLOBAL variables */
extern 	string 	CMT_HOME, BASE_filename, MASK_filename, BASE_outname, BASE_filename_2;
extern 	float	maxAngle, maxAngle_2;
extern 	int		CONFIG__seeds;

extern	int 	CONFIG__minLength;
extern	float	CONFIG__stepSize;
extern	int		CONFIG__maxSteps;

float	ANGLE_thr;
float	ANGLE_thr_2;



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
void streamline(Array<Array<float,2>,3>* STIX, Array<Array<float,2>,3>* STIX2, NII<FLOAT32>* niiODF, NII<UINT8>* niiMASK, NII<UINT8>* niiSEED)
{
	FIBER*			 	fiber = new FIBER(3,CONFIG__maxSteps);
	FIBER				tmp;
	Array<float,1> 		COORD(3), seed_COORD(3), dir(3);
	Array<int,1> 		VOXEL_stix(3), VOXEL_wm(3);
	int 				step, totDir, idx, is_complete, tot_fibers = 0, tot_orphans = 0;
	short int			dim[3]    = {niiMASK->hdr.dim[1], niiMASK->hdr.dim[2], niiMASK->hdr.dim[3]};
	float				pixdim[3] = {niiMASK->hdr.pixdim[1], niiMASK->hdr.pixdim[2], niiMASK->hdr.pixdim[3]};
	float				ratio[3]  = {niiMASK->hdr.pixdim[1]/niiODF->hdr.pixdim[2], niiMASK->hdr.pixdim[2]/niiODF->hdr.pixdim[3], niiMASK->hdr.pixdim[3]/niiODF->hdr.pixdim[4]};

    ranlib::Uniform<float> 	uniformGenerator;
    uniformGenerator.seed( (unsigned int)time(0) );


	// create ".trk" file(s)
	FILE* TRKc_fp = TRK__create( BASE_outname + ".trk", dim, pixdim );

	/* cycle on each voxel = 1 of the SEED mask */
	int percent = 0, tot = dim[0]*dim[1]*dim[2];
	for(int z=0; z < dim[2] ;z++)
	for(int y=0; y < dim[1] ;y++)
	for(int x=0; x < dim[0] ;x++)
	{
		percent++;
		if ( niiSEED->img(x,y,z)==0 || niiMASK->img(x,y,z)==0 ) continue;

		for(int seedNum=0; seedNum<CONFIG__seeds ;seedNum++)
		{
			// SETUP
 			seed_COORD = (float)x+uniformGenerator.random()-0.5, (float)y+uniformGenerator.random()-0.5, (float)z+uniformGenerator.random()-0.5;
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


				/* SAVE fiber to .trk file */
				if ( (step-1)*CONFIG__stepSize*pixdim[0] >= CONFIG__minLength )
				{
					if ( is_complete )
					{
						TRK__append( TRKc_fp, fiber, step, pixdim );
						tot_fibers++;
					}
 					else
					{
						tot_orphans++;
					}
				}

			} // seedDir loop
		} // seedNum loop
		printf("\r   [ %5.1f%% ]", 100.0 * (double)percent / (double)tot);

	} // niiSEED loop
	printf("\r   [ 100.0%% ]\n");


	// write the TOTAL number of found fibers
	fseek(TRKc_fp, 1000-12, SEEK_SET);
	fwrite((char*)&tot_fibers, 1, 4, TRKc_fp);
	fclose(TRKc_fp);

	printf("\n   %d fibers found and %d still orphans!\n", tot_fibers, tot_orphans);
}



/************************************************************************************************/
/******                                 main__tractography()                               ******/
/************************************************************************************************/
int main__tractography()
{
	ANGLE_thr   = cos(maxAngle/180.0*3.14159265);
	ANGLE_thr_2 = cos(maxAngle_2/180.0*3.14159265);

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
	string dirlistFilename = CMT_HOME+"/c++/bin/181_vecs.dat";

	cout <<COLOR(37,40,1)<< "-> Reading 'ODF DIRECTIONS' list...\n" <<COLOR_reset;

	Array<float,2> dirlist(181,3);

	FILE* fp = fopen(dirlistFilename.c_str(),"r");
	if (fp==NULL)
		{ cerr << "\n"<<COLOR_strERR<<"Unable to open file '"<< dirlistFilename <<"'!\n\n"<<COLOR_reset; exit(1); }
	size_t bytesRead = fread((char*)dirlist.data(),1,4*3*181,fp);
	fclose(fp);

	// calculate NEIGHBORS of each vertex (used later for max computation)
	vector<int> neigh[181];

	for (int d=0;d<181;d++)
	{
		neigh[d].clear();
		for (int d2=0;d2<2*181;d2++)
		{
			int coef=1;
			int d1=d2;
			if (d2>=181)
			{
				d1=d2-181;
				coef=-1;
			}
			float dist = pow(dirlist(d,0)-coef*dirlist(d1,0),2)+
						 pow(dirlist(d,1)-coef*dirlist(d1,1),2)+
						 pow(dirlist(d,2)-coef*dirlist(d1,2),2);
			if (dist<0.05)
				neigh[d].push_back(d1);
		}
	}

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


	/* MAX CALCULATION */
	Array<unsigned char,4> MAXs(niiODF->hdr.dim[2], niiODF->hdr.dim[3], niiODF->hdr.dim[4], 181);

	for(int x=0; x<niiODF->hdr.dim[2] ;x++)
		for(int y=0; y<niiODF->hdr.dim[3] ;y++)
			for(int z=0; z<niiODF->hdr.dim[4] ;z++)
			{
				for (int d=0; d<181; d++)
				{
					int max=d;
					for (int ct=0; ct<neigh[d].size(); ct++)
					{
						int d1 = neigh[d][ct];
						if ( niiODF->img(d1,x,y,z) > niiODF->img(max,x,y,z) ) max=d1;
					}
					if ( max==d && niiODF->img(d,x,y,z)>0 )
						MAXs(x,y,z,d) = 1;
					else
						MAXs(x,y,z,d) = 0;
				}
			}


	/* CREATE STIX structure */
	cout <<COLOR(37,40,1)<< "-> Creating STIX structure...\n" <<COLOR_reset;

	STIX = new Array< Array<float,2>,3>( niiODF->hdr.dim[2], niiODF->hdr.dim[3], niiODF->hdr.dim[4] );
	Array<float,1> 				dir(3);
	int 						nMax;

	for(int x=0; x<niiODF->hdr.dim[2] ;x++)
		for(int y=0; y<niiODF->hdr.dim[3] ;y++)
			for(int z=0; z<niiODF->hdr.dim[4] ;z++)
			{
				nMax = count( MAXs(x,y,z,Range::all())==1 );
				(*STIX)(x,y,z).resize(nMax,3);

				for(int i=0,d=0; d<nMax ;i++)
					if ( MAXs(x,y,z,i)==1 )
					{
						dir(0) = dirlist(i,0) * niiODF->img(i,x,y,z);
						dir(1) = dirlist(i,1) * niiODF->img(i,x,y,z);
						dir(2) = dirlist(i,2) * niiODF->img(i,x,y,z);
						normalize(dir);

						(*STIX)(x,y,z)(d++,Range(0,2)) = dir;
					}
			}

	niiODF->img.free();
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


			/* MAX CALCULATION */
			for(int x=0; x<niiODF->hdr.dim[2] ;x++)
				for(int y=0; y<niiODF->hdr.dim[3] ;y++)
					for(int z=0; z<niiODF->hdr.dim[4] ;z++)
					{
						for (int d=0; d<181; d++)
						{
							int max=d;
							for (int ct=0; ct<neigh[d].size(); ct++)
							{
								int d1 = neigh[d][ct];
								if ( niiODF->img(d1,x,y,z) > niiODF->img(max,x,y,z) ) max=d1;
							}
							if ( max==d && niiODF->img(d,x,y,z)>0 )
								MAXs(x,y,z,d) = 1;
							else
								MAXs(x,y,z,d) = 0;
						}
					}


			/* CREATE STIX structure */
			cout <<COLOR(37,40,1)<< "-> Creating STIX/2 structure...\n" <<COLOR_reset;

			STIX2 = new Array< Array<float,2>,3>( niiODF->hdr.dim[2], niiODF->hdr.dim[3], niiODF->hdr.dim[4] );

			for(int x=0; x<niiODF->hdr.dim[2] ;x++)
				for(int y=0; y<niiODF->hdr.dim[3] ;y++)
					for(int z=0; z<niiODF->hdr.dim[4] ;z++)
					{
						nMax = count( MAXs(x,y,z,Range::all())==1 );
						(*STIX2)(x,y,z).resize(nMax,3);

						for(int i=0,d=0; d<nMax ;i++)
							if ( MAXs(x,y,z,i)==1 )
							{
								dir(0) = dirlist(i,0) * niiODF->img(i,x,y,z);
								dir(1) = dirlist(i,1) * niiODF->img(i,x,y,z);
								dir(2) = dirlist(i,2) * niiODF->img(i,x,y,z);
								normalize(dir);

								(*STIX2)(x,y,z)(d++,Range(0,2)) = dir;
							}
					}

			niiODF->img.free();
			cout <<"   [ OK ]\n\n";
		}
	}
	else
	{
		STIX2 = NULL;
	}

	MAXs.free();


/*------------------------*/
/*  Perform TRACTOGRAPHY  */
/*------------------------*/

	/* Run TRACTOGRAPHY */
	cout <<COLOR(37,40,1)<< "-> Performing TRACTOGRAPHY...\n" <<COLOR_reset;

	clock_t start_time = time(NULL);

 	streamline(STIX, STIX2, niiODF, niiMASK, niiMASK);

	double elapsed_time = (time(NULL)-start_time);
	printf("   Time elapsed: %dh %d' %d''\n", int(elapsed_time/3600.0), (int)(elapsed_time/60.0), (int)fmod(elapsed_time,60.0));

	cout <<"\n";
}

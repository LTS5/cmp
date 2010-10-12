extern string	TRK_filename, ROI_filename, CMX_basename, MEASURE;





/************************************************************************************************/
/******                                   main__cmx_matrix()                               ******/
/************************************************************************************************/
int main__cmx_matrix()
{
	/* READING 'ROI_HR_th' dataset */
 	printf("-> Reading 'GRAY MATTER' labels dataset...\n");

 	NII<INT16>* niiROI = nifti_load<INT16>( ROI_filename );
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

 	NII<INT16>* niiVOL = nifti_load<INT16>( ROI_prefix+"__forRoiSizeCalc.nii" );
	if ( niiVOL == NULL )
		{ cerr << "\n[ERROR] Unable to open file '"<< ROI_prefix <<"__forRoiSizeCalc.nii'!\n\n"; exit(1); }
	if ( niiVOL->hdr.datatype != 4 )
		{ cerr << "\n[ERROR] File '"<< ROI_prefix <<"__forVolCalc.nii' has a WRONG DATA TYPE! It should be INT16!\n\n"; exit(1); }

	// calculate VOLUME of each region
	Array<int,1> ROI_size(83);	// roi numbers are in 0..82 range (LABEL-1)
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

	Array<UINT8,4> CONNECTIONS;
	CONNECTIONS.resize( niiROI->hdr.dim[1], niiROI->hdr.dim[2], niiROI->hdr.dim[3], 83 );
	CONNECTIONS = 0;

	printf("   [ %dx%dx%dx%d dataset created ]\n\n", CONNECTIONS.extent(0),CONNECTIONS.extent(1),CONNECTIONS.extent(2),CONNECTIONS.extent(3));


	/* OPEN the '.trk' file */
	printf("-> Opening '.trk' file...\n");

	TRK__hdr 	hdr;
	FILE* 		trk = TRK__open( TRK_filename.c_str(), &hdr );

	printf("   [ %d fibers found ]\n\n", hdr.n_count);


	/* CYCLE through all the fibers */
	printf("-> Processing fibers...\n");

	Array<float,2>	fiber(3,1000);
	Array<int,1>  	P1(3), P2(3);
	short int		L1, L2;

	Array<float,2> matrix(83,83);
	matrix = 0;

	int tot = 0;
	for(int i=0; i<hdr.n_count ; i++)
	{
		printf("\r   [ %5.1f%% ]", 100.0 * (double)i / (double)hdr.n_count);
		TRK__read(trk, &fiber);


		// FIRST endpoint (P1,L1)
		fiber__mm2vox( fiber(Range(0,2),0), &P1, hdr.dim, hdr.voxel_size);
		L1 = niiROI->img( P1(0),P1(1),P1(2) );
		if (L1<1 || L1>83)
		{
			// try with the next point in the fiber
			fiber__mm2vox( fiber(Range(0,2),1), &P1, hdr.dim, hdr.voxel_size);
			L1 = niiROI->img( P1(0),P1(1),P1(2) );
			if (L1<1 || L1>83) continue;
		}


		// SECOND endpoint (P2,L2)
		fiber__mm2vox( fiber(Range(0,2),fiber.extent(1)-1), &P2, hdr.dim, hdr.voxel_size);
		L2 = niiROI->img( P2(0),P2(1),P2(2) );
		if (L2<1 || L2>83)
		{
			// try with the previous point in the fiber
			fiber__mm2vox( fiber(Range(0,2),fiber.extent(1)-2), &P2, hdr.dim, hdr.voxel_size);
			L2 = niiROI->img( P2(0),P2(1),P2(2) );
			if (L2<1 || L2>83) continue;
		}


		// calculate MATRIX value for this connection (P1,L1) --> (P2,L2)
		if ( MEASURE.compare("percentage")==0 )
		{
			// used for "percentage" measure
			if ( CONNECTIONS( P1(0),P1(1),P1(2), L2-1 ) == 0 )
			{
				CONNECTIONS( P1(0),P1(1),P1(2), L2-1 ) = 1;
				matrix(L1-1,L2-1)++;
			}

			if ( CONNECTIONS( P2(0),P2(1),P2(2), L1-1 ) == 0 )
			{
				CONNECTIONS( P2(0),P2(1),P2(2), L1-1 ) = 1;
				matrix(L2-1,L1-1)++;
			}
		}
		else
		{
			// used for "density" and "count" measure
			matrix(L1-1,L2-1)++;
			if ( L1 != L2 ) matrix(L2-1,L1-1)++;
		}

		tot++;
	}
	fclose(trk);
	CONNECTIONS.free();


	// NORMALIZE the value for the ROIs size
	for(int y=0; y<83 ;y++)
	for(int x=y; x<83 ;x++)
	{
		int vol = ROI_size(x) + ROI_size(y);

		if ( MEASURE.compare("percentage")==0 )
		{
			// used for "percentage" measure
			if ( vol <= 0 )		matrix(x,y) = 0;
			else				matrix(x,y) = ( matrix(x,y) + matrix(y,x) ) / vol;
		}
		else
		{
			// used for "count" and "density" measure
			if ( MEASURE.compare("density")==0 )
			{
				// "density"
				if ( vol <= 0 )		matrix(x,y) = 0;
				else				matrix(x,y) = matrix(x,y) / vol;
			}
			else
			{
				// "count"
				matrix(x,y) = matrix(x,y) / tot;
			}
		}

		matrix(y,x) = matrix(x,y);
	}

	printf("\r   [ %d connections found ]\n\n",tot);




	/* WRITE the connection matrix */
	string filename = CMX_basename +"__"+ MEASURE +".dat";
	cout << "-> Saving matrix to '" <<filename<< "'...\n";

 	FILE* fp = fopen(filename.c_str(),"w");
	if (fp == NULL) { printf("\n\n[ERROR] Unable to create file '%s'\n\n", filename.c_str()); exit(1); }

	short resolution = 83;
	fwrite((char*)&resolution, 1, 2, fp);

	for(int y=0; y<83 ;y++)
	for(int x=0; x<83 ;x++)
	{
		float value = matrix(x,y);
		fwrite((char*)&value, 1, 4, fp);	// always float numbers
	}

	fclose(fp);

	cout <<"   [ OK ]\n\n";
}

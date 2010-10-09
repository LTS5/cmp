short resolution = 83;

int main__fibers_stats()
{
	Array<int,2> totFibers(resolution,resolution); totFibers = 0;
	Array<float,2> matrix(resolution,resolution);  matrix = 0;


	/* READING 'SCALAR' dataset */
 	printf("-> Reading 'SCALAR' dataset...\n");

 	NII<FLOAT32>* niiSCALAR = nifti_load<FLOAT32>( MAP_filename );
	if ( niiSCALAR == NULL )
		{ cerr << "\n[ERROR] Unable to open file '"<< MAP_filename <<"'!\n\n"; exit(1); }
	if ( niiSCALAR->hdr.datatype != 16 )
		{ cerr << "\n[ERROR] File '"<< MAP_filename <<"' has a WRONG DATA TYPE! It should be FLOAT32!\n\n"; exit(1); }
	printf("   [ OK ]\n\n");


	/* READING 'GM MASK' dataset */
 	printf("-> Reading 'GM MASK' dataset...\n");

 	NII<INT16>* niiROI = nifti_load<INT16>( ROI_filename );
	if ( niiROI == NULL )
		{ cerr << "\n[ERROR] Unable to open file '"<< ROI_filename <<"'!\n\n"; exit(1); }
	if ( niiROI->hdr.datatype != 4 )
		{ cerr << "\n[ERROR] File '"<< ROI_filename <<"' has a WRONG DATA TYPE! It should be INT16!\n\n"; exit(1); }

	if ( min(niiROI->img) < 0 || max(niiROI->img) > resolution )
		{ cerr << "\n[ERROR] datset contains labels values out of VALID RANGE (0.."<< resolution <<")|\n\n"; exit(1); }

	printf("   [ max label = %d ]\n\n", resolution);


	/* OPEN the '.trk' file */
	printf("-> Opening '.trk' file...\n");

	TRK__hdr 	hdr;
	FILE* 		trk = TRK__open( TRK_filename.c_str(), &hdr );

	printf("   [ %d fibers found ]\n\n", hdr.n_count);


	/* check for the FOV between the datasets */
	if ( niiROI->hdr.dim[1]!=niiSCALAR->hdr.dim[1] || niiROI->hdr.dim[2]!=niiSCALAR->hdr.dim[2] || niiROI->hdr.dim[3]!=niiSCALAR->hdr.dim[3] ||
		 niiROI->hdr.pixdim[1]!=niiSCALAR->hdr.pixdim[1] || niiROI->hdr.pixdim[2]!=niiSCALAR->hdr.pixdim[2] || niiROI->hdr.pixdim[3]!=niiSCALAR->hdr.pixdim[3]
		)
	{
		cout <<"\n" <<COLOR_strERR<< "SCALAR MAP and GM MASK have different geometries!\n\n"<< COLOR_reset;
		exit(1);
	}


	/* CYCLE through all the fibers */
	printf("-> Processing fibers...\n");

	Array<float,2>		fiber(3,1000);
	Array<int,1>  		P(3);

	Array<int,1>		LABELS(1000);			// to keep labels along a track
	Array<float,1>		SCALARS(1000);			// to keep values along a track
	Array<int,1>		ENDPOINTS(100);			// to keep segments endpoints
	Array<float,1>		SUM(99);				// to keep asum of values in each sub-fiber
	Array<int,1>		LEN(99);

	short int			n;						// number of endpoints
	short int			L, Lprev;

	int tot = 0;
	float	scalar_value;
	for(int f=0; f< hdr.n_count ; f++)
	{
		printf("\r   [ %5.1f%% ]", 100.0 * (double)f / (double)hdr.n_count);
		TRK__read(trk, &fiber);


		// search for sub-fibers
		n = 0;
		L = 0;
		for(int i=0; i<fiber.extent(1) ;i++)
		{
			fiber__mm2vox( fiber(Range(0,2),i), &P, hdr.dim, hdr.voxel_size);

			Lprev = L;
			L = niiROI->img( P(0),P(1),P(2) );
			LABELS(i)  = L;
			SCALARS(i) = niiSCALAR->img( P(0),P(1),P(2) );

			if ( L>=1 && L<=resolution && L!=Lprev )
			{
				// create another endpoint
				ENDPOINTS(n)	= i;
				SUM(n)			= 0;
				LEN(n)			= 0;
				n++;
			}
			else if (L==0 && n>0) {
				SUM(n-1) += SCALARS(i);	// sum this point only if it is not in GM
				LEN(n-1)++;
			}
		}
		if (n<2) continue;

		// calculate the average SCALAR value along each sub-fiber (each combination of endpoints)
		float partial_sum, partial_len;
		int L1, L2;

		if (DEBUG==1 && n>2)
		{
			cout << "<<<<<  fiber #"<< f <<" >>>>>"<<endl;
			cout <<"LABELS  = "<< LABELS(Range(0,fiber.extent(1)-1)) <<endl;
			cout <<"SCALARS = "<< SCALARS(Range(0,fiber.extent(1)-1)) <<endl;
			cout <<"ENDPOINTS = "<< ENDPOINTS(Range(0,n-1)) <<endl;
			cout <<"SUM = "<< SUM(Range(0,n-1)) <<endl;
			cout <<"LEN = "<< LEN(Range(0,n-1)) <<endl;
			cout << endl;
		}

		for(int i=0; i<n-1 ;i++)
		{
			partial_sum = 0;
			partial_len = 0;
			for(int j=i+1; j<n ;j++)
			{
				partial_sum += SUM(j-1);
				partial_len += LEN(j-1);
				if ( partial_len >= 5 )
				{
				    tot++;

					// update the matrix
					L1 = LABELS(ENDPOINTS(i))-1;
					L2 = LABELS(ENDPOINTS(j))-1;
					matrix( L1,L2 ) += partial_sum / partial_len;
					matrix( L2,L1 ) = matrix( L1,L2 );
					totFibers( L1,L2 )++;
					if ( L1 != L2 )	totFibers( L2, L1 )++;
				}
			}
		}
	}
	fclose(trk);

	printf("\n\n   [ %d connections found ]\n", tot);


	// calc the average value for ALL the fibers between two ROIs
	for(int i=0; i<resolution ;i++)
	for(int j=i; j<resolution ;j++)
	{
		if ( totFibers(i,j)>0 )
			matrix(i,j) = matrix(i,j) / totFibers(i,j);
		else
			matrix(i,j) = 0;
		matrix(j,i) = matrix(i,j);
	}


	/* WRITE the matrix containing the average scalar values for each regions pair */
	printf("\n-> Saving matrix to '%s'...\n", CMX_filename.c_str());

 	FILE* fp = fopen(CMX_filename.c_str(),"w");
	if (fp == NULL) { printf("\n\n[ERROR] Unable to create file '%s'\n\n",CMX_filename.c_str()); exit(1); }

	fwrite((char*)&resolution, 1, 2, fp);

	for(int y=0; y<resolution ;y++)
	for(int x=0; x<resolution ;x++)
	{
		float value = matrix(x,y);
		fwrite((char*)&value, 1, 4, fp);	// always float numbers
	}

	fclose(fp);

	printf("   [ OK ]\n\n");
	return 0;
}

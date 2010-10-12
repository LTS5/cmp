
int matrix_update(Array<float,2>* fiber, short int step)
{
	Array<int,1>  	P1(3), P2(3);
	short int		L1, L2;

	// FIRST endpoint (P1,L1)
	P1 = round((*fiber)(0,0)), round((*fiber)(1,0)), round((*fiber)(2,0));
	L1 = niiROI->img( P1(0),P1(1),P1(2) );
	if (L1<1 || L1>83)
	{
		// try with the next point in the fiber
		P1 = round((*fiber)(0,1)), round((*fiber)(1,1)), round((*fiber)(2,1));
		L1 = niiROI->img( P1(0),P1(1),P1(2) );
		if (L1<1 || L1>83) return 0;
	}

	// SECOND endpoint (P2,L2)
	P2 = round((*fiber)(0,step-1)), round((*fiber)(1,step-1)), round((*fiber)(2,step-1));
	L2 = niiROI->img( P2(0),P2(1),P2(2) );
	if (L2<1 || L2>83)
	{
		// try with the previous point in the fiber
		P2 = round((*fiber)(0,step-2)), round((*fiber)(1,step-2)), round((*fiber)(2,step-2));
		L2 = niiROI->img( P2(0),P2(1),P2(2) );
		if (L2<1 || L2>83) return 0;
	}


	/* calculate MATRIX(s) value for this connection (P1,L1) --> (P2,L2) */

	// "percentage" measure (index=0)
	if ( CONNECTIONS( P1(0),P1(1),P1(2), L2-1 ) == 0 )
	{
		CONNECTIONS( P1(0),P1(1),P1(2), L2-1 ) = 1;
		matrix(L1-1,L2-1,0)++;
	}

	if ( CONNECTIONS( P2(0),P2(1),P2(2), L1-1 ) == 0 )
	{
		CONNECTIONS( P2(0),P2(1),P2(2), L1-1 ) = 1;
		matrix(L2-1,L1-1,0)++;
	}

	// "density" and "count" measures (index=1 and index=2)
	matrix(L1-1,L2-1,1)++;
	matrix(L1-1,L2-1,2)++;
	if ( L1 != L2 ) {
		matrix(L2-1,L1-1,1)++;
		matrix(L2-1,L1-1,2)++;
	}

	return 1;
}




void matrix_normalize()
{
	int vol;

	// NORMALIZE the value for the ROIs size
	for(int y=0; y<83 ;y++)
	for(int x=y; x<83 ;x++)
	{
		vol = ROI_size(x) + ROI_size(y);

		// "percentage"
		if ( vol <= 0 )		matrix(x,y,0) = 0;
		else				matrix(x,y,0) = ( matrix(x,y,0) + matrix(y,x,0) ) / vol;

		// "density"
		if ( vol <= 0 )		matrix(x,y,1) = 0;
		else				matrix(x,y,1) = matrix(x,y,1) / vol;

		// "count"
		matrix(x,y,2) = matrix(x,y,2);

		matrix(y,x,0) = matrix(x,y,0);
		matrix(y,x,1) = matrix(x,y,1);
		matrix(y,x,2) = matrix(x,y,2);
	}
}


/* SAVE the connection matrix(s) to disk */
void matrix_save()
{
	cout << "-> Saving matrix(s)...\n";

	string filename0, filename1, filename2;

	filename0 = BASE_outname +"__percentage.dat";
	filename1 = BASE_outname +"__density.dat";
	filename2 = BASE_outname +"__count.dat";

 	FILE* fp0 = fopen(filename0.c_str(),"w");
	if (fp0 == NULL) { printf("\n\n[ERROR] Unable to create file '%s'\n\n", filename0.c_str()); exit(1); }
 	FILE* fp1 = fopen(filename1.c_str(),"w");
	if (fp1 == NULL) { printf("\n\n[ERROR] Unable to create file '%s'\n\n", filename1.c_str()); exit(1); }
 	FILE* fp2 = fopen(filename2.c_str(),"w");
	if (fp2 == NULL) { printf("\n\n[ERROR] Unable to create file '%s'\n\n", filename2.c_str()); exit(1); }

	short resolution = 83;
	fwrite((char*)&resolution, 1, 2, fp0);
	fwrite((char*)&resolution, 1, 2, fp1);
	fwrite((char*)&resolution, 1, 2, fp2);

	float value;
	for(int y=0; y<83 ;y++)
	for(int x=0; x<83 ;x++)
	{
		value = matrix(x,y,0); fwrite((char*)&value, 1, 4, fp0);
		value = matrix(x,y,1); fwrite((char*)&value, 1, 4, fp1);
		value = matrix(x,y,2); fwrite((char*)&value, 1, 4, fp2);
	}

	fclose(fp0);
	fclose(fp1);
	fclose(fp2);

	cout <<"   [ OK ]\n\n";
}

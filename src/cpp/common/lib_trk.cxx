int CONFIG__maxSteps = 1000;		// [TODO] should be related to the variable defined in tractography.cxx


struct TRK__hdr
{
    char                id_string[6];
    short int           dim[3];
    float               voxel_size[3];
    float               origin[3];
    short int           n_scalars;
    char                scalar_name[10][20];
    short int           n_properties;
    char                property_name[10][20];
    char                reserved[508];
    char                voxel_order[4];
    char                pad2[4];
    float               image_orientation_patient[6];
    char                pad1[2];
    unsigned char       invert_x;
    unsigned char       invert_y;
    unsigned char       invert_z;
    unsigned char       swap_xy;
    unsigned char       swap_yz;
    unsigned char       swap_zx;
    int                 n_count;
    int                 version;
    int                 hdr_size;
};




/************************************************************************************************/
/******                                     .trk files                                     ******/
/************************************************************************************************/
FILE* TRK__create( string filename, short int* DIM, float* PIXDIM )
{
    FILE* fp = fopen(filename.c_str(),"w+b");
	if (fp == NULL) { printf("\n\n[ERROR] Unable to create file '%s'\n\n",filename.c_str()); exit(1); }

	TRK__hdr	hdr;

	sprintf(hdr.id_string,"TRACK");
	for(int i=0; i<3 ;i++)
	{
		hdr.dim[i] 			= DIM[i];
		hdr.voxel_size[i] 	= PIXDIM[i];
		hdr.origin[i] 		= 0;
	}
    hdr.n_scalars = 0;
    hdr.n_properties = 0;
    sprintf(hdr.voxel_order,"LPS");
    sprintf(hdr.pad2,"LPS");
    hdr.image_orientation_patient[0] = 1.0;
	hdr.image_orientation_patient[1] = 0.0;
	hdr.image_orientation_patient[2] = 0.0;
	hdr.image_orientation_patient[3] = 0.0;
	hdr.image_orientation_patient[4] = 1.0;
	hdr.image_orientation_patient[5] = 0.0;
    hdr.pad1[0] = 0;
	hdr.pad1[1] = 0;
    hdr.invert_x = 0;
    hdr.invert_y = 0;
    hdr.invert_z = 0;
    hdr.swap_xy = 0;
    hdr.swap_yz = 0;
    hdr.swap_zx = 0;
    hdr.n_count = 0;
    hdr.version = 1;
    hdr.hdr_size = 1000;

	fwrite((char*)&hdr, 1, 1000, fp);

	return fp;
}



FILE* TRK__open( string filename, TRK__hdr* hdr )
{
	size_t bytesRead;
    FILE* fp = fopen(filename.c_str(),"rb");

	if (fp == NULL) { printf("\n\n[ERROR] Unable to open file '%s'\n\n",filename.c_str()); exit(1); }

	if (hdr != NULL)
		bytesRead = fread((char*)hdr, 1, 1000, fp);
	else
		fseek(fp, 1000, SEEK_SET);

	return fp;
}



//void TRK__append( FILE* fp, Array<float,2>* fiber, int numPoints, float* PIXDIM )
//{
//	if ( numPoints > CONFIG__maxSteps )
//	{
//		char tmp[1000];
//		sprintf(tmp, "  trying to write a fiber with %d points!!!\n\n", numPoints);
//		COLOR_print("\n[ERROR]", COLOR_black,COLOR_red);
//		COLOR_print(tmp, COLOR_red, COLOR_black);
//		exit(1);
//	}
//
//	int 	pos = 0;
//	float 	tmp[3*CONFIG__maxSteps];
//
// 	for(int i=0; i<numPoints ;i++)
// 	{
// 	    tmp[pos++] = ( (*fiber)(0,i)+0.5 ) * PIXDIM[0];
// 	    tmp[pos++] = ( (*fiber)(1,i)+0.5 ) * PIXDIM[1];
// 	    tmp[pos++] = ( (*fiber)(2,i)+0.5 ) * PIXDIM[2];
// 	}
//
//	if ( fwrite((char*)&numPoints, 1, 4, fp) != 4 )
//	{
//		printf("\n\n[ERROR] Unable to write the fiber with %d points! File size is %ld.\n\n", numPoints, ftell(fp));
//		exit(1);
//	}
//
//	fwrite((char*)&tmp, 1, 4*pos, fp);
//}

void TRK__append( FILE* fp, Array<float,2>* fiber, int numPoints, float* PIXDIM )
{
	if ( numPoints > CONFIG__maxSteps )
	{
		char tmp[1000];
		sprintf(tmp, "  trying to write a fiber with %d points!!!\n\n", numPoints);
		COLOR_print("\n[ERROR]", COLOR_black,COLOR_red);
		COLOR_print(tmp, COLOR_red, COLOR_black);
		exit(1);
	}

	int 	pos = 0;
	float 	tmp[3*CONFIG__maxSteps];
	int 	numSaved  = ceil((float)(numPoints-1)/2)+1;

	// save only 1 point out of 2 (in reversed order)
 	for(int i=numPoints-1; i>0 ;i-=2)
 	{
 	    tmp[pos++] = ( (*fiber)(0,i)+0.5 ) * PIXDIM[0];
 	    tmp[pos++] = ( (*fiber)(1,i)+0.5 ) * PIXDIM[1];
 	    tmp[pos++] = ( (*fiber)(2,i)+0.5 ) * PIXDIM[2];
 	}
	// but include always the last one (i.e. the first one in the reversed)
	tmp[pos++] = ( (*fiber)(0,0)+0.5 ) * PIXDIM[0];
	tmp[pos++] = ( (*fiber)(1,0)+0.5 ) * PIXDIM[1];
	tmp[pos++] = ( (*fiber)(2,0)+0.5 ) * PIXDIM[2];

	if (pos != numSaved*3)
	{
		printf("\n\n[ERROR] %d != %d!\n\n", pos, numSaved);
		exit(1);
	}

	if ( fwrite((char*)&numSaved, 1, 4, fp) != 4 )
	{
		printf("\n\n[ERROR] Unable to write the fiber with %d points! File size is %ld.\n\n", numSaved, ftell(fp));
		exit(1);
	}

	fwrite((char*)&tmp, 1, 4*pos, fp);
}


void TRK__read( FILE* fp, Array<float,2>* fiber )
{
	size_t bytesRead;
	int numPoints;
	bytesRead = fread((char*)&numPoints, 1, 4, fp);

	if ( numPoints >= CONFIG__maxSteps || numPoints <= 0 )
	{
		printf("\n\n[ERROR] trying to read a fiber with %d points!!!\n\n", numPoints);
		exit(1);
	}

	fiber->resize(3,numPoints);


	float tmp[3];
 	for(int i=0; i<numPoints; i++)
 	{
		bytesRead = fread((char*)tmp, 1, 12, fp);
 	    (*fiber)(0,i) = tmp[0];
		(*fiber)(1,i) = tmp[1];
		(*fiber)(2,i) = tmp[2];
 	}
}



void fiber__mm2vox( Array<float,1> P_mm, Array<int,1>* P, short int* dim, float* pixdim)
{
	(*P)(0) = round( P_mm(0) / pixdim[0] - 0.5 );
	(*P)(1) = round( P_mm(1) / pixdim[1] - 0.5 );
	(*P)(2) = round( P_mm(2) / pixdim[2] - 0.5 );
	if ( (*P)(0)<0 ) (*P)(0) = 0;
	if ( (*P)(1)<0 ) (*P)(1) = 0;
	if ( (*P)(2)<0 ) (*P)(2) = 0;
	if( (*P)(0) > dim[0]-1 ) (*P)(0) = dim[0]-1;
	if( (*P)(1) > dim[1]-1 ) (*P)(1) = dim[1]-1;
	if( (*P)(2) > dim[2]-1 ) (*P)(2) = dim[2]-1;
}

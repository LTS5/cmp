#ifdef INT_2_BYTES
	typedef	char				INT8;
	typedef	unsigned char		UINT8;
	typedef	int					INT16;
	typedef	unsigned int		UINT16;
	typedef	long				INT32;
	typedef	unsigned long		UINT32;
	typedef	double				FLOAT32;
#else
	typedef	char				INT8;
	typedef	unsigned char		UINT8;
	typedef	short				INT16;
	typedef	unsigned short		UINT16;
	typedef	int					INT32;
	typedef	unsigned int		UINT32;
	typedef	float				FLOAT32;
#endif


template <class T> class NII
{
	public:
		nifti_1_header		hdr;
		Array<T,4>			img;

		NII() { img.setStorage( ColumnMajorArray<4>() ); };
};



/***************************/
/*  MAKE a '.nii' dataset  */
/***************************/
template <class T>
NII<T>* nifti_make( short* dim, float* pixdim )
{
	NII<T>* myNII = new NII<T>;

	try
	{
		myNII->img.resize(dim[0], dim[1], dim[2], dim[3]);
	}
	catch(exception& ex)
    {
		return NULL;
    }

	myNII->hdr.dim[0] = 4;
	myNII->hdr.dim[1] = dim[0];
	myNII->hdr.dim[2] = dim[1];
	myNII->hdr.dim[3] = dim[2];
	myNII->hdr.dim[4] = dim[3];

	myNII->hdr.pixdim[0] = 1;
	myNII->hdr.pixdim[1] = pixdim[0];
	myNII->hdr.pixdim[2] = pixdim[1];
	myNII->hdr.pixdim[3] = pixdim[2];
	myNII->hdr.pixdim[4] = pixdim[3];

	myNII->hdr.sizeof_hdr 	= 348;

	myNII->hdr.magic[0] = 'n';
	myNII->hdr.magic[1] = '+';
	myNII->hdr.magic[2] = '1';
	myNII->hdr.magic[3] = 0;

	nifti_aux_setHdr( myNII );

	return myNII;
}

template <class T> void nifti_aux_setHdr( NII<T>* myNII ) { }

template <> void nifti_aux_setHdr( NII<INT8>* myNII )
{
	myNII->hdr.datatype		= NIFTI_TYPE_INT8;
	myNII->hdr.bitpix 		= 8;
}
template <> void nifti_aux_setHdr( NII<UINT8>* myNII )
{
	myNII->hdr.datatype		= NIFTI_TYPE_UINT8;
	myNII->hdr.bitpix 		= 8;
}

template <> void nifti_aux_setHdr( NII<INT16>* myNII )
{
	myNII->hdr.datatype		= NIFTI_TYPE_INT16;
	myNII->hdr.bitpix 		= 16;
}
template <> void nifti_aux_setHdr( NII<UINT16>* myNII )
{
	myNII->hdr.datatype		= NIFTI_TYPE_UINT16;
	myNII->hdr.bitpix 		= 16;
}

template <> void nifti_aux_setHdr( NII<INT32>* myNII )
{
	myNII->hdr.datatype		= NIFTI_TYPE_INT32;
	myNII->hdr.bitpix 		= 32;
}
template <> void nifti_aux_setHdr( NII<UINT32>* myNII )
{
	myNII->hdr.datatype		= NIFTI_TYPE_UINT32;
	myNII->hdr.bitpix 		= 32;
}

template <> void nifti_aux_setHdr( NII<FLOAT32>* myNII )
{
	myNII->hdr.datatype		= NIFTI_TYPE_FLOAT32;
	myNII->hdr.bitpix 		= 32;
}




/***************************/
/*  LOAD a '.nii' dataset  */
/***************************/
template <class T>
NII<T>* nifti_load( string filename )
{
	NII<T>* myNII = new NII<T>;

	FILE *fp;
	int ret;

	fp = fopen(filename.c_str(),"rb");
	if (fp == NULL)	return NULL;

	ret = fread(&(myNII->hdr), 348, 1, fp);
	if (ret != 1) return NULL;

	ret = fseek(fp, (long)(myNII->hdr.vox_offset), SEEK_SET);
	if (ret != 0) return NULL;

	try
	{
		myNII->img.resize(myNII->hdr.dim[1], myNII->hdr.dim[2], myNII->hdr.dim[3], myNII->hdr.dim[4]);
	}
	catch(exception& ex)
    {
		return NULL;
    }

	ret = fread(myNII->img.data(), sizeof(T), myNII->hdr.dim[1]*myNII->hdr.dim[2]*myNII->hdr.dim[3]*myNII->hdr.dim[4], fp);
	if (ret != myNII->hdr.dim[1]*myNII->hdr.dim[2]*myNII->hdr.dim[3]*myNII->hdr.dim[4]) return NULL;
	fclose(fp);

	return myNII;
}



/***************************/
/*  SAVE a '.nii' dataset  */
/***************************/
template <class T>
int nifti_save( NII<T>* myNII, string filename )
{
	FILE *fp;
	int ret;


	/********** write first 348 bytes of header   */
	fp = fopen(filename.c_str(),"wb");
	if (fp == NULL) return 1;

	ret = fwrite(&(myNII->hdr), 348, 1, fp);
	if (ret != 1) return 1;


	/********** if nii, write extender pad and image data   */
	nifti1_extender pad={0,0,0,0};
	ret = fwrite(&pad, 4, 1, fp);
	if (ret != 1) return 1;

	ret = fwrite(myNII->img.data(), (size_t)(myNII->hdr.bitpix/8), myNII->hdr.dim[1]*myNII->hdr.dim[2]*myNII->hdr.dim[3]*myNII->hdr.dim[4], fp);
	if (ret != myNII->hdr.dim[1]*myNII->hdr.dim[2]*myNII->hdr.dim[3]*myNII->hdr.dim[4]) return 1;
	fclose(fp);

	return 0;
}

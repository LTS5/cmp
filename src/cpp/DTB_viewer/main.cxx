#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <assert.h>
#include <string.h>
using namespace std;

#include <nifti1.h>
#include <blitz/array.h>
using namespace blitz;

#include "lib_nii.cxx"
#include "lib_ui.cxx"


#ifdef __APPLE__
	#include <GLUT/glut.h>
	#include <OpenGL/gl.h>
	#include <OpenGL/glu.h>
#else
	#include <GL/glut.h>
	#include <GL/gl.h>
#endif


int      xrot,yrot,zrot;
int      startx,starty; //per la rotazione con il mouse
int      moving;     //mouse
GLfloat  xtrasl,ytrasl,ztrasl;
GLfloat  zoom;
GLfloat* vect, * vect1;
GLfloat* id, * matrix;
GLfloat* rot,* rot1,* rot2,* rot3;         //matrice per le rotazioni
GLfloat  luce0[4];
int      scrsizex=800,scrsizey=600; //screen
GLuint   w1;

float	scale=1;
int		normalization = 0;

float dir[12][3];


//baricentro
float b1,b2,b3;

int   centerz=0, centerx=0, centery=0;
int   sizex,sizey,sizez;
float pixx,pixy,pixz;

int   vmode=2;
int   proj=2;

vector<int> neigh[181];  	// triangulation


Array<float,2> dirlist(181,3);
NII<FLOAT32>* niiODF;
Array< FLOAT32,4> normODF;
Array< FLOAT32,3> GFA;
float	mapOPACITY = 1;

#include "gl_aux_functions.cxx"
#include "glut_callbacks.cxx"



int main(int argc, char** argv)
{
	char* tmp = getenv("CMT_HOME");
	if ( tmp==NULL )
		{ cerr << "\n"<<COLOR_strERR<<"Environmental variable 'CMT_HOME' not set!\n\n"<<COLOR_reset; exit(1); }
	string CMT_HOME = tmp;

	if ( argc<2 ) {
		cerr << "\n[ERROR] Please specify the BASE_filename of DSI data!\n\n";
		exit(1);
	}
	string BASE_filename = argv[1];


	/* READING the gradients' directions file */
	string dirlistFilename = CMT_HOME + "/c++/bin/181_vecs.dat";

	cout <<"-> Reading 'ODF DIRECTIONS' list...\n";

	FILE* fp = fopen(dirlistFilename.c_str(),"r");
	if (fp==NULL)
		{ cerr << "\n"<<COLOR_strERR<<"Unable to open file '"<< dirlistFilename <<"'!\n\n"<<COLOR_reset; exit(1); }
	size_t bytesRead = fread((char*)dirlist.data(),1,4*3*181,fp);
	fclose(fp);

	cout <<"   [ OK ]\n\n";


	/* READING 'ODF' dataset */
	string ODF_filename = BASE_filename + "odf.nii";

	cout << "\n-> Reading 'ODF' dataset...\n";

	niiODF = nifti_load<FLOAT32>( ODF_filename );
	if ( niiODF == NULL )
	{ cerr << "\n" << "Unable to open file '"<< ODF_filename <<"'!\n\n"; exit(1); }
	if ( niiODF->hdr.datatype != 16 )
	{ cerr << "\n" << "File '"<< ODF_filename <<".nii' has a WRONG DATA TYPE! It should be FLOAT32!\n\n"; exit(1); }

	printf("      dim   : %d x %d x %d\n", niiODF->hdr.dim[2],niiODF->hdr.dim[3],niiODF->hdr.dim[4]);
	printf("      pixdim: %.4f x %.4f x %.4f\n", niiODF->hdr.pixdim[2],niiODF->hdr.pixdim[3],niiODF->hdr.pixdim[4]);

	cout <<"   [ OK ]\n\n";


	/* reading volume size */
	sizex=niiODF->hdr.dim[2];
	sizey=niiODF->hdr.dim[3];
	sizez=niiODF->hdr.dim[4];

	pixx=niiODF->hdr.pixdim[2];
	pixy=niiODF->hdr.pixdim[3];
	pixz=niiODF->hdr.pixdim[4];

	centerx=sizex/2;
	centery=sizey/2;
	centerz=sizez/2;

	normODF.resize(181,sizex,sizey,sizez);
	GFA.resize(sizex,sizey,sizez);


	/* calculate QFORM matrix (needed for correct reorientation of gradient directions) */
	cout <<"-> Reorienting GRADIENT DIRECTIONS...\n";

	float d = niiODF->hdr.quatern_d;
	float c = niiODF->hdr.quatern_c;
	float b = niiODF->hdr.quatern_b;
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
		cerr << "\n\n" << "The 'qform' is not handled by this tractography software!\n";
		cerr << "\n   qform = "<< QFORM << "\n\n";
	}

	for(int i=0; i<181 ; i++)
	{
		Array<float,1> tmp( dirlist(i,Range(0,2)) );
		dirlist(i,0) = tmp(0)*QFORM(0,0) + tmp(1)*QFORM(1,0) + tmp(2)*QFORM(2,0);
		dirlist(i,1) = tmp(0)*QFORM(0,1) + tmp(1)*QFORM(1,1) + tmp(2)*QFORM(2,1);
		dirlist(i,2) = tmp(0)*QFORM(0,2) + tmp(1)*QFORM(1,2) + tmp(2)*QFORM(2,2);
		dirlist(i,1) = -dirlist(i,1);       // [NOTE] don't know why
	}

	cout <<"   [ OK ]\n\n";


	// normalization of ODF (by the maximum value)
	for(int x=0; x<sizex ; x++)
	for(int y=0; y<sizey ; y++)
	for(int z=0; z<sizez ; z++)
	{
		float sum=0, max=0;
		for (int i=0; i<181; i++) {
			float val =niiODF->img(i,x,y,z);
			sum+=val;
			if (val>max) max=val;
		}
		if (max>0)
			for (int i=0; i<181; i++)
				niiODF->img(i,x,y,z) /= max;
	}


	/* Calculate the GFA map */
	Array<float,1> ODF(181);
	float STD, RMS, MEAN, SUM;
	MEAN = 1.0 / 181.0;

	cout << "-> Calculating GFA in each voxel...\n";
	for(int x=0; x<sizex ;x++)
	for(int y=0; y<sizey ;y++)
	for(int z=0; z<sizez ;z++)
	{
		ODF = niiODF->img(Range::all(),x,y,z);
		SUM = sum(ODF);
		if (SUM<=0) continue;

		ODF = ODF / SUM;
		STD = sqrt( sum(pow2(ODF-MEAN)) / (181-1) );
		RMS = sqrt( sum(pow2(ODF)) / 181.0 );
		GFA(x,y,z) = STD / RMS;
	}
	cout <<"   [ OK ]\n\n";


	/* setup triangulation */
	for (int d=0; d<181; d++)
	{
		neigh[d].clear();
		for (int d2=0; d2<2*181; d2++)
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


	/* SETUP OpenGL enviromnent */
	glutInit(&argc,argv);
	glutInitDisplayMode ( GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH ) ;

	glutInitWindowSize(scrsizex,scrsizey);
	w1 = glutCreateWindow("DTB_viewer");
	gluLookAt(0.0, 0.0, 120.0,
			  0.0, 0.0, 0.0,
			  0.0, 1.0, 0.0);

	init();

	glutKeyboardFunc(keyboard);
	glutSpecialFunc(specialkey);
	glutDisplayFunc(display);
	glutMouseFunc(mouse);
	glutMotionFunc(motion);
	glutReshapeFunc(reshape);

	glutMainLoop();
}



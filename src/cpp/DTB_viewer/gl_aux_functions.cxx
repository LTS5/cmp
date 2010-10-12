float len(float* v)
{
	return sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2]);
}


void normal(float* v)
{
	float temp=len(v);
	if (temp==0) temp=1;

	v[0]/=temp;
	v[1]/=temp;
	v[2]/=temp;
}


void prodvett(float* v1,float* v2, float* v3)
{
	v3[0]=v1[1]*v2[2]-v2[1]*v1[2];
	v3[1]=v1[2]*v2[0]-v2[2]*v1[0];
	v3[2]=v1[0]*v2[1]-v2[0]*v1[1];
}

float prodscal(float* v1,float* v2)
{
	return v1[0]*v2[0]+v1[1]*v2[1]+v1[2]*v2[2];
}


void vectXMat(GLfloat* v, GLfloat* m, GLfloat* result)
{
	//prodotto vettore matrice
	for (int i=0; i<4; i++)
	{
		result[i]=0;
		for (int j=0; j<4; j++)
			result[i]=result[i]+m[i+4*j]*v[j];
	}
};

void matXMat(GLfloat* m, GLfloat* m1, GLfloat* result)
{

	for (int i=0; i<4; i++)
	{
		for (int j=0; j<4; j++)
		{
			result[4*i+j]=0;
			for (int t=0; t<4; t++)
				result[4*i+j]=result[4*i+j]+m[4*i+t]*m1[4*t+j];
		}
	}
}


void identity(GLfloat* result)
{
	for (int i=0; i<4; i++)
	{
		for (int j=0; j<4; j++)
			if (i==j) result[4*i+j]=1;else result[4*i+j]=0;
	}
}


void rotateZ(GLfloat* m, GLfloat ang, GLfloat* result)
{

	for (int i=0; i<16 ; i++) matrix[i]=0;
	matrix[0]=cos(ang/180*3.1415);
	matrix[5]=cos(ang/180*3.1415);
	matrix[1]=-sin(ang/180*3.1415);
	matrix[4]=sin(ang/180*3.1415);
	matrix[10]=1;
	matrix[15]=1;
	matXMat(matrix,m,result);
}


void rotateY(GLfloat* m, GLfloat ang, GLfloat* result)
{
	for (int i=0; i<16 ; i++) matrix[i]=0;
	matrix[0]=cos(ang/180*3.1415);
	matrix[10]=cos(ang/180*3.1415);
	matrix[8]=-sin(ang/180*3.1415);
	matrix[2]=sin(ang/180*3.1415);
	matrix[5]=1;
	matrix[15]=1;
	matXMat(matrix,m,result);
}


void rotateX(GLfloat* m, GLfloat ang, GLfloat* result)
{
	for (int i=0; i<16 ; i++) matrix[i]=0;
	matrix[5]=cos(ang/180*3.1415);
	matrix[10]=cos(ang/180*3.1415);
	matrix[6]=-sin(ang/180*3.1415);
	matrix[9]=sin(ang/180*3.1415);
	matrix[0]=1;
	matrix[15]=1;
	matXMat(matrix,m,result);
}


void translate(GLfloat* m,GLfloat x,GLfloat y,GLfloat z, GLfloat* result)
{
	for (int i=0; i<16 ; i++) matrix[i]=0;
	matrix[0]=1;
	matrix[5]=1;
	matrix[10]=1;
	matrix[15]=1;
	matrix[12]=x;
	matrix[13]=y;
	matrix[14]=z;
	matXMat(matrix,m,result);
}

void init(void)
{
	/* Matrice di proiezione */
	glMatrixMode(GL_PROJECTION);
	gluPerspective(40.0, 1.0, 0.1,1000.0);
	glMatrixMode(GL_MODELVIEW);
	glEnable(GL_DEPTH_TEST);
	glEnable(GL_CULL_FACE);
	glClear(GL_COLOR_BUFFER_BIT);

	xtrasl=0;
	ytrasl=0;

	xrot=0;
	yrot=0;
	zrot=0;
	zoom=12;

	vect=(GLfloat*)calloc(4,sizeof(GLfloat));
	vect1=(GLfloat*)calloc(4,sizeof(GLfloat));

	//carica la matrice identita globale
	id = (GLfloat*)calloc(16,sizeof(GLfloat));
	identity(id);

	matrix=(GLfloat*)calloc(16,sizeof(GLfloat)); //temp per fare i conti
	rot=(GLfloat*)calloc(16,sizeof(GLfloat));
	rot1=(GLfloat*)calloc(16,sizeof(GLfloat));
	rot2=(GLfloat*)calloc(16,sizeof(GLfloat));
	rot3=(GLfloat*)calloc(16,sizeof(GLfloat));
	identity(rot);

	dir[0][0]=0; dir[0][1]=1; dir[0][2]=1;
	dir[1][0]=0; dir[1][1]=-1; dir[1][2]=1;
	dir[2][0]=0; dir[2][1]=-1; dir[2][2]=-1;
	dir[3][0]=0; dir[3][1]=1; dir[3][2]=-1;

	dir[4][1]=0; dir[4][0]=1; dir[4][2]=1;
	dir[5][1]=0; dir[5][0]=-1; dir[5][2]=1;
	dir[6][1]=0; dir[6][0]=-1; dir[6][2]=-1;
	dir[7][1]=0; dir[7][0]=1; dir[7][2]=-1;

	dir[8][2]=0; dir[8][0]=1; dir[8][1]=1;
	dir[9][2]=0; dir[9][0]=-1; dir[9][1]=1;
	dir[10][2]=0; dir[10][0]=-1; dir[10][1]=-1;
	dir[11][2]=0; dir[11][0]=1; dir[11][1]=-1;


	// calculate the NORMALIZED form of ODFs
	for (int i=0; i<sizex; i++)
	for (int j=0; j<sizey; j++)
	for (int k=0; k<sizez; k++)
	{
		float min=2e31, max=0, val;
		for (int d=0; d<181; d++) {
			val = niiODF->img(d,i,j,k);
			if (min>val) min=val;
			if (max<val) max=val;
		}

		for (int d=0; d<181; d++)
			normODF(d,i,j,k) = (niiODF->img(d,i,j,k)-min)/(max-min);
	}

	printf("[ init done ]\n");
}


/* KEYBOARD callback */
void keyboard ( unsigned char key, GLint x, GLint y )
{
	switch(key)
	{
	case ' ': proj  = (1+proj)%3; break;
	case 'v': vmode = (vmode+1)%3; break;
	case 'V': vmode = (vmode-1)%3; break;
	case 'n': normalization = 1-normalization; break;
	case 'o': mapOPACITY = mapOPACITY-0.1; if (mapOPACITY<0) mapOPACITY=0; break;
	case 'O': mapOPACITY = mapOPACITY+0.1; if (mapOPACITY>1) mapOPACITY=1; break;


	case 's': scale *= 1.1; break;
	case 'S': scale /= 1.1; break;

	case 27 : exit (0); break;
	}

	glutSetWindow(w1);
	glutPostRedisplay();
}


/* SPECIAL KEY callback */
void specialkey(int key, int x, int y)
{
	switch(key)
	{
		case 100: // left
			switch (proj)
			{
				case 0: if (centery+1<sizey) centery++; break;
				case 1: if (centerx+1<sizex) centerx++; break;
				case 2: if (centerx+1<sizex) centerx++; break;
			}
			break;
		case 102: // right
			switch (proj)
			{
				case 0: if (centery>0) centery--; break;
				case 1: if (centerx>0) centerx--; break;
				case 2: if (centerx>0) centerx--; break;
			}
			break;
		case 101: // up
			switch (proj)
			{
				case 0: if (centerz>0) centerz--; break;
				case 1: if (centery>0) centery--; break;
				case 2: if (centerz>0) centerz--; break;
			}
			break;
		case 103: // down
			switch (proj)
			{
				case 0: if (centerz+1<sizez) centerz++; break;
				case 1: if (centery+1<sizey) centery++; break;
				case 2: if (centerz+1<sizez) centerz++; break;
			}
			break;
		case 104: // page up
			switch (proj)
			{
				case 0: if (centerx>0) centerx--; break;
				case 1: if (centerz>0) centerz--; break;
				case 2: if (centery>0) centery--; break;
			}
			break;
		case 105: // page down
			switch (proj)
			{
				case 0: if (centerx+1<sizex) centerx++; break;
				case 1: if (centerz+1<sizez) centerz++; break;
				case 2: if (centery+1<sizey) centery++; break;
			}
			break;
	}

	glutSetWindow(w1);
	glutPostRedisplay();
}




/* MOUSE callback */
static void mouse(GLint button, GLint state, GLint x, GLint y)
{
	if (state == GLUT_DOWN)
	{
		if (button == GLUT_LEFT_BUTTON)
		{
			moving = 1;
			startx = x;
			starty = y;
		}
		else if (button == GLUT_RIGHT_BUTTON)
		{
			moving = 2;
			startx = x;
			starty = y;
		}
		else if (button == GLUT_MIDDLE_BUTTON)
		{
			moving = 3;
			startx = x;
			starty = y;
		}
	}
	else if (state == GLUT_UP) moving = 0;
}


/* Movimento */
static void motion(GLint x, GLint y)
{
	if (moving==1)
	{
		yrot=(startx-x)/1;
		xrot=(starty-y)/1;

		//porto il centro di rotazione nel baricentro
		translate(id,-.0,-.0,0,rot1);

		rotateY(id,yrot,rot3);
		matXMat(rot,rot1,rot2);
		rotateX(id,xrot,rot1);
		matXMat(rot2,rot1,rot);
		matXMat(rot,rot3,rot2);

		//riporto il centro di rotazione in pos. originale
		translate(id,+0.0,+0.0,-0,rot1);
		matXMat(rot2,rot1,rot);

		startx = x;
		starty = y;
	}

	if (moving==2)
	{
		zoom=zoom+(y-starty)/10.0;
		starty = y;
	}

	if (moving==3)
	{
		xtrasl = xtrasl - (startx-x)/3.0;
		ytrasl = ytrasl + (starty-y)/3.0;
		startx = x;
		starty = y;
	}

	glutSetWindow(w1);
	glutPostRedisplay();
}




void reshape(int w, int h)
{
	glViewport(0, 0, (GLsizei) w, (GLsizei) h);
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	gluPerspective(40.0, (float)w/h, 0.1,1000.0);

	scrsizex=w;
	scrsizey=h;
}



/* Funzione di Rendering */
void display(void)
{
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
	glPushMatrix();
	glTranslatef(xtrasl, ytrasl, -zoom);
	glMultMatrixf(rot);

	glLineWidth(1);

	int maxx=20;
	int maxy=20;
	int maxz=20;

	int wx=maxx;
	int wy=maxy;
	int deltaz=maxz;

	if (proj==0) wx=0;
	if (proj==1) deltaz=0;
	if (proj==2) wy=0;

	int idx0,idx1,idx2;
	if (proj==0) {
		idx0=1; idx1=2; idx2=0;
	}
	if (proj==1) {
		idx0=0; idx1=1; idx2=2;
	}
	if (proj==2) {
		idx0=0; idx1=2; idx2=1;
	}

	for (int i=-wx; i<=wx; i++)
	for (int j=-wy; j<=wy; j++)
	for(int k=-deltaz; k<=deltaz; k++)
	{
		if (centerx+i<0 || centerx+i>=sizex || centery+j<0 || centery+j>=sizey || k+centerz<0 || k+centerz>=sizez)
			continue;

		double avg[3] = {0,0,0};
		double avgct=0;
		double gavg=0;

		float rmsd=1;
		float ss=0.1;

		float map[181];
		int   mapmax[181];

		/* stix/ODF/sphere*/
		if (vmode==0 || vmode==1)
		{

			// calculate ODF maxima
			for (int d=0; d<181; d++)
			{
				int max = d;
				if (normalization)
					map[d] = 2*GFA(centerx+i,centery+j,centerz+k) * normODF(d,centerx+i,centery+j,centerz+k);
				else
					map[d] = niiODF->img(d,centerx+i,centery+j,centerz+k);

				for (int ct=0; ct<neigh[d].size(); ct++) {
					int d1=neigh[d][ct];
					if (normODF(d1,centerx+i,centery+j,centerz+k) > normODF(max,centerx+i,centery+j,centerz+k)) max=d1;
				}
				if (max==d && map[d]>0) mapmax[d]=1;
				else mapmax[d]=0;
			}

			/* STIX visualization */
			if ( vmode==0 )
			for (int d=0; d<181; d++)
				if (mapmax[d])
				{
// 					float cr=map[d]*scale;
					float cr=1;
					glLineWidth(2);
					glColor3f(cr*fabs(dirlist(d,idx0)),cr*fabs(dirlist(d,idx1)),cr*fabs(dirlist(d,idx2)));

					glBegin(GL_LINES);
					for (int le=-1; le<=1; le+=2) {
						if (proj==0)
							glVertex3f(pixy*(0.5+j)+le*rmsd*dirlist(d,idx0),pixz*(0.5+k)+le*rmsd*dirlist(d,idx1),pixx*(0.5+i)+le*rmsd*dirlist(d,idx2));
						if (proj==1)
							glVertex3f(pixx*(0.5+i)+le*rmsd*dirlist(d,idx0),pixy*(0.5+j)+le*rmsd*dirlist(d,idx1),pixz*(0.5+k)+le*rmsd*dirlist(d,idx2));
						if (proj==2)
							glVertex3f(pixx*(0.5+i)+le*rmsd*dirlist(d,idx0),pixz*(0.5+k)+le*rmsd*dirlist(d,idx1),pixy*(0.5+j)+le*rmsd*dirlist(d,idx2));
					}
					glEnd();
					glLineWidth(1);
				}

			for (int d=0; d<181; d++)
				for (int dir=-1; dir<=1; dir+=2)
				{
					float le=1;
					float cr=map[d];//*scale;

					glColor3f(cr,cr,cr);
					if (mapmax[d]) glColor3f(1,0,0);

					/* ODF visualization */
					if (vmode==1)
					{
						//  vicini
						for (int ct=0; ct<neigh[d].size(); ct++)
							if (d<neigh[d][ct]) {
								int   d1=neigh[d][ct];
								float cr1=map[d1];//*scale;

								int   coef=1;
								float dist1=pow(dir*dirlist(d,idx0)-coef*dir*dirlist(d1,idx0),2)+
												pow(dir*dirlist(d,idx1)-coef*dir*dirlist(d1,idx1),2)+
												pow(dir*dirlist(d,idx2)-coef*dir*dirlist(d1,idx2),2);
								coef=-1;
								float dist2=pow(dir*dirlist(d,idx0)-coef*dir*dirlist(d1,idx0),2)+
												pow(dir*dirlist(d,idx1)-coef*dir*dirlist(d1,idx1),2)+
												pow(dir*dirlist(d,idx2)-coef*dir*dirlist(d1,idx2),2);
								if (dist1<dist2)
									coef=1;
								else
									coef=-1;

								glBegin(GL_LINES);
								glColor3f(cr*fabs(dirlist(d,idx0)),cr*fabs(dirlist(d,idx1)),cr*fabs(dirlist(d,idx2)));
								if (mapmax[d]) glColor3f(1,1,1);

								le=dir;
								le*=map[d];

								if (proj==0)
									glVertex3f(pixy*(0.5+j)+le*dirlist(d,idx0),pixz*(0.5+k)+le*dirlist(d,idx1),pixx*(0.5+i)+le*dirlist(d,idx2));
								if (proj==1)
									glVertex3f(pixx*(0.5+i)+le*dirlist(d,idx0),pixy*(0.5+j)+le*dirlist(d,idx1),pixz*(0.5+k)+le*dirlist(d,idx2));
								if (proj==2)
									glVertex3f(pixx*(0.5+i)+le*dirlist(d,idx0),pixz*(0.5+k)+le*dirlist(d,idx1),pixy*(0.5+j)+le*dirlist(d,idx2));

								le=dir;
								le*=map[d1];

								glColor3f(cr1,cr1,cr1);
								glColor3f(cr1*fabs(dirlist(d1,idx0)),cr1*fabs(dirlist(d1,idx1)),cr1*fabs(dirlist(d1,idx2)));
								if (mapmax[d1]) glColor3f(1,1,1);

								if (proj==0)
									glVertex3f(pixy*(0.5+j)+le*coef*dirlist(d1,idx0),pixz*(0.5+k)+le*coef*dirlist(d1,idx1),pixx*(0.5+i)+le*coef*dirlist(d1,idx2));
								if (proj==1)
									glVertex3f(pixx*(0.5+i)+le*coef*dirlist(d1,idx0),pixy*(0.5+j)+le*coef*dirlist(d1,idx1),pixz*(0.5+k)+le*coef*dirlist(d1,idx2));
								if (proj==2)
									glVertex3f(pixx*(0.5+i)+le*coef*dirlist(d1,idx0),pixz*(0.5+k)+le*coef*dirlist(d1,idx1),pixy*(0.5+j)+le*coef*dirlist(d1,idx2));
								glEnd();
							}
					}
				}
		}


		// draw scalar maps
		if (vmode==0 || vmode==1 || vmode==2)
		{
			float color = scale*GFA(centerx+i,centery+j,centerz+k);
 			glEnable(GL_BLEND);
			if (vmode==0 || vmode==1)
				glColor4f(color,color,color,mapOPACITY);
			else
				glColor4f(color,color,color,1.0);
 			glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);


			glBegin(GL_QUADS);
			if (proj==0) {
				glVertex3f(pixy*(j),pixz*(k),pixx*(i));
				glVertex3f(pixy*(j+1),pixz*(k),pixx*(i));
				glVertex3f(pixy*(j+1),pixz*(k+1),pixx*(i));
				glVertex3f(pixy*(j),pixz*(k+1),pixx*(i));
			}
			if (proj==1) {
				glVertex3f(pixx*(i),pixy*(j),pixz*(k));
				glVertex3f(pixx*(i+1),pixy*(j),pixz*(k));
				glVertex3f(pixx*(i+1),pixy*(j+1),pixz*(k));
				glVertex3f(pixx*(i),pixy*(j+1),pixz*(k));
			}
			if (proj==2) {
				glVertex3f(pixx*(i),pixz*(k),pixy*(0.5+j));
				glVertex3f(pixx*(i+1),pixz*(k),pixy*(0.5+j));
				glVertex3f(pixx*(i+1),pixz*(k+1),pixy*(0.5+j));
				glVertex3f(pixx*(i),pixz*(k+1),pixy*(0.5+j));
			}
			glEnd();
			glDisable(GL_BLEND);
		}
	}


	glPopMatrix();
	glMatrixMode(GL_PROJECTION);
	glPopMatrix();
	glMatrixMode(GL_MODELVIEW);

	glPopMatrix();
	glutSwapBuffers();
}

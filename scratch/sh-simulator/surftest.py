# start ipython with:
# ipython -wthread

# there is  SPHEREPACK 3.2 with is wrapped for python
# this might ease your life a lot
# http://code.google.com/p/pyspharm/

# there is also a spherical harmonics explorer
# http://root42.blogspot.com/2010/09/spherical-harmonics-explorer.html
# but i do not know if you can download it

# there is also another python package for reconstruction
# http://code.google.com/p/diffusion-mri/
# the code is here: http://github.com/matthew-brett/diffusion_mri

# for the visualization
# we need numpy and mayavi
import numpy as np
from enthought.mayavi.mlab import *

pi = np.pi
cos = np.cos
sin = np.sin

# modified from example
# http://code.enthought.com/projects/mayavi/docs/development/html/mayavi/auto/mlab_helper_functions.html#mesh
dphi, dtheta = pi/250.0, pi/250.0
[phi,theta] = np.mgrid[0:pi+dphi*1.5:dphi, 0:2*pi+dtheta*1.5:dtheta]

#m0 = 4; m1 = 3; m2 = 2; m3 = 3; m4 = 6; m5 = 2; m6 = 6; m7 = 4;
#r = sin(m0*phi)**m1 + cos(m2*phi)**m3 + sin(m4*theta)**m5 + cos(m6*theta)**m7

r = 4*sin(phi)**4 + cos(2 * phi)
x = r*sin(phi)*cos(theta)
y = r*cos(phi)
z = r*sin(phi)*sin(theta);

# if you want, you can put color
col = np.random.random ( x.shape )

# without color
# me = mesh(x, y, z, colormap="bone")

# with (random) color
me = mesh(x, y, z, scalars = col, colormap="Spectral")

# you can use these colormaps:
# http://www.scipy.org/Cookbook/Matplotlib/Show_colormaps


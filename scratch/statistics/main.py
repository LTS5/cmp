import networkx as nx
import numpy as np
from pylab import *

# show fiber length histogram
a=np.load('lengths.npy')
hist(a,100)

# load matrix and show it
g=nx.read_gpickle('matrices/cmat.pickle')
G=g['scale33']['graph']
ma=nx.to_numpy_matrix(G)
figure()
imshow(ma,vmin=ma.min(), vmax=ma.max(), interpolation='nearest')

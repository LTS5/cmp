"""
Cortical parcellation idea
Stephan Gerhard

Using PyMetis: http://mathema.tician.de/software/pymetis

Ubuntu:
required packages: python, boost, dev packages.
adapt pymetis setup.py with:         Libraries("BOOST_PYTHON", ["boost_python-mt-py26"]),

"""
import numpy as np
import networkx as nx
from pymetis import part_graph

# data init
scalp=np.array([[1,1,0], [1,0,0.5],[0,1,-0.5]])
# project
def sp(vec):
    return np.array([vec[0]/ (1 - vec[2]), vec[1] / (1-vec[2])])
pmap = np.ones( (scalp.shape[1], 2) )
for i in range(scalp.shape[1]):
	pmap[i,:] = sp(scalp[i,:])

# create a graph from the mesh
faces = np.array( [ [0,1,2], [2,1,4], [3,4,2] ] ).tolist()
h=nx.Graph()
for f in faces:
	# add three edges for each triangle
	a,b,c = f
	h.add_edges_from([(a,b),(b,c),(c,a)])

# print h.adjacency_list()

# partition the graph
cuts, part_vert = part_graph(2, h.adjacency_list())

print "number of cuts", cuts
print "partition", part_vert

# visualize partition to control using partition as scaler value


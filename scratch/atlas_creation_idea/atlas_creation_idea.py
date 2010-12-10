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
# import pymatlab

import nibabel.gifti as gi

a=gi.read('rh.inflated.gii')
vert = a.darrays[0].data
face = a.darrays[1].data

#import pymatlab
#from pymatlab import Session
#m=Session()
# http://surfer.nmr.mgh.harvard.edu/fswiki/CorticalParcellation

#m.run("[v,l,c] = read_annotation('/home/stephan/Dev/PyWorkspace/cmp/scratch/atlas_creation/cmp/rh.myaparc_33.annot');")

# data init
verts = np.array( [ [0,1,1], [2,3,2], [2,1,2], [2,5,4], [5,4,3] ] )
faces = np.array( [ [0,1,2], [2,1,4], [3,4,2] ] ).tolist()
# select one region, and extract it as subgraph
labels = np.array( [ 0,2,2,1,1] )

# create a graph from the mesh
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


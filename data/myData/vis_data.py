import nibabel as ni
import numpy as np
import networkx as nx
from dipy.viz import fos
from pylab import *

# show whole numpy matrix
set_printoptions(threshold=nan)

print "Load data..."
endpoints = np.load('endpoints.npy')
fiblen = np.load('fiblen.npy')
G = nx.read_gpickle('connectionmatrix.pickle')
fib, hdr = ni.trackvis.read('streamline.trk')
print "Done."

# convert graph to matrix, brain region 1 is row 0!
arr = nx.to_numpy_matrix(G)
#print "connection matrix", arr

# display matrix using matplotlib
#imshow(arr, vmin=np.min(arr), vmax=np.max(arr), interpolation='nearest')
#show()

# show all fibers worked on
def show_all():
    T=[i[0] for i in fib]
    r=fos.ren()
    fos.add(r,fos.line(T,fos.white,opacity=1.0))
    fos.show(r)

def show_bst():
    T=[]
    for fi in G.edge[81][83]['fiblist']:
        T.append(fib[fi][0])
    r=fos.ren()
    fos.add(r,fos.line(T,fos.white,opacity=1.0))
    fos.show(r)

def show_reg(reg = 83):
    r=fos.ren()
    fos.clear(r)
    T=[i[0] for i in fib]
    colors=np.ones((len(T),3))
    
    # grab all outgoing fibers
    for edgk, edgv in G.edge[reg].items():
        # for each outgoing, find a random color
        color=np.random.rand(1,3)
        for i in edgv['fiblist']:
            colors[i] = color

    fos.add(r,fos.line(T,colors,opacity=1.0))
    fos.show(r)

def show_reg_only(reg = 83):
    T = []
    col = []
    # grab all outgoing fibers
    for edgk, edgv in G.edge[reg].items():
        # for each outgoing, find a random color
        color=np.random.rand(1,3)
        for i in edgv['fiblist']:
            T.append(fib[i][0])
            col.append(color)
    # convert color list to array
    colors=np.ones((len(col),3))
    for i in range(len(col)):
        colors[i] = col[i]
    r=fos.ren()    
    fos.add(r,fos.line(T,colors,opacity=1.0))
    fos.show(r)
    

#show_all()
show_reg_only()
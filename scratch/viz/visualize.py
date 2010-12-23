# Goal 1: Show all outgoing fibers from a particular given region to all the other regions
# Goal 2: Plot this for all the the subjects and all the regions

import nibabel as ni
import numpy as np
import networkx as nx
import dipy.viz.fvtk as fvtk
# from dipy.tracking.metrics import downsample
import pylab as p
import pickle

# Parameters
srcregion = 49
parcellation = 'scale33'

# Load data
def load():
    print "read numpy data"
    globals['ep'] = np.load('endpoints.npy')
    le = np.load('lengths.npy')
    print "read cmat"
    cmat=nx.read_gpickle('matrices/cmat.pickle')
    globals()['g'] = cmat[parcellation]['graph']
    print "read fibers"
    fib0, hdr = ni.trackvis.read('streamline_filtered.trk')
    fib = [i[0] for i in fib0]
    
def create_data():
    g = globals()['g']
    # loop over all outregions
    outreg = g.edge[srcregion].keys()
    print g
    print outreg
    fbig = []
    for out in outreg:
        print "work on region", out
        fili=g.edge[srcregion][out]['fiblist']
        fibero=[]
        for i in fili:
            fibero.append(fib[i]) 
        fbig.append(fibero)
    globals()['fbig'] = fbig
    
def visualize():
    r=fvtk.ren()
    for i, ele in enumerate(fbig):
        print "working on ith", i
        # one color for all fibers 
        colors=np.random.rand(1,3)
        colors=colors.repeat(len(ele),axis=0)
        c=fvtk.line(ele,colors)
        fvtk.add(r,c)
    return r

create_data()
r = visualize()
fvtk.show(r)

#r=fos.ren()
#fos.add(r, fos.line(fibero,fos.yellow))
#fos.show(r)

#sp=fvtk.sphere(position=(0,0,0), radius = 10)
#fvtk.add(r,sp)

#fvtk.record(r,outdir = '', n_frames=1, size=(400,400), cam_pos= (0,0,100))


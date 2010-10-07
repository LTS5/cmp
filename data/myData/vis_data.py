import nibabel as ni
import numpy as np
import networkx as nx
from dipy.viz import fos
from dipy.core import track_metrics as tm
import pylab as p
import pickle

# show whole numpy matrix
#p.set_printoptions(threshold=np.nan)

print "Load data..."
ver = 'small'
n = 85
endpoints = np.load('%s/endpoints.npy'% ver)
fiblen = np.load('%s/fiblen.npy'% ver)
G = nx.read_gpickle('%s/connectionmatrix.pickle'% ver)
#fib0, hdr = ni.trackvis.read('/home/cmt/data/test_project_one/testsubject1/tp1/4__CMT/fibers/%s-streamline_spline.trk' % ver)
fib0, hdr = ni.trackvis.read('%s/streamline.trk'% ver)

# copy tracks, here can decimate fibers!
fib = [i[0] for i in fib0]
# show only 1 percent, can cause index errors below
# fib = fib[::100]

# downsample fibers
def ds(fib, points = 3):
    print 'Representing tracks using only %s pts...' % str(points)
    fib2=[tm.downsample(t,points) for t in fib]
    return fib2

fib = ds(fib)

#f=open('downsamp.pickle','r')
#fib = pickle.load(f)
#f.close()

# cut shortest fibers
#idx=np.where(fiblen<20)[0]
#fibc = [fib[i] for i in idx]

# remove diagonal fibers (within brain regions)
for i in range(1, n + 1):
    if G.has_edge(i,i):
        G.remove_edge(i,i)

# convert graph to matrix, brain region 1 is row 0!
arr = nx.to_numpy_matrix(G)
#print "connection matrix", arr

# display matrix using matplotlib
#p.imshow(arr, vmin=np.min(arr), vmax=np.max(arr), interpolation='nearest')
#p.show()

# show all fibers worked on
def show_all(fib):
    T=fib
    r=fos.ren()
    fos.add(r,fos.line(T,fos.white,opacity=1.0))
    fos.show(r)

def show_bst(fib):
    T=[]
    for fi in G.edge[81][83]['fiblist']:
        T.append(fib[fi])
    r=fos.ren()
    fos.add(r,fos.line(T,fos.white,opacity=1.0))
    fos.show(r)

def show_reg(fib, r, op = 1.0, reg = 83):
    """ Shows all fibers with a particular region colored """
    T=fib
    colors=np.ones((len(T),3))
    # grab all outgoing fibers
    for edgk, edgv in G.edge[reg].items():
        # for each outgoing, find a random color
        color=np.random.rand(1,3)
        for i in edgv['fiblist']:
            colors[i] = color
    fos.add(r,fos.line(T,colors,opacity=op))


def show_list_reg(fib, r, op = [1.0], regl = [83]):
    """ Add a list of regions with a distinct color to the renderer """
    for j,reg in enumerate(regl):
        T = []
        col = []
        color=np.random.rand(1,3)
        # grab all outgoing fibers
        for edgk, edgv in G.edge[reg].items():
            for i in edgv['fiblist']:
                T.append(fib[i])
                col.append(color)
        # convert color list to array
        colors=np.ones((len(col),3))
        for i in range(len(col)):
            colors[i] = col[i]
        fos.add(r,fos.line(T,colors,opacity=op[j]))


def show_reg_only(fib, r, op = 1.0, reg = 83):
    """ Show region only, add it to renderer """
    T = []
    col = []
    # grab all outgoing fibers
    for edgk, edgv in G.edge[reg].items():
        # for each outgoing, find a random color
        color=np.random.rand(1,3)
        for i in edgv['fiblist']:
            T.append(fib[i])
            col.append(color)
    # convert color list to array
    colors=np.ones((len(col),3))
    for i in range(len(col)):
        colors[i] = col[i]
    fos.add(r,fos.line(T,colors,opacity=op))
    
def show_fiblen_hist():
    """ Shows histogram of fiber lenghts. Note the bump around 100 [mm] """
    p.hist(fiblen, bins=1000)
    
def show_std_across_trct(runs = ['01', '02', '03', '04']):
    """ Show standard deviation across tractography runs and histogram"""
    a = np.zeros( (85,85,len(runs) ) )
    for i, v in enumerate(runs):
        g = nx.read_gpickle('%s/connectionmatrix.pickle' % v)
        arr = nx.to_numpy_matrix(g)
        a[:,:,i] = arr
    s = np.std(a,2)
    print "histogram"
    print s

    p.histogram(np.resize(s, (1,n*n) ))
    print "index of connection brain regions with std bigger than 100"
    print np.where(s > 100)

r=fos.ren()
fos.clear(r)
# show_reg_only(fib, r, 0.2, 83)
show_list_reg(fib,r, [1.0, 0.2, 0.2], [1,2,3])
fos.show(r)
#show_reg(fib)
#show_fiblen_hist()
#show_std_across_trct()
#show_all()


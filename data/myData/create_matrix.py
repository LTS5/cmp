import nibabel as ni
import numpy as np
import networkx as nx

# load reduced .trk file with 10 fibers only
fib, hdr = ni.trackvis.read('stream.trk')

# number of fibers
n = len(fib)

# matrix for endpoints
# first fiber has id 0, i.e. matrix row entry 0
endpoints = np.zeros( (n, 2, 3), dtype=np.float32 )

# matrix for fiber lengths
fiblen = np.zeros( (n, 1), dtype=np.float32)

for i, fi in enumerate(fib):
    f = fi[0]
    
    # store startpoint
    endpoints[i,0,:] = f[0,:]
    # store endpoint
    endpoints[i,1,:] = f[-1,:]
    
    # calculate length: euclidian distance over the points
    l = 0.0
    for j in xrange(1, f.shape[0]):
        a = f[j-1,:]
        b = f[j,:]
        l += np.linalg.norm(a-b)
    fiblen[i] = l
    
# retrieve starting and ending roi using endpoints
roi = ni.load('ROI_HR_th.nii')
roid = roi.get_data()
roih = roi.get_header()

# number of rois, extract maximum from volume, afterwards use configuration
Nrois = int(np.max(roid))

print "number of rois", Nrois
print "trk voxel size", hdr['voxel_size']
print "trk voxel dim", hdr['dim']
print "roi voxel dim", roih['dim']
print "roi pixel dim", roih['pixdim']

# create a networkx graph to store the values (later: use configuration graphml)
G = nx.Graph()
# add nodes for rois
G.add_nodes_from( range(1, Nrois+1) )

for i in range(endpoints.shape[0]):
    
    # look up starting point
    start = endpoints[i,0,:]
    end = endpoints[i,1,:]
    
    for pos, coord in [('start',start), ('end',end)]:
    
        # find out voxel index in roi volume
        idx = np.zeros( (3,), dtype=np.int16 )
        idx[0] = int(round( coord[0] / hdr['voxel_size'][0] - 0.5 ))
        idx[1] = int(round( coord[1] / hdr['voxel_size'][1] - 0.5 ))
        idx[2] = int(round( coord[2] / hdr['voxel_size'][2] - 0.5 ))
        # there seem to be value below 0, is the formula above correct?
        # clamping!
        idx[idx<0] = 0
        if idx[0]>hdr['dim'][0]:
            idx[0] = hdr['dim'][0]
        if idx[1]>hdr['dim'][1]:
            idx[1] = hdr['dim'][1]
        if idx[2]>hdr['dim'][2]:
            idx[2] = hdr['dim'][2]
        
        # look up in roi volume
        if pos == 'start':
            start_roi = roid[idx[0], idx[1], idx[2]]
        elif pos == 'end':
            end_roi = roid[idx[0], idx[1], idx[2]]
            
    print "fiber", i, "from roi", start_roi, " to roi ", end_roi
    
    # add edge to graph
    if G.has_edge(start_roi, end_roi):
        G.edge[start_roi][end_roi]['fiblist'].append(i)
    else:
        G.add_edge(start_roi, end_roi, fiblist = [i])
    
print "show graph edges", G.edges(data=True)

# store the stuff

#np.save('endpoints.npy', endpoints)
#np.save('fiblen.npy', fiblen)
#nx.write_graphml(G, 'connectionmatrix.graphml')

    

    
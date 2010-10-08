# we have inputs
trk_fname = 'streamline.trk'
rois = {'scale33' : {fname : 'roi_scale33.nii'},
        'scale60' : {fname : 'roi_scale60.nii'},
        }
mes =  {'adc' : {fname : 'adc.nii'},
        'fa' : {fname : 'fa.nii'},
        }

# asserts
# - trk.dimension == rois.dimension == mes.dimension
# - trk has valid header

# the trk files lists all the fibers, their id is the position in the list
# this id has to be stored in the new cmat data structure so we can use it
# for validation of the results (= see what actual fibers connect two regions)

# data structure layout
# a dictionary
# key: rois key name
# value: undirected networkx graph
#        - contains metadata: which roi file, what trk file
# the graph has 
# nodes: contain all about the brain region, enumerated as in the rois file, starting with 1
# edges: tuples (1,3) means from brain region 1 to 3. each edge contains a dictionary for the data, namely

# edge dict:
# keys: the measures 'adc', 'fa', ...; 'fiber_id'
# values: 
# for the measures, this are lists that contain the scalar values coming from the measure volume along the fiber
# for the 'fiber_id': the indices into the original .trk file fiber lists.

# example

# graph.edge[1][3] = { 'adc' : [ [3,2,3,2.3,4.2], [23.3,32,23] ],
#                      'fiber_id' : [23,399]}

# -> between brain region 1 and 3, there are two fibers, fiber 23 and 399.
# fiber 23 has 5 points including start and end (?), fiber 399 has only 3.
# the adc values along this fibers are stored in the list of lists keyed by 'adc'

# advantage
# - we need this big data structure for further analysis
# - it is easy to compute mean/max/min/std/histograms across fibers, across edges between brain regions
# - it allows to selectively visualize only the fibers between brain regions, as we keep this information
# - additional measures can easily be added


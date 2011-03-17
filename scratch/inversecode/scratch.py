# Jennifer Andreotti

import nibabel as ni
import numpy as np
import os.path as op
from util import length

datafolder = '/home/sgerhard/data/project01_dsi/ale01/tp1/CMP/cff/original_tp1.cff_FILES'
ctrack = op.join(datafolder, 'CTrack')
cvolume = op.join(datafolder, 'CVolume')
cdata = op.join(datafolder, 'CData')

# load data
print "load volume..."
myvolume = ni.load(op.join(cvolume, 'gfa_scalar_map.nii.gz'))
myvolumedata = myvolume.get_data()

print "load label array..."
mylabelarray = np.load(op.join(cdata, 'fiber_labels_(freesurferaparc).npy'))

print "load fibers..."
mytracks, mytracksheaders = ni.trackvis.read(op.join(ctrack, 'filtered_tractography.trk'))
fibers = [fiber[0] for fiber in mytracks] # list comprehension

# first fiber
# fibers[0]
# first fiber, start point, x,y,z
# fibers[0][0,:]
# first fiber, last point, x,y,z
# fibers[0][-1,:]

def test(a):
    print "me", a
#test("test")
  
print "number of fibers", len(fibers)

# Translate from mm to index
# endpoints[i,0,0] = int( endpoints[i,0,0] / float(voxelSize[0]))

# convert the first fiber to  a sequence of voxel indices i,j,k
# idx = (fibers[0] / np.array([1,1,1]) ).astype(np.int32)

# scalar values along first fiber
# myvolumedata[idx[:,0],idx[:,1],idx[:,2]]

# compute length of first fiber
length(fibers[0])

# return indices of all the fibers from 64 to 78
idx = np.where(mylabelarray == 64.78)[0]

for i in idx:
    myfiber = fiber[i]
    # happy computing

# matrix F: voxels x fibers

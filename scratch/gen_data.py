import nibabel as ni
from pylab import *
import numpy as np

a=ni.load('ROI_HR_th.nii')
d=a.get_data()

hdr = ni.trackvis.empty_header()

hdr['voxel_size'] = np.array([1,1,1])
hdr['dim'] = np.array(d.shape)

# fibers

#fi = np.array([[90.1, 100.2, 8.2], [90.1, 100.2, 87.2]])
# 90,100, 8 : 83
# -> 90,100,87: 8

fi = np.array([[90.1, 104.2, 0.0], [90.1, 100.2, 87.2]])
# 90,100, 8 : 83
# -> 90,100,87: 8

fib = [(fi,None,None)]

ni.trackvis.write('test.trk', fib, hdr)

# fib, hdr = ni.trackvis.read('stream.trk')



# imshow(d[:,:,0], interpolation='nearest')
# show()
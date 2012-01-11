from glob import glob
import os, os.path as op
import numpy as np
import scipy as sp
import nibabel as nb
import math

def dsi_preprocess(dsiarr, gradientmat, callb = None):
    """ Compute an ADC-like measure for DSI data

    Parameters
    ----------
    dsiarr : (I,J,K,M)
        The DSI volumes for each q value. M is the number of volumes including
        mean b0 as the first volume.
    gradientmat : (X,Y,Z,M)
        Gradient table for the M acquired DSI volumes including the
        b0 encoding direction.
    callback : function
        A function to be called with a string parameter
        E.g. for logging purposes

    Returns
    -------
    q_axis : TODO

    data : TODO

    mid_pos : TODO
    """
    

    callb("test")
        
    assert(dsiarr.shape[-1] == gradientmat.shape[0])
    I, J, K, N = dsiarr.shape
    # Build q axis for fitting
    all_norms = np.empty([N,1]) # compute the norms of the vectors in the q-space
    for i in range(q_points.shape[0]):
        all_norms[i] = np.sqrt(np.dot(q_points[i,:],q_points[i,:]))
    unique_norms = np.unique(all_norms) # determine the 'constant module shells' in the q-space
    q_axis = np.concatenate((-np.flipud(unique_norms),unique_norms[1:]),1) # generate the q axis for the S signal to be fitted (defined for each voxel)

    print "Number of sampling points in the new q axis: " + str(q_axis.shape[0])

    # For each voxel, compute the signal S values, averaged on each 'constant module shell'
    # initialization of the ndarray which will contain S for each voxel
    data = np.ndarray(shape = (I,J,K,q_axis.shape[0]))
    mid_pos = math.floor(q_axis.shape[0]/2.0)
    pc = -1
    print "Averaging raw data for q-shells..."
    # compute the signal values for all the points of the q-axis
    for i in range(unique_norms.shape[0]):
        # Percent counter
        pcN = int(round( float(100*i)/unique_norms.shape[0] ))
        if pcN > pc and pcN%1 == 0:
            pc = pcN
            print str(pc) + " %"

        this_norm = unique_norms[i]

        # volumes indexes for current value in the q-axis
        this_indexes = np.where(all_norms == this_norm)
        this_data = np.ndarray(shape=(I,J,K,np.size(this_indexes,1)))

        count = 0
        for j in this_indexes[0]:
            img_array = np.asarray(dsiarr[:,:,:,int(j)])
            this_data[:,:,:,count] = img_array
            count += 1

        # average the volumes for current q-value
        data[:,:,:,mid_pos+i] = np.mean(this_data, axis=3)
        data[:,:,:,mid_pos-i] = data[:,:,:,mid_pos+i]

    print "[ OK ]"
    return q_axis, data, mid_pos


def dsi_adc(q_axis, data, mid_pos):
    """ TODO

    Returns
    -------
    ADC4, ADC8 : (I,J,K) volumes
        Returns TODO

    """

    # Fit with a polynomial the signals S and derive the ADC and the kurtosis
    # initialization of the output maps
    I, J, K, N = data.shape

    ADC4 = np.zeros((I,J,K))
    #Ku4 = np.zeros((b0.shape[0],b0.shape[1],b0.shape[2]))
    #P04 = np.zeros((b0.shape[0],b0.shape[1],b0.shape[2]))

    ADC8 = np.zeros(((I,J,K)))
    #Ku8 = np.zeros((b0.shape[0],b0.shape[1],b0.shape[2]))
    #P08 = np.zeros((b0.shape[0],b0.shape[1],b0.shape[2]))

    pc = -1
    count = 0
    n = I * J * K
    print "Polynomial fitting for each voxel signal over q-axis..."
    # loop throughout all the voxels of the volume
    for i in range(b0.shape[0]):

        for j in range(b0.shape[1]):

            for k in range(b0.shape[2]):

                # Percent counter
                count = count + 1
                pcN = int(round( float(100*count)/n ))
                if pcN > pc and pcN%1 == 0:
                   pc = pcN
                   print str(pc) + " %"

                # for the current voxel, extract the signal to be fitted
                S = data[i,j,k,:]
                # normalization respect to the b0
                S = S / S[mid_pos]

                coeff = sp.polyfit(q_axis,S,8)
                ADC8[i,j,k] = (-coeff[-3] / (2 * math.pi * math.pi))
    #            Ku8[i,j,k] = (6 * coeff[-5] / (coeff[-3] * coeff[-3])) - 3
    #            temp = np.polyval(coeff, q_axis)
    #            P08[i,j,k] = np.sum(temp)

                coeff = sp.polyfit(q_axis,S,4)
                ADC4[i,j,k] = (-coeff[-3] / (2 * math.pi * math.pi))
    #            Ku4[i,j,k] = (6 * coeff[-5] / (coeff[-3] * coeff[-3])) - 3
    #            temp = np.polyval(coeff, q_axis)
    #            P04[i,j,k] = np.sum(temp)

    print "[ OK ]"
    return ADC4, ADC8
    

def dsi_adc_slowfast(q_axis, data, mid_pos):
    """ Compute an ADC-like fast slow measures

    Parameters
    ----------
    q_axis : TODO

    dta : TODO

    Returns
    -------
    ADC4slow, ADC4fast, ADC8slow, ADC8fast : (I,J,K) volumes
        Returns TODO

    """

    I, J, K, N = data.shape
    tupe = (I,J,K)
    
    # Compute fast component (low b-values, extracellular) and slow component (high b-values, intracellular)
    ADC4_fast = np.zeros(tupe)
    ADC4_slow = np.zeros(tupe)
    ADC8_fast = np.zeros(tupe)
    ADC8_slow = np.zeros(tupe)
    n = I * J * K

    c = 0.5 * math.sqrt(3000 / (8000 / (5*5))) # parameter for the signal weighting
    alfa = 0.5                                 # parameter for the signal weighting
    g = gcomp = np.zeros(len(q_axis))
    ind = 0
    for q in q_axis:
        g[ind] = alfa * math.exp(-(q*q) / (2*c*c)) # 'fast diffusion' weighting function
        ind = ind + 1
    gcomp = 1 - g                                  # 'slow diffusion' weighting function
    pc = -1
    count = 0
    print "Slow and fast curves polynomial fitting for each voxel signal over q-axis..."
    for i in range(b0.shape[0]): # loop throughout all the voxels of the volume
        for j in range(b0.shape[1]):
            for k in range(b0.shape[2]):

                # Percent counter
                count = count + 1
                pcN = int(round( float(100*count)/n ))
                if pcN > pc and pcN%1 == 0:
                    pc = pcN
                    print str(pc) + " %"

                S = data[i,j,k,:] # for the current voxel, extract the signal to be fitted
                Snorm = S / S[mid_pos] # normalization respect to the b0

                Snorm_fast = Snorm * g
                Snorm_slow = Snorm * gcomp

                coeff = sp.polyfit(q_axis,Snorm_fast,8)
                ADC8_fast[i,j,k] = (-coeff[-3] / (2 * math.pi * math.pi))

                coeff = sp.polyfit(q_axis,Snorm_slow,8)
                ADC8_slow[i,j,k] = (-coeff[-3] / (2 * math.pi * math.pi))

                coeff = sp.polyfit(q_axis,Snorm_fast,4)
                ADC4_fast[i,j,k] = (-coeff[-3] / (2 * math.pi * math.pi))

                coeff = sp.polyfit(q_axis,Snorm_slow,4)
                ADC4_slow[i,j,k] = (-coeff[-3] / (2 * math.pi * math.pi))

    print "[ OK ]"

    return ADC4slow, ADC4fast, ADC8slow, ADC8fast


if __name__ == '__main__':

    # Read DSI data (to DSIq5 numpy array)

    DSI_path = '/home/sgerhard/data/project_atlas/PH0002/tp1/CMP/raw_diffusion/2x2x2'
    print "DSI data path: " + DSI_path

    files = glob(op.join(DSI_path, 'MR*.nii.gz')) # list of DSI volumes, resolution 2x2x2
    files = sorted(files)
    N = len(files) # number of acquired volumes

    b0img = nb.load(op.join(DSI_path,'MR0000.nii.gz'))
    hdr = b0img.get_header()
    affine = b0img.get_affine()

    b0 = b0img.get_data()
    DSIq5 = np.ndarray(shape=(b0.shape[0],b0.shape[1],b0.shape[2],N), dtype=float)
    count = 0
    for thisfile in files:
        print "load file", thisfile
        img = nb.load(op.join(DSI_path,thisfile))
        DSIq5[:,:,:,count] = img.get_data()
        count = count + 1
        
    print DSIq5.shape

    grad_514_path = '/home/agriffa/dev/cmp/cmp/data/diffusion/gradient_tables/dsi_grad_514.txt'
    q_points = np.genfromtxt(grad_514_path)
    q_points = q_points[:,1:] # from Van Wedeen matrix, select the coordinates columns only (last three columns)
    q_points = q_points[0:N,:] # from Van Wedeen matrix, select the first N lines only
    q_points = q_points * 5 # coordinates of the sampling points in q-space

    def pri(stri):
        print stri

    # do preprocessign
    q_axis, data, mid_pos = dsi_preprocess(DSIq5, q_points, callb = pri )
    # compute the value
    ADC4, ADC8 = dsi_adc(q_axis, data)

    # compute slow/fast adc
    #ADC4slow, ADC4fast, ADC8slow, ADC8fast = dsi_adc_slowfast(q_axis, data, mid_pos)

    # Save output maps
    # ADC8
    img = nb.Nifti1Image(ADC8, affine, hdr)
    img.to_filename('/home/agriffa/Desktop/ADC_normalized_signal/ADC8.nii.gz')
    sp.io.savemat('/home/agriffa/Desktop/ADC_normalized_signal/ADC8.mat', mdict={'matrix': ADC8})

    # ADC4
    img = nb.Nifti1Image(ADC4, affine, hdr)
    img.to_filename('/home/agriffa/Desktop/ADC_normalized_signal/ADC4.nii.gz')
    sp.io.savemat('/home/agriffa/Desktop/ADC_normalized_signal/ADC4.mat', mdict={'matrix': ADC4})

    # Ku8
#    img = nb.Nifti1Image(Ku8, affine, hdr)
#    img.to_filename('/home/agriffa/Desktop/ADC_normalized_signal/Ku8')
#    sp.io.savemat('/home/agriffa/Desktop/ADC_normalized_signal/Ku8.mat', mdict={'matrix': Ku8})
#    # Ku4
#    img = nb.Nifti1Image(Ku4, affine, hdr)
#    img.to_filename('/home/agriffa/Desktop/ADC_normalized_signal/Ku4')
#    sp.io.savemat('/home/agriffa/Desktop/ADC_normalized_signal/Ku4.mat', mdict={'matrix': Ku4})
#    # P08
#    img = nb.Nifti1Image(P08,, affine, hdr)
#    img.to_filename('/home/agriffa/Desktop/ADC_normalized_signal/P08')
#    sp.io.savemat('/home/agriffa/Desktop/ADC_normalized_signal/P08.mat', mdict={'matrix': P08})
#    # P04
#    img = nb.Nifti1Image(P04,affine)
#    img.to_filename('/home/agriffa/Desktop/ADC_normalized_signal/P04')
#    sp.io.savemat('/home/agriffa/Desktop/ADC_normalized_signal/P04.mat', mdict={'matrix': P04})

    # ADC8_fast
    img = nb.Nifti1Image(ADC8_fast,affine, hdr)
    img.to_filename('/home/agriffa/Desktop/ADC_normalized_signal/ADC8_fast.nii.gz')
    sp.io.savemat('/home/agriffa/Desktop/ADC_normalized_signal/ADC8_fast.mat', mdict={'matrix': ADC8_fast})
    # ADC8_slow
    img = nb.Nifti1Image(ADC8_slow,affine, hdr)
    img.to_filename('/home/agriffa/Desktop/ADC_normalized_signal/ADC8_slow.nii.gz')
    sp.io.savemat('/home/agriffa/Desktop/ADC_normalized_signal/ADC8_slow.mat', mdict={'matrix': ADC8_slow})
    # ADC4_fast
    img = nb.Nifti1Image(ADC4_fast,affine, hdr)
    img.to_filename('/home/agriffa/Desktop/ADC_normalized_signal/ADC4_fast.nii.gz')
    sp.io.savemat('/home/agriffa/Desktop/ADC_normalized_signal/ADC4_fast.mat', mdict={'matrix': ADC4_fast})
    # ADC4_slow
    img = nb.Nifti1Image(ADC4_slow,affine, hdr)
    img.to_filename('/home/agriffa/Desktop/ADC_normalized_signal/ADC4_slow.nii.gz')
    sp.io.savemat('/home/agriffa/Desktop/ADC_normalized_signal/ADC4_slow.mat', mdict={'matrix': ADC4_slow})

""" A general design of the conversion script to generate connectivity matrices """

import numpy as np
import networkx as nx
import nibabel as ni

# Input
#######

# TrackVis .trk file

trk_file = {'my_trackfile':'fibertracks.trk', 'trackfile2', 'other.trk'}

# A set of ROI files with potentially multiple resolutions
# ROI Nifti files

roi_file = { 'resolution1' : {'file':'ROI_res1.nii',\
                              'nr_of_regions': 100},\
             'resolution2': {'file':'ROI_res2.nii',
                             'nr_of_regions': 200}
             }


# Set of images that contain measures per voxel
# e.g. # FA.nii # ADC.nii

measure_file= {'FA':'FA.nii', 'ADC':'ADC.nii'}

# Function to operate on the set of fibers between ROIs

# Function to operate on the individual fibers



# Output
########

# Connectivity Matrices
# for each measure image and resolution

def compute_matrices_1(trk_file, measure_file)

	loop trackfiles
		loop measures
			compute mean,max,min,start_i,start_j,start_w, end_i,end_j,end_w
			store(trackfile_measure.npy) (nrfibers,nr_measures+index_start_point+index_end_point)
			

def compute_matrices2(output_file_from_cm_1, roi_files)

	loop_over_fibers, generate array for each roi1-roi2, compute average.

    for roi_k, roi_v in roi_file.items():
        # loop over roi files
        roi_f = open(roi_v['file'], 'r')
        
        # open trackvis file binary
        
        for me_k, me_v in measure_file.items():
            # loop over measures
            # open measure file
            measure_f = open(me_v, 'r') 

            # putative output filename for matrix
            fname = "%s_%s_matrix.npy" % (roi_k, me_k)
            
            # create an empty networkx graph with the nr_of_regions
            # to accumulate the computed lists for individual fibers
            netw = nx.empty_graph(roi_v['nr_of_regions'])

            # loop over all fibers
            
                # find start and end node
                
                # for a single fiber, loop over points
                # accumulate points in an array
                # after finish, apply fiber_func and  
                
                # enter in networkx graph, for start to end edge, the
                # computed scalar value to the list. create a new one when 
                # the edge is not existing
            
            # the networkx graph is now constructed for this ROI file
            # and measure, now we can apply the bundle_func to operate
            # on the accumlated lists between ROIs/nodes
            
            # create a connection matrix from the network
            # and store it under fname
             

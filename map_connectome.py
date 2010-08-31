#!/usr/bin/env python

# Connectome Mapping Pipeline TEMPLATE
# EPFL, CHUV, 2010

import os.path

#########################################
# Data and project specific configuration
#########################################

from cmt.configuration import PipelineConfiguration
myp = PipelineConfiguration()

# path to CMT_HOME using environment variable, or set directly
myp.cmt_home = os.path.join(os.environ['CMT_HOME'])
myp.dtdir = os.environ['DSI_PATH']

# My Subjects

subject_list = { ('subject1', 'tp1') : {'workingdir' : '/XXX/THE/PATH'},
                 ('subject2', 'tp1') : {'workingdir' : '/XXX/THE/PATH'},
                }


#########################
# Import the pipeline nodes
#########################

# import the raw_step%i from cmt.modules.*

## 1. REGISTRATION
## 2. FREESURFER
## 3. MASK: ROI_HR_th.nii / fsmask_1mm.nii CREATION (MASKCREATION)
## 4. DIFFUSION TOOLKIT
## 5. REGISTRATION: Apply registration ROI/WM --> b0
## 6. TRACTOGRAPHY
## 7. CONNECTION MATRIX
## 8. CONVERTER

#############################
# 4. Setup the pipeline nodes
#############################

# Tell fsl to generate all output in uncompressed nifti format
print fsl.FSLInfo.version()
fsl.FSLInfo.outputtype('NIFTI')

# setup the way matlab should be called
mlab.MatlabCommandLine.matlab_cmd = "matlab -nodesktop -nosplash -r"

# force FREESURFER to work in a different folder
fs.FSInfo.subjectsdir(os.path.abspath('fsdata'))

############################
# Connect the pipeline nodes
############################

mc_pipeline = pe.Pipeline()
mc_pipeline.config['workdir'] = os.path.abspath(workingdir)

# XXX: means what exactly ? 
mc_pipeline.config['use_parameterized_dirs'] = True

# mc_pipeline.connect(...)

######################
# Execute the pipeline
######################

if __name__ == '__main__':
    pass
    # mc_pipeline.run()
    # mc_pipeline.export_graph()

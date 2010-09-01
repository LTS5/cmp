#!/usr/bin/env python

# Connectome Mapping Pipeline TEMPLATE
# EPFL, CHUV, 2010

import os.path
from cmt.modules import *

#########################################
# Data and project specific configuration
#########################################

from cmt.configuration import PipelineConfiguration
myp = PipelineConfiguration()

myp.project_name = 'Testproject'
myp.project_dir = '/home/stephan/Dev/PyWorkspace/cmt-pipeline/branches/stephan/data/test_project'

myp.reg_mode = 'L'
myp.sharpness_odf = [0]
myp.do_wm_manual_correction = False
myp.wm_exchange_folder = None

myp.nr_of_gradient_directions = 515
myp.nr_of_sampling_directions = 181

myp.subject_list = { ('control001', 'tp1') :
                     {'workingdir' : os.path.join(myp.project_dir, 'control001', 'tp1'),
                      'age' : 55,
                      'sex' : X,
                      'description' : 'This subject is totally health!'},
                   }

#########################
# setting the environment
#########################
myp.cmt_home = os.path.join(os.environ['CMT_HOME'])
# "/home/stephan/Dev/PyWorkspace/cmt-pipeline/branches/stephan"
myp.cmt_binary = myp.get_cmt_binary_path()

myp.freesurfer_home = os.path.join(os.environ['FREESURFER_HOME'])
# "/home/stephan/Software/freesurfer" -> /bin

myp.fsl_home = os.path.join(os.environ['FSL_HOME'])
# "/usr/share/fsl" -> /bin

myp.dtk_home = os.environ['DTDIR']
# "/home/stephan/Software/dtk"
dtk_matrices = op.join(self.dtk_dir, 'matrices')

myp.matlab_home = "/home/stephan/Software/MATLAB/bin"
myp.matlab_prompt = "matlab -nosplash -nodesktop -r "

# XXX: NEED TO SOURC
# source "${FSL_HOME}/etc/fslconf/fsl.sh"
# source "${FREESURFER_HOME}/SetUpFreeSurfer.sh"
# export MATLABPATH="${CMT_HOME}:${CMT_HOME}/matlab_related:${CMT_HOME}/matlab_related/nifti:${CMT_HOME}/matlab_related/tractography:${CMT_HOME}/registration"

########################
# Run the pipeline steps
########################

#freesurfer.run()
diffusion.run()
tractograph.run()
cffconverter.run()

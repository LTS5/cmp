#!/usr/bin/env python

# Connectome Mapping Pipeline TEMPLATE
# EPFL, CHUV, 2010

import os.path
from cmt import *
from cmt.logme import *
import datetime as dt

#################################################
# Project and processing specific configuration #
#################################################

from cmt.configuration import PipelineConfiguration

myp = PipelineConfiguration('Testproject One')
myp.project_dir = os.path.join(os.path.dirname(__file__) )
myp.project_metadata = {# required metadata
                        'generator' : 'cmt 1.1',
                        'initial-creator' : 'Stephan Gerhard',
                        'institution' : 'EPFL / CHUV',
                        'creation-date' : '2010-09-17',
                        'modification-date' : '2010-09-17',
                        'species' : 'Homo sapiens',
                        'targetspace' : 'MNI305',
                        'legal-notice' : '',
                        'reference' : '',
                        'url' : '',
                        'description' : 'This is the first connectome file created with cmt',
                        # optional metadata
                        'metadata' : {'nr_of_subjects' : 2,
                                      'project_dir' : myp.project_dir}
                        }

myp.registration_mode = 'L'
myp.processing_mode = 'DSI'
myp.mode_parameters = {'nr_of_gradient_directions' : 515,
                       'nr_of_sampling_directions' : 181,
                       'lin_reg_param' : '-usesqform -nosearch -dof 6 -cost mutualinfo',
                       'odf_recon_param' : '-b0 1 -dsi -p 4 -sn 0 -ot nii',
                       'streamline_param' : '--angle 60 --rSeed 4',
                       # if nonlinear registration is used at all
                       # f  ->  smaller values give larger brain outline estimates
                       # g  ->  positive values give larger brain outline at bottom, smaller at top
                       'nlin_reg_bet_T2_param' : '-f 0.35 -g 0.15',
                       'nlin_reg_bet_b0_param' : '-f 0.2 -g 0.2',
                       'nlin_reg_fnirt_param' : ''}

# 1: run through the freesurfer step without stopping
# 2: prepare whitematter mask for correction (store it in subject dir/NIFTI
# 3: rerun freesurfer part with corrected white matter mask
myp.wm_handling = 1

# file types for raw data
myp.raw_glob = "*.ima"

# inspect the results of the registration by starting a fslview/trackvis instance
myp.inspect_registration = True

myp.subject_list = { ('testsubject1', 'tp1') :
                     {'workingdir' : os.path.join(myp.project_dir, 'testsubject1', 'tp1'),
                      'age' : 55,
                      'sex' :'X',
                      'description' : 'This subject is totally healthy!'},
                   }

#######################################
# Setting up the software environment #
#######################################

myp.freesurfer_home = os.path.join(os.environ['FREESURFER_HOME'])
myp.fsl_home = os.path.join(os.environ['FSL_HOME'])
myp.dtk_home = os.environ['DTDIR']
myp.dtk_matrices = os.path.join(myp.dtk_home, 'matrices')
myp.matlab_home = "/home/stephan/Software/MATLAB/"
myp.matlab_bin = os.path.join(myp.matlab_home, 'bin')
myp.matlab_prompt = "matlab -nosplash -r " #"matlab -nosplash -nodesktop -r "
os.environ['FSLOUTPUTTYPE'] = 'NIFTI'


#######################################
# Consistency check the configuration #
#######################################

myp.consistency_check()

##########################
# Run the pipeline steps #
##########################

# setup only one subject, will loop over all subjects later
sid =  ('testsubject1', 'tp1') 

# setup logger for the subject
myp.subject_list[sid]['logger'] = \
    getLog(os.path.join(myp.get_log4subject(sid), \
                        'pipeline-%s-%s-%s.log' % (str(dt.datetime.now()), sid[0], sid[1] ) )) 

dicomconverter.run(myp, sid )
#registration.run(myp, sid )
#freesurfer.run(myp, sid )
#maskcreation.run(myp, sid )
#diffusion.run(myp, sid )
#apply_registration.run(myp, sid )
#tractography.run(myp, sid )
#connectionmatrix.run(myp, sid )

# out-of-main-loop:
#cffconverter.run(myp)
#!/usr/bin/env python

# Connectome Mapping Pipeline TEMPLATE
# EPFL, CHUV, 2010

import os.path
import cmt
 
#################################################
# Project and processing specific configuration #
#################################################

myp = cmt.configuration.PipelineConfiguration('Testproject One')
myp.project_dir = '/home/cmt/data/test_project_dsi'
myp.project_metadata = {# required metadata
                        'generator' : 'cmt 1.1',
                        'initial-creator' : 'Stephan Gerhard',
                        'institution' : 'EPFL / CHUV',
                        'creation-date' : '2010-09-17',
                        'modification-date' : '2010-09-17',
                        'species' : 'Homo sapiens',
                        #'targetspace' : 'RAS',
                        'legal-notice' : '',
                        'reference' : '',
                        'url' : '',
                        'description' : 'This is the first connectome file created with cmt',
                        # optional metadata
                        'metadata' : {'nr_of_subjects' : 2,
                                      'project_dir' : myp.project_dir}
                        }

myp.registration_mode = 'L'

myp.processing_mode = ('DSI', 'Lausanne2011')

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

# email notification
myp.emailnotify = ['christophe.chenes@gmail.com']

# dti processing mode
# dti_recon $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion/iso/*_000.hdr $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion/iso/$MY_SUBJECT -gm  $DTI_PATH/dti_30_gradient.txt -b 1000 -b0 1 -iop 1 0 0 0 1 0 -oc -p 3 -sn 0 -ot nii
# param : -b 1000 -b0 1 -iop 1 0 0 0 1 0 -oc -p 3 -sn 0 -ot nii
# gradient map : -gm  $DTI_PATH/dti_30_gradient.txt

# 1: run through the freesurfer step without stopping
# 2: prepare whitematter mask for correction (store it in subject dir/NIFTI
# 3: rerun freesurfer part with corrected white matter mask
myp.wm_handling = 1

# inspect the results of the registration by starting a fslview instance
myp.inspect_registration = False

myp.subject_list = { ('christophe1', 'tp1') :
                     {'workingdir' : os.path.join(myp.project_dir, 'christophe1', 'tp1'),
                      'age' : 22,
                      'sex' :'X',
                      'description' : 'This subject is totally healthy!',
                      # file endings for raw data
                      'raw_glob_diffusion' : '*.ima',
                      'raw_glob_T1' : '*.ima',
                      'raw_glob_T2' : '*.ima'},
                   }

#######################################
# Setting up the software environment #
#######################################

#myp.freesurfer_home = os.path.join(os.environ['FREESURFER_HOME'])
#myp.fsl_home = os.path.join(os.environ['FSL_HOME'])
#myp.dtk_home = os.environ['DTDIR']
#myp.dtk_matrices = os.path.join(myp.dtk_home, 'matrices')
#myp.matlab_home = "/home/stephan/Software/MATLAB/"
#myp.matlab_bin = os.path.join(myp.matlab_home, 'bin')
#myp.matlab_prompt = "matlab -nosplash -r " #"matlab -nosplash -nodesktop -r "
#os.environ['FSLOUTPUTTYPE'] = 'NIFTI'

##########################
# Run the pipeline steps #
##########################

myp.preprocessing = False
myp.dicomconverter = False
myp.registration = False
myp.freesurfer = False
myp.maskcreation = False
myp.diffusion = False
myp.apply_registration = False
myp.tractography = False
myp.fiberfiltering = False
myp.connectionmatrix = True
myp.cffconverter = False

####################
# Finally, map it! #
####################
cmt.connectome.mapit(myp)

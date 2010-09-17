""" The configuration modules exposes a configuration class based on traits
that is used to create the configuration for a project. Traits attribute are used
to check if the pipeline supports the options """

import enthought.traits.api as traits
import os.path as op
import sys

class PipelineConfiguration(traits.HasTraits):
       
    # project name
    project_name = traits.Str(desc="the name of the project")
        
    # project metadata (for connectome file)
    project_metadata = traits.Dict(desc="project metadata to be stored in the connectome file")

    # data path where the project is
    project_dir = traits.Directory(exists=True, desc="data path to where the project is stored")
    
    # subject list
    subject_list = traits.Dict(desc="a dictionary representing information about single subjects")
    
    # choose between 'L' (linear) and 'N' (non-linear)
    registration_mode = traits.Either("L", "N", desc="registration mode: linear or non-linear")
    
    # going to support qBall, HARDI
    processing_mode = traits.Enum( ['DSI', 'DTI'], desc="diffusion MRI processing mode available")   
    
    # do you want to do manual whit matter mask correction?
    wm_handling = traits.Int(desc="in what state should the freesurfer step be processed")
    
    # dicom format for the raw data
    raw_glob = traits.Str(desc='file glob for raw data files')
    
    # start up fslview
    inspect_registration = traits.Bool(desc='start fslview to inspect the the registration results')

    # matlab invocation prompt
    matlab_prompt = traits.Str("matlab -nodesktop -nosplash -r")  
        
    ################################
    # External package Configuration
    ################################

    
    # XXX: think about
    # /colortable_and_gcs
    # /matlab_related
    # /registration
    # /resampled_lpi_atlas

    cmt_home = traits.Directory(exists=True, desc="contains data files shipped with the pipeline")
    cmt_bin = traits.Directory(exists=True, desc="contains binary files shipped with the pipeline")
    cmt_matlab = traits.Directory(exists=True, desc="contains matlab related files shipped with the pipeline")
    freesurfer_home = traits.Directory(exists=True, desc="path to Freesurfer 5.0+")
    fsl_home = traits.Directory(exists=True, desc="path to FSL")
    dtk_home = traits.Directory(exists=True, desc="path to diffusion toolkit")
    dtk_matrices = traits.Directory(exists=True, desc="path to diffusion toolkit matrices")
    matlab_home = traits.Directory(exists=True, desc="path to matlab")

    def __init__(self, **kwargs):
        # NOTE: In python 2.6, object.__init__ no longer accepts input
        # arguments.  HasTraits does not define an __init__ and
        # therefore these args were being ignored.
        super(PipelineConfiguration, self).__init__(**kwargs)

    def consistency_check(self):
        """ Provides a checking facility for configuration objects """
        
        # check if software paths exists
        pas = [self.cmt_home, self.cmt_bin, self.cmt_matlab, self.freesurfer_home, \
               self.fsl_home, self.dtk_home, self.dtk_matrices, self.matlab_home]
        for p in pas:
            if not op.exists(p):
                msg = 'Required software path does not exists: %s' % p
                Exception(msg)
                
        if self.processing_mode == 'DSI':
            ke = self.mode_parameters.keys()
            if not 'sharpness_odf' in ke:
                Exception('Parameter "sharpness_odf" not set as key in mode_parameters. Required for DSI.')
            else:
                if len(self.mode_parameters['sharpness_odf']) > 2:
                    Exception('Too many values for sharpness_odf parameter. Maximally two.')
                
            if not 'nr_of_gradient_directions' in ke:
                Exception('Parameter "nr_of_gradient_directions" not set as key in mode_parameters. Required for DSI.')
                
            if not 'nr_of_sampling_directions' in ke:
                Exception('Parameter "nr_of_sampling_directions" not set as key in mode_parameters. Required for DSI.')
                
            
        
    def get_raw4subject(self, subject):
        """ Return raw data path for subject """
        return op.join(self.get_subj_dir(subject), '1__RAWDATA')
        
    def get_fs4subject(self, subject):
        """ Returns the subject root folder path for freesurfer files """
        return op.join(self.get_subj_dir(subject), '3__FREESURFER')
        
    def get_nifti4subject(self, subject):
        """ Returns the subject root folder path for nifti files """
        return op.join(self.get_subj_dir(subject), '2__NIFTI')

    def get_cmt_rawdiff4subject(self, subject):
        return op.join(self.get_subj_dir(subject), '4__CMT', 'raw_diffusion')
        
    def get_cmt_fsout4subject(self, subject):
        return op.join(self.get_subj_dir(subject), '4__CMT', 'fs_output')
    
    def get_cmt_fibers4subject(self, subject):
        return op.join(self.get_subj_dir(subject), '4__CMT', 'fibers')
        
    def get_cmt_fsmask4subject(self, subject):
        return op.join(self.get_cmt_fsout4subject(subject), 'registred', 'HR__registered-TO-b0')

    def get_subj_dir(self, subject):
        return self.subject_list[subject]['workingdir']
    
    def get_dsi_matrix(self):
        """ Returns the correct DSI matrix given the parameters
        
        1. dsi dir
        2. number of gradient directions
        3. number of sampling directions
        """
        
        # XXX: check fist if it is available at all
        fpath = op.join(self.dtk_matrices, "DSI_matrix_%sx%s.dat" % (self.nr_of_gradient_directions, self.nr_of_sampling_directions))
        if not op.exists(fpath):
            print "DSI matrix does not exists: %s" % fpath
            
        return fpath
    
    def get_cmt_binary_path(self):
        """ Returns the path to the binary files for the current platform
        and architecture """
        
        if sys.platform == 'linux2':
    
            import platform as pf
            if '32' in pf.architecture()[0]:
                return op.join(op.dirname(__file__), "linux2", "bit32")
            elif '64' in pf.architecture()[0]:
                return op.join(op.dirname(__file__), "linux2", "bit64")
            else:
                raise('No binary files compiled for your platform!')
    

    
""" The configuration modules exposes a configuration class based on traits
that is used to create the configuration for a project. Traits attribute are used
to check if the pipeline supports the options """

import enthought.traits.api as traits
import os.path as op
import sys

from enthought.traits.api import HasTraits, Instance, Any, Int, Array, NO_COMPARE, Either, Bool, Str

class PipelineConfiguration(traits.HasTraits):
    
    # data path where the projects are
    project_dir = traits.Directory(exists=True, desc="data path to where the projects are stored")
    
    # project name
    project_name = traits.Str(desc="the name of the project")
        
    # subject list
    subject_list = traits.Dict(desc="a list of subject names corresponding to their folders")
        
    # for each subject, this is the time-point where to move
    # "tracto masks" from (LEAVE EMPTY if using the same time-point)
    # from_tp = []()
    # XXX, sg: what is this for? can this go into subject metadata?
    
    # choose between 'L' (linear) and 'N' (non-linear)
    reg_mode = traits.Either("L", "N", desc="registration mode: linear or non-linear")
    
    # sharpness for the 2? ODF (NB: set to 0 if using only 1 ODF)
#    sharpness_20df = "0"
    sharpness_odf = traits.ListInt(desc="number of sharpness parameters")
    # XXX: is it a list? or an integer that creates a sequence?
    
    # do you want to do manual whit matter mask correction?
    do_wm_manual_correction = traits.Bool(desc="do you want to do manual whit matter mask correction?")
    
    # folder where to STORE/RETRIEVE files for 'wm mask' manual correction
    wm_exchange_folder = traits.Directory(exits=False, desc="folder where to store and retrieve files for 'wm mask' manual correction")
    # XXX: shouldn't this be a folder relative to the subject/timepoint folder?
    
    nr_of_gradient_directions = traits.Int # 515
    nr_of_sampling_directions = traits.Int # 181
    
    # use `workingdir` as the disk location to use when running the processes and keeping their outputs.
    # workingdir = traits.Directory(exists=True, desc="disk location to use when running the processes")
    # XXX: not sure yet if we needs this
    
    ################################
    # External package Configuration
    ################################
    
    cmt_home = traits.Directory(exists=True, desc="contains data files shipped with the pipeline")
    
    cmt_bin = traits.Directory(exists=True, desc="contains binary files shipped with the pipeline")
    cmt_matlab = traits.Directory(exists=True, desc="contains matlab related files shipped with the pipeline")
    
    # XXX: think about
    # /colortable_and_gcs
    # /matlab_related
    # /registration
    # /resampled_lpi_atlas
    
    freesurfer_home = traits.Directory(exists=True, desc="")
    # XXX: do we need this?
    # freesurfer_subjects = traits.Directory(exists=True, desc="")

    fsl_home = traits.Directory(exists=True, desc="")

    dtk_home = traits.Directory(exists=True, desc="")
    dtk_matrices = traits.Directory(exists=True, desc="")

    matlab_home = traits.Directory(exists=True, desc="")
    matlab_prompt = traits.Str("matlab -nodesktop -nosplash -r")  


    
    def __init__(self, **kwargs):
        # NOTE: In python 2.6, object.__init__ no longer accepts input
        # arguments.  HasTraits does not define an __init__ and
        # therefore these args were being ignored.
        super(PipelineConfiguration, self).__init__(**kwargs)
        
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
        return op.join(self.dtk_matrices, "DSI_matrix_%sx%s.dat" % (self.nr_of_gradient_directions, self.nr_of_sampling_directions))
    
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
    
    
    
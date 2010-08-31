""" The configuration modules exposes a configuration class based on traits
that is used to create the configuration for a project. Traits attribute are used
to check if the pipeline supports the options """

import enthought.traits.api as traits
import os.path as op

from enthought.traits.api import HasTraits, Instance, Any, Int, Array, NO_COMPARE, Either, Bool, Str

class PipelineConfiguration(traits.HasTraits):
    
    # data path where the projects are
#    data_dir = os.path.abspath('data')
    data_dir = traits.Directory(exists=True, desc="data path where the projects are stored")
    
    # project name
#    project = "testproject"
    project = traits.Str(desc="the name of the project")
    
    # subject list
#    subject_list = ['testsubject_tp1']
    subject_list = traits.ListStr(desc="a list of subject names corresponding to their folders")
    
    # for each subject, a tuple of timepoints to process
#    my_tp = [('tp1')]
    
    # for each subject, this is the time-point where to move
    # "tracto masks" from (LEAVE EMPTY if using the same time-point)
#    from_tp = []()
    
    # choose between 'L' (linear) and 'N' (non-linear)
#    reg_mode = "L"
    reg_mode = traits.Either("L", "N", desc="registration mode: linear or non-linear")
    
    # sharpness for the 2? ODF (NB: set to 0 if using only 1 ODF)
#    sharpness_20df = "0"
    sharpness_odf = traits.ListInt(desc="number of sharpness parameters")
    # XXX: is it a list? or an integer that creates a sequence?
    
    # folder where to STORE/RETRIEVE files for 'wm mask' manual correction
#    wm_exchange_folder = os.path.abspath("/home/dsi/Desktop/wm_correction")
    wm_exchange_folder = traits.Directory(exits=False, desc="folder where to store and retrieve files for 'wm mask' manual correction")
    
    # use `workingdir` as the disk location to use when running the processes and
    # keeping their outputs.
#    workingdir = os.path.abspath("workdir")
    workingdir = traits.Directory(exists=True, desc="disk location to use when running the processes")
    
    freesurfer_home = traits.Directory(exists=True, desc="")
    #FREESURFER_HOME="/home/stephan/Software/freesurfer"
    #export FSL_HOME="/usr/share/fsl"
    # FREESURFER configuration
    #source "${FREESURFER_HOME}/SetUpFreeSurfer.sh"

    fsl_home = traits.Directory(exists=True, desc="")
    # FSL configuration
    #source "${FSL_HOME}/etc/fslconf/fsl.sh"
    #export PATH="${FSL_HOME}/bin:${PATH}"

    cmt_home = traits.Directory(exists=True, desc="contains data files shipped with the pipeline")
    #export CMT_HOME="/home/stephan/Dev/PyWorkspace/cmt-pipeline/branches/stephan"
    # CMT_HOME directory (contains data files shipped with the pipeline, such as
    # /colortable_and_gcs, /resampled_lpi_atlas, 181_vecs.dat, compiled C++ code,
    # XXX: what else?)
    #    cmt_home = os.path.abspath('cmt-pipeline')
    # CONNECTOME configuration
    #export PATH="${CMT_HOME}:${CMT_HOME}/c++/bin:$PATH"
    
    dtdir = traits.Directory(exists=True, desc="")
    dsi_path = traits.Directory(exists=True, desc="")
    dsi_path = op.join(self.dtdir, 'matrices')
    #export DTDIR="/home/stephan/Software/dtk"
    #export DSI_PATH="${DTDIR}/matrices/"
    #export PATH="${DTDIR}:${PATH}"

    matlabdir = traits.Directory(exists=True, desc="")
    matlabcmd = traits.Directory(exists=True, desc="")
    matlab_prompt = traits.Str("matlab -nodesktop -nosplash -r")  
    #export PATH="${MATLABDIR}:${PATH}"
    #export MATLABPATH="${CMT_HOME}:${CMT_HOME}/matlab_related:${CMT_HOME}/matlab_related/nifti:${CMT_HOME}/matlab_related/tractography:${CMT_HOME}/registration"
    #export MY_MATLAB="matlab -nosplash -nodesktop -r "    
    #export MATLABDIR="/home/stephan/Software/MATLAB/bin"
    #export MATLABCMD=$pathtomatlabdir/bin/$platform/MATLAB
    
    nr_of_gradient_directions = traits.Int # 515
    nr_of_X = traits.Int # 181
    
    def __init__(self, **kwargs):
        # NOTE: In python 2.6, object.__init__ no longer accepts input
        # arguments.  HasTraits does not define an __init__ and
        # therefore these args were being ignored.
        super(PipelineConfiguration, self).__init__(**kwargs)
        
    def get_dsi_matrix(self):
        """ Returns the correct DSI matrix given the parameters
        
        1. dsi dir
        2. number of gradient directions
        3. what?
        """
        
        # XXX: check fist if it is available at all
        return op.joing(self.dsi_path, "DSI_matrix_%sx%s.dat" % (self.nr_of_gradient_directions, self.nr_of_X))
    
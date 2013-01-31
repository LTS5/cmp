# Copyright (C) 2009-2011, Ecole Polytechnique Federale de Lausanne (EPFL) and
# Hospital Center and University of Lausanne (UNIL-CHUV), Switzerland
# All rights reserved.
#
#  This software is distributed under the open-source license Modified BSD.

""" The configuration is based on traits and used to create the configuration for a project. """

import traits.api as traits
import os.path as op, os
import sys
import datetime as dt

from cmp.logme import getLog
from cmp.pipeline import pipeline_status
from cmp.util import KeyValue
from .info import __version__
try:
    dipy_here = True
    import dipy
except ImportError:
    dipy_here = False


class PipelineConfiguration(traits.HasTraits):
       
    # project settings
    project_dir = traits.Directory(exists=False, desc="data path to where the project is stored")
        
    # project metadata (for connectome file)
    project_metadata = traits.Dict(desc="project metadata to be stored in the connectome file")
    # DEPRECATED: this field is deprecated after version >1.0.2
    generator = traits.Str()
    
    # parcellation scheme
    parcellation_scheme = traits.Enum("NativeFreesurfer", ["Lausanne2008", "NativeFreesurfer"], desc="used parcellation scheme")
    
    # choose between 'L' (linear) and 'N' (non-linear) and 'B' (bbregister)
    registration_mode = traits.Enum("Linear", ["Linear", "Nonlinear", "BBregister"], desc="registration mode: linear or non-linear or bbregister")

    # choose between 'L' (linear) and 'B' (bbregister)
    rsfmri_registration_mode = traits.Enum("Linear", ["Linear", "BBregister"], desc="registration mode: linear or bbregister")

    diffusion_imaging_model = traits.Enum( "DSI", ["DSI", "DTI", "QBALL"])
    
    # DSI
    nr_of_gradient_directions = traits.Str('515')
    nr_of_sampling_directions = traits.Str('181')
    odf_recon_param = traits.Str('-b0 1 -dsi -p 4 -sn 0')
    hardi_recon_param = traits.Str('-b0 1 -p 3 -sn 0')

    # DTI
    gradient_table_file = traits.File(exists=False)
    gradient_table = traits.Enum('siemens_64', ['custom', 'mgh_dti_006', 'mgh_dti_018', 'mgh_dti_030', 'mgh_dti_042', 'mgh_dti_060',
     'mgh_dti_072', 'mgh_dti_090', 'mgh_dti_120', 'mgh_dti_144', 'siemens_06',
     'siemens_12', 'siemens_20', 'siemens_256', 'siemens_30', 'siemens_64'])
    nr_of_b0 = traits.Str('1')
    max_b0_val = traits.Str('1000')
    dti_recon_param = traits.Str('')
    dtb_dtk2dir_param = traits.Str('')
    
    # tractography
    streamline_param = traits.Str('--angle 60  --seeds 32')
    
    # registration
    lin_reg_param = traits.Str('-usesqform -nosearch -dof 6 -cost mutualinfo')
    nlin_reg_bet_T2_param = traits.Str('-f 0.35 -g 0.15')
    nlin_reg_bet_b0_param = traits.Str('-f 0.2 -g 0.2')
    nlin_reg_fnirt_param = traits.Str('--subsamp=8,4,2,2 --miter==5,5,5,5 --lambda=240,120,90,30 --splineorder=3 --applyinmask=0,0,1,1 --applyrefmask=0,0,1,1')
    bb_reg_param = traits.Str('--init-header --dti')
    
    # dicom converter
    do_convert_diffusion = traits.Bool(True)
    do_convert_T1 = traits.Bool(True)
    do_convert_T2 = traits.Bool(False)
    do_convert_fMRI = traits.Bool(False)

    # rsfmri
    rsfmri_lin_reg_param = traits.Str('-usesqform -nosearch -dof 6 -cost mutualinfo')
    rsfmri_bb_reg_param = traits.Str('--init-header --dti')
    do_save_mat = traits.Bool(True)
    
    # DEPRECATED:
    subject_raw_glob_diffusion = traits.Str( "*.*" )
    subject_raw_glob_T1 = traits.Str( "*.*" )
    subject_raw_glob_T2 = traits.Str( "*.*" )
    extract_diffusion_metadata = traits.Bool(False)

    # subject
    subject_name = traits.Str(  )
    subject_timepoint = traits.Str( )
    subject_workingdir = traits.Directory()
    subject_logger = None
    subject_metadata = [KeyValue(key='description', value=''),
                        KeyValue(key='', value=''),
                        KeyValue(key='', value=''),
                        KeyValue(key='', value=''),
                        KeyValue(key='', value=''),
                        KeyValue(key='', value=''),]
    
    active_createfolder = traits.Bool(True)
    active_dicomconverter = traits.Bool(False)
    active_registration = traits.Bool(False)
    active_segmentation = traits.Bool(False)
    active_parcellation = traits.Bool(False)
    active_applyregistration = traits.Bool(False)
    active_reconstruction = traits.Bool(False)
    active_tractography = traits.Bool(False)
    active_fiberfilter = traits.Bool(False)
    active_connectome = traits.Bool(False)
    active_statistics = traits.Bool(False)
    active_rsfmri = traits.Bool(False)
    active_cffconverter = traits.Bool(False)
    skip_completed_stages = traits.Bool(False)

    # metadata
    creator = traits.Str()
    email =  traits.Str()
    publisher = traits.Str()
    created = traits.Date()
    modified = traits.Date()
    license =  traits.Str()
#    rights = traits.Str()
    reference = traits.Str()
#    relation =  traits.Str()
    species = traits.Str('Homo sapiens')
    description = traits.Str()

    # segmentation
    recon_all_param = traits.Str('-all -no-isrunning')

    # parcellation
    custompar_nrroi = traits.Int()
    custompar_nodeinfo = traits.File()
    custompar_volumeparcell = traits.File()
    
    # fiber filtering
    apply_splinefilter = traits.Bool(True, desc='apply the spline filtering from diffusion toolkit')
    apply_fiberlength = traits.Bool(True, desc='apply cutoff to fiber lengths')
    fiber_cutoff_lower = traits.Float(20.0, desc='cut fibers that are shorter in length than given length in mm')
    fiber_cutoff_upper = traits.Float(500.0, desc='cut fibers that are longer in length than given length in mm') 

    # measures
    connection_P0 = traits.Bool(False)
    connection_gfa = traits.Bool(False)
    connection_kurtosis = traits.Bool(False)
    connection_skewness = traits.Bool(False)
    connection_adc = traits.Bool(False)
    connection_fa = traits.Bool(False)

    # cff converter
    cff_fullnetworkpickle = traits.Bool(True, desc='stores the full network pickle generated by connectome creation')
    cff_cmatpickle = traits.Bool(True)
    cff_originalfibers = traits.Bool(True, desc='stores original fibers')
    cff_filteredfibers = traits.Bool(True, desc='stores filtered fibers')
    cff_finalfiberlabels = traits.Bool(True, desc='stores final fibers and their labelarrays')
    cff_fiberarr = traits.Bool(True)
    cff_rawdiffusion = traits.Bool(True)
    cff_scalars = traits.Bool(True)
    cff_rawT1 = traits.Bool(True)
    cff_rawT2 = traits.Bool(True)
    cff_roisegmentation = traits.Bool(True, desc='stores multi-resolution parcellation volumes')
    cff_surfaces = traits.Bool(True, desc='stores individually genertated surfaces')
    cff_surfacelabels = traits.Bool(True, desc='stores individually genertated surfaces')

    # do you want to do manual white matter mask correction?
    wm_handling = traits.Enum(1, [1,2,3], desc="in what state should the freesurfer step be processed")
    
    # custom parcellation
    parcellation = traits.Dict(desc="provide the dictionary with your parcellation.")
    
    # start up fslview
    inspect_registration = traits.Bool(False, desc='start fslview to inspect the the registration results')
    fsloutputtype = traits.Enum( 'NIFTI', ['NIFTI'] )

    # connectome creation
    compute_curvature = traits.Bool(False)

    # email notification, needs a local smtp server
    # sudo apt-get install postfix
    emailnotify = traits.ListStr([], desc='the email address to send stage completion status message')
    
    freesurfer_home = traits.Directory(exists=False, desc="path to Freesurfer")
    fsl_home = traits.Directory(exists=False, desc="path to FSL")
    dtk_home = traits.Directory(exists=False, desc="path to diffusion toolkit")

    # This file stores descriptions of the inputs/outputs to each stage of the
    # CMP pipeline.  It can be queried using the PipelineStatus python object 
    pipeline_status_file = traits.Str( "cmp.status" )
    
    # Pipeline status object
    pipeline_status = pipeline_status.PipelineStatus()

    def _get_lausanne_parcellation(self, parcel = "NativeFreesurfer"):
        
        if parcel == "Lausanne2008":
            return {
                'scale33' : {'number_of_regions' : 83,
                                        # contains name, url, color, freesurfer_label, etc. used for connection matrix
                                        'node_information_graphml' : op.join(self.get_lausanne_parcellation_path('resolution83'), 'resolution83.graphml'),
                                        # scalar node values on fsaverage? or atlas?
                                        'surface_parcellation' : None,
                                        # scalar node values in fsaverage volume?
                                        'volume_parcellation' : None,
                                        # the subdirectory name from where to copy parcellations, with hemispheric wildcard
                                        'fs_label_subdir_name' : 'regenerated_%s_36',
                                        # should we subtract the cortical rois for the white matter mask?
                                        'subtract_from_wm_mask' : 1,
                                        },
                            'scale60' : {'number_of_regions' : 129,
                                        'node_information_graphml' : op.join(self.get_lausanne_parcellation_path('resolution150'), 'resolution150.graphml'),
                                        'surface_parcellation' : None,
                                        'volume_parcellation' : None,
                                        'fs_label_subdir_name' : 'regenerated_%s_60',
                                        'subtract_from_wm_mask' : 1,
                                        },
                            'scale125' : {'number_of_regions' : 234,
                                        'node_information_graphml' : op.join(self.get_lausanne_parcellation_path('resolution258'), 'resolution258.graphml'),
                                        'surface_parcellation' : None,
                                        'volume_parcellation' : None,
                                        'fs_label_subdir_name' : 'regenerated_%s_125',
                                        'subtract_from_wm_mask' : 1,
                                        },
                            'scale250' : {'number_of_regions' : 463,
                                        'node_information_graphml' : op.join(self.get_lausanne_parcellation_path('resolution500'), 'resolution500.graphml'),
                                        'surface_parcellation' : None,
                                        'volume_parcellation' : None,
                                        'fs_label_subdir_name' : 'regenerated_%s_250',
                                        'subtract_from_wm_mask' : 1,
                                        },
                            'scale500' : {'number_of_regions' : 1015,
                                        'node_information_graphml' : op.join(self.get_lausanne_parcellation_path('resolution1015'), 'resolution1015.graphml'),
                                        'surface_parcellation' : None,
                                        'volume_parcellation' : None,
                                        'fs_label_subdir_name' : 'regenerated_%s_500',
                                        'subtract_from_wm_mask' : 1,
                                        },
                           }
        else:
            return {'freesurferaparc' : {'number_of_regions' : 83,
                                        # contains name, url, color, freesurfer_label, etc. used for connection matrix
                                        'node_information_graphml' : op.join(self.get_lausanne_parcellation_path('freesurferaparc'), 'resolution83.graphml'),
                                        # scalar node values on fsaverage? or atlas? 
                                        'surface_parcellation' : None,
                                        # scalar node values in fsaverage volume?
                                        'volume_parcellation' : None,
                                        }
            }
    
    def __init__(self, **kwargs):
        # NOTE: In python 2.6, object.__init__ no longer accepts input
        # arguments.  HasTraits does not define an __init__ and
        # therefore these args were being ignored.
        super(PipelineConfiguration, self).__init__(**kwargs)

        # the default parcellation provided
        self.parcellation = self._get_lausanne_parcellation(parcel = "NativeFreesurfer")

        self.can_use_dipy = dipy_here
                
        # no email notify
        self.emailnotify = []
        
        # default gradient table for DTI
        self.gradient_table_file = self.get_cmp_gradient_table('siemens_64')
        
        # try to discover paths from environment variables
        try:
            self.freesurfer_home = op.join(os.environ['FREESURFER_HOME'])
            self.fsl_home = op.join(os.environ['FSLDIR'])
            self.dtk_home = os.environ['DTDIR']
            self.dtk_matrices = op.join(self.dtk_home, 'matrices')
        except KeyError:
            pass
        
        self.fsloutputtype = 'NIFTI'
        os.environ['FSLOUTPUTTYPE'] = self.fsloutputtype
        os.environ['FSLOUTPUTTYPE'] = 'NIFTI'
                
    def consistency_check(self):
        """ Provides a checking facility for configuration objects """
        
        # project name not empty
        if not op.exists(self.project_dir):
            msg = 'Your project directory does not exist!'
            raise Exception(msg)
        
        # check metadata
        if self.creator == '':
            raise Exception('You need to enter creator metadata!')
        if self.publisher == '':
            raise Exception('You need to enter publisher metadata!')
        if self.email == '':
            raise Exception('You need to enter email of a contact person!')
        
        # check if software paths exists
        pas = {'configuration.freesurfer_home' : self.freesurfer_home,
               'configuration.fsl_home' : self.fsl_home,
               'configuration.dtk_home' : self.dtk_home,
               'configuration.dtk_matrices' : self.dtk_matrices}
        for k,p in pas.items():
            if not op.exists(p):
                msg = 'Required software path for %s does not exists: %s' % (k, p)
                raise Exception(msg)

        if self.subject_workingdir == '':
            msg = 'No working directory defined for subject'
            raise Exception(msg)
#        else:
#            wdir = self.get_subj_dir()
#            if not op.exists(wdir):
#                msg = 'Working directory %s does not exists for subject' % (wdir)
#                raise Exception(msg)
#            else:
#                wdiff = op.join(self.get_raw_diffusion())
#                print wdiff
#                if not op.exists(wdiff):
#                    msg = 'Diffusion MRI subdirectory %s does not exists for the subject' % wdiff
#                    raise Exception(msg)
#                wt1 = op.join(self.get_rawt1())
#                if not op.exists(wt1):
#                    msg = 'Structural MRI subdirectory %s T1 does not exist in RAWDATA' % wt1
#                    raise Exception(msg)
        
    def get_cmp_home(self):
        """ Return the cmp home path """
        return op.dirname(__file__)
        
    def get_rawdata(self):
        """ Return raw data path for the subject """
        return op.join(self.get_subj_dir(), 'RAWDATA')
    
    def get_log(self):
        """ Get subject log dir """
        return op.join(self.get_subj_dir(), 'LOG')
    
    def get_logname(self, suffix = '.log'):
        """ Get a generic name for the log and pickle files """
        a=dt.datetime.now()
        return 'pipeline-%s-%02i%02i-%s-%s%s' % ( a.date().isoformat(),
                                                       a.time().hour,
                                                       a.time().minute,
                                                       self.subject_name,
                                                       self.subject_timepoint,
                                                       suffix )
    
    def get_logger(self):
        """ Get the logger instance created """
        if self.subject_logger is None:
            # setup logger for the subject
            self.subject_logger = \
                getLog(os.path.join(self.get_log(), self.get_logname())) 
            return self.subject_logger
        else: 
            return self.subject_logger
        
    def get_rawglob(self, modality):
        """ DEPRECATED: Get the file name endings for modality """
        
        if modality == 'diffusion':
            if not self.subject_raw_glob_diffusion == '':
                return self.subject_raw_glob_diffusion
            else:
                raise Exception('No raw_glob_diffusion defined for subject')

        elif modality == 'T1':
            if not self.subject_raw_glob_T1 == '':
                return self.subject_raw_glob_T1
            else:
                raise Exception('No raw_glob_T1 defined for subject')
            
        elif modality == 'T2':
            if not self.subject_raw_glob_T2 == '':
                return self.subject_raw_glob_T2
            else:
                raise Exception('No raw_glob_T2 defined for subject')

    def get_dicomfiles(self, modality):
        """ Get a list of dicom files for the requested modality. Tries to
        discover them automatically
        """
        from glob import glob

        if modality == 'diffusion':
            pat = self.get_raw_diffusion()
        elif modality == 'T1':
            pat = self.get_rawt1()
        elif modality == 'T2':
            pat = self.get_rawt2()
        elif modality == 'fMRI':
            pat = self.get_rawrsfmri()

        # discover files with *.* and *
        difiles = sorted( glob(op.join(pat, '*.*')) + glob(op.join(pat, '*')) )

        # exclude potential .nii and .nii.gz files
        difiles = [e for e in difiles if not e.endswith('.nii') and not e.endswith('.nii.gz')]

        # check if no files and throw exception
        if len(difiles) == 0:
            raise Exception('Could not find any DICOM files in folder %s' % pat )

        return difiles

    def get_rawrsfmri(self):
        """ Get raw functional MRI path for subject """
        return op.join(self.get_rawdata(), 'fMRI')

    def get_rawt1(self):
        """ Get raw structural MRI T1 path for subject """
        return op.join(self.get_rawdata(), 'T1')

    def get_rawt2(self):
        """ Get raw structural MRI T2 path for subject """
        return op.join(self.get_rawdata(), 'T2')

    def get_subj_dir(self):
        return self.subject_workingdir

    def get_raw_diffusion(self):
        """ Get the raw diffusion path for subject """
        if self.diffusion_imaging_model == 'DSI':
            return op.join(self.get_subj_dir(), 'RAWDATA', 'DSI')
        elif self.diffusion_imaging_model == 'DTI':
            return op.join(self.get_subj_dir(), 'RAWDATA', 'DTI')
        elif self.diffusion_imaging_model == 'QBALL':
            return op.join(self.get_subj_dir(), 'RAWDATA', 'QBALL')

    def get_fs(self):
        """ Returns the subject root folder path for freesurfer files """
        return op.join(self.get_subj_dir(), 'FREESURFER')
    
    def get_stats(self):
        """ Return statistic output path """
        return op.join(self.get_subj_dir(), 'STATS')
    
    def get_cffdir(self):
        """ Returns path to store connectome file """
        return op.join(self.get_cmp(), 'cff')
    
    def get_nifti(self):
        """ Returns the subject root folder path for nifti files """
        return op.join(self.get_subj_dir(), 'NIFTI')

    def get_nifti_trafo(self):
        """ Returns the path to the subjects transformation / registration matrices """
        return op.join(self.get_nifti(), 'transformations')

    def get_nifti_bbregister(self):
        """ Returns the path to the subjects transformation / registration matrices, bbregister mode """
        return op.join(self.get_nifti(), 'bbregister')

    def get_diffusion_metadata(self):
        """ Diffusion metadata, i.e. where gradient_table.txt is stored """
        return op.join(self.get_nifti(), 'diffusion_metadata')
    
    def get_nifti_wm_correction(self):
        """ Returns the path to the subjects wm_correction path """
        return op.join(self.get_nifti(), 'wm_correction')
        
    def get_cmp(self):
        return op.join(self.get_subj_dir(), 'CMP')

    def get_cmp_rawdiff(self, ):
        return op.join(self.get_cmp(), 'raw_diffusion')

    def get_cmp_rawdiff_reconout(self):
        """ Returns the output path for diffusion reconstruction without prefix"""
        if self.diffusion_imaging_model == 'DSI':
            return op.join(self.get_cmp(), 'raw_diffusion', 'odf_0')
        elif self.diffusion_imaging_model == 'DTI':
            return op.join(self.get_cmp(), 'raw_diffusion', 'dti_0')
        elif self.diffusion_imaging_model == 'QBALL':
            return op.join(self.get_cmp(), 'raw_diffusion', 'qball_0')

    def get_cmp_rawdiff_resampled(self):
        return op.join(self.get_cmp_rawdiff(), '2x2x2')
        
    def get_cmp_fsout(self):
        return op.join(self.get_cmp(), 'fs_output')
    
    def get_cmp_fibers(self):
        return op.join(self.get_cmp(), 'fibers')

    def get_cmp_scalars(self):
        return op.join(self.get_cmp(), 'scalars')
        
    def get_cmp_matrices(self):
        return op.join(self.get_cmp_fibers(), 'matrices')

    def get_cmp_fmri(self):
        return op.join(self.get_cmp(), 'fMRI')
    
    def get_cmp_tracto_mask(self):
        return op.join(self.get_cmp_fsout(), 'HR')
    
    def get_cmp_tracto_mask_tob0(self):
        return op.join(self.get_cmp_fsout(), 'HR__registered-TO-b0')
          
    def get_custom_gradient_table(self):
        """ Returns the absolute path to the custom gradient table
        with optional b-values in the 4th row """
        return self.gradient_table_file
    
    def get_cmp_gradient_table(self, name):
        """ Return default gradient tables shipped with CMP. These are mainly derived from
        Diffusion Toolkit """
        cmp_path = op.dirname(__file__)
        return op.join(cmp_path, 'data', 'diffusion', 'gradient_tables', name + '.txt')
    
    def get_dtb_streamline_vecs_file(self, as_text = False):
        """ Returns the odf directions file used for DTB_streamline """
        cmp_path = op.dirname(__file__)
        if as_text:
            return op.join(cmp_path, 'data', 'diffusion', 'odf_directions', '181_vecs.txt')
        else:
            return op.join(cmp_path, 'data', 'diffusion', 'odf_directions', '181_vecs.dat')
    
    # XXX
    def get_cmp_scalarfields(self):
        """ Returns a list with tuples with the scalar field name and the
        absolute path to its nifti file """
        
        ret = []
        
        if self.diffusion_imaging_model == 'DSI':
            # add gfa per default
            ret.append( ('gfa', op.join(self.get_cmp_scalars(), 'dsi_gfa.nii.gz')))
            # XXX: add adc per default
            
        elif  self.diffusion_imaging_model == 'DTI':
            # nothing to add yet for DTI
            pass
        
        return ret

        
    def get_dtk_dsi_matrix(self):
        """ Returns the DSI matrix from Diffusion Toolkit
        
        The parameters have to be set in the configuration object with keys:
        1. number of gradient directions : 'nr_of_gradient_directions'
        2. number of sampling directions : 'nr_of_sampling_directions'
        
        Example
        -------
        
        confobj.nr_of_gradient_directions = 515
        confobj.nr_of_sampling_directions = 181
        
        Returns matrix including absolute path to DSI_matrix_515x181.dat
        
        """
         
        grad = self.nr_of_gradient_directions
        samp = self.nr_of_sampling_directions
        fpath = op.join(self.dtk_matrices, "DSI_matrix_%sx%s.dat" % (grad, samp))
        if not op.exists(fpath):
            msg = "DSI matrix does not exists: %s" % fpath
            raise Exception(msg)
        return fpath
    
    
    def get_lausanne_atlas(self, name = None):
        """ Return the absolute path to the lausanne parcellation atlas
        for the resolution name """
        
        cmp_path = op.dirname(__file__)
        
        provided_atlases = ['myatlas_36_rh.gcs',
                            'myatlasP1_16_rh.gcs',
                            'myatlasP17_28_rh.gcs',
                            'myatlasP29_36_rh.gcs',
                            'myatlas_60_rh.gcs',
                            'myatlas_125_rh.gcs',
                            'myatlas_250_rh.gcs',
                            
                            'myatlas_36_lh.gcs',
                            'myatlasP1_16_lh.gcs',
                            'myatlasP17_28_lh.gcs',
                            'myatlasP29_36_lh.gcs',
                            'myatlas_60_lh.gcs',
                            'myatlas_125_lh.gcs',
                            'myatlas_250_lh.gcs']
        
        if name in provided_atlases:
            return op.join(cmp_path, 'data', 'colortable_and_gcs', 'my_atlas_gcs', name)
        else:
            msg = "Atlas %s does not exists" % name
            raise Exception(msg)

    def get_freeview_lut(self, name):
        """ Returns the Look-Up-Table as text file for a given parcellation scheme
        in  a dictionary """

        cmp_path = op.dirname(__file__)
        if name == "NativeFreesurfer":
            return {'freesurferaparc' : op.join(cmp_path, 'data', 'parcellation', 'nativefreesurfer', 'freesurferaparc', 'FreeSurferColorLUT_adapted.txt')}
        else:
            return ""
        
    def get_lausanne_parcellation_path(self, parcellationname):
        
        cmp_path = op.dirname(__file__)

        if self.parcellation_scheme == "Lausanne2008":
            allowed_default_parcel = ['resolution83', 'resolution150', 'resolution258', 'resolution500', 'resolution1015']
            if parcellationname in allowed_default_parcel:
                return op.join(cmp_path, 'data', 'parcellation', 'lausanne2008', parcellationname)
            else:
                msg = "Not a valid default parcellation name for the lausanne2008 parcellation scheme"
                raise Exception(msg)

        else:
            allowed_default_parcel = ['freesurferaparc']
            if parcellationname in allowed_default_parcel:
                return op.join(cmp_path, 'data', 'parcellation', 'nativefreesurfer', parcellationname)
            else:
                msg = "Not a valid default parcellation name for the NativeFreesurfer parcellation scheme"
                raise Exception(msg)
            
        
    def get_cmp_binary_path(self):
        """ Returns the path to the binary files for the current platform
        and architecture """
        
        if sys.platform == 'linux2':
    
            import platform as pf
            if '32' in pf.architecture()[0]:
                return op.join(op.dirname(__file__), "binary", "linux2", "bit32")
            elif '64' in pf.architecture()[0]:
                return op.join(op.dirname(__file__), "binary", "linux2", "bit64")
        else:
            raise('No binary files compiled for your platform!')
    
    def get_pipeline_status_file(self):
        """Returns the absolute path of the pipeline status file"""
        return op.join(self.get_subj_dir(), self.pipeline_status_file)
    
    def init_pipeline_status(self):
        """Create the 'cmp.status'.  The 'cmp.status' file contains information
        about the inputs/outputs of each pipeline stage"""        
        status_file = op.join(self.get_subj_dir(), self.pipeline_status_file)   
        self.pipeline_status.Pipeline.name = "cmp"
        self.pipeline_status.SaveToFile(status_file)

        
    def update_pipeline_status(self):
        """Update the pipeline status on disk with the current status in memory"""
        status_file = op.join(self.get_subj_dir(), self.pipeline_status_file)
        self.pipeline_status.SaveToFile(status_file)
        

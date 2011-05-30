# Example script to setup the pipeline configuration
# Use cmpgui.print_traits() to show all the available attributes
# from within IPython

import cmp
from cmp.gui import CMPGUI
cmpgui = CMPGUI()

cmpgui.project_dir =                u'/home/sgerhard/data/project01_dsi'
cmpgui.subject_workingdir =         u'/home/sgerhard/data/project01_dsi/ale01/tp1'
cmpgui.subject_timepoint =          u'tp1'
cmpgui.subject_name =               u'ale01'
cmpgui.subject_raw_glob_T1 =        '*.*'
cmpgui.subject_raw_glob_T2 =        '*.*'
cmpgui.subject_raw_glob_diffusion = '*.*'

cmpgui.active_applyregistration =   True
cmpgui.active_cffconverter =        True
cmpgui.active_connectome =          True
cmpgui.active_createfolder =        True
cmpgui.active_dicomconverter =      True
cmpgui.active_fiberfilter =         True
cmpgui.active_parcellation =        True
cmpgui.active_reconstruction =      True
cmpgui.active_registration =        True
cmpgui.active_segmentation =        True
cmpgui.active_statistics =          False
cmpgui.active_tractography =        True
cmpgui.apply_fiberlength =          True
cmpgui.apply_splinefilter =         True

cmpgui.cff_cmatpickle =             True
cmpgui.cff_fiberarr =               True
cmpgui.cff_filteredfibers =         True
cmpgui.cff_finalfiberlabels =       True
cmpgui.cff_fullnetworkpickle =      True
cmpgui.cff_originalfibers =         True
cmpgui.cff_rawT1 =                  True
cmpgui.cff_rawT2 =                  True
cmpgui.cff_rawdiffusion =           True
cmpgui.cff_roisegmentation =        True
cmpgui.cff_scalars =                True
cmpgui.cff_surfacelabels =          True
cmpgui.cff_surfaces =               True
cmpgui.compute_curvature =          True

cmpgui.diffusion_imaging_model =    'DTI'
cmpgui.do_convert_T1 =              True
cmpgui.do_convert_T2 =              True
cmpgui.do_convert_diffusion =       True
cmpgui.dtb_dtk2dir_param =          u''
cmpgui.dti_recon_param =            u''
cmpgui.dtk_home =                   '/home/sgerhard/soft/dtk/'
cmpgui.dtk_matrices =               '/home/sgerhard/soft/dtk/matrices'

cmpgui.extract_diffusion_metadata = False
cmpgui.fiber_cutoff_lower =         20.0
cmpgui.fiber_cutoff_upper =         500.0
cmpgui.freesurfer_home =            '/home/sgerhard/soft/freesurfer50/'
cmpgui.fsl_home =                   '/usr/share/fsl/4.1'
cmpgui.fsloutputtype =              'NIFTI'
cmpgui.gradient_table =             'custom'
cmpgui.gradient_table_file =        u'/home/sgerhard/dev/cmp/cmp/data/diffusion/gradient_tables/siemens_64.txt'
cmpgui.hardi_recon_param =          '-b0 1 -p 3 -sn 1'



cmpgui.lin_reg_param =              '-usesqform -nosearch -dof 6 -cost mutualinfo'
cmpgui.max_b0_val =                 '1000'
cmpgui.modified =                   None
cmpgui.nlin_reg_bet_T2_param =      '-f 0.35 -g 0.15'
cmpgui.nlin_reg_bet_b0_param =      '-f 0.2 -g 0.2'
cmpgui.nlin_reg_fnirt_param =       '--subsamp=8,4,2,2 --mit... --applyrefmask=0,0,1,1'
cmpgui.nr_of_b0 =                   '1'

cmpgui.parcellation =               {'freesurferaparc' : 
{'node_information_graphml' : '/home/sgerhard/dev/packages/cmp/data/parcellation/nativefreesurfer/freesurferaparc/resolution83.graphml',
  'number_of_regions' : 84,
  'surface_parcellation' : None,
  'volume_parcellation' : None}}
cmpgui.parcellation_scheme =        'NativeFreesurfer'
cmpgui.pipeline_status_file =       'cmp.status'

cmpgui.created =                    None
cmpgui.creator =                    u'sg'
cmpgui.description =                ''
cmpgui.email =                      u'sg'
cmpgui.emailnotify =                []
cmpgui.license =                    ''
cmpgui.project_metadata =           {}
cmpgui.species =                    'Homo sapiens'
cmpgui.publisher =                  u'sg'

cmpgui.recon_all_param =            '-all -no-isrunning'
cmpgui.reference =                  ''
cmpgui.registration_mode =          'Linear'
cmpgui.skip_completed_stages =      False
cmpgui.streamline_param =           '--angle 60  --seeds 32'

cmp.connectome.mapit(cmpgui)

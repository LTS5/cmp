# Copyright (C) 2009-2011, Ecole Polytechnique Federale de Lausanne (EPFL) and
# Hospital Center and University of Lausanne (UNIL-CHUV), Switzerland
# All rights reserved.
#
#  This software is distributed under the open-source license Modified BSD.

""" Defines the graphical user interface to the Connectome Mapper
"""
import os.path
import traceback
#import threading

from enthought.traits.api import HasTraits, Int, Str, Directory, List,\
                 Bool, File, Button, Enum, Instance
    
from enthought.traits.ui.api import View, Item, HGroup, Handler, \
                    message, spring, Group, VGroup, TableEditor, UIInfo

    
from enthought.traits.ui.table_column \
    import ObjectColumn

import cmp    
from cmp.configuration import PipelineConfiguration
from cmp.util import KeyValue
from cmp.helpgui import HelpDialog

#class CMPThread( threading.Thread ):
#
#    def __init__(self, gconf): 
#        threading.Thread.__init__(self) 
#        self.gconf = gconf 
# 
#    def run(self): 
#        print "Starting CMP Thread..."
#        cmp.connectome.mapit(self.gconf)
#        print "Ended CMP Thread."
#        # release
        
table_editor = TableEditor(
    columns     = [ ObjectColumn( name = 'key',  width = 0.2 ),
                    ObjectColumn( name = 'value',   width = 0.6 ), ],
    editable    = True,
    deletable   = True,
    sortable    = True,
    sort_model  = True,
    auto_size   = False,
    row_factory = KeyValue
)

class CMPGUIHandler ( Handler ):
    
    def object_run_changed(self, info):
        object = info.object
        if info.initialized:
            # first do a consistency check
            object.consistency_check()
            # this should work for wx backend
            # https://mail.enthought.com/pipermail/enthought-dev/2010-March/025896.html
            
            #print "hide GUI-------------"
            # map the connectome
            try:
                #info.ui.control.Show(False)
                cmp.connectome.mapit(object)
            except Exception, e:
                # output traceback to error log and on the screen
                err = traceback.format_exc()
                object.get_logger().error("Exception occured: " + str(e))
                object.get_logger().error(err)
            finally:
                pass #info.ui.control.Show(True)
            

class CMPGUI( PipelineConfiguration ):
    """ The Graphical User Interface for the CMP
    """
    
    def __init__(self, **kwargs):
        # NOTE: In python 2.6, object.__init__ no longer accepts input
        # arguments.  HasTraits does not define an __init__ and
        # therefore these args were being ignored.
        super(CMPGUI, self).__init__(**kwargs)
        
    about = Button
    run = Button
    save = Button
    load = Button
    help = Button

    inspect_dicomconverter = Button
    inspect_registration = Button
    inspect_segmentation = Button
    inspect_whitemattermask = Button
    inspect_parcellation = Button
    inspect_reconstruction = Button
    inspect_tractography = Button
    inspect_tractography_filtered = Button
    inspect_fiberfilter = Button
    inspect_connectionmatrix = Button
  
    main_group = Group(
                    VGroup(
                    Item('project_dir', label='Project Directory:', tooltip = 'Please select the root folder of your project'),
                    #Item('generator', label='Generator', ),
                    Item('diffusion_imaging_model', label='Imaging Modality'),
                      label="Project Settings"
                    ),
                    HGroup(
                        VGroup(
                        Item('active_createfolder', label = 'Create Folder'),
                        Item('active_dicomconverter', label = 'DICOM Converter', tooltip = "converts DICOM to the Nifti format"),
                        Item('active_registration', label = 'Registration'),
                        Item('active_segmentation', label = 'Segmentation'),
                        Item('active_parcellation', label = 'Parcellation'),
                        Item('active_applyregistration', label = 'Apply registration'),
    		            Item('active_reconstruction', label = 'Reconstruction'),
                        Item('active_tractography', label = 'Tractography', tooltip = 'performs tractography'),
                        Item('active_fiberfilter', label = 'Fiber Filtering', tooltip = 'applies filtering operation to the fibers'),
                        Item('active_connectome', label = 'Connectome Creation', tooltip= 'creates the connectivity matrices'),
                        # Item('active_statistics', label = 'Statistics'),
                        Item('active_cffconverter', label = 'CFF Converter', tooltip='converts processed files to a connectome file'),
                        Item('skip_completed_stages', label = 'Skip Previously Completed Stages:'),
                        label="Stages"     
                        ),
                        VGroup(
                        #Item('inspect_rawT1', label = 'Inspect Raw T1', show_label = False),
                        Item('inspect_dicomconverter', label = 'Inspect raw data', show_label = False),
                        Item('inspect_registration', label = 'Registration', show_label = False),
                        Item('inspect_segmentation', label = 'Segmentation', show_label = False),
                        #Item('inspect_whitemattermask', label = 'White Matter Mask', show_label = False),
                        Item('inspect_parcellation', label = 'Parcellation', show_label = False),
                        #Item('inspect_reconstruction', label = 'Reconstruction', show_label = False), # DTB_viewer
                        Item('inspect_tractography', label = 'Tractography Original', show_label = False),
                        Item('inspect_tractography_filtered', label = 'Tractography Filtered', show_label = False),
                        Item('inspect_connectionmatrix', label = 'Connection Matrix', show_label = False),
                        label="Inspector")
                        #VGroup(
                        #label="Status",
                        #)
                    ),
                    label = "Main",
                    show_border = False
                    )

    metadata_group = Group(
                    VGroup(
                        Item('creator', label = "Creator"),
                        Item('email', label = "E-Mail"),
                        Item('publisher', label = "Publisher"),
                        Item('created', label = "Creation Date"),
                        Item('modified', label = "Modification Date"),
                        Item('license', label = "License"),
                        #Item('rights', label = "Rights"),
                        Item('reference', label = "References"),
                        #Item('relation', label = "Relations"),
                        Item('species', label = "Species"),
                        Item('description', label = "Project Description"),
                    ),
                    label = "Metadata",
                    show_border = False
                )

    subject_group = Group(
        VGroup(
            Item('subject_name',label="Name"),
            Item('subject_timepoint',label="Timepoint"),
            Item('subject_workingdir',label="Working Directory"),
            Item( 'subject_metadata',
                  label  = 'Metadata',
                  editor = table_editor ),
            show_border = True
        ),
        label = "Subject"
        )

    dicomconverter_group = Group(
        VGroup(
            Item('do_convert_diffusion', label="Convert Diffusion data?"),
            #Item('subject_raw_glob_diffusion',label="Diffusion File Pattern", enabled_when = 'do_convert_diffusion'),
            Item('do_convert_T1', label="Convert T1 data?"),
            #Item('subject_raw_glob_T1',label="T1 File Pattern", enabled_when = 'do_convert_T1'),
            Item('do_convert_T2', label="Convert T2 data?"),
            #Item('subject_raw_glob_T2',label="T2 File Pattern", enabled_when = 'do_convert_T2'),
            # Item('extract_diffusion_metadata', label="Try extracting Diffusion metadata"),
            show_border = True
        ),       
        visible_when = "active_dicomconverter",             
        label = "DICOM Converter"                        
        )

    registration_group = Group(
        VGroup(
               Item('registration_mode', label="Registration"),
               VGroup(
                      Item('lin_reg_param', label='FLIRT Parameters'),
                      enabled_when = 'registration_mode == "Linear"',
                      label = "Linear Registration"
                      ),
               VGroup(
                      Item('nlin_reg_bet_T2_param', label="BET T2 Parameters"),
                      Item('nlin_reg_bet_b0_param', label="BET b0 Parameters"),
                      Item('nlin_reg_fnirt_param', label="FNIRT Parameters"),
                      enabled_when = 'registration_mode == "Nonlinear"',
                      label = "Nonlinear Registration"
               ),
               show_border = True,
               enabled_when = "active_registration"
            ),
        visible_when = "active_registration",
        label = "Registration",                         
        )

    parcellation_group = Group(
        VGroup(
               Item('parcellation_scheme', label="Parcellation Scheme"),
#               VGroup(
#                      Item('custompar_nrroi', label="Number of ROI"),
#                      Item('custompar_nodeinfo', label="Node Information (GraphML)"),
#                      Item('custompar_volumeparcell', label="Volumetric parcellation"),
#                      enabled_when = 'parcellation_scheme == "custom"',
#                      label = "Custom Parcellation"
#               ),
#               show_border = True,
#               enabled_when = "active_registration"
            ),
        visible_when = "active_parcellation",
        label = "Parcellation",                         
        )
    
    reconstruction_group = Group(
        VGroup(
               Item('nr_of_gradient_directions', label="Number of Gradient Directions"),
               Item('nr_of_sampling_directions', label="Number of Sampling Directions"),
               Item('nr_of_b0', label="Number of b0 volumes"),
               Item('odf_recon_param', label="odf_recon Parameters"),
               Item('dtb_dtk2dir_param', label="DTB_dtk2dir Parameters"),
               show_border = True,
               visible_when = "diffusion_imaging_model == 'DSI'"   
            ),
        VGroup(
               Item('gradient_table', label="Gradient Table"),
               Item('gradient_table_file', label="Gradient Table File"),
               Item('nr_of_b0', label="Number of b0 volumes"),
               Item('max_b0_val', label="Maximum b value"),
               Item('dti_recon_param', label="dti_recon Parameters"),
               Item('dtb_dtk2dir_param', label="DTB_dtk2dir Parameters"),
               show_border = True,
               visible_when = "diffusion_imaging_model == 'DTI'"
            ),
        VGroup(
               Item('gradient_table', label="Gradient Table"),
               Item('gradient_table_file', label="Gradient Table File"),
               Item('nr_of_gradient_directions', label="Number of Gradient Directions"),
               Item('nr_of_sampling_directions', label="Number of Sampling Directions"),
               Item('nr_of_b0', label="Number of b0 volumes"),
               #Item('max_b0_val', label="Maximumb b value"),
               Item('hardi_recon_param', label="odf_recon Parameters"),
               Item('dtb_dtk2dir_param', label="DTB_dtk2dir Parameters"),
               show_border = True,
               visible_when = "diffusion_imaging_model == 'QBALL'"
            ),
        visible_when = "active_reconstruction",
        label = "Reconstruction",                         
        )

    segementation_group = Group(
        VGroup(
               Item('recon_all_param', label="recon_all Parameters"),
               show_border = True,
            ),
        enabled_when = "active_segmentation",
        visible_when = "active_segmentation",
        label = "Segmentation",

    )

    tractography_group = Group(
        VGroup(
               Item('streamline_param', label="DTB_streamline Parameters"),
               show_border = True,
               visible_when = "diffusion_imaging_model == 'DSI' or diffusion_imaging_model == 'QBALL'",
            ),
        VGroup(
               Item('streamline_param', label="DTB_streamline Parameters"),
               show_border = True,
               visible_when = "diffusion_imaging_model == 'DTI'"   
            ),
        enabled_when = "active_tractography",
        visible_when = "active_tractography",
        label = "Tractography",                         
        )
    
    fiberfilter_group = Group(
        VGroup(
               Item('apply_splinefilter', label="Apply spline filter"),
               Item('apply_fiberlength', label="Apply cutoff filter"),
               Item('fiber_cutoff_lower', label='Lower cutoff length (mm)', enabled_when = 'apply_fiberlength'),
               Item('fiber_cutoff_upper', label='Upper cutoff length (mm)', enabled_when = 'apply_fiberlength'),
               show_border = True,
               enabled_when = "active_fiberfilter"   
            ),
        visible_when = "active_fiberfilter",
        label = "Fiber Filtering",                         
        )

    applyregistration_group = Group(
        VGroup(
               Item('parcellation_scheme', label="Used Parcellation Scheme"),
               show_border = True,
               enabled_when = "active_applyregistration"
            ),
        visible_when = "active_applyregistration",
        label = "Apply Registration",
        )

    connectioncreation_group = Group(
        VGroup(
               Item('compute_curvature', label="Compute curvature"),
               Item('parcellation_scheme', label="Used Parcellation Scheme"),
               show_border = True,
               enabled_when = "active_connectome"
            ),
        visible_when = "active_connectome",
        label = "Connectome Creation",
        )

    cffconverter_group = Group(
        VGroup(
               Item('cff_fullnetworkpickle', label="All connectomes"),
              # Item('cff_cmatpickle', label='cmat.pickle'),
               Item('cff_originalfibers', label="Original Tractography"),
               Item('cff_filteredfibers', label="Filtered Tractography"),
               Item('cff_fiberarr', label="Filtered fiber arrays"),
               Item('cff_finalfiberlabels', label="Final Tractography and Labels"),
               Item('cff_scalars', label="Scalar maps"),
               Item('cff_rawdiffusion', label="Raw Diffusion Data"),
               Item('cff_rawT1', label="Raw T1 data"),
               Item('cff_rawT2', label="Raw T2 data"),
               Item('cff_roisegmentation', label="Parcellation Volumes"),
               Item('cff_surfaces', label="Surfaces", tooltip = 'stores individually generated surfaces'),
               #Item('cff_surfacelabels', label="Surface labels", tooltip = 'stores the labels on the surfaces'),
               show_border = True,
            ),
        visible_when = "active_cffconverter",
        label = "CFF Converter",                         
        )                    

    configuration_group = Group(
        VGroup(
               Item('emailnotify', label='E-Mail Notification'),
               #Item('wm_handling', label='White Matter Mask Handling', tooltip = """1: run through the freesurfer step without stopping
#2: prepare whitematter mask for correction (store it in subject dir/NIFTI
#3: rerun freesurfer part with corrected white matter mask"""),
               Item('freesurfer_home',label="Freesurfer Home"),
               Item('fsl_home',label="FSL Home"),
               Item('dtk_home',label="DTK Home"),
               show_border = True,
            ),
        label = "Configuration",                         
        )
        
    view = View(
        Group(
            HGroup(
              main_group,
              metadata_group,
              subject_group,
              dicomconverter_group,
              registration_group,
              segementation_group,
              parcellation_group,
              applyregistration_group,
              reconstruction_group,
              tractography_group,
              fiberfilter_group,
              connectioncreation_group,
              cffconverter_group,
              configuration_group,
              orientation= 'horizontal',
              layout='tabbed',
              springy=True
            ),
            spring,
            HGroup( 
                Item( 'about', label = 'About', show_label = False),
                Item( 'help', label = 'Help', show_label = False),
                Item( 'save', label = 'Save State', show_label = False),
                Item( 'load', label = 'Load State', show_label = False),
                spring,
                Item( 'run', label = 'Map Connectome!', show_label = False),
            ),
        ),
        resizable = True,
        width=0.3,
        handler = CMPGUIHandler,
        title     = 'Connectome Mapper',
    )
    
    def _about_fired(self):
        a=HelpDialog()
        a.configure_traits(kind='livemodal')
        
    def _help_fired(self):
        a=HelpDialog()
        a.configure_traits(kind='livemodal')
    
    def load_state(self, cmpconfigfile):
        """ Load CMP Configuration state directly.
        Useful if you do not want to invoke the GUI"""
        import enthought.sweet_pickle as sp        
        output = open(cmpconfigfile, 'rb')
        data = sp.load(output)
        self.__setstate__(data.__getstate__())
        # make sure that dtk_matrices is set
        self.dtk_matrices = os.path.join(self.dtk_home, 'matrices')
        # update the subject directory
        if os.path.exists(self.project_dir):
            self.subject_workingdir = os.path.join(self.project_dir, self.subject_name, self.subject_timepoint)
        output.close()

    def save_state(self, cmpconfigfile):
        """ Save CMP Configuration state directly.
        Useful if you do not want to invoke the GUI
        
        Parameters
        ----------
        cmpconfigfile : string
            Absolute path and filename to store the CMP configuration
            pickled object
        
        """
        # check if path available
        if not os.path.exists(os.path.dirname(cmpconfigfile)):
            os.makedirs(os.path.abspath(os.path.dirname(cmpconfigfile)))
            
        import enthought.sweet_pickle as sp
        output = open(cmpconfigfile, 'wb')
        # Pickle the list using the highest protocol available.
        # copy object first
        tmpconf = CMPGUI()
        tmpconf.copy_traits(self)
        sp.dump(tmpconf, output, -1)
        output.close()
        
    def show(self):
        """ Show the GUI """
        #self.configure_traits()
        self.edit_traits(kind='livemodal')
                    
#    def _gradient_table_file_default(self):
#    	return self.get_gradient_table_file()

    # XXX this is not automatically invoked!       
    def _get_gradient_table_file(self):

        if self.gradient_table == 'custom':
            gradfile = self.get_custom_gradient_table()
        else:
            gradfile = self.get_cmp_gradient_table(self.gradient_table)

        if not os.path.exists(gradfile):
            msg = 'Selected gradient table %s does not exist!' % gradfile
            raise Exception(msg)

        return gradfile

    def _subject_timepoint_changed(self, value):
        if self.subject_name != '':
            self.subject_workingdir = os.path.join(self.project_dir, self.subject_name, value)
        self.subject_timepoint = value

    def _subject_workingdir_changed(self, value):
        if self.subject_name == '' and self.subject_timepoint == '':
            # fill in the subject name and timepoint
            splitpath = os.path.split(value)

            tp =  splitpath[1]
            name = os.path.split(splitpath[0])[1]

            self.subject_name = name
            self.subject_timepoint = tp
            
        self.subject_workingdir = value

    def _gradient_table_changed(self, value):
        if value == 'custom':
            self.gradient_table_file = self.get_custom_gradient_table()
        else:
            self.gradient_table_file = self.get_cmp_gradient_table(value)
            
        if not os.path.exists(self.gradient_table_file):
            msg = 'Selected gradient table %s does not exist!' % self.gradient_table_file
            raise Exception(msg)
    
    def _parcellation_scheme_changed(self, value):
        if value == "Lausanne2008":
            self.parcellation = self._get_lausanne_parcellation(parcel = "Lausanne2008")
        else:
            self.parcellation = self._get_lausanne_parcellation(parcel = "NativeFreesurfer")

    def _inspect_dicomconverter_fired(self):
        cmp.dicomconverter.inspect(self)

    def _inspect_registration_fired(self):
        cmp.registration.inspect(self)

    def _inspect_tractography_fired(self):
        cmp.tractography.inspect(self)
        
    def _inspect_tractography_filtered_fired(self):
        cmp.fiberfilter.inspect(self)
        
    def _inspect_segmentation_fired(self):
        cmp.freesurfer.inspect(self)

    def _inspect_parcellation_fired(self):
        cmp.maskcreation.inspect(self)

    def _inspect_connectionmatrix_fired(self):
        cmp.connectionmatrix.inspect(self)

    def _run_fired(self):
        pass
        # execute the pipeline thread
        
        # first do a consistency check
        #self.consistency_check()
        
        # otherwise store the pickle
        #self.save_state(os.path.join(self.get_log(), self.get_logname(suffix = '.pkl')) )
        
        # hide the gui
        # run the pipeline
        #print "mapit"
        #cmp.connectome.mapit(self)
        # show the gui
        
        #cmpthread = CMPThread(self)
        #cmpthread.start()

    def _load_fired(self):
        import enthought.sweet_pickle as sp
        from enthought.pyface.api import FileDialog, OK
        
        wildcard = "CMP Configuration State (*.pkl)|*.pkl|" \
                        "All files (*.*)|*.*"
        dlg = FileDialog(wildcard=wildcard,title="Select a configuration state to load",\
                         resizeable=False, \
                         default_directory=self.project_dir,)
        
        if dlg.open() == OK:            
            if not os.path.isfile(dlg.path):
                return
            else:
                self.load_state(dlg.path)

    def _save_fired(self):
        import pickle
        import enthought.sweet_pickle as sp
        import os.path
        from enthought.pyface.api import FileDialog, OK
        
        wildcard = "CMP Configuration State (*.pkl)|*.pkl|" \
                        "All files (*.*)|*.*"
        dlg = FileDialog(wildcard=wildcard,title="Filename to store configuration state",\
                         resizeable=False, action = 'save as', \
                         default_directory=self.subject_workingdir,)
        
        if dlg.open() == OK:
            if not dlg.path.endswith('.pkl'):
                dlg.path = dlg.path + '.pkl'
            self.save_state(dlg.path)

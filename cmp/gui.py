""" Defines the graphical user interface to the Connectome Mapping Pipeline
"""
import os.path    
#import threading

from enthought.traits.api import HasTraits, Int, Str, Directory, List,\
                 Bool, File, Button, Enum
    
from enthought.traits.ui.api import View, Item, HGroup, Handler, \
                    message, spring, Group, VGroup, TableEditor

from enthought.traits.ui.table_column \
    import ObjectColumn

import cmp    
from cmp.configuration import PipelineConfiguration
from cmp.util import KeyValue

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

    inspect_registration = Button
    inspect_segmentation = Button
    inspect_whitemattermask = Button
    inspect_parcellation = Button
    inspect_reconstruction = Button
    inspect_tractography = Button
    inspect_tractography_filtered = Button
    inspect_fiberfilter = Button
    inspect_connectomefile = Button
  
    main_group = Group(
                    VGroup(
                    Item('project_name', label='Project Name:', tooltip = 'Please enter a name for your project'),
                    Item('project_dir', label='Project Directory:'),
                    Item('generator', label='Generator', ),
                      label="Project Settings"
                    ),
                    VGroup(
                    Item('diffusion_imaging_model', label='Imaging Model'),
                    Item('diffusion_imaging_stream', label='Imaging Stream'),
                    show_border = False,
                      label="Imaging Stream"
                    ),
                    HGroup(
                        VGroup(
                        Item('active_dicomconverter', label = 'DICOM Converter', tooltip = "converts DICOM to the Nifti format"),
                        Item('active_registration', label = 'Registration'),
                        Item('active_segmentation', label = 'Segmentation'),
                        Item('active_parcellation', label = 'Parcellation'),
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
                        Item('inspect_registration', label = 'Registration', show_label = False),
                        Item('inspect_segmentation', label = 'Segmentation', show_label = False),
                        #Item('inspect_whitemattermask', label = 'White Matter Mask', show_label = False),
                        #Item('inspect_parcellation', label = 'Parcellation', show_label = False),
                        #Item('inspect_reconstruction', label = 'Reconstruction', show_label = False),
                        Item('inspect_tractography', label = 'Tractography Orig', show_label = False),
                        Item('inspect_tractography_filtered', label = 'Tractography Filtered', show_label = False),
                        Item('inspect_fiberfilter', label = 'Filtered Fibers', show_label = False),
                        #Item('inspect_connectomefile', label = 'Connectome File', show_label = False),
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
                        Item('author', label = "Author"),
                        Item('institution', label = "Institution"),
                        Item('creationdate', label = "Creation Date"),
                        Item('modificationdate', label = "Modification Date"),
                        Item('species', label = "Species"),
                        Item('legalnotice', label = "Legal Notice"),
                        Item('reference', label = "Reference"),
                        Item('url', label = "URL"),
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
            Item('subject_raw_glob_diffusion',label="Diffusion File Pattern"),
            Item('subject_raw_glob_T1',label="T1 File Pattern"),
            Item('subject_raw_glob_T2',label="T2 File Pattern"),
            Item( 'subject_metadata',
                  label  = 'Metadata',
                  editor = table_editor ),
            show_border = True
        ),
        label = "Subject"
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
               VGroup(
                      Item('custompar_nrroi', label="Number of ROI"),
                      Item('custompar_nodeinfo', label="Node Information (GraphML)"),
                      Item('custompar_volumeparcell', label="Volumetric parcellation"),
                      enabled_when = 'parcellation_scheme == "custom"',
                      label = "Custom Parcellation"
               ),
               show_border = True,
               enabled_when = "active_registration"
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
               show_border = True,
               visible_when = "diffusion_imaging_model == 'DSI'"   
            ),
        VGroup(
               Item('gradient_table', label="Gradient Table"),
               Item('gradient_table_file', label="Gradient Table File"),
               Item('nr_of_b0', label="Number of b0 volumes"),
               Item('max_b0_val', label="Maximumb b value"),
               Item('dti_recon_param', label="dti_recon Parameters"),
               show_border = True,
               visible_when = "diffusion_imaging_model == 'DTI'"
            ),
        visible_when = "active_reconstruction",
        label = "Reconstruction",                         
        )
    
    tractography_group = Group(
        VGroup(
               Item('streamline_param', label="DTB_streamline Parameters"),
               show_border = True,
               visible_when = "diffusion_imaging_model == 'DSI'",   
            ),
        VGroup(
               Item('streamline_param_dti', label="dti_tracker Parameters"),
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
               Item('fiber_cutoff', label='Cutoff length (mm)', enabled_when = 'apply_fiberlength'),
               show_border = True,
               enabled_when = "active_fiberfilter"   
            ),
        visible_when = "active_fiberfilter",
        label = "Fiber Filtering",                         
        )

    cffconverter_group = Group(
        VGroup(
               Item('cff_fullnetworkpickle', label="All connectomes"),
               Item('cff_cmatpickle', label='cmat.pickle'),
               Item('cff_filteredfibers', label="Tractography"),
               Item('cff_roisegmentation', label="Parcellation Volumes"),
               Item('cff_rawdiffusion', label="Raw Diffusion Data"),
               Item('cff_rawT1', label="Raw T1 data"),
               Item('cff_rawT2', label="Raw T2 data"),
               Item('cff_surfaces', label="Individual surfaces", tooltip = 'stores individually generated surfaces'),
               show_border = True,
            ),
        visible_when = "active_cffconverter",
        label = "CFF Converter",                         
        )                    

    configuration_group = Group(
        VGroup(
               Item('emailnotify', label='E-Mail Notification'),
               Item('wm_handling', label='White Matter Mask Handling', tooltip = """1: run through the freesurfer step without stopping
2: prepare whitematter mask for correction (store it in subject dir/NIFTI
3: rerun freesurfer part with corrected white matter mask"""),
               Item('freesurfer_home',label="Freesurfer Home"),
               Item('fsl_home',label="FSL Home"),
               Item('dtk_home',label="DTK Home"),
               Item('dtk_matrices',label="DTK Matrices"),
               show_border = True,
            ),
        label = "Configuration",                         
        )
        
    view = View(
        HGroup(
            VGroup(
                HGroup(
                  main_group,
                  metadata_group,
                  subject_group,
                  registration_group,
                  parcellation_group,
                  reconstruction_group,
                  tractography_group,
                  fiberfilter_group,
                  cffconverter_group,
                  configuration_group,
                  orientation= 'horizontal',
                  layout='tabbed',
                  #springy=True
                ),
                spring,
                HGroup( 
                    #Item( 'validate_form', label = 'Validate Form', show_label = False),
                    Item( 'about', label = 'About', show_label = False),
                    Item( 'save', label = 'Save State', show_label = False),
                    Item( 'load', label = 'Load State', show_label = False),
                    spring,
                    Item( 'run', label = 'Map Connectome!', show_label = False),
                ),
            ),
            VGroup(
                   Item('stagedescription', style = 'readonly', show_label = False)
                   )
        ),
        resizable = True,
        title     = 'Connectome Mapping Pipeline',
    )
    
    def _about_fired(self):
        msg = """Connectome Mapping Pipeline
Version 1.0

Copyright (C) 2010, Ecole Polytechnique Federale de Lausanne (EPFL) and
Hospital Center and University of Lausanne (UNIL-CHUV), Switzerland
                
Contact
-------
info@connectomics.org
http://www.connectomics.org/

Contributors
------------
* Jean-Philippe Thiran
* Reto Meuli
* Stephan Gerhard
* Alessandro Daducci
* Leila Cammoun
* Patric Hagmann
* Alia Lemkaddem
* Elda Fischi
* Christophe Chenes
* Xavier Gigandet

External Contributors
---------------------

Children's Hospital Boston:
* Ellen Grant
* Daniel Ginsburg
* Rudolph Pienaar

"""
        print msg
    
    def load_state(self, cmpconfigfile):
        """ Load CMP Configuration state directly.
        Useful if you do not want to invoke the GUI"""
        import enthought.sweet_pickle as sp        
        output = open(cmpconfigfile, 'rb')
        data = sp.load(output)
        self.__setstate__(data.__getstate__())
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
        self.configure_traits()
                    
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
	
    def _gradient_table_changed(self, value):
        if value == 'custom':
            self.gradient_table_file = self.get_custom_gradient_table()
        else:
            self.gradient_table_file = self.get_cmp_gradient_table(value)
            
        if not os.path.exists(self.gradient_table_file):
            msg = 'Selected gradient table %s does not exist!' % self.gradient_table_file
            raise Exception(msg)
    
    def _inspect_registration_fired(self):
        cmp.registration.inspect(self)

    def _inspect_tractography_fired(self):
        cmp.tractography.inspect(self)
        
    def _inspect_tractography_filtered_fired(self):
        cmp.tractography.inspect(self, filtered = True)
        
    def _inspect_fiberfilter_fired(self):
        cmp.fiberfilter.inspect(self)

    def _inspect_segmentation_fired(self):
        cmp.freesurfer.inspect(self)

    def _active_dicomconverter_changed(self, value):
        self.stagedescription = """DICOM Converter\n==========\n\n
What is this module about?"""
        
    def _active_registration_changed(self, value):
        self.stagedescription = "Registration\n"

    def _active_segmentation_changed(self, value):
        self.stagedescription = "Segmentation\n============"

    def _active_parcellation_changed(self, value):
        self.stagedescription = "Parcellation\n============"

    def _active_reconstruction_changed(self, value):
        self.stagedescription = "Reconstruction\n============"

    def _active_tractography_changed(self, value):
        self.stagedescription = "Tractography\n============"

    def _active_fiberfilter_changed(self, value):
        self.stagedescription = "Fiber Filtering\n============"

    def _active_connectome_changed(self, value):
        self.stagedescription = "Connectome Creation\n============"
        
    def _active_cffconverter_changed(self, value):
        self.stagedescription = "CFF Converter\n============"
        
    def _skip_completed_stages_changed(self, value):
        self.stagedescription = "Skip completed stages\n============"

    def _run_fired(self):
        # execute the pipeline thread
        # store the pickle
        self.save_state(os.path.join(self.get_log(), self.get_logname(suffix = '.pkl')) )
        cmp.connectome.mapit(self)
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
                         resizeable=False, \
                         default_directory=self.subject_workingdir,)
        
        if dlg.open() == OK:
            self.save_state(dlg.path)

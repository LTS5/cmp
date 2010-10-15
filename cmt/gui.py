""" Defines the graphical user interface to the Connectome Mapping Toolkit
"""

from enthought.traits.api import HasTraits, Int, Str, Directory, List,\
                 Bool, File, Button, Enum
    
from enthought.traits.ui.api import View, Item, HGroup, Handler, \
                    message, spring, Group, VGroup
                    
import threading
from cmt.configuration import PipelineConfiguration
import cmt.connectome

class CMTThread( threading.Thread ):

    def __init__(self, gconf): 
        threading.Thread.__init__(self) 
        self.gconf = gconf 
 
    def run(self): 
        print "Starting CMT Thread..."
        cmt.connectome.mapit(self.gconf)
        print "Ended CMT Thread."
        

class CMTGUI( PipelineConfiguration ):
    """ The Graphical User Interface for the CMT
    """
    
    def __init__(self, **kwargs):
        # NOTE: In python 2.6, object.__init__ no longer accepts input
        # arguments.  HasTraits does not define an __init__ and
        # therefore these args were being ignored.
        super(CMTGUI, self).__init__(**kwargs)
        
    about = Button
    run = Button
    save = Button
    load = Button

    main_group = Group(
                    VGroup(
                    Item('project_name', label='Project Name:', tooltip = 'Please enter a name for your project'),
                    Item('project_dir', label='Project Directory:'),
                    Item('generator', label='Generator', ),
                      label="Project Settings"
                    ),
                    VGroup(
                    Item('active_dicomconverter', label = 'DICOM Converter'),
                    Item('active_registration', label = 'Registration'),
                    Item('active_segmentation', label = 'Segmentation'),
                    Item('active_maskcreation', label = 'Mask Creation'),
		    Item('active_reconstruction', label = 'Reconstruction'),
                    Item('active_tractography', label = 'Tractography'),
                    Item('active_fiberfilter', label = 'Fiberfiltering'),
                    Item('active_connectome', label = 'Connectome Creation'),
                    Item('active_cffconverter', label = 'CFF Converter'),
                    label="Execute"     
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
            Item('subject_description',label="Description"),
            Item('subject_raw_glob_diffusion',label="Diffusion File Pattern"),
            Item('subject_raw_glob_T1',label="T1 File Pattern"),
            Item('subject_raw_glob_T2',label="T2 File Pattern",
                 enabled_when = "registration_mode == 'N'"),
            show_border = True
        ),
        label = "Subject"
        )

    registration_group = Group(
        VGroup(
               Item('registration_mode', label="Registration"),
               VGroup(
                      Item('lin_reg_param', label='FLIRT Parameters'),
                      enabled_when = 'registration_mode == "L"',
                      label = "Linear Registration"
                      ),
               VGroup(
                      Item('nlin_reg_bet_T2_param', label="BET T2 Parameters"),
                      Item('nlin_reg_bet_b0_param', label="BET b0 Parameters"),
                      Item('nlin_reg_fnirt_param', label="FNIRT Parameters"),
                      enabled_when = 'registration_mode == "N"',
                      label = "Nonlinear Registration"
               ),
               show_border = True,
               enabled_when = "active_registration"
            ),
        visible_when = "active_registration",
        label = "Registration",                         
        )
            
    reconstruction_group = Group(
        VGroup(
               Item('diffusion_imaging_model'),
               Item('diffusion_imaging_stream'),
               show_border = False,               
               ),
        VGroup(
               Item('nr_of_gradient_directions'),
               Item('nr_of_sampling_directions'),
               Item('odf_recon_param'),
               show_border = True,
               enabled_when = "active_reconstruction"   
            ),
        VGroup(
               # XXX: Item('b0_value'),
               show_border = True,
               enabled_when = "diffusion_imaging_model == 'DTI'"
            ),
        visible_when = "active_reconstruction",
        label = "Reconstruction",                         
        )
    
    tractography_group = Group(
        VGroup(
               Item('streamline_param'),
               show_border = True,
               enabled_when = "active_tractography"   
            ),
        visible_when = "active_tractography",
        label = "Tractography",                         
        )
    
    configuration_group = Group(
        VGroup(
               Item('emailnotify', label='E-Mail Notification'),
               Item('wm_handling', label='White Matter Mask Handling', tooltip = """1: run through the freesurfer step without stopping
2: prepare whitematter mask for correction (store it in subject dir/NIFTI
3: rerun freesurfer part with corrected white matter mask"""),
               Item('inspect_registration',label="Inspect Registration", tooltip = 'Stop execution and inspect the results of the registration with FSLView'),
               Item('freesurfer_home',label="Freesurfer Home"),
               Item('fsl_home',label="FSL Home"),
               Item('dtk_home',label="DTK Home"),
               Item('dtk_matrices',label="DTK Matrices"),
               show_border = True,
            ),
        label = "Configuration",                         
        )
        
    view = View(
        VGroup(
            HGroup(
              main_group,
              metadata_group,
              subject_group,
              registration_group,
              reconstruction_group,
              tractography_group,
              configuration_group,
              orientation= 'horizontal',
              layout='tabbed'
            ),
            spring,
            HGroup( 
                #Item( 'validate_form', label = 'Validate Form', show_label = False),
                Item( 'about', label = 'About', show_label = False),
                Item( 'save', label = 'Save', show_label = False),
                Item( 'load', label = 'Load', show_label = False),
                spring,
                Item( 'run', label = 'Run!', show_label = False),
            ),
        ),
        resizable = True,
        title     = 'Connectome Mapping Toolkit',
    )
    
    def _about_fired(self):
        msg = """Connectome Mapping Toolkit
Version 1.0

Copyright (C) 2010, Ecole Polytechnique Federale de Lausanne (EPFL) and
Hospital Center and University of Lausanne (UNIL-CHUV), Switzerland
                
Contributors
------------
Development:
* Stephan Gerhard
* Christophe Chenes

Image Processing:
* Alessandro Daducci
* Alia Lemkaddem
* Patric Hagmann
        
Testing:
* Elda Fischi
"""
        print msg
    
    def load_state(self, cmtconfigfile):
        """ Load CMT Configuration state directly.
        Useful if you do not want to invoke the GUI"""
        import enthought.sweet_pickle as sp        
        output = open(cmtconfigfile, 'rb')
        data = sp.load(output)
        self.__setstate__(data.__getstate__())
        output.close()

    def save_state(self, cmtconfigfile):
        """ Save CMT Configuration state directly.
        Useful if you do not want to invoke the GUI"""
        import pickle
        import enthought.sweet_pickle as sp
        output = open(cmtconfigfile, 'wb')
        # Pickle the list using the highest protocol available.
        sp.dump(self, output, -1)
        output.close()
                            
    def _run_fired(self):
        # execute the pipeline thread
        cmtthread = CMTThread(self)
        cmtthread.start()

    def _load_fired(self):
        import enthought.sweet_pickle as sp
        from enthought.pyface.api import FileDialog, OK
        
        wildcard = "CMT Configuration State (*.pkl)|*.pkl|" \
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
        print "blubb"
        import pickle
        import enthought.sweet_pickle as sp
        import os.path
        from enthought.pyface.api import FileDialog, OK
        
        wildcard = "CMT Configuration State (*.pkl)|*.pkl|" \
                        "All files (*.*)|*.*"
        dlg = FileDialog(wildcard=wildcard,title="Filename to store configuration state",\
                         resizeable=False, \
                         default_directory=self.subject_workingdir,)
        
        if dlg.open() == OK:
            self.save_state(dlg.path)

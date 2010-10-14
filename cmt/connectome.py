# Connectome Mapping Execution Engine

import cmt

def mapit2(cobj):
    
    # XXX check if we need to run the preprocessing step
    cmt.preprocessing.run( cobj )

    if cobj.active_dicomconverter:
        cmt.dicomconverter.run( cobj, subjid )
        
    if cobj.active_registration:
        cmt.registration.run( cobj, subjid )
        
    if cobj.active_segmentation:
        cmt.freesurfer.run( cobj, subjid )
        
    if cobj.active_maskcreation:
        cmt.maskcreation.run( cobj, subjid )
        cmt.apply_registration.run( cobj, subjid )
        
    if cobj.active_reconstruction:
        cmt.dtk.run( cobj, subjid )
        
    if cobj.active_tractography:
        cmt.tractography.run( cobj, subjid )
        
    if cobj.active_fiberfilter:
        cmt.fiberfilter.run( cobj, subjid )

    if cobj.active_connectome:
        cmt.connectionmatrix.run( cobj, subjid )
        
    if cobj.active_cffconverter:
        cmt.cffconverter.run( cobj )
   
            
    

def mapit(cobj):
    """ Maps the connectome """
    
    # loop over subjects
    for subjid, subjval in cobj.subject_list.items():
    
        if cobj.preprocessing:
            cmt.preprocessing.run( cobj, subjid )

        if cobj.dicomconverter:
            cmt.dicomconverter.run( cobj, subjid )
            
        if cobj.registration:
            cmt.registration.run( cobj, subjid )
            
        if cobj.freesurfer:
            cmt.freesurfer.run( cobj, subjid )
            
        if cobj.maskcreation:
            cmt.maskcreation.run( cobj, subjid )
            
        if cobj.dtk:
            cmt.dtk.run( cobj, subjid )
            
        if cobj.apply_registration:
            cmt.apply_registration.run( cobj, subjid )
            
        if cobj.tractography:
            cmt.tractography.run( cobj, subjid )

        if cobj.fiberfilter:
            cmt.fiberfilter.run( cobj, subjid )
                        
        if cobj.connectionmatrix:
            cmt.connectionmatrix.run( cobj, subjid )
            
        if cobj.cffconverter:
            cmt.cffconverter.run( cobj )
            

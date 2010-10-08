# Connectome Mapping Execution Engine

import cmt

def mapit(cobj):
    """ Maps the connectome """
    
    # loop over subjects
    for subjid, subjval in cobj.subject_list.items():
    
        if cobj.preprocessing:
            cmt.preprocesing( cobj, subjid )

        if cobj.dicomconverter:
            cmt.dicomconverter( cobj, subjid )
            
        if cobj.registration:
            cmt.registration( cobj, subjid )
            
        if cobj.freesurfer:
            cmt.freesurfer( cobj, subjid )
            
        if cobj.maskcreation:
            cmt.maskcreation( cobj, subjid )
            
        if cobj.diffusion:
            cmt.diffusion( cobj, subjid )
            
        if cobj.apply_registration:
            cmt.apply_registration( cobj, subjid )
            
        if cobj.tractography:
            cmt.tractography( cobj, subjid )

        if cobj.fiberfiltering:
            cmt.fiberfiltering( cobj, subjid )
                        
        if cobj.connectionmatrix:
            cmt.connectionmatrix( cobj, subjid )
            
        if cobj.cffconverter:
            cmt.cffconverter( cobj )
            
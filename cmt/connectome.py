# Connectome Mapping Execution Engine

import cmt

def mapit(cobj):
    
    cobj.consistency_check()
    cmt.preprocessing.run( cobj )

    if cobj.active_dicomconverter:
        cmt.dicomconverter.run( cobj )
        
    if cobj.active_registration:
        cmt.registration.run( cobj )
        
    if cobj.active_segmentation:
        cmt.freesurfer.run( cobj )
        
    if cobj.active_maskcreation:
        cmt.maskcreation.run( cobj )
        cmt.apply_registration.run( cobj )
        
    if cobj.active_reconstruction:
        cmt.dtk.run( cobj )
        
    if cobj.active_tractography:
        cmt.tractography.run( cobj )
        
    if cobj.active_fiberfilter:
        cmt.fiberfilter.run( cobj )

    if cobj.active_connectome:
        cmt.connectionmatrix.run( cobj )
        
    if cobj.active_cffconverter:
        cmt.cffconverter.run( cobj )
   

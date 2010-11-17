# Connectome Mapping Execution Engine

import cmt

def mapit(cobj):
    
    cobj.consistency_check()
    cobj.init_pipeline_status()
    
    # Add all of the stages to the pipeline status file
    # This needs to be done before starting processing so
    # that the stages in the pipeline are laid out before
    # processing begins
    stages = [ cmt.dicomconverter,
               cmt.registration,
               cmt.freesurfer,
               cmt.maskcreation,
               cmt.apply_registration,
               cmt.dtk,
               cmt.tractography,
               cmt.fiberfilter,
               cmt.fiberstatistics,
               cmt.connectionmatrix,
               cmt.fiberstatistics,
               cmt.cffconverter ]               
    for stage in stages:
        cobj.pipeline_status.AddStage( stage.__name__ )
        if hasattr(stage,'declare_inputs'):
            stage.declare_inputs(cobj)
        if hasattr(stage,'declare_outputs'):            
            stage.declare_outputs(cobj)
        
    
    # Save pipeline to disk    
    cobj.update_pipeline_status()
               
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

    if cobj.active_statistics:
        cmt.fiberstatistics.run( cobj )
        
    if cobj.active_cffconverter:
        cmt.cffconverter.run( cobj )
   
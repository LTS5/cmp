# Connectome Mapping Execution Engine

import cmt
from logme import *

def mapit(cobj):
    
    cobj.consistency_check()

    cobj.init_pipeline_status()
    
    # Add all of the stages to the pipeline status file
    # This needs to be done before starting processing so
    # that the stages in the pipeline are laid out before
    # processing begins
    stages = [ (cmt.dicomconverter, cobj.active_dicomconverter),
               (cmt.registration, cobj.active_registration),
               (cmt.freesurfer, cobj.active_segmentation),        
               (cmt.maskcreation, cobj.active_maskcreation),
               (cmt.apply_registration, cobj.active_maskcreation),
               (cmt.dtk, cobj.active_reconstruction),
               (cmt.tractography, cobj.active_tractography),
               (cmt.fiberfilter, cobj.active_fiberfilter),
               (cmt.connectionmatrix, cobj.active_connectome),
              # (cmt.fiberstatistics, cobj.active_statistics),               
               (cmt.cffconverter, cobj.active_cffconverter) ]
    
    for stage,stageEnabled in stages:
        cobj.pipeline_status.AddStage( stage.__name__ )
        if hasattr(stage,'declare_inputs'):
            stage.declare_inputs(cobj)
        if hasattr(stage,'declare_outputs'):            
            stage.declare_outputs(cobj)      
    
    # Save pipeline to disk    
    cobj.update_pipeline_status()
               
    cmt.preprocessing.run( cobj )
    
    # Set the logger function for the PipelineStatus object
    cobj.pipeline_status.SetLoggerFunctions(cobj.get_logger().error, cobj.get_logger().info)
    
    # Execute the pipeline
    for stage, stageEnabled in stages:
        if stageEnabled == True:        
            curStageObj = cobj.pipeline_status.GetStage( stage.__name__ )
                        
            # Check if the inputs exist            
            if curStageObj != None:            
                if cobj.pipeline_status.CanRun( curStageObj ) == False:
                    msg = "Required input file missing for stage: '%s'" % (stage.__name__)
                    cobj.get_logger().error( msg )
                    raise Exception( msg )
                # If stage was already completed and user asked to skip completed stages, skip
                # this stage.
                elif (cobj.skip_completed_stages == True and
                      cobj.pipeline_status.RanOK( curStageObj ) == True):
                    cobj.get_logger().info( "Skipping previously completed stage: '%s'" % ( stage.__name__) )
                    continue
                        
            # Run the stage            
            if hasattr(stage, 'run'):                
                stage.run( cobj )
                
            # Check if the stage ran properly
            if curStageObj != None:
                if cobj.pipeline_status.RanOK( curStageObj ) == False:
                    msg = "Required output file not generated for stage: '%s'" % (stage.__name__)
                    cobj.get_logger().error( msg )
                    raise Exception( msg )
                
                

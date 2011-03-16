# Copyright (C) 2009-2011, Ecole Polytechnique Fédérale de Lausanne (EPFL) and
# Hospital Center and University of Lausanne (UNIL-CHUV), Switzerland
# All rights reserved.
#
#  This software is distributed under the open-source license Modified BSD.

# Connectome Mapping Execution Engine

import cmp
from logme import *

def setup_pipeline_status(cobj):
    cobj.init_pipeline_status()
    
    # Add all of the stages to the pipeline status file
    # This needs to be done before starting processing so
    # that the stages in the pipeline are laid out before
    # processing begins
    stages = [ (cmp.dicomconverter, cobj.active_dicomconverter),
               (cmp.registration, cobj.active_registration),
               (cmp.freesurfer, cobj.active_segmentation),        
               (cmp.maskcreation, cobj.active_parcellation),
               (cmp.apply_registration, cobj.active_parcellation),
               (cmp.dtk, cobj.active_reconstruction),
               (cmp.tractography, cobj.active_tractography),
               (cmp.fiberfilter, cobj.active_fiberfilter),
               (cmp.connectionmatrix, cobj.active_connectome),
              # (cmp.fiberstatistics, cobj.active_statistics),               
               (cmp.cffconverter, cobj.active_cffconverter) ]
    
    for stage,stageEnabled in stages:
        cobj.pipeline_status.AddStage( stage.__name__, True )
        if hasattr(stage,'declare_inputs'):
            stage.declare_inputs(cobj)
        if hasattr(stage,'declare_outputs'):            
            stage.declare_outputs(cobj)      
    
    # Save pipeline to disk    
    cobj.update_pipeline_status()
    
    return stages

def mapit(cobj):
    
    cobj.consistency_check()
    
    stages = setup_pipeline_status(cobj)

    cmp.preprocessing.run( cobj )
        
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
                      cobj.pipeline_status.RanOK( curStageObj, 
                                                  checkTimestamp=True,
                                                  timestampRootFile=cobj.get_pipeline_status_file() ) == True):
                    cobj.get_logger().info( "Skipping previously completed stage: '%s'" % ( stage.__name__) )
                    continue
                        
            # Run the stage            
            if hasattr(stage, 'run'):                
                stage.run( cobj )
                
            # Check if the stage ran properly
            if curStageObj != None:
                if cobj.pipeline_status.RanOK( stage=curStageObj, 
                                               storeTimestamp=True, 
                                               timestampRootFile=cobj.get_pipeline_status_file() ) == False:
                    msg = "Required output file not generated for stage: '%s'" % (stage.__name__)
                    cobj.get_logger().error( msg )
                    raise Exception( msg )
                

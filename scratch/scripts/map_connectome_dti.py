#!/usr/bin/env python
#
#
# NAME
#
#    connectome_web.py
#
# DESCRIPTION
#
#    This is a wrapper for the Connectome Mapping Toolkit such that
#    it can be executed from the CHB web front-end.
#
# AUTHORS
#
#    Daniel Ginsburg
#    Rudolph Pienaar
#    Children's Hospital Boston, 2010
#

import cmp,cmp.connectome,cmp.configuration,cmp.pipeline,cmp.logme
import sys
import os
import shutil, glob
from optparse import OptionParser

def parseCommandLine(conf):
    """Setup and parse command-line options"""
    
    parser = OptionParser(usage="%prog [options]")
    parser.add_option("-p", "--projectName",
                      dest="projectName",
                      help="Project name")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose")
    parser.add_option("-d","--workingDir",
                      dest="workingDir",
                      help="Subject Working Directory")
    parser.add_option("--b0",
                      dest="b0",
                      type="int",
                      help="Number of B0 volumes")
    parser.add_option("--bValue",
                      dest="bValue",
                      type="int",
                      help="B Value")
    parser.add_option("--gm",
                      dest="gradientMatrix",                      
                      help="Gradient file")
    parser.add_option("--dtiDir",
                      dest="dtiDir",
                      help="DTI DICOM Input directory")
    parser.add_option("--t1Dir",
                      dest="t1Dir",
                      help="T1 DICOM Input directory")
    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.error("Wrong number of arguments")
    
    # Parse command-line options        
    if options.workingDir == None:
        parser.error('You must specify --workingDir')
    else:
        conf.subject_workingdir = options.workingDir
        conf.subject_name = os.path.basename(conf.subject_workingdir) 
                
    if options.projectName:
        conf.project_name = options.projectName
        
    if options.gradientMatrix:
        conf.gradient_table_file = options.gradientMatrix
        conf.gradient_table = 'custom'
        
    if options.b0:
        conf.nr_of_b0 = options.b0

    if options.bValue:
        conf.max_b0_val = options.bValue
        
    return options
    
def prepForExecution(conf, options):
    """Prepare the files for execution of the cmp pipeline"""
    
    # Must specify the T1 and DTI input directories
    if options.t1Dir == None:
        sys.exit('You must specify --t1Dir')

    if options.dtiDir == None:
        sys.exit('You must specify --dtiDir')        
        
    # First, setup the pipeline status so we can determine the inputs
    cmp.connectome.setup_pipeline_status(conf)
    
    # Get the first stage by number
    stage = conf.pipeline_status.GetStage(num=1)
    
    # Get the DTI and T1 DICOM input folders
    dtiInput = conf.pipeline_status.GetStageInput(stage, 'dti-dcm')
    t1Input = conf.pipeline_status.GetStageInput(stage, 't1-dcm')
    
    # Create the input folders
    if not os.path.exists(dtiInput.rootDir):
        os.makedirs(dtiInput.rootDir)

    if not os.path.exists(t1Input.rootDir):        
        os.makedirs(t1Input.rootDir)
    
    # Copy the DICOM's
    for file in glob.glob(os.path.join(options.dtiDir, dtiInput.filePath)):
        shutil.copy(file, dtiInput.rootDir)
                
    for file in glob.glob(os.path.join(options.t1Dir, t1Input.filePath)):
        shutil.copy(file, t1Input.rootDir)
    
        
def main():
    """Main entrypoint for program"""
    
    # Create configuration object
    conf = cmp.configuration.PipelineConfiguration()
    
    # Default Options
    conf.freesurfer_home = os.environ['FREESURFER_HOME']
    conf.fsl_home = os.environ['FSL_DIR']
    conf.dtk_matrices = os.environ['DSI_PATH']
    conf.dtk_home = os.path.dirname(conf.dtk_matrices) # DTK home is one up from the matrices 
    conf.subject_raw_glob_diffusion = '*.dcm'
    conf.subject_raw_glob_T1 = '*.dcm'
    conf.subject_raw_glob_T2 = '*.dcm'
    
    conf.diffusion_imaging_model = "DTI"
    conf.streamline_param = ''
    
    # XXX: These are hardcoded for now until I figure out how they
    #      should be set
    conf.project_dir = '/chb/arch/python/cmp'
    
    # Setup and parse command-line options
    options = parseCommandLine(conf)
            
    # Prepare the directory structure for execution
    prepForExecution(conf, options)
    
    # Before running, reset the pipeline status because it will 
    # get created in mapit()
    conf.pipeline_status = cmp.pipeline_status.PipelineStatus()
        
    # Execute the 'cmp' pipeline!
    cmp.connectome.mapit(conf)
        
if __name__ == '__main__':
    main()    






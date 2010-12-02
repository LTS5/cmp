#
#
# NAME
#
#    pipeline_status
#
# DESCRIPTION
#
#    This module contain a class for interfacing with a Google Protocol
#    Buffer object that represents the state/status of a pipeline.
#
# AUTHORS
#
#    Daniel Ginsburg
#    Rudolph Pienaar
#    Children's Hospital Boston, 2010
#
import pipeline_pb2
import sys
import os.path as op
import networkx as nx
import glob

class PipelineStatus():
    """Interface to Pipeline protocol buffer"""
    
    def __init__(self, filename=None):
        """Constructor"""
        self.Pipeline = pipeline_pb2.Pipeline()
        
        # By default, use stdin/stderr for logging
        self.logError = sys.stderr.write
        self.logInfo = sys.stdin.write
        if filename != None:
            self.LoadFromFile(filename)
            
    def SetLoggerFunctions(self, logErrorFunc, logInfoFunc):
        """Set the functions used to log errors and info, by
        default if not set this will be sys.stderr.write and
        sys.stdin.write"""
        self.logError = logErrorFunc
        self.logInfo = logInfoFunc
                                        
    def LoadFromFile(self, filename):
        """Save the current state of the pipeline to a file"""
        try:
            f = open(filename, "rb")            
            self.Pipeline.ParseFromString(f.read())
            f.close()
        except:
            self.logError("Could not open file: " + filename)
        
    def SaveToFile(self, filename):
        """Load the pipeline state from a file"""
        try:
            f = open(filename, "wb")
            f.write(self.Pipeline.SerializeToString());
            f.close();
        except:
            self.logError("Could not write file: " + filename)
            
    def AddStage(self, name):
        """Add a new stage to the pipeline if it does not exist.  If it does already exist,
        just return the existing stage.  Returns the stage"""
        for stage in self.Pipeline.stages:
            if stage.name == name:
                return stage
            
        newStage = self.Pipeline.stages.add()
        newStage.num = len(self.Pipeline.stages)
        newStage.name = name;        
        return newStage;
    
    def AddType(self, tag, description):
        """Add a new file type by tag and description"""
        for type in self.Pipeline.types:
            if type.tag == tag:
                self.logError("Type already exists, can not add: '%s'" % (tag))
                return type

        type = self.Pipeline.types.add()
        type.tag = tag
        type.desc = description
        return type        
    
    def GetStage(self, name):
        """Get a stage by name"""
        for stage in self.Pipeline.stages:
            if stage.name == name:
                return stage

        self.logError('Pipeline does not contain stage %d' % (name))
        return None
    
    def CanRun(self, stage):
        """Checks a stage inputs to determine if the stage can run"""
        for curInput in stage.inputs:        
            filePath = op.join(curInput.rootDir, curInput.filePath)
            matchingFiles = glob.glob(filePath)
            if len(matchingFiles) >= 1:
                continue
            elif len(matchingFiles) == 0:
                self.logInfo("Stage '%s' missing input, file not found: %s" % (stage.name, filePath))
                return False
        
        # If we get here, then all files were found    
        return True
    
    def RanOK(self, stage):
        """Determines if all stage outputs were produced"""        
        if len(stage.outputs) == 0:
            self.logInfo("Stage %s has no outputs defined" % (stage.name))            
            return False;
                
        for curOutput in stage.outputs:
            filePath = op.join(curOutput.rootDir, curOutput.filePath)
            matchingFiles = glob.glob(filePath)
            if len(matchingFiles) >= 1:                
                continue
            elif len(matchingFiles) == 0:                
                self.logInfo("Stage '%s' did not complete, file not found: %s " % (stage.name, filePath))
                return False
        
        # If we get here, then all files were found    
        return True
    
    def AddStageInput(self, stage, rootDir, inputFilePath, inputName=None, typeTag=None):
        """Add new input to stage
        
        Inputs
        ----------
        stage:                 stage object to add new input to
        rootDir:               root directory of stage input
        inputFilePath:         path to file (or wildcard) from rootDir
        inputName: [optional]  name of input, if not specified, will be inputFilePath
        typeTag:   [optional]  type tag of input (referring to type declared with AddType), if not
                               specified, no typeTag is set.
    
        Outputs
        -------
        stage:                 Newly created input
    
        """
        newInput = stage.inputs.add()
        
        if inputName == None:
            inputName = inputFilePath
            
        return self.__AddStageInputOutput(newInput, rootDir, inputFilePath, inputName, typeTag)
            
    def AddStageOutput(self, stage, rootDir, outputFilePath, outputName=None, typeTag=None):
        """Add new output to stage
        
        Inputs
        ----------
        stage:                 stage object to add new output to
        rootDir:               root directory of stage output
        outputFilePath:        path to file (or wildcard) from rootDir
        inputName: [optional]  name of output, if not specified, will be outputFilePath
        typeTag:   [optional]  type tag of output (referring to type declared with AddType), if not
                               specified, no typeTag is set.
    
        Outputs
        -------
        stage:                 Newly created output
    
        """
        newOutput = stage.outputs.add()
        if outputName == None:
            outputName = outputFilePath
        return self.__AddStageInputOutput(newOutput, rootDir, outputFilePath, outputName, typeTag)                
    
    def AddStageInputFromObject(self, stage, inputOutputObject):
        """Copy input or output as an input to another stage"""
        newInput = stage.inputs.add()
        newInput.filePath = inputOutputObject.filePath;
        newInput.name = inputOutputObject.name;
        newInput.rootDir = inputOutputObject.rootDir
        return newInput
            
    def AddStageOutputFromObject(self, stage, inputOutputObject):
        """Copy input or output as an output from another stage"""
        newOutput = stage.outputs.add()
        newOutput.filePath = inputOutputObject.filePath
        newOutput.name = inputOutputObject.name
        newOutput.rootDir = inputOutputObject.rootDir
        return newOutput
    
    def GenerateDependencyGraph(self):
        """Using networkx, generate a dependency graph that maps the
        dependencies between stages.
        """ 
        g = nx.DiGraph()
        for stage in self.Pipeline.stages:
            g.add_node(stage.name)
        
        # Loop through the stages and connect the matching inputs and
        # outputs along edges
        for curStage in self.Pipeline.stages:
            for input in curStage.inputs:
                for searchStage in self.Pipeline.stages:
                    if curStage.num != searchStage.num:
                        for output in searchStage.outputs:                        
                            if input.filePath == output.filePath and input.rootDir == output.rootDir:
                                g.add_edge(searchStage.name, curStage.name,name=input.name)
        return g                
        
    
    def __AddStageInputOutput(self, inputOutput, rootDir, filePath, name, typeTag):
        """Used internally for adding stage input/output """
        inputOutput.filePath = filePath
        inputOutput.name = name;
        inputOutput.rootDir = rootDir
        if typeTag != None:
            inputOutput.typeTag = typeTag
        return inputOutput    

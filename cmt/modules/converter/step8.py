""" Convert a selection of files from the subject folder into
a connectome file format for visualization and analysis in the connectomeviewer """


def run(conf, subject_tuple):
    """ Run the converter step
    
    Parameters
    ----------
    conf : PipelineConfiguration object
    subject_tuple : tuple, (subject_id, timepoint)
        Process the given subject
        
    """
    globals()['gconf'] = conf
    globals()['sid'] = subject_tuple
    
    print "Happy converting!"
    
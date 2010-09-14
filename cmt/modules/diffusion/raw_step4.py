import os, os.path as op
import sys
import logging
log = logging.getLogger()

from glob import glob
import subprocess


def resample_dsi():

    log.info("STEP 4a: Resample the DSI dataset to 2x2x2 mm^3")

    input_dsi_file = op.join(gconf.get_nifti4subject(sid), 'DSI.nii')
    ouput_dsi_file = op.join(gconf.get_cmt_rawdiff4subject(sid), 'DSI_resampled_2x2x2.nii')
    
    # os.mkdirs(op.join(gconf.get_cmt_rawdiff4subject(sid), '2x2x2'))
    ## what is this folder for?
    
    if not op.exists(input_dsi_file):
        log.error("File does not exists: %s" % input_dsi_file)
    else:
        log.debug("Found file %s" % input_dsi_file)
    
    proc = subprocess.call(['mri_convert','-vs 2 2 2', input_dsi_file, ouput_dsi_file],
                           
                                    cwd = gconf.get_cmt_rawdiff4subject(sid))
    print "Return code", proc
    
#    proc = subprocess.call(['fslsplit', input_dsi_file, "MR", "-t"],
#                                cwd = gconf.get_cmt_rawdiff4subject(sid))
#    
#    print "Return code", proc
    
##                                shell=True,
#                                stdout = subprocess.PIPE,
#                                stderr = subprocess.PIPE)
#    
#    out, err = proc.communicate()
#    print out
#    print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
#    outfiles = glob(op.join(gconf.get_cmt_rawdiff4subject(sid), 'MR*.nii.gz'))
    
#    print outfiles
    
#    for file in outfiles[:2]:
#        print "======"
#        print "File", file
#        
#        proc = subprocess.call(['mri_convert',"--voxsize", "2.0 2.0 2.0", file, "tmp.nii.gz"],
#                                    cwd = gconf.get_cmt_rawdiff4subject(sid))
        
#                                    shell = True,
#                                    stdout=subprocess.PIPE,
#                                    stderr=subprocess.PIPE)

#        out, err = proc.communicate()
#        print out
    
#        proc = subprocess.call(['fslmaths',"tmp.nii.gz", file, "-dt", "short"],
#                                    cwd = gconf.get_cmt_rawdiff4subject(sid))
#                                    shell = True,
#                                    stdout=subprocess.PIPE,
#                                    stderr=subprocess.PIPE)
    
#        out, err = proc.communicate()
#        print out
    
#        os.unlink(op.join(gconf.get_cmt_rawdiff4subject(sid), 'tmp.nii.gz'))

def compute_odfs():    

    log.info("STEP 4b: Compute the ODFs field(s)")
    
    ouput_dsi_file = op.join(gconf.get_cmt_rawdiff4subject(sid), 'DSI_resampled_2x2x2.nii')
    
    if not op.exists(ouput_dsi_file):
        log.error("No input file available: %s" % ouput_dsi_file)
    
    for sharp in gconf.sharpness_odf:
        
        odf_out_path = op.join(gconf.get_cmt_rawdiff4subject(sid), 'odf_%s' % str(sharp))
        try:
            os.makedirs(odf_out_path)
        except os.error:
            log.info("%s was already existing" % str(odf_out_path))
    
        # calculate ODF map
        
        # XXX: rm -f "odf_${sharpness}/dsi_"*
        
        proc = subprocess.call(['odf_recon', \
                                 ouput_dsi_file, \
                                 str(gconf.nr_of_gradient_directions),\
                                 str(gconf.nr_of_sampling_directions), \
                                 op.join(odf_out_path, "dsi_"), \
                                 "-b0", "1", "-mat %s" % gconf.get_dsi_matrix(), \
                                 "-dsi", "-p 4", "-sn 0", "-ot nii", "-s %s" % str(sharp)],
                                 cwd = gconf.get_cmt_rawdiff4subject(sid))
        
        if not op.exists(op.join(odf_out_path, "dsi_odf.nii")):
            log.error("Unable to reconstruct ODF!")
            
        # calculate GFA map
        # XXX: rm -f "odf_${sharpness}/dsi_gfa.nii"
        
        proc = subprocess.Popen(['DTB_gfa', \
                                 "--dsi 'dsi_'"],
                                    cwd = odf_out_path,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        
        if not op.exists(op.join(odf_out_path, "dsi_gfa.nii")):
            log.error("Unable to calculate GFA map!")
    
    log.info("[ DONE ]")

def run(conf, subject_tuple):
    """ Run the diffusion step
    
    Parameters
    ----------
    conf : PipelineConfiguration object
    subject_tuple : tuple, (subject_id, timepoint)
        Process the given subject
        
    """
    
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['sid'] = subject_tuple

    resample_dsi()
    compute_odfs()
    
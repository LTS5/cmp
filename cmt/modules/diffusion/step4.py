import os, os.path as op
import sys
import logging
log = logging.getLogger()

from glob import glob
import subprocess

def resample_dsi():

    log.info("STEP 4a: Resample the DSI dataset to 2x2x2 mm^3")

    input_dsi_file = op.join(gconf.get_nifti4subject(sid), 'DSI.nii')
    ouput_dsi_file = op.join(gconf.get_cmt_rawdiff4subject(sid), 'DSI_resampled_2x2x2.nii.gz')
    
    # os.mkdirs(op.join(gconf.get_cmt_rawdiff4subject(sid), '2x2x2'))
    ## what is this folder for?
    
    if not op.exists(input_dsi_file):
        log.error("File does not exists: %s" % input_dsi_file)
    else:
        log.debug("Found file: %s" % input_dsi_file)
    
    log.debug("Output DSI file: %s" % ouput_dsi_file)
    
    log.info("Starting mri_convert ...")
    proc = subprocess.Popen(['mri_convert -vs 2 2 2 %s %s' % (input_dsi_file, ouput_dsi_file)],
                           shell = True,
                           stdout = subprocess.PIPE,
                           stderr = subprocess.PIPE,
                           cwd = gconf.get_cmt_rawdiff4subject(sid))
    out, err = proc.communicate()
    log.info(out)
    
    
    #### XXX: converting to short!
    
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
    
    ouput_dsi_file = op.join(gconf.get_cmt_rawdiff4subject(sid), 'DSI_resampled_2x2x2.nii.gz')
    
    if not op.exists(ouput_dsi_file):
        log.error("No input file available: %s" % ouput_dsi_file)
    
    for sharp in gconf.mode_parameters['sharpness_odf']:
        
        odf_out_path = op.join(gconf.get_cmt_rawdiff4subject(sid), 'odf_%s' % str(sharp))
        try:
            os.makedirs(odf_out_path)
        except os.error:
            log.info("%s was already existing" % str(odf_out_path))
    
        # calculate ODF map
        
        # XXX: rm -f "odf_${sharpness}/dsi_"*

        odf_cmd = ['odf_recon %s %s %s %s -b0 1 -mat %s -dsi -p 4 -sn 0 -ot nii -s %s' % (ouput_dsi_file, 
                                 str(gconf.mode_parameters['nr_of_gradient_directions']),
                                 str(gconf.mode_parameters['nr_of_sampling_directions']), 
                                 op.join(odf_out_path, "dsi_"),
                                 gconf.get_dsi_matrix(),
                                 str(sharp) ) ]
        
        log.info("Starting odf_recon ...")
        proc = subprocess.Popen(odf_cmd,
                                shell = True,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE,
                                cwd = gconf.get_cmt_rawdiff4subject(sid))
        
        out, err = proc.communicate()
        log.info(out)
        
        if not op.exists(op.join(odf_out_path, "dsi_odf.nii")):
            log.error("Unable to reconstruct ODF!")
            
        # calculate GFA map
        # XXX: rm -f "odf_${sharpness}/dsi_gfa.nii"
        
        log.info("Starting DTB_gfa ...")
        proc = subprocess.Popen(['DTB_gfa %s' % "--dsi 'dsi_'"],
                                 cwd = odf_out_path,
                                 shell = True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE
                                 )
        
        out, err = proc.communicate()
        log.info(out)

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
    
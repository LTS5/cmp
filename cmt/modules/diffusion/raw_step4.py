import os, os.path as op
import logging as log
from glob import glob
import subprocess

global gconf
global subject_dir
global new_rad_diff_path

def resample_dsi():
    log.info("STEP 4a: Resample the DSI dataset to 2x2x2 mm^3")

    input_dsi_file = op.join(subject_dir, '2__NIFTI', 'DSI.nii')
    
    if not op.exists(input_dsi_file):
        log.error("File does not exists: %s" % input_dsi_file)
    
    proc = subprocess.Popen(['fslsplit',input_dsi_file, "MR", "-t"],
                                cwd = new_raw_diff_path,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    
    outfiles = glob(op.join(new_raw_diff_path, 'MR*.nii'))
    for file in outfiles:
        proc = subprocess.Popen(['mri_convert',file, "tmp.nii" "-vs 2 2 2"],
                                    cwd = new_raw_diff_path,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
     
        proc = subprocess.Popen(['fslmaths',"tmp.nii", file, "-dt short"],
                                    cwd = new_raw_diff_path,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
    
        os.unlink(op.join(new_raw_diff_path, 'tmp.nii'))

def compute_odfs():    
    log.info("STEP 4b: Compute the ODFs field(s)")
    
    if not op.exists(op.join(new_raw_diff_path, "MR0000.nii")):
        log.error("No input file MR0000.nii generated")
    
    for sharp in gconf.sharpness:
        
        odf_out_path = os.mkdirs(op.join(subject_dir, '4__CMT', 'raw_diffusion', 'odf_%s' % str(shapr)))
    
        # calculate ODF map
        
        # XXX: rm -f "odf_${sharpness}/dsi_"*
        
        proc = subprocess.Popen(['odf_recon', \
                                 op.join(new_raw_diff_path, "MR0000.nii"), \
                                 str(gconf.nr_of_gradient_directions),\
                                 str(gconf_nr_of_X), \
                                 op.join(odf_out_path, "dsi_"), \
                                 "-b0 1", "-mat %s" % gconf.get_dsi_matrix(), \
                                 "-dsi", "-p 4", "-sn 0", "-ot nii", "-s %s" % sharp],
                                    cwd = new_raw_diff_path,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        
        if not os.exists(op.join(odf_out_path, "dsi_odf.nii")):
            log.error("Unable to reconstruct ODF!")
            
        # calculate GFA map
        # XXX: rm -f "odf_${sharpness}/dsi_gfa.nii"
        
        proc = subprocess.Popen(['DTB_gfa', \
                                 "--dsi 'dsi_'"],
                                    cwd = odf_out_path,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        
        if not os.exists(op.join(odf_out_path, "dsi_gfa.nii")):
            log.error("Unable to calculate GFA map!")
            
        # rm -R "2x2x2" &> /dev/null    # remove temp 2x2x2/MR*.nii files
    
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
    gconf = conf
    subject_dir = gconf[subject_tuple]['workingdir']
    new_raw_diff_path = os.mkdirs(op.join(subject_dir, '4__CMT', 'raw_diffusion', '2x2x2'))
    
    resample_dsi()
    compute_odfs()
    
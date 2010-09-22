import os, os.path as op
from glob import glob
from time import time
import shutil
import subprocess
import sys
from ...logme import *

def mymove(src, dst, log):
    """ Custom move function with target checking and logging """
    
    if not op.exists(src):
        log.error("Source does not exist: %s" % src)
        return
    
    if op.exists(dst):
        ndst = dst + '_OLD'
        log.debug("Target file already exists. Rename it to %s" % ndst)
        if op.exists(dst):
            if op.isfile(dst):
                shutil.move(dst,ndst)
    
    log.info("Move file %s to %s" % (src, dst))
    shutil.copy(src, dst)
    
def create_annot_label():

    log.info("Create the cortical labels necessary for our ROIs")
    log.info("=================================================")
    
    subjects_dir = gconf.get_subj_dir(sid)

    fs_label_dir = op.join(gconf.get_fs4subject(sid), 'label')
    fs_dir = gconf.get_fs4subject(sid)
    
    paths = []
    
    for p in gconf.parcellation.keys():
        for hemi in ['lh', 'rh']:
            spath = gconf.parcellation[p]['fs_label_subdir_name'] % hemi
            paths.append(spath)
    
    for p in paths:
        try:
            os.makedirs(op.join(fs_label_dir, p))
        except:
            pass
        
    comp = [
    ('rh', 'myatlas_33_rh.gcs', 'rh.myaparc_33.annot', 'regenerated_rh_35',''),
    ('rh', 'myatlasP1_16_rh.gcs','rh.myaparcP1_16.annot','regenerated_rh_500','myaparcP1_16'),
    ('rh', 'myatlasP17_28_rh.gcs','rh.myaparcP17_28.annot','regenerated_rh_500','myaparcP17_28'),
    ('rh', 'myatlasP29_35_rh.gcs','rh.myaparcP29_35.annot','regenerated_rh_500','myaparcP29_35'),
    ('rh','myatlas_60_rh.gcs','rh.myaparc_60.annot','regenerated_rh_60','myaparc_60'),
    ('rh','myatlas_125_rh.gcs','rh.myaparc_125.annot','regenerated_rh_125','myaparc_125'),
    ('rh','myatlas_250_rh.gcs','rh.myaparc_250.annot','regenerated_rh_250','myaparc_250'),
    ('lh', 'myatlas_33_lh.gcs', 'lh.myaparc_33.annot', 'regenerated_lh_35',''),
    ('lh', 'myatlasP1_16_lh.gcs','lh.myaparcP1_16.annot','regenerated_lh_500','myaparcP1_16'),
    ('lh', 'myatlasP17_28_lh.gcs','lh.myaparcP17_28.annot','regenerated_lh_500','myaparcP17_28'),
    ('lh', 'myatlasP29_35_lh.gcs','lh.myaparcP29_35.annot','regenerated_lh_500','myaparcP29_35'),
    ('lh','myatlas_60_lh.gcs','lh.myaparc_60.annot','regenerated_lh_60', 'myaparc_60'),
    ('lh','myatlas_125_lh.gcs','lh.myaparc_125.annot','regenerated_lh_125','myaparc_125'),
    ('lh','myatlas_250_lh.gcs','lh.myaparc_250.annot','regenerated_lh_250','myaparc_250'),
    ]

    for out in comp:      
        mris_cmd = """mris_ca_label "3__FREESURFER" %s "%s/surf/rh.sphere.reg" "%s" "%s/label/%s" """ % (out[0], fs_dir, gconf.get_lausanne_atlas(out[1]), fs_dir, out[3])    
        runCmd( mris_cmd, log )
        log.info('-----------')
        if not out[4] == '':
            annot = '--annotation "%s"' % out[4]
        else:
            annot = ''
        mri_an_cmd = 'mri_annotation2label --subject "3__FREESURFER" --hemi %s --outdir "%s/label/%s/" %s' % (out[0], fs_dir, out[3], annot)
        runCmd( mri_an_cmd, log )
        log.info('-----------')

    # extract cc and unknown to add to tractography mask
    
    shutil.copy(op.join(fs_label_dir, 'regenerated_rh_35', 'rh.unknown.label'), op.join(fs_label_dir, 'rh.unknown.label'))
    shutil.copy(op.join(fs_label_dir, 'regenerated_lh_35', 'lh.unknown.label'), op.join(fs_label_dir, 'lh.unknown.label'))
    shutil.copy(op.join(fs_label_dir, 'regenerated_rh_35', 'rh.corpuscallosum.label'), op.join(fs_label_dir, 'rh.corpuscallosum.label'))
    shutil.copy(op.join(fs_label_dir, 'regenerated_lh_35', 'lh.corpuscallosum.label'), op.join(fs_label_dir, 'lh.corpuscallosum.label'))

    # XXX: error: you must specify a registration method, where to save to?, why?
    mri_cmd = """mri_label2vol --label "rh.corpuscallosum.label" --label "lh.corpuscallosum.label" --label "rh.unknown.label" --label "lh.unknown.label" --temp "%s/mri/orig.mgz" --o  "cc_unknown.nii" """ % fs_dir    
    runCmd( mri_cmd, log )

    runCmd( 'mris_volmask "3__FREESURFER"', log)

    mri_cmd = 'mri_convert -i "%s/mri/ribbon.mgz" -o "%s/mri/ribbon.nii"' % (fs_dir, fs_dir)
    runCmd( mri_cmd, log )
        
    mri_cmd = 'mri_convert -i "%s/mri/aseg.mgz" -o "%s/mri/aseg.nii"' % (fs_dir, fs_dir)
    runCmd( mri_cmd, log )

    log.info("[ DONE ]")  

def reorganize():
    log.info("Move datasets into 'fs_output/registred/HR' folder")
    
    fs_dir = gconf.get_fs4subject(sid)
    
    # crop to the "space of original T1"
    log.info(" * Cropping datasets to ORIGINAL GEOMETRY of T1...")
    
    ds = [
     'mri/aseg','mri/ribbon', 'label/cc_unknown', \
     'label/regenerated_lh_35/ROI_lh','label/regenerated_rh_35/ROI_rh', \
     'label/regenerated_rh_60/ROI_rh','label/regenerated_lh_60/ROI_lh',  \
    'label/regenerated_rh_125/ROI_rh','label/regenerated_lh_125/ROI_lh', \
    'label/regenerated_rh_250/ROI_rh','label/regenerated_lh_250/ROI_lh', \
    'label/regenerated_rh_500/ROI_rh','label/regenerated_lh_500/ROI_lh', ]

    for d in ds:
        log.info("Processing %s:" % d)
        
        fpa = op.join(fs_dir, d)
        
        mri_cmd = 'mri_convert -rl "%s/mri/orig/001.mgz" -rt nearest "%s.nii" -nc "%s_tmp.nii"' % (fs_dir, fpa, fpa)
        
        runCmd( mri_cmd,log )
        
        src = '%s_tmp.nii' % fpa
        dst = '%s.nii' % fpa
        mymove(src, dst, log )        
        
    
    # create subfolders in '4__CMT' folder
    
    #rm -fR "fs_output/registred/HR"
    reg_path = op.join(gconf.get_cmt_fsout4subject(sid), 'registred', 'HR')
    try:
        os.makedirs(reg_path)
    except:
        pass

     # XXX: this piece of code only works for the default lausanne pipeline 
     
    for p in gconf.parcellation.keys():
        log.info("Create path %s" % p )
        try:
            os.makedirs(op.join(reg_path, p))
        except:
            pass
        
        
    # copy datasets from '3__FREESURFER' folder
    src = op.join(fs_dir, 'mri', 'aseg.nii')
    dst = reg_path    
    mymove(src,dst,log)
    
    src = op.join(fs_dir, 'mri', 'ribbon.nii')
    dst = reg_path    
    mymove(src,dst,log)    

    # XXX: adapt this when clear above
    src = op.join(fs_dir, 'label', 'cc_unknown.nii')
    dst = reg_path    
    mymove(src,dst,log)    
    
    for p in gconf.parcellation.keys():
        for hemi in ['lh', 'rh']:
            spath = gconf.parcellation[p]['fs_label_subdir_name'] % hemi
            src = op.join(fs_dir, 'label', spath, 'ROI_%s.nii' % hemi)
            dst = op.join(reg_path, p)
            mymove(src,dst,log)
            
    log.info("[ DONE ]")

def create_roi():
    log.info("Create the ROIs:")

    matlab_cmd = gconf.matlab_prompt + """ "roi_creation( '%s','%s' ); exit" """ % (sid[0], sid[1])
    runCmd( matlab_cmd, log )
    
    log.info("[ DONE ]")  
    
def create_final_mask():
    log.info("Create final ROI mask, cortex and deep gray structures")
    # $MY_MATLAB "roi_merge( '${MY_SUBJECT}','${MY_TP}' ); exit"
    log.info("[ DONE ]")  

def finalize_wm():
    log.info("Finalize WM mask")
    #$MY_MATLAB "mask_creation( '${MY_SUBJECT}','${MY_TP}' ); exit"
    log.info("[ DONE ]")  

def finalize_roi():
    log.info("Finalize ROI mask")
    # $MY_MATLAB "script_roi_finalize; exit"
    log.info("[ DONE ]")  


def run(conf, subject_tuple):
    """ Run the first mask creation step
    
    Parameters
    ----------
    conf : PipelineConfiguration object
    subject_tuple : tuple, (subject_id, timepoint)
        Process the given subject
        
    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['sid'] = subject_tuple
    globals()['log'] = gconf.get_logger4subject(sid) 
    start = time()
    
    log.info("ROI_HR_th.nii / fsmask_1mm.nii CREATION")
    log.info("=======================================")
    
    from os import environ
    env = environ
    env['SUBJECTS_DIR'] = gconf.get_subj_dir(sid)
    env['DATA_path'] = gconf.project_dir
    env['CMT_HOME'] = gconf.get_cmt_home()
    cp = gconf.get_cmt_home()
    env['MATLABPATH'] = "%s:%s/matlab_related:%s/matlab_related/nifti:%s/matlab_related/tractography:%s/registration" % (cp, cp, cp, cp, cp)
    
#    create_annot_label()
    create_roi()
    #reorganize()
#    create_final_mask()
#    finalize_wm()
#    finalize_roi()
    
    log.info("Module took %s seconds to process." % (time()-start))
    
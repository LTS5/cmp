import os, os.path as op
from glob import glob
from time import time
import shutil
import subprocess
import sys
from ...logme import *

import nibabel as ni
import networkx as nx
import numpy as np
from cmt.util import mymove

def create_annot_label():

    log.info("Create the cortical labels necessary for our ROIs")
    log.info("=================================================")
    
    subjects_dir = gconf.get_subj_dir()

    fs_label_dir = op.join(gconf.get_fs(), 'label')
    fs_dir = gconf.get_fs()
    
    paths = []
    
    for p in gconf.parcellation.keys():
        for hemi in ['lh', 'rh']:
            spath = gconf.parcellation[p]['fs_label_subdir_name'] % hemi
            paths.append(spath)
    
    # XXX: this makedirs should go in the preprocessing module
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
        mris_cmd = 'mris_ca_label "FREESURFER" %s "%s/surf/%s.sphere.reg" "%s" "%s" ' % (out[0], 
		fs_dir, out[0], gconf.get_lausanne_atlas(out[1]), op.join(fs_label_dir, out[2]))    
        runCmd( mris_cmd, log )
        log.info('-----------')

        if not out[4] == '':
            annot = '--annotation "%s"' % out[4]
        else:
            annot = ''
        mri_an_cmd = 'mri_annotation2label --subject "FREESURFER" --hemi %s --outdir "%s" %s' % (out[0], op.join(fs_label_dir, out[3]), annot)
        runCmd( mri_an_cmd, log )
        log.info('-----------')

    # extract cc and unknown to add to tractography mask, we do not want this as a region of interest
    # in FS 5.0, unknown and corpuscallosum are not available for the 35 scale, but for the other scales only, take the ones from _60
	rhun = op.join(fs_label_dir, 'rh.unknown.label')
	lhun = op.join(fs_label_dir, 'lh.unknown.label')
	rhco = op.join(fs_label_dir, 'rh.corpuscallosum.label')
	lhco = op.join(fs_label_dir, 'lh.corpuscallosum.label')
    shutil.copy(op.join(fs_label_dir, 'regenerated_rh_60', 'rh.unknown.label'), rhun)
    shutil.copy(op.join(fs_label_dir, 'regenerated_lh_60', 'lh.unknown.label'), lhun)
    shutil.copy(op.join(fs_label_dir, 'regenerated_rh_60', 'rh.corpuscallosum.label'), rhco)
    shutil.copy(op.join(fs_label_dir, 'regenerated_lh_60', 'lh.corpuscallosum.label'), lhco)

    mri_cmd = """mri_label2vol --label "%s" --label "%s" --label "%s" --label "%s" --temp "%s" --o  "%s" --identity """ % (rhun, lhun, rhco, lhco, op.join(fs_dir, 'mri', 'orig.mgz'), op.join(fs_dir, 'label', 'cc_unknown.nii') )
    runCmd( mri_cmd, log )

    runCmd( 'mris_volmask "FREESURFER"', log)

    mri_cmd = 'mri_convert -i "%s/mri/ribbon.mgz" -o "%s/mri/ribbon.nii"' % (fs_dir, fs_dir)
    runCmd( mri_cmd, log )
        
    mri_cmd = 'mri_convert -i "%s/mri/aseg.mgz" -o "%s/mri/aseg.nii"' % (fs_dir, fs_dir)
    runCmd( mri_cmd, log )

    log.info("[ DONE ]")  

def create_roi():
    """ Creates the ROI_%s.nii files using the given parcellation information
    from networks. Iteratively create volume. """
    
    log.info("Create the ROIs:")

    fs_dir = gconf.get_fs()
    
    # load aseg volume
    aseg = ni.load(op.join(fs_dir, 'mri', 'aseg.nii'))
    asegd = aseg.get_data()
    
    for parkey, parval in gconf.parcellation.items():
        
        pg = nx.read_graphml(parval['node_information_graphml'])
        
        # each node represents a brain region
        # create a big 256^3 volume for storage of all ROIs
        rois = np.zeros( (256, 256, 256), dtype=np.int16 )

        for brk, brv in pg.nodes_iter(data=True):
            
            if brv['dn_hemisphere'] == 'left':
                hemi = 'lh'
            elif brv['dn_hemisphere'] == 'right':
                hemi = 'rh'
                
            if brv['dn_region'] == 'subcortical':

                log.info("---------------------")
                log.info("Work on %s brain region: %s" % (brv['dn_region'], brv['dn_freesurfer_structname']) )
                log.info("---------------------")

                # if it is subcortical, retrieve roi from aseg
                idx = np.where(asegd == int(brv['dn_fs_aseg_val']))
                rois[idx] = int(brv['dn_intensityvalue'])
            
            elif brv['dn_region'] == 'cortical':

                log.info("---------------------")
                log.info("Work on %s brain region: %s" % (brv['dn_region'], brv['dn_freesurfer_structname']) )
                log.info("---------------------")

                labelpath = op.join(fs_dir, 'label', parval['fs_label_subdir_name'] % hemi)
                # construct .label file name
                
                fname = '%s.%s.label' % (hemi, brv['dn_freesurfer_structname'])

                # execute fs mri_label2vol to generate volume roi from the label file
                # store it in temporary file to be overwritten for each region

                mri_cmd = 'mri_label2vol --label "%s" --temp "%s" --o "%s" --identity' % (op.join(labelpath, fname),
                        op.join(fs_dir, 'mri', 'orig.mgz'), op.join(labelpath, 'tmp.nii'))
                runCmd( mri_cmd, log )
                
                tmp = ni.load(op.join(labelpath, 'tmp.nii'))
                tmpd = tmp.get_data()

                # find voxel and set them to intensityvalue in rois
                idx = np.where(tmpd == 1)
                rois[idx] = int(brv['dn_intensityvalue'])
                
                        
        # store volume eg in ROI_scale33.nii
        out_roi = op.join(fs_dir, 'label', 'ROI_%s.nii' % parkey)
        
        log.info("Save output image to %s" % out_roi)
        img = ni.Nifti1Image(rois, aseg.get_affine(), aseg.get_header())
        ni.save(img, out_roi)
    
    log.info("[ DONE ]")  
    

def create_wm_mask():
    
    log.info("Create white matter mask")
    
    fs_dir = gconf.get_fs()
    fs_cmd_dir = gconf.get_cmt_fsout()
    reg_path = gconf.get_cmt_tracto_mask()
    
    # load ribbon as basis for white matter mask
    fsmask = ni.load(op.join(fs_dir, 'mri', 'ribbon.nii'))
    fsmaskd = fsmask.get_data()

    wmmask = np.zeros( fsmask.get_data().shape )
    
    # these data is stored and can be extracted from fs_dir/stats/aseg.txt
    
    # extract right and left white matter (hardcoded, think about it XXX 
    idx_lh = np.where(fsmaskd == 120)
    idx_rh = np.where(fsmaskd == 20)
    
    wmmask[idx_lh] = 1
    wmmask[idx_rh] = 1
    
    # remove subcortical nuclei from white matter mask
    # alternatively: we can do tractography through them and later do what?
    
    # XXX: REMOVE the voxels labeled in 'scale33/ROI_HR_th'
    # XXX: REMOVE voxels from csfA, csfB, gr_ncl and remaining structures from 'aseg.nii' dataset
    # XXX: erosion procedures?

    aseg = ni.load(op.join(fs_dir, 'mri', 'aseg.nii'))
    asegd = aseg.get_data()
    
#4: Left-Lateral-Ventricle
#5: Left-Inf-Lat-Vent
#14: 3rd-Ventricle
#15: 4th-Ventricle
#24: CSF
#43: Right-Lateral-Ventricle
#44: Right-Inf-Lat-Vent
#72: 5th-Ventricle
# XXX: more to discuss

    for i in [4,5,14,15,24,43,44,72]:
        idx = np.where(asegd == i)
        wmmask[idx] == 0
    
    # ADD voxels from 'cc_unknown.nii' dataset
    
    ccun = ni.load(op.join(fs_dir, 'label', 'cc_unknown.nii'))
    ccund = ccun.get_data()
    idx = np.where(ccund != 0)
    wmmask[idx] = 1
    
    # XXX: subtracting wmmask from ROI. necessary?
    for parkey, parval in gconf.parcellation.items():
        
        # check if we should subtract the cortical rois from this parcellation
        if parval.has_key('subtract_from_wm_mask'):
            if not bool(int(parval['subtract_from_wm_mask'])):
                continue
        else:
            continue

        log.info("Loading %s to subtract cortical ROIs from white matter mask" % ('ROI_%s.nii' % parkey) )
        roi = ni.load(op.join(gconf.get_fs(), 'label', 'ROI_%s.nii' % parkey))
        roid = roi.get_data()
        
        assert roid.shape[0] == wmmask.shape[0]
        
        pg = nx.read_graphml(parval['node_information_graphml'])
        
        for brk, brv in pg.nodes_iter(data=True):
            
            if brv['dn_region'] == 'cortical':
                
                log.info("Subtracting cortical region %s with intensity value %s" % (brv['dn_region'], brv['dn_intensityvalue']))
    
                idx = np.where(roid == int(brv['dn_intensityvalue']))
                wmmask[idx] = 0
    
    # output white matter mask. crop and move it afterwards
    wm_out = op.join(fs_dir, 'mri', 'fsmask_1mm.nii')
    img = ni.Nifti1Image(wmmask, fsmask.get_affine(), fsmask.get_header() )
    log.info("Save white matter mask: %s" % wm_out)
    ni.save(img, wm_out)

def crop_and_move_datasets():
    
    log.info("Cropping and moving datasets to CMT/fs_output/registred/HR folder")
    
    fs_dir = gconf.get_fs()
    fs_cmd_dir = gconf.get_cmt_fsout()
    reg_path = gconf.get_cmt_tracto_mask()
    
    # datasets to crop and move: (from, to)
    ds = [
          (op.join(fs_dir, 'mri', 'aseg.nii'), op.join(reg_path, 'aseg.nii') ),
          (op.join(fs_dir, 'mri', 'ribbon.nii'), op.join(reg_path, 'ribbon.nii') ),
          (op.join(fs_dir, 'mri', 'fsmask_1mm.nii'), op.join(reg_path, 'fsmask_1mm.nii') ),
          (op.join(fs_dir, 'label', 'cc_unknown.nii'), op.join(reg_path, 'cc_unknown.nii') )
          ]
    
    for p in gconf.parcellation.keys():
        ds.append( (op.join(fs_dir, 'label', 'ROI_%s.nii' % p), op.join(reg_path, p, 'ROI_HR_th.nii')) )
    
    orig = op.join(fs_dir, 'mri', 'orig', '001.mgz')
        
    for d in ds:
        log.info("Processing %s:" % d[0])
        
        # does it exist at all?
        if not op.exists(d[0]):
            raise Exception('File %s does not exist.' % d[0])
        # reslice to original volume because the roi creation with freesurfer
        # changed to 256x256x256 resolution
        mri_cmd = 'mri_convert -rl "%s" -rt nearest "%s" -nc "%s"' % (orig, d[0], d[1])
        runCmd( mri_cmd,log )


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
    
    # Matlab legacy:
    from os import environ
    env = environ
    env['SUBJECTS_DIR'] = gconf.get_subj_dir()
    #env['DATA_path'] = gconf.project_dir
    #env['CMT_HOME'] = gconf.get_cmt_home()
    #cp = gconf.get_cmt_home()
    #env['MATLABPATH'] = "%s:%s/matlab_related:%s/matlab_related/nifti:%s/matlab_related/tractography:%s/registration" % (cp, cp, cp, cp, cp)
    
    create_annot_label()
    create_roi()
    create_wm_mask()    
    crop_and_move_datasets()
    
    log.info("Module took %s seconds to process." % (time()-start))

    if not len(gconf.emailnotify) == 0:
        msg = "Mask creation module finished!\nIt took %s seconds." % int(time()-start)
        send_email_notification(msg, gconf.emailnotify, log)  


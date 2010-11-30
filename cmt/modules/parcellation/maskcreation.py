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
    # in FS 5.0, unknown and corpuscallosum are not available for the 35 scale (why?),
    # but for the other scales only, take the ones from _60
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
        log.info("Working on parcellation: " + parkey)
        log.info("========================")
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
                log.info("Work on brain region: %s" % (brv['dn_region']) )
                log.info("Freesurfer Struct Name: %s" %  brv['dn_freesurfer_structname'] )
                log.info("---------------------")

                # if it is subcortical, retrieve roi from aseg
                idx = np.where(asegd == int(brv['dn_fs_aseg_val']))
                rois[idx] = int(brv['dn_intensityvalue'])
            
            elif brv['dn_region'] == 'cortical':
                log.info(brv)
                log.info("---------------------")
                log.info("Work on brain region: %s" % (brv['dn_region']) )
                log.info("Freesurfer Struct Name: %s" %  brv['dn_freesurfer_structname'] )
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
    
    # these data is stored and could be extracted from fs_dir/stats/aseg.txt
    
    # extract right and left white matter 
    idx_lh = np.where(fsmaskd == 120)
    idx_rh = np.where(fsmaskd == 20)
    
    wmmask[idx_lh] = 1
    wmmask[idx_rh] = 1
    
    # remove subcortical nuclei from white matter mask
    aseg = ni.load(op.join(fs_dir, 'mri', 'aseg.nii'))
    asegd = aseg.get_data()

    try:
        import scipy.ndimage.morphology as nd
    except ImportError:
        raise Exception('Need scipy for binary erosion of white matter mask')

    # need binary erosion function
    imerode = nd.binary_erosion
    
    # ventricle erosion    
    csfA = np.zeros( asegd.shape )
    csfB = np.zeros( asegd.shape )

    # structuring elements for erosion
    se1 = np.zeros( (3,3,5) )
    se1[1,:,2] = 1; se1[:,1,2] = 1; se1[1,1,:] = 1
    se = np.zeros( (3,3,3) );
    se[1,:,1] = 1; se[:,1,1] = 1; se[1,1,:] = 1

    # lateral ventricles, thalamus proper and caudate
    # the latter two removed for better erosion, but put back afterwards
    idx = np.where( (asegd == 4) |
                    (asegd == 43) |
                    (asegd == 11) |
                    (asegd == 50) |
                    (asegd == 31) |
                    (asegd == 63) |
                    (asegd == 10) |
                    (asegd == 49) )
    csfA[idx] = 1
    csfA = imerode(imerode(csfA, se1),se)
    
    # thalmus proper and cuadate are put back because they are not lateral ventricles
    idx = np.where( (asegd == 11) |
                    (asegd == 50) |
                    (asegd == 10) |
                    (asegd == 49) )
    csfA[idx] = 0

    # REST CSF, IE 3RD AND 4TH VENTRICULE AND EXTRACEREBRAL CSF    
    idx = np.where( (asegd == 5) |
                    (asegd == 14) |
                    (asegd == 15) |
                    (asegd == 24) |
                    (asegd == 44) |
                    (asegd == 72) |
                    (asegd == 75) |
                    (asegd == 76) |
                    (asegd == 213) |
                    (asegd == 221))    
    # 43 ??, 4??  213?, 221?
    # more to discuss.
    for i in [5,14,15,24,44,72,75,76,213,221]:
        idx = np.where(asegd == i)
        csfB[idx] = 1
    
    # do not remove the subthalamic nucleus for now from the wm mask
    # 23, 60
    # would stop the fiber going to the segmented "brainstem"
        
    # grey nuclei, either with or without erosion
    gr_ncl = np.zeros( asegd.shape )
    
    # with erosion
    for i in [10,11,12,49,50,51]:
        idx = np.where(asegd == i)
        # temporary volume
        tmp = np.zeros( asegd.shape )
        tmp[idx] = 1
        tmp = imerode(tmp,se)
        idx = np.where(tmp == 1)
        gr_ncl[idx] = 1
        
    # without erosion
    for i in [13,17,18,26,52,53,54,58]:
        idx = np.where(asegd == i)
        gr_ncl[idx] = 1

    # remove remaining structure, e.g. brainstem
    remaining = np.zeros( asegd.shape )
    idx = np.where( asegd == 16 )
    remaining[idx] = 1
    
    # now remove all the structures from the white matter
    idx = np.where( (csfA != 0) | (csfB != 0) | (gr_ncl != 0) | (remaining != 0) )
    wmmask[idx] = 0
    log.info("Removing lateral ventricles and eroded grey nuclei and brainstem from white matter mask")
    
    # ADD voxels from 'cc_unknown.nii' dataset
    ccun = ni.load(op.join(fs_dir, 'label', 'cc_unknown.nii'))
    ccund = ccun.get_data()
    idx = np.where(ccund != 0)
    log.info("Add corpus callosum and unknown to wm mask")
    wmmask[idx] = 1
    # XXX add unknown dilation for connecting corpus callosum?
#    se2R = zeros(15,3,3); se2R(8:end,2,2)=1;
#    se2L = zeros(15,3,3); se2L(1:8,2,2)=1;
#    temp = (cc_unknown.img==1 | cc_unknown.img==2);
#    fsmask.img(imdilate(temp,se2R))    =  1;
#    fsmask.img(imdilate(temp,se2L))    =  1;
#    fsmask.img(cc_unknown.img==3)    =  1;
#    fsmask.img(cc_unknown.img==4)    =  1;
    
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
    
    fs_dir = gconf.get_fs()
    fs_cmd_dir = gconf.get_cmt_fsout()
    reg_path = gconf.get_cmt_tracto_mask()
    
    log.info("Cropping and moving datasets to %s" % reg_path)
    
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


def run(conf):
    """ Run the first mask creation step
    
    Parameters
    ----------
    conf : PipelineConfiguration object
    subject_tuple : tuple, (subject_id, timepoint)
        Process the given subject
        
    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['log'] = gconf.get_logger() 
    start = time()
    
    log.info("ROI_HR_th.nii / fsmask_1mm.nii CREATION")
    log.info("=======================================")
    
    from os import environ
    env = environ
    env['SUBJECTS_DIR'] = gconf.get_subj_dir()
    
    create_annot_label()
    create_roi()
    create_wm_mask()    
    crop_and_move_datasets()
    
    log.info("Module took %s seconds to process." % (time()-start))

    if not len(gconf.emailnotify) == 0:
        msg = "Mask creation module finished!\nIt took %s seconds." % int(time()-start)
        send_email_notification(msg, gconf.emailnotify, log)  


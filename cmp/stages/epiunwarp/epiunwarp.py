# Copyright (C) 2009-2011, Ecole Polytechnique Federale de Lausanne (EPFL) and
# Hospital Center and University of Lausanne (UNIL-CHUV), Switzerland
# All rights reserved.
#
# Author: code@oscaresteban.es (Oscar Esteban)
# Date: 07/23/2012
# Version: 1.0 (functional prototype)
# Description: This file implments the needed routines to apply distortion
#              correction to EPI imaging.
# TODO List: The module works ad hoc, it is needed to include the appropriate
#            DICOM conversion options, and to agree on a naming convention
#            for connecting the stage into the pipeline
#
# This file is implemented basically adapting the existing script epiunwarp4.fsl
#
#
# This software is distributed under the open-source license Modified BSD.

import os, os.path as op
from glob import glob
import subprocess
import sys
from time import time
import shutil
from ...logme import *
from cmp.util import reorient
import nibabel as ni
import numpy as np
import numpy.ma as ma
import math


def prepare_input( isComplex=False ):
    mag_name = op.join( gconf.get_epiunwarp(), 'magnitude.nii.gz' ) 
    if isComplex:
        out1_name = op.join(gconf.get_epiunwarp(), 'fieldmap_cmplx1.nii.gz')
        out2_name = op.join(gconf.get_epiunwarp(), 'fieldmap_cmplx2.nii.gz')
        cmd_cplx1 = 'fslcomplex -complex %s %s %s' % ( real1 , img1 , out1_name) # Construct complex of 1st echo
        runCmd( cmd_cplx1, log )
        cmd_cplx2 = 'fslcomplex -complex %s %s %s' % ( real2 , img2 , out2_name) # Construct complex of 2nd echo
        runCmd( cmd_cplx2, log )
        cmd_mag = 'fslcomplex -realabs %s %s' % ( out1_name, mag_name ) # Construct mag from 1st echo
	runCmd( cmd_mag, log )
    else:
	cmd_mag = 'fslroi %s %s 0 1' % ( op.join( gconf.get_nifti(), 'Fieldmap_magnitude.nii.gz' ), mag_name )
        runCmd( cmd_mag,log ) # Keep only the first frame from mag
        


def extract_epi():
    """ Extract the reference volume from EPI image,
        fMRI: middle time point
        DWI: B0
    """
    log.info( "Extracting time point for the example func..." )
    return op.join(gconf.get_epiunwarp(), 'DTI_000.nii.gz' )

def mask_brain():
    """ Create brain mask from the magnitude    """
    log.info( "Extracting brain from magnitude volume..." )
    outname =  op.join(gconf.get_epiunwarp(), 'mask.nii.gz')
    mag_name = op.join( gconf.get_epiunwarp(), 'magnitude.nii.gz' ) 
    bet_cmd = 'bet %s %s' % ( mag_name , outname )
    runCmd( bet_cmd, log )
    bin_cmd = 'mri_binarize --i %s --o %s --min 0.001' % ( outname, outname )
    runCmd( bin_cmd, log )
    log.info( "Brain extracted. Dilating brain mask..." )
    dil_cmd = 'fslmaths %s -bin %s' % ( outname, outname )
    for i in range(0,3):
	runCmd( dil_cmd, log )

def phase_unwrap( isComplex=False ):
    """ Execute PRELUDE for phase unwarping """   
    mask_name=( op.join(gconf.get_epiunwarp(), 'mask.nii.gz') )
    if isComplex:
	log.info( "Unwarping phase (phase of 2 echoes)" )
	epi_cmd_fmt = 'prelude -c %s -o %s -f -v -m %s' 
	runCmd( epi_cmd_fmt % ( fm_cmpx_name, ph1_name, mask_name ) , log )
	runCmd( epi_cmd_fmt % ( fm_cmpx_name, ph2_name, mask_name ) , log )
	# load ph1_nii, ph2_nii
    else:
	phd_nii = ni.load( op.join(gconf.get_nifti(), 'Fieldmap_phasediff.nii.gz') )
	# Rescale the delta phase to be -pi and pi
        # Make sure the phase is float precision
	phasediffdata = np.array( phd_nii.get_data().reshape(-1), dtype=float)
	phd_min = np.min(phasediffdata)
	phd_max = np.max(phasediffdata)
	A = (2*math.pi) / (phd_max-phd_min)  
	B = math.pi - ( A * phd_max )
	phddata_norm =  phasediffdata * A + B
	# Save file
        ph_norm_nii = ni.Nifti1Image( phddata_norm.reshape( phd_nii.get_shape() ), phd_nii.get_affine(), phd_nii.get_header() )
	phd_norm_name = op.join(gconf.get_epiunwarp(), 'phasediff_2pi.nii.gz')
	ni.save( ph_norm_nii, phd_norm_name )	

        log.info( "Unwarping phase (phase of echo diff)" )
        mag_name=op.join(gconf.get_epiunwarp(), 'magnitude.nii.gz')
        phd_prelude_name=op.join(gconf.get_epiunwarp(), 'phase_prelude.nii.gz') 
	runCmd( 'prelude -p %s -a %s -o %s -f -v -m %s' % ( phd_norm_name, mag_name, phd_prelude_name, mask_name ) , log )
	# Load ph1_nii
	ph1_nii = ni.load( phd_prelude_name )
	# Create a fake ph2_nii
	dumb_img = np.zeros( ph1_nii.get_shape() )
	ph2_nii = ni.Nifti1Image( dumb_img, ph1_nii.get_affine(), ph1_nii.get_header() )
    # Finally merge components
    out_nii = ni.funcs.concat_images( ( ph1_nii , ph2_nii ) )
    ni.save( out_nii, op.join(gconf.get_epiunwarp(), 'phase_unwrapped.nii.gz') )

def create_vsm( tediff, esp, sigmamm = 0.0 ):
    """ Create the voxel shift map (vsm) in the mag/phase space. use mag as input
        to assure that vsm is same dimension as mag. The input only affects the output dimension.
        The content of the input has no effect on the vsm. The de-warped mag volume is
        meaningless and will be thrown away
    """
    mask_name=( op.join(gconf.get_epiunwarp(), 'mask.nii.gz') )
    mag_name=( op.join(gconf.get_epiunwarp(), 'magnitude.nii.gz') )
    magdw_name=( op.join(gconf.get_epiunwarp(), 'magdw.nii.gz') )
    ph_name=( op.join(gconf.get_epiunwarp(), 'phase_unwrapped.nii.gz') )
    vsmmag_name=( op.join(gconf.get_epiunwarp(), 'vsmmag.nii.gz') )

    vsm_cmd = 'fugue -i %s -u %s -p %s --dwell=%s --asym=%s --mask=%s --saveshift=%s' % ( mag_name, magdw_name, ph_name, esp, tediff, mask_name, vsmmag_name)

    if( sigmamm > 0.0 ):
	vsm_cmd = '%s --smooth2=%s' % ( vsm_cmd, sigmamm )

    runCmd( vsm_cmd, log )

    vsmmag_nii = ni.load( vsmmag_name ) #load vsmmag_nii
    vsmmag_data = vsmmag_nii.get_data()
    mask_data = ni.load( mask_name ).get_data()
    vsmmag_data[ mask_data==0 ] = 0
    vsmmag_masked = ma.masked_values( vsmmag_nii.get_data().reshape(-1), 0.0 )
    print vsmmag_masked.mean()
    vsmmag_masked = vsmmag_masked - vsmmag_masked.mean() # Remove the mean in-brain shift from VSM
    # save
    vsmmag_nii._data = vsmmag_masked.reshape( vsmmag_nii.get_shape() )
    ni.save( vsmmag_nii, op.join(gconf.get_epiunwarp(), 'vsmmag_meancorrected.nii.gz')  )


def register_to_epi():
    """ Register magfw to example epi. There are some parameters here that may need to be tweaked. Should probably strip the mag
        Pre-condition: forward warp the mag in order to reg with func. What does mask do here?
    """
    mag_name=( op.join(gconf.get_epiunwarp(), 'magnitude.nii.gz') )
    magfw_name=( op.join(gconf.get_epiunwarp(), 'magfw.nii.gz') )
    vsmmag_name=( op.join(gconf.get_epiunwarp(), 'vsmmag.nii.gz') )
    mask_name=( op.join(gconf.get_epiunwarp(), 'mask.nii.gz') )
    magfw_out=( op.join(gconf.get_epiunwarp(), 'magfw_reg.nii.gz') )
    magfw_mat_out=( op.join(gconf.get_epiunwarp(), 'magfw_reg.mat') ) 
    runCmd( 'fugue -i %s -w %s --loadshift=%s --mask=%s' % ( mag_name, magfw_name, vsmmag_name, mask_name ), log ) # Forward Map
    ref_epi = extract_epi()
    reg_cmd='flirt -in %s -ref %s -out %s -omat %s -bins 256 -cost corratio -searchrx -10 10 -searchry -10 10 -searchrz -10 10 -dof 6 -interp trilinear' % ( magfw_name, ref_epi, magfw_out, magfw_mat_out )
    runCmd( reg_cmd, log )
    """ Resample VSM and brain mask into epi space """
    runCmd( 'cp %s %s' % (vsmmag_name, op.join(gconf.get_epiunwarp(), 'vsmmag.bak.nii.gz') ), log )
    runCmd( 'cp %s %s' % (mask_name, op.join(gconf.get_epiunwarp(), 'mask.bak.nii.gz')), log )
    res_cmd= 'flirt -in %s -ref %s -out %s -init %s -applyxfm' % ( vsmmag_name, ref_epi, vsmmag_name, magfw_mat_out )
    runCmd( res_cmd, log )
    res_cmd= 'flirt -in %s -ref %s -out %s -init %s -applyxfm' % ( mask_name, ref_epi, mask_name, magfw_mat_out )
    runCmd( res_cmd, log )

def fugue_exf():
    dexf_cmd='fugue -i %s -u %s --loadshift=%s --mask=%s' % ( exf, exfdw, vsm, mask_res )
    runCmd( dexf_cmd, log )


def fugue_epi():
    vsm_name = op.join(gconf.get_epiunwarp(), 'vsmmag_meancorrected.nii.gz') 
    mask_name=( op.join(gconf.get_epiunwarp(), 'mask.nii.gz') )
    out_name= ( op.join(gconf.get_nifti(), 'epi_unwarped.nii.gz' ) )

    # Split volumes
    epi_nii = ni.load( op.join(gconf.get_nifti(), 'DTI.nii.gz') )
    vols = ni.funcs.four_to_three( epi_nii )


    i = 0
    out_vols = [ ]
    for vol in vols:
	vol_name = op.join(gconf.get_epiunwarp(), 'DTI_%03d.nii.gz' % i ) 
	out_vol_name = op.join(gconf.get_epiunwarp(), 'DTI_unwarp_%03d.nii.gz' % i ) 
        ni.save( vol, vol_name )
    	# Execute fugue
	fugue_cmd='fugue -i %s -u %s --loadshift=%s --mask=%s' % ( vol_name, out_vol_name, vsm_name, mask_name )
   	runCmd( fugue_cmd, log )
#	out_vols.append( ni.load( out_vol_name )  )
	i = i+1 

    # Merge back
    merge_cmd='fslmerge -t %s `ls %s`' % ( out_name, op.join( gconf.get_epiunwarp(), 'DTI_unwarp_*.nii.gz' ) )
    runCmd( merge_cmd, log )
#    final_nii = ni.funcs.concat_images( out_vols )
#    ni.save( final_nii, out_name )
	
	
    
            
def run(conf):
    """ Run the first sequence unwarpping step
    
    Parameters
    ----------
    conf : PipelineConfiguration object
        
    """
    # setting the global configuration variable
    globals()['gconf'] = conf
    globals()['log'] = gconf.get_logger()
    nifti_dir = gconf.get_nifti()


    start = time()
    
    log.info("EPI Sequences unwarpping")
    log.info("=========================")
    
    isFMRI = False    # TODO: check if fMRI
    isComplex = False # TODO: check if fieldmap is complex
    reverseEncode = 1.0
    if gconf.rev_enc_dir_param:
       reverseEncode = -1.0
    
    prepare_input( isComplex )
    mask_brain()
    phase_unwrap( isComplex )
    create_vsm( gconf.tediff_param, reverseEncode * gconf.esp_param, gconf.sigma_param )

    if gconf.reg_epi_param:
       register_to_epi()

    if( isFMRI ):
	    fugue_exf()

    fugue_epi()
    
    log.info("Module took %s seconds to process." % (time()-start))

    if not len(gconf.emailnotify) == 0: 
        msg = ["EPI unwarp", int(time()-start)]
        send_email_notification(msg, gconf, log)    
        
def declare_inputs(conf):
    """Declare the inputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)

    nifti_dir = conf.get_nifti()
    conf.pipeline_status.AddStageInput(stage, nifti_dir, 'DSI.nii.gz', 'dsi-nii-gz')
    conf.pipeline_status.AddStageInput(stage, nifti_dir, 'Fieldmap_magnitude.nii.gz', 'Fieldmap-magnitude-nii-gz')
    conf.pipeline_status.AddStageInput(stage, nifti_dir, 'Fieldmap_phasediff.nii.gz', 'Fieldmap-phasediff-nii-gz')

    
def declare_outputs(conf):
    """Declare the outputs to the stage to the PipelineStatus object"""
    
    stage = conf.pipeline_status.GetStage(__name__)

    nifti_dir = conf.get_nifti()
    conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'epi_unwarped.nii.gz', 'epi-unwarped-nii.-gz')
    #conf.pipeline_status.AddStageOutput(stage, nifti_dir, 'Diffusion_b0_corrected.nii.gz', 'diffusion-resampled-nii.-gz')      

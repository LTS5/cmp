#!/bin/bash
#
##### map_connectome.sh ############
##
#1) Preparation
export MY_MATLAB='matlab -nosplash -nodesktop -r '
export MY_SUBJECT=$1
export RAW_DIFFUSION=$2
export RAW_T1=$3
cd $CMT_SUBJECTS_DIR/$MY_SUBJECT

#10) Convert DSI dicom into analyze  
cd $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion
diff_unpack $RAW_DIFFUSION $MY_SUBJECT -split
$MY_MATLAB "cv_dicom2analyze_iso_2mm_qball([getenv('CMT_SUBJECTS_DIR'),'/',getenv('MY_SUBJECT'),'/raw_diffusion'],[getenv('MY_SUBJECT'),'.nii'],[getenv('CMT_SUBJECTS_DIR'),'/',getenv('MY_SUBJECT'),'/raw_diffusion/iso']);exit;"

#11) compute odf map
hardi_mat $CMT_SUBJECTS_DIR/gradient_qball.txt $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion/iso/temp_mat.dat -ref $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion/iso/*_000.hdr -iop 1 0 0 0 1 0 -oc 
odf_recon $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion/iso/*_000.hdr 257 181 $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion/iso/$MY_SUBJECT -b0 1 -iop 1 0 0 0 1 0  -mat  $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion/iso/temp_mat.dat -nt -p 3 -sn 0 -ot nii

#12) Run tractography 
mri_convert -odt float -vs 2 2 2 $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_T1/${MY_SUBJECT}_T1_registred.nii.gz \
           $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion/iso/${MY_SUBJECT}_T1_resampled.nii 
$MY_MATLAB "MY_SUBJECT=getenv('MY_SUBJECT');script_tracto_qball;exit;"

#13) Create connection matrices 
$MY_MATLAB "MY_SUBJECT=getenv('MY_SUBJECT');script_connection_matrix;exit;"

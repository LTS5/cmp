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

#2) Prepare and register data
prep_register.sh $MY_SUBJECT $RAW_DIFFUSION $RAW_T1 'x -y -z'

#3) Run Freesurfer recon-all 
#recon-all -s $MY_SUBJECT -all -notal-check -no-isrunning

#4) Create the cortical labels necessary for our ROIs   
#create_annot_label.sh $MY_SUBJECT

#5) Create the ROIs 
#$MY_MATLAB "roi_creation(getenv('MY_SUBJECT'));exit"

#6) Convert stuff into left-posterior-inferior referential 
#convert2lpi.sh $MY_SUBJECT

#7) Reorganize stuff 
#reorganize_stuff.sh $MY_SUBJECT

#8) Create final ROI mask, cortex and deep gray structures  
$MY_MATLAB "roi_merge(getenv('MY_SUBJECT'));exit"

#9) Finalize white matter mask 
$MY_MATLAB "mask_creation(getenv('MY_SUBJECT'));exit"

#9b) Finalize ROI mask
$MY_MATLAB "script_roi_finalize;exit"

#10) Convert DTI dicom into analyze  
#cd $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion

#diff_unpack $RAW_DIFFUSION $MY_SUBJECT -split

#$MY_MATLAB "cv_dicom2analyze_iso_2mm_dti_HUG([getenv('CMT_SUBJECTS_DIR'),'/',getenv('MY_SUBJECT'),'/raw_diffusion'],[getenv('MY_SUBJECT'),'.nii'],[getenv('CMT_SUBJECTS_DIR'),'/',getenv('MY_SUBJECT'),'/raw_diffusion/iso']);exit;"

#11) compute odf map
#dti_recon $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion/iso/*_000.hdr $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion/iso/$MY_SUBJECT -gm  $DTI_PATH/dti_30_gradient.txt -b 1000 -b0 1 -iop 1 0 0 0 1 0 -oc -p 3 -sn 0 -ot nii

#12) Run tractography 
#mri_convert -odt float -vs 2 2 2 $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_T1/${MY_SUBJECT}_T1_registred.nii.gz \
            $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion/iso/${MY_SUBJECT}_T1_resampled.nii 
#$MY_MATLAB "MY_SUBJECT=getenv('MY_SUBJECT');script_tracto_dti_HUG;exit;"

#13) Create connection matrices 
$MY_MATLAB "MY_SUBJECT=getenv('MY_SUBJECT');script_connection_matrix;exit;"


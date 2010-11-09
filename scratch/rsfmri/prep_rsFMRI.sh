#!/bin/bash

MY_SUBJECT=$1
RAW_RSFMRI=$2
cd $CMT_SUBJECTS_DIR/$MY_SUBJECT/rsFMRI
mkdir registered
mkdir nifti

# convert fmri dicom into individual nifti
mri_convert $RAW_RSFMRI -ot nii ${MY_SUBJECT}_rsFMRI.nii
fslsplit ${MY_SUBJECT}_rsFMRI.nii ./nifti/${MY_SUBJECT}_rsFMRI
rm -f ${MY_SUBJECT}_rsFMRI.nii

# if temporal interolation needed to be put here.

# calculate transformation
cd $CMT_SUBJECTS_DIR/$MY_SUBJECT/rsFMRI/nifti
flirt -in ${MY_SUBJECT}_rsFMRI0000.nii.gz -ref $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion/${MY_SUBJECT}_b0_resampled.nii.gz -omat transformation.mat -dof 6

# apply registration
for f in `ls *.nii.gz`
do
 echo $f
flirt -in $f -ref $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion/${MY_SUBJECT}_b0_resampled.nii.gz -applyxfm -init transformation.mat -out ../registered/${f:0:${#f}-7}_reg.nii.gz
done

cd $CMT_SUBJECTS_DIR/$MY_SUBJECT/rsFMRI/registered
for f in `ls *.nii.gz`
do
 echo $f
fslswapdim $f x -y z ${f:0:${#f}-7}_lpi.nii.gz
fslchfiletype ANALYZE ${f:0:${#f}-7}_lpi.nii.gz
done

rm -f *.nii.gz
rm -rf ../nifti





for DTI:

In the classical pipeline, after the use of dtk, we used a script called script_tracto.m to convert the data and launch tractography. For DTI, I created a script_tracto_dti.m, which is basically identical to the classical one, but that calls cv_dtk2matlab_dti.m instead of the classical cv_dtk2matlab.m to convert the data. This script reads the tensor volume created by dtk and copy the data in a stixv structure. To read the tensor, the script uses the function cv_niftii2vv.m (vv stands for vector volume... ^^)

for QBALL:

you only need to use hardi_mat instead of dti_recon, something similar to this:

hardi_mat $CMT_SUBJECTS_DIR/gradient_qball.txt $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion/iso/temp_mat.dat -ref $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion/iso/*_000.hdr -iop 1 0 0 0 1 0 -oc 
odf_recon $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion/iso/*_000.hdr 257 181 $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion/iso/$MY_SUBJECT -b0 1 -iop 1 0 0 0 1 0  -mat  $CMT_SUBJECTS_DIR/$MY_SUBJECT/raw_diffusion/iso/temp_mat.dat -nt -p 3 -sn 0 -ot nii

then, the same as for DTI, you need to use script_tracto_qball.m, which calls in turn cv_dtk2matlab_qball, which is identical to the classical cv_dtk2matlab.m (i think the only exception is one scalar map that is not loaded because not available for QBI). 


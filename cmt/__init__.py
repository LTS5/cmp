# PREPROCESSING
import modules.preprocessing.organize as preprocessing

# DICOM CONVERTER
import modules.converter.dicomconverter as dicomconverter

# REGISTRATION
import modules.registration.registration as registration

# FREESURFER
import modules.freesurfer.freesurfer as freesurfer

# MASK: ROI_HR_th.nii / fsmask_1mm.nii CREATION
import modules.mask.maskcreation as maskcreation

# DIFFUSION TOOLKIT
import modules.diffusion.dtk as diffusion

# REGISTRATION: Apply registration ROI/WM --> b0
import modules.registration.apply_registration as apply_registration

# TRACTOGRAPHY
import modules.tractography.tractography as tractography

# FIBER FILTERING
import modules.postpressing.fiberfiltering as fiberfiltering

# FIBER CLUSTERING
import modules.postpressing.fiberclustering as fiberclustering

# CONNECTION MATRIX
import modules.connectionmatrix.step7 as connectionmatrix

# CFF CONVERTER
import modules.converter.cffconverter as cffconverter

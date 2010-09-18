# 0. DICOM CONVERTER
import modules.converter.raw_step0 as dicomconverter

# 1. REGISTRATION
import modules.registration.raw_step1 as registration

# 2. FREESURFER
import modules.freesurfer.raw_step2 as freesurfer

# 3. MASK: ROI_HR_th.nii / fsmask_1mm.nii CREATION (MASKCREATION)
#import modules.mask.raw_step3 as maskcreation

# 4. DIFFUSION TOOLKIT
import modules.diffusion.raw_step4 as diffusion

# 5. REGISTRATION: Apply registration ROI/WM --> b0
import modules.registration.raw_step5 as data_registration

# 6. TRACTOGRAPHY
import modules.tractography.raw_step6 as tractography

# 7. CONNECTION MATRIX
#import modules.connectionmatrix.raw_step7 as connectionmatrix

# 8. CFF CONVERTER
import modules.converter.raw_step8 as cffconverter

# 0. DICOM CONVERTER
import modules.converter.step0 as dicomconverter

# 1. REGISTRATION
import modules.registration.step1 as registration

# 2. FREESURFER
import modules.freesurfer.step2 as freesurfer

# 3. MASK: ROI_HR_th.nii / fsmask_1mm.nii CREATION (MASKCREATION)
#import modules.mask.step3 as maskcreation

# 4. DIFFUSION TOOLKIT
import modules.diffusion.step4 as diffusion

# 5. REGISTRATION: Apply registration ROI/WM --> b0
import modules.registration.step5 as apply_registration

# 6. TRACTOGRAPHY
import modules.tractography.step6 as tractography

# 7. CONNECTION MATRIX
#import modules.connectionmatrix.step7 as connectionmatrix

# 8. CFF CONVERTER
import modules.converter.step8 as cffconverter

# 1. REGISTRATION
#import registration.raw_step1 as registration

# 2. FREESURFER
import freesurfer.raw_step2 as freesurfer

# 3. MASK: ROI_HR_th.nii / fsmask_1mm.nii CREATION (MASKCREATION)
#import mask.raw_step3 as maskcreation

# 4. DIFFUSION TOOLKIT
import diffusion.raw_step4 as diffusion

# 5. REGISTRATION: Apply registration ROI/WM --> b0
#import registration.raw_step5 as freesurfer_registration

# 6. TRACTOGRAPHY
import tractography.raw_step6 as tractography

# 7. CONNECTION MATRIX
#import connectionmatrix.raw_step7 as connectionmatrix

# 8. CONVERTER
import converter.raw_step8 as cffconverter

import nibabel as nib
import numpy as np

# convert
fname = '/home/stephan/dev/cmp_test/project01/control01/tp1_run3/FREESURFER/mri/aparc+aseg.mgz'
fout = '/home/stephan/dev/cmp_test/project01/control01/tp1_run3/FREESURFER/mri/aparc+aseg.nii.gz'
# mri_convert aparc+aseg.mgz aparc+aseg.nii.gz
WMout = '/home/stephan/dev/cmp_test/project01/control01/tp1_run3/FREESURFER/mri/WM.nii.gz'


#%% label mapping
#%  -------------
#CORTICAL{1} = [ 1  2  3  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34];
#CORTICAL{2} = [31 13  9 21 27 25 19 29 15 23  1 24  4 30 26 11  6  2  5 22 16 14 10 20 12  7  8 18 30 17  3 28 33];

CORTICAL = {1 : [ 1, 2, 3,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34],
            2 : [31,13, 9,21,27,25,19,29,15,23, 1,24, 4,30,26,11, 6, 2, 5,22,16,14,10,20,12, 7, 8,18,30,17, 3,28,33]}

#SUBCORTICAL{1} = [48 49 50 51 52 53 54 58 59 60    9 10 11 12 13 17 18 26 27 28];
#SUBCORTICAL{2} = [34 34 35 36 37 40 41 38 39 39   75 75 76 77 78 81 82 79 80 80];

SUBCORTICAL = {1:[48,49,50,51,52,53,54,58,59,60,   9,10,11,12,13,17,18,26,27,28],
               2:[34,34,35,36,37,40,41,38,39,39,  75,75,76,77,78,81,82,79,80,80]}

#OTHER{1} = [16 251 252 253 254 255 86 1004 2004];
#OTHER{2} = [83  84  84  84  84  84 84   84   84];

OTHER = {1:[16,251,252,253,254,255,86,1004,2004],
         2:[83, 84, 84, 84, 84,  84, 84,   84,   84]}

#WM = [2 29 32 41 61 64 77:86 100:117 155:158 195:196 199:200 203:204 212 219 223 250:255];

WM = [2, 29, 32, 41, 61, 64] +  range(77,86+1) + range(100, 117+1) + range(155,158+1) + range(195,196+1) + range(199,200+1) + range(203,204+1) + [212, 219, 223] + range(250,255+1)


#%% create WM mask
#%  --------------
#niiWM = niiAPARC;
#niiWM.hdr.dime.datatype = 2; % uint8
#niiWM.hdr.dime.bitpix   = 8;
#niiWM.img = uint8( niiAPARC.img .* 0 );

niiAPARCimg = nib.load(fout)
niiAPARCdata = niiAPARCimg.get_data()

niiWM = np.zeros( niiAPARCdata.shape, dtype = np.uint8 )

#% labels given by Cristina
#for i = 1:length(WM)
#    niiWM.img( niiAPARC.img == WM(i) ) = 1;
#end
#
for i in WM:
     niiWM[niiAPARCdata == i] = 1
#    
#
#% we include SUBCORTICAL ROIs to WM as well...
#for i = 1:length(SUBCORTICAL{1})
#    niiWM.img( niiAPARC.img == SUBCORTICAL{1}(i) ) = 1;
#end

for i in SUBCORTICAL[1]:
     niiWM[niiAPARCdata == i] = 1
     
img = nib.Nifti1Image(niiWM, niiAPARCimg.get_affine(), niiAPARCimg.get_header())
nib.save(img, WMout)

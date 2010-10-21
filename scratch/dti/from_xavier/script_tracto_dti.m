% STEP D4 : Nifti -> Matlab STIXV
cd([getenv('CMT_SUBJECTS_DIR'),'/',MY_SUBJECT,'/raw_diffusion/iso']);
pwd
load dirlist
[adc,b0,dwi,fa,stixv,t1] = cv_dtk2matlab_dti(MY_SUBJECT,dirlist);

save stixv stixv
save scalars adc b0 dwi fa t1
load hdr
%%cv_sv2analyze('b0',hdr,b0,'b');

% STEP A1 : Dicom -> T1 analyze
%%[t1]=cv_dicom2t1('...');
%%load t1_hdr
%%cv_sv2analyze('t1',hdr,t1,'b');

% STEP T1 : Tractography streamline
%load stixv                                                                  % load data
[wm,hdr]=cv_analyze2sv([getenv('CMT_SUBJECTS_DIR'),'/',MY_SUBJECT,'/fs_output/registred/HR/fsmask_1mm'],'b');                                    % 
% add one slice at top and bottom
sz=size(wm.data) % volume size in 1 mm isotropic voxels.
stixv.data=cat( 3, cell(sz(1)/2,sz(2)/2), stixv.data, cell(sz(1)/2,sz(2)/2) );
wm.data=cat( 3, zeros(sz(1),sz(2),2), wm.data, zeros(sz(1),sz(2),2) ); 
adc.data=cat( 3, zeros(sz(1)/2,sz(2)/2), adc.data, zeros(sz(1)/2,sz(2)/2) );          %
fa.data=cat( 3, zeros(sz(1)/2,sz(2)/2), fa.data, zeros(sz(1)/2,sz(2)/2) );          %
t1.data=cat( 3, zeros(sz(1)/2,sz(2)/2), t1.data, zeros(sz(1)/2,sz(2)/2) );          %
wm.data(wm.data==-1)=1;   

cd([getenv('CMT_SUBJECTS_DIR'),'/',MY_SUBJECT,'/raw_diffusion/']);
mkdir fibers
cd fibers
cv_wholebrainsimul_stixv(stixv,wm,1000,4,'fa',fa,'adc',adc,'t1',t1);                % start the tractography

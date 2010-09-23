% STEP D4 : Nifti -> Matlab STIXV
cd([getenv('CMT_SUBJECTS_DIR'),'/',MY_SUBJECT,'/raw_diffusion/iso']);
pwd

%loading gradient list Siemens 30 directions
load gradlist

%transforming DTK data into matlab (considering TV as an SITXV)
[adc,b0,dwi,fa,stixv,t1] = cv_dtk2matlab_dti_HUG(MY_SUBJECT,grad_list31);

save stixv stixv
save scalars adc b0 dwi fa t1

%loading header for HUG data
load hdr_hug
hdr=hdr_hug;
%%cv_sv2analyze('b0',hdr,b0,'b');

% STEP A1 : Dicom -> T1 analyze
%%[t1]=cv_dicom2t1('...');
%%load t1_hdr
%%cv_sv2analyze('t1',hdr,t1,'b');

% STEP T1 : Tractography streamline
%load stixv                                                                  % load data
[wm,hdr]=cv_analyze2sv([getenv('CMT_SUBJECTS_DIR'),'/',MY_SUBJECT,'/fs_output/registred/HR/fsmask_1mm'],'l');   
                                 % 
% add one slice at top and bottom
sz=size(wm.data) % volume size in 1 mm isotropic voxels.
stixv.data=cat( 3, cell(sz(1)/2,sz(2)/2), stixv.data, cell(sz(1)/2,sz(2)/2) );
wm.data=cat( 3, zeros(sz(1),sz(2),2), wm.data, zeros(sz(1),sz(2),2) ); 
adc.data=cat( 3, zeros(sz(1)/2,sz(2)/2), adc.data, zeros(sz(1)/2,sz(2)/2) );          %
fa.data=cat( 3, zeros(sz(1)/2,sz(2)/2), fa.data, zeros(sz(1)/2,sz(2)/2) );          %

% Eliminer derniere slice
% generalment on n'enleve jamais la premiere slice...c plutot la derniere

sz_t1=size(t1.data)
if(sz_t1(1)>sz(1)/2)
    t1.data=t1.data(1:sz(1)/2,:,:);    % eliminer slice y = 111
end

if(sz_t1(2)>sz(2)/2)
    t1.data=t1.data(:,1:sz(2)/2,:);    % eliminer slice y = 111
end

t1.data=cat( 3, zeros(sz(1)/2,sz(2)/2), t1.data, zeros(sz(1)/2,sz(2)/2) );          %
wm.data(wm.data==-1)=1;   

cd([getenv('CMT_SUBJECTS_DIR'),'/',MY_SUBJECT,'/raw_diffusion/']);
mkdir fibers
cd fibers
cv_wholebrainsimul_stixv(stixv,wm,1000,4,'fa',fa,'adc',adc,'t1',t1);                % start the tractography

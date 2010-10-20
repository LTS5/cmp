function mask_creation( MY_SUBJECT,MY_TP )
DATA_path = getenv('DATA_path');


%% START copying the WHITE MATTER voxels from 'ribbon.nii' dataset
cd([DATA_path,'/',MY_SUBJECT,'/',MY_TP,'/4__CMT/fs_output/registred/HR/']);

fsmask = load_untouch_nii( 'ribbon.nii' );

temp = fsmask.img;

fsmask.img=fsmask.img.*0;
fsmask.img( temp==120 ) =  1;
fsmask.img( temp==20 )  =  1; % AT THIS STAGE FSMASK IS A MASK OF WHITE MATTER
clear temp

%% REMOVE voxels from csfA, csfB, gr_ncl and remaining structures from 'aseg.nii' dataset
aseg = load_untouch_nii( 'aseg.nii' ); % ASEG IS THE SEGMENTED BRAIN


% sofisticated ventricle erosion
se1 = zeros(3,3,5); se1(2,:,3)=1; se1(:,2,3)=1; se1(2,2,:)=1;
se  = zeros(3,3,3); se(2,:,2)=1;se(:,2,2)=1;se(2,2,:)=1;

csfA = aseg;		csfA.img=csfA.img.*0;
csfA.img(aseg.img==4|aseg.img==43|aseg.img==11|aseg.img==50|aseg.img==31|aseg.img==63|aseg.img==10|aseg.img==49) = 1; % THIS IS WHAT WE CONSIDER LATERAL WENTRICLES, THALAMUS PROPER AND CAUDATE ARE TEMPORARILY INCLUDED FOR BETTER EROSION, LATER THEY ARE BUT BACK
csfA.img = imerode(imerode(csfA.img,se1),se); % WE REDUCE WENTRICULAR SIZE BY EROSION TO HAVE MORE WHITE MATTER; SE AND SE1 ARE THE STRUCTURING ELEMENTS OF THE EROSION
temp=(aseg.img==11|aseg.img==50|aseg.img==10|aseg.img==49);
csfA.img(temp)=0; % THALAMUS PROPER AND CAUDATE ARE PUT BACK TO ZERO SINCE DO NOT BELONG TO LATERAL VENTRICLES

csfB = aseg;		csfB.img=csfB.img.*0;
csfB.img(aseg.img==5|aseg.img==14|aseg.img==15|aseg.img==24|aseg.img==44|aseg.img==72|aseg.img==75|aseg.img==76|aseg.img==213|aseg.img==221) = 1; % THIS IS THE REST CSF, IE 3RD AND 4TH VENTRICULE AND EXTRACEREBRAL CSF


% NB: these erosions need to be matched to cmx_merge_ROI_rh_lh_level_br_str.m

% some special preparation for stn % THE FOLLOWING IS A WAY TO REDUCE THE
% SIZE OF THE SUBTHALAMIC NUCLEUS. IF THIS NUCLEUS IS TOO BIG THE
% CORTICO-SPINAL TRACT CANNOT BE MAPPED WELL AND STOPS INACCURATELY IN THE
% SUBTHALAMUS. IF YOU FIND A SIMPLER WAY TO DIMINISH THIS STRUCTURE SIZE
% PLEASE GO AHEAD. BUT THIS REQUIRE SOME EXPERIMENTATION.
subthal_left = aseg;
subthal_left.img = subthal_left.img.*0;
subthal_left.img(aseg.img==28) = 28;
temp=sum(sum(subthal_left.img));
z_max=max(find(temp>0));
z_min=min(find(temp>0));
subthal_left.img(:,:,1:(ceil(z_min+(z_max-z_min)/2))) = 0;
% subthal_left.img=imerode(imerode(subthal_left.img,se),se);
subthal_left.img=imerode(subthal_left.img,se);

subthal_right = aseg;
subthal_right.img = subthal_right.img.*0;
subthal_right.img(aseg.img==60) = 60;
temp=sum(sum(subthal_right.img));
z_max=max(find(temp>0));
z_min=min(find(temp>0));
subthal_right.img(:,:,1:(ceil(z_min+(z_max-z_min)/2))) = 0;
% subthal_right.img=imerode(imerode(subthal_right.img,se),se);
subthal_right.img=imerode(subthal_right.img,se);

% thalamus, caudate, putamen, pallidum, accumbens, stn, hippocampus,
% amygdala % THESE NUCLEI ARE ALL THE GRAY NUCLEI WE WANT TO CONSIDER, SOME
% ARE ERODED AND SOME NOT.
gr_ncl=aseg;
gr_ncl.img=gr_ncl.img.*0;
% gr_ncl.img(...
% 	imerode(imerode(aseg.img==10,se),se) |...
% 	imerode(imerode(aseg.img==11,se),se) | ...
% 	imerode(imerode(aseg.img==12,se),se) | ...
% 	aseg.img==13 | ...
% 	aseg.img==17 | ...
% 	aseg.img==18 | ...
% 	aseg.img==26 | ...
% 	subthal_left.img==28 | ...
% 	imerode(imerode(aseg.img==49,se),se) | ...
% 	imerode(imerode(aseg.img==50,se),se) | ...
% 	imerode(imerode(aseg.img==51,se),se) | ...
% 	aseg.img==52 | ...
% 	aseg.img==53 | ...
% 	aseg.img==54 | ...
% 	aseg.img==58 | ...
% 	subthal_right.img==60 ...
% ) = 1;
gr_ncl.img(...
	imerode(aseg.img==10,se) |...
	imerode(aseg.img==11,se) | ...
	imerode(aseg.img==12,se) | ...
	aseg.img==13 | ...
	aseg.img==17 | ...
	aseg.img==18 | ...
	aseg.img==26 | ...
	subthal_left.img==28 | ...
	imerode(aseg.img==49,se) | ...
	imerode(aseg.img==50,se) | ...
	imerode(aseg.img==51,se) | ...
	aseg.img==52 | ...
	aseg.img==53 | ...
	aseg.img==54 | ...
	aseg.img==58 | ...
	subthal_right.img==60 ...
) = 1;


% Brain-stem 
remaining = aseg;
remaining.img = remaining.img.*0;
remaining.img( aseg.img==16 ) = 1;
           %!!! be sure acquisition include 16 (BrainStem), if not remove 60 28 as
           %in this commented line aseg.img==60|aseg.img==28


fsmask.img( csfA.img>0 | csfB.img>0 | gr_ncl.img>0 | remaining.img>0 ) = 0; % HERE WE CONSTRUCT THE FINAL WHITE MATTER MASK WHERE ALL THE CSF IN VENTRICLES OR AROUND THE BRAIN, THE GRAY NUCLEI AND BRAIN STEM ARE REMOVED.



%% REMOVE the voxels labeled in 'scale33/ROI_HR_th'
cd([DATA_path,'/',MY_SUBJECT,'/',MY_TP,'/4__CMT/fs_output/registred/HR/scale33/']);
ROIs = load_untouch_nii( 'ROI_HR_th.nii' );
fsmask.img( ROIs.img>0 ) = 0; % JUST MAKE SURE THAT ALL THE VOXELS CLASSIFIED AS ROIS ARE NOT IN THE WHITE MATTER MASK



%% ADD voxels from 'cc_unknown.nii' dataset
cd([DATA_path,'/',MY_SUBJECT,'/',MY_TP,'/4__CMT/fs_output/registred/HR/']);
cc_unknown = load_untouch_nii( 'cc_unknown.nii' );		%1 2 cc (rh lh) 3 4 unknown(rh lh) % VOXELS LABELED AS UNKNOWN ARE STRUCTURES IN CONTINUITY WITH THE CORITICAL ROIS BUT ARE NOT CORTEX. THESE VOXELS SHOULD BE LABELED AS WHITE MATTER. I HAVE ARTIFICIALLY DILATED SOME OF THEM TO EASE TRACTOGRAPHY PARTICULARLY THROUGH CORPUS CALLOSUM.

se2R = zeros(15,3,3); se2R(8:end,2,2)=1;
se2L = zeros(15,3,3); se2L(1:8,2,2)=1;

temp = (cc_unknown.img==1 | cc_unknown.img==2);
fsmask.img(imdilate(temp,se2R))	=  1;
fsmask.img(imdilate(temp,se2L))	=  1;
fsmask.img(cc_unknown.img==3)	=  1;
fsmask.img(cc_unknown.img==4)	=  1;


%% SAVE the finale 'fsmask_1mm' dataset
cd([DATA_path,'/',MY_SUBJECT,'/',MY_TP,'/4__CMT/fs_output/registred/HR/']);
save_untouch_nii( fsmask, 'fsmask_1mm.nii' ) 


% REMEMBER THAT AT THE END WE NEED TO MAKE SURE THAT THE WHITE MATTER MASK
% IS PERFECTLY COMPLEMENTRAY TO ROIS (CORTEX AND DEEP STRUCTURES)

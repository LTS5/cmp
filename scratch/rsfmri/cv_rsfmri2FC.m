function [FC83 FC150 FC258 FC500 FC1015]=cv_rsfmri2FC(SUBJECT)
%
% This script takes fMRI files and compute FC for SC-rsFC evaluation

% step 1 DICOM --> NIFTII (diff_unpack)
% step 2 Register images --- script_rsfMRI.sh (LINUX)
%disp('WARNING: CHECK THAT DATA HAVE BEEN ACQUIRED HEAD TO FEET NON INTERLEAVED IF PERFORMING TIME CORRECTION')

time_corr=0 % put 1 if you want time correction

CMT_SUBJECTS_DIR=getenv('CMT_SUBJECTS_DIR');

% LOAD DATA (load the wm mask and the rois)
disp('loading data...')
cd(strcat(CMT_SUBJECTS_DIR,'/',SUBJECT,'/fs_output/registred/HR'))
[wm]=cv_analyze2sv('fsmask_1mm','b');
[aseg,h]=cv_analyze2sv('aseg_lpi','l');
csfA=aseg;csfA.data=csfA.data.*0;
csfA.data(aseg.data==4|aseg.data==43|aseg.data==11|aseg.data==50|aseg.data==31|aseg.data==63|aseg.data==10|aseg.data==49)=1;
cd scale500
[roi_labels]=cv_analyze2sv('ROI_HR_th','b');

cd(strcat(CMT_SUBJECTS_DIR,'/',SUBJECT,'/rsFMRI/registered'))
% build index of roi_labels
sz=size(roi_labels.data);
for i=1:max(roi_labels.data(:))
    idx{i}=find(roi_labels.data==i);
end
idx{i+1}=find(wm.data~=0);
idx{i+2}=find(csfA.data~=0);
%list of files
d=dir('*reg_lpi.img');
raw_fmri=zeros(max(roi_labels.data(:)),length(d)-1); % matrix that contains the time series of each roi
% for every file
if time_corr==1 (this is if time slice correction is applied, a priori not in Stuffelbeams data)
for i=1:size(d,1)-1
    % load and flip data
    [img,hdr]=cv_analyze2sv(d(i).name(1:end-4),'l');
    [img2,hdr2]=cv_analyze2sv(d(i+1).name(1:end-4),'l');
    for j=1:size(img.data,3)
        img.data(:,:,j)=fliplr(img.data(:,:,j));
        img2.data(:,:,j)=fliplr(img2.data(:,:,j));
    end
    %time correction
    sz=size(img.data,3);
    temp=img;
    for j=1:sz-1
        temp.data(:,:,j)=(j*img.data(:,:,j) + (sz-j)*img2.data(:,:,j))./sz;
    end
    % store signal into out (stores the time series averaged over the roi)
    for k=1:length(idx)
        raw_fmri(k,i)=mean(temp.data(idx{k}));
    end
end
else
for i=1:size(d,1)
    % load and flip data
    [img,hdr]=cv_analyze2sv(d(i).name(1:end-4),'l');
   sz=size(img.data,3);
    temp=img;
    % store signal into out
    for k=1:length(idx)
        raw_fmri(k,i)=mean(temp.data(idx{k}));
    end
end
end
		
% stephan you should stop here. (be sure that at this stage you have the average wm and ventricule time series)
% LINEAR DETRENDING
disp('applying linear detrending...')
% init variables
N=1015;
detrend_factor = 25; %time-window for detrending
start_time = 0;  %first time point to be analysed
total_time = size(d,1)-time_corr; %final time point to be analysed
discard = 5;  %how many frames to discard at beginning of dataset
total_time = total_time - discard + 1;  %total number of time steps
myinds = zeros(N,1); %the indices to be processes in each subject (we discard some ROIs in some individuals because signal is so low)
%resting gramatter BOLD
rest_corr = raw_fmri(1:N,discard:end);
rest_corr(isnan(rest_corr)) = 0;
%whitematter BOLD
rest_wm = raw_fmri(N+1,discard:end);
%ventricular BOLD
rest_ventric = raw_fmri(N+2,discard:end);
%now locate and remove the regions with v.low low signal
rr = rest_corr;
mr = mean(rr');
ind = find(mr>100);
rr = rr(ind,:); %ignore the ROIs with low signal.
myinds = mr > 100; %remember which ROIs we discarded and kept
%detrend the gray, white and ventricular time series, linear piecewise
%regression. (one could use filtering here, too. bandpass 0.1 -- 0.01
%Hz seems to give v. similar results fine)
drr = detrend(rr','linear',[start_time:detrend_factor:total_time])';
dwm = detrend(rest_wm', 'linear', [start_time:detrend_factor:total_time])';
dvent = detrend(rest_ventric', 'linear', [start_time:detrend_factor:total_time])';
%calculate the mean global signal
drr(isnan(drr)) = 0;
drr_mean = mean(drr);

% REGRESSION
disp('computing regressions...')
%initialize variables.
drr_reg = zeros(length(ind),total_time);
drr_reg_wm_vent = zeros(length(ind),total_time);
%now perform a linear regression of a global mean on both
for i=1:length(ind)
    [B,BINT,drr_reg(i,:)] = regress(drr(i,:)',[drr_mean' ones(total_time,1)]);
    [B,BINT,drr_reg_wm_vent(i,:)] = regress(drr(i,:)',[drr_mean' dwm' dvent' ones(total_time,1)]);
end;

% PEARSON CORRELATIONS
disp('computing pearson correlations...')
[COR_d_reg_wm_vent,R] = corr(drr_reg_wm_vent');   %correlations for detrended and global/wm/ventric regressed BOLD
[COR_d_reg,R] = corr(drr_reg');   %correlations for detrended and global regressed BOLD
[COR_d_only,R] = corr(drr');   %correlations for locally detrended BOLD
% move correlation matrices and time series back to 1000-region indices
% we are simply putting the ROIs back into the 1000 element ordering,
% and zeroiing the diagonal
FC.COR_d_reg_wm_vent_all = zeros(N,N);  %correlations, after detrending and then regression of global, ventricular and white matter signals
FC.COR_d_reg_all = zeros(N,N); %correlations, after detrending and regression of global signal only
FC.COR_d_only_all = zeros(N,N); %correlations after detrending only
FC.COR_d_reg_wm_vent_all(ind,ind) = COR_d_reg_wm_vent; 
FC.COR_d_reg_wm_vent_all(:,:) = FC.COR_d_reg_wm_vent_all(:,:) .* ~eye(N);
FC.COR_d_reg_all(ind,ind) = COR_d_reg; 
FC.COR_d_reg_all(:,:) = FC.COR_d_reg_all(:,:) .* ~eye(N);
FC.COR_d_only_all(ind,ind) = COR_d_only; 
FC.COR_d_only_all(:,:) = FC.COR_d_only_all(:,:) .* ~eye(N);
FC.drr_reg_wm_vent_all = zeros(N,total_time); %time series after detrending and then regression of global, ventricular and white matter
FC.drr_reg_all = zeros(N,total_time); %time series after detrending and then regression of global signal
FC.drr_only_all = zeros(N,total_time); %time series after detrending
FC.drr_reg_wm_vent_all(ind,:) = drr_reg_wm_vent;
FC.drr_reg_all(ind,:) = drr_reg;
FC.drr_only_all(ind,:) = drr;

FC1015=FC;

% averaging for other resolutions
disp('compute low resolution matrices...')
load roi_index
for my_res=1:4
N=max(roi_index(:,my_res));
FC.COR_d_reg_wm_vent_all_lowres=zeros(N);
FC.COR_d_reg_all_lowres=zeros(N);
FC.COR_d_only_all_lowres=zeros(N);
for i=1:N
    for j=1:N
        if i == j
            temp=FC.COR_d_reg_wm_vent_all(roi_index(roi_index(:,my_res)==i,5),roi_index(roi_index(:,my_res)==j,5));
            FC.COR_d_reg_wm_vent_all_lowres(i,j)=mean(nonzeros(temp(~eye(size(temp)))));
            temp=FC.COR_d_reg_all(roi_index(roi_index(:,my_res)==i,5),roi_index(roi_index(:,my_res)==j,5));
            FC.COR_d_reg_all_lowres(i,j)=mean(nonzeros(temp(~eye(size(temp)))));
            temp=FC.COR_d_only_all(roi_index(roi_index(:,my_res)==i,5),roi_index(roi_index(:,my_res)==j,5));
            FC.COR_d_only_all_lowres(i,j)=mean(nonzeros(temp(~eye(size(temp)))));
        else
            temp=FC.COR_d_reg_wm_vent_all(roi_index(roi_index(:,my_res)==i,5),roi_index(roi_index(:,my_res)==j,5));
            FC.COR_d_reg_wm_vent_all_lowres(i,j)=mean(temp(:));
            temp=FC.COR_d_reg_all(roi_index(roi_index(:,my_res)==i,5),roi_index(roi_index(:,my_res)==j,5));
            FC.COR_d_reg_all_lowres(i,j)=mean(temp(:));
            temp=FC.COR_d_only_all(roi_index(roi_index(:,my_res)==i,5),roi_index(roi_index(:,my_res)==j,5));
            FC.COR_d_only_all_lowres(i,j)=mean(temp(:));
        end
    end
end
if my_res==1
FC83.COR_d_reg_wm_vent_all=FC.COR_d_reg_wm_vent_all_lowres;
FC83.COR_d_reg_all=FC.COR_d_reg_all_lowres;
FC83.COR_d_only_all=FC.COR_d_only_all_lowres;
elseif my_res==2
FC150.COR_d_reg_wm_vent_all=FC.COR_d_reg_wm_vent_all_lowres;
FC150.COR_d_reg_all=FC.COR_d_reg_all_lowres;
FC150.COR_d_only_all=FC.COR_d_only_all_lowres;
elseif my_res==3
FC258.COR_d_reg_wm_vent_all=FC.COR_d_reg_wm_vent_all_lowres;
FC258.COR_d_reg_all=FC.COR_d_reg_all_lowres;
FC258.COR_d_only_all=FC.COR_d_only_all_lowres;
elseif my_res==4
FC500.COR_d_reg_wm_vent_all=FC.COR_d_reg_wm_vent_all_lowres;
FC500.COR_d_reg_all=FC.COR_d_reg_all_lowres;
FC500.COR_d_only_all=FC.COR_d_only_all_lowres;
end
end
cd(strcat(CMT_SUBJECTS_DIR,'/',SUBJECT,'/rsFMRI'));
clear FC
who

eval(['save ',strcat(SUBJECT,'_FCb.mat'),' FC83 FC1015']); 

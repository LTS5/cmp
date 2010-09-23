function roi_merge( MY_SUBJECT, MY_TP )

	for level = [33 60 125 250 500]
		roi_merge_level( MY_SUBJECT,MY_TP, level )
	end


	%---------------------------
	% NESTED function
	%---------------------------
	function roi_merge_level( MY_SUBJECT, MY_TP, level )
		se = zeros(3,3,3); se(2,:,2)=1;se(:,2,2)=1;se(2,2,:)=1;% 3D structural element

		DATA_path = getenv('DATA_path');
		aseg = load_untouch_nii( fullfile(DATA_path,MY_SUBJECT,MY_TP,'4__CMT/fs_output/registred/HR/aseg.nii') );


		fprintf('\n-> level: %d\n', level);


		%% RIGHT HEMISPHERE
		hemi = 'rh';
		ROIs_rh = load_untouch_nii( fullfile( DATA_path,MY_SUBJECT,MY_TP, ['4__CMT/fs_output/registred/HR/scale' num2str(level) ], ['ROI_' hemi '.nii']) );
		fprintf('   #cortex rois rh = %d\n', max(ROIs_rh.img(:)));

		% integrate thalamus, caudate, putamen, pallidum, accumbens, subthalamus, hippocampus and amygdala
		thalamus_subj_right = aseg;
		thalamus_subj_right.img = aseg.img*0;
		thalamus_subj_right.img(aseg.img==49) = 1;
		% thalamus_subj_right.img = imerode(imerode(thalamus_subj_right.img,se),se);
		thalamus_subj_right.img = imerode(thalamus_subj_right.img,se);
		thalam_right = thalamus_subj_right;
		% thalam_right.img = thalamus_subj_right.img.*((thalamus_subj_right.img>0)-imerode(thalamus_subj_right.img>0,se));
		clear thalamus_subj_right

		caudate_subj_right = aseg;
		caudate_subj_right.img = aseg.img*0;
		caudate_subj_right.img(aseg.img==50) = 1;
		% caudate_subj_right.img = imerode(imerode(caudate_subj_right.img,se),se);
		caudate_subj_right.img = imerode(caudate_subj_right.img,se);
		caudate_right = caudate_subj_right;
		% caudate_right.img = caudate_subj_right.img.*((caudate_subj_right.img>0)-imerode(caudate_subj_right.img>0,se));
		clear caudate_subj_right

		putam_subj_right = aseg;
		putam_subj_right.img = aseg.img*0;
		putam_subj_right.img(aseg.img==51) = 1;
		% putam_subj_right.img = imerode(imerode(putam_subj_right.img,se),se);
		putam_subj_right.img = imerode(putam_subj_right.img,se);
		putam_right = putam_subj_right;
		% putam_right.img = putam_subj_right.img.*((putam_subj_right.img>0)-imerode(putam_subj_right.img>0,se));
		clear putam_subj_right

		palli_subj_right = aseg;
		palli_subj_right.img = aseg.img*0;
		palli_subj_right.img(aseg.img==52) = 1;
		palli_right = palli_subj_right;
		% palli_right.img = palli_subj_right.img.*((palli_subj_right.img>0)-imerode(palli_subj_right.img>0,se));
		clear palli_subj_right

		accu_subj_right = aseg;
		accu_subj_right.img = aseg.img*0;
		accu_subj_right.img(aseg.img==58) = 1;
		accu_right = accu_subj_right;
		% accu_right.img = accu_subj_right.img.*((accu_subj_right.img>0)-imerode(accu_subj_right.img>0,se));
		clear accu_subj_right

		subthal_subj_right = aseg;
		subthal_subj_right.img = aseg.img*0;
		subthal_subj_right.img(aseg.img==60) = 1;
		temp=sum(sum(subthal_subj_right.img));
		z_max=max(find(temp>0));
		z_min=min(find(temp>0));
		subthal_subj_right.img(:,:,1:(ceil(z_min+(z_max-z_min)/2))) = 0;
		% subthal_subj_right.img = imerode(imerode(subthal_subj_right.img,se),se);
		subthal_subj_right.img = imerode(subthal_subj_right.img,se);
		subthal_right = subthal_subj_right;
		% subthal_right.img = subthal_subj_right.img.*((subthal_subj_right.img>0)-imerode(subthal_subj_right.img>0,se));
		clear subthal_subj_right

		hippo_subj_right = aseg;
		hippo_subj_right.img = aseg.img*0;
		hippo_subj_right.img(aseg.img==53) = 1;
		hippo_right = hippo_subj_right;
		clear hippo_subj_right

		amygd_subj_right = aseg;
		amygd_subj_right.img = aseg.img*0;
		amygd_subj_right.img(aseg.img==54) = 1;
		amygd_right = amygd_subj_right;
		clear amygd_subj_right


		%% LEFT HEMISPHERE
		hemi='lh';
		ROIs_lh = load_untouch_nii( fullfile( DATA_path,MY_SUBJECT,MY_TP, ['4__CMT/fs_output/registred/HR/scale' num2str(level) ], ['ROI_' hemi '.nii']) );
		fprintf('   #cortex rois lh = %d\n', max(ROIs_lh.img(:)));

		% integrate thalamus, caudate, putamen, pallidum, accumbens, subthalamus, hippocampus and amygdala
		thalamus_subj_left=aseg;
		thalamus_subj_left.img=aseg.img*0;
		thalamus_subj_left.img(aseg.img==10)=1;
		% thalamus_subj_left.img=imerode(imerode(thalamus_subj_left.img,se),se);
		thalamus_subj_left.img=imerode(thalamus_subj_left.img,se);
		thalam_left=thalamus_subj_left;
		% thalam_left.img=thalamus_subj_left.img.*((thalamus_subj_left.img>0)-imerode(thalamus_subj_left.img>0,se));
		clear thalamus_subj_left

		caudate_subj_left=aseg;
		caudate_subj_left.img=aseg.img*0;
		caudate_subj_left.img(aseg.img==11)=1;
		% caudate_subj_left.img=imerode(imerode(caudate_subj_left.img,se),se);
		caudate_subj_left.img=imerode(caudate_subj_left.img,se);
		caudate_left=caudate_subj_left;
		% caudate_left.img=caudate_subj_left.img.*((caudate_subj_left.img>0)-imerode(caudate_subj_left.img>0,se));
		clear caudate_subj_left

		putam_subj_left=aseg;
		putam_subj_left.img=aseg.img*0;
		putam_subj_left.img(aseg.img==12)=1;
		% putam_subj_left.img=imerode(imerode(putam_subj_left.img,se),se);
		putam_subj_left.img=imerode(putam_subj_left.img,se);
		putam_left=putam_subj_left;
		% putam_left.img=putam_subj_left.img.*((putam_subj_left.img>0)-imerode(putam_subj_left.img>0,se));
		clear putam_subj_left

		palli_subj_left=aseg;
		palli_subj_left.img=aseg.img*0;
		palli_subj_left.img(aseg.img==13)=1;
		palli_left=palli_subj_left;
		% palli_left.img=palli_subj_left.img.*((palli_subj_left.img>0)-imerode(palli_subj_left.img>0,se));
		clear palli_subj_left

		accu_subj_left=aseg;
		accu_subj_left.img=aseg.img*0;
		accu_subj_left.img(aseg.img==26)=1;
		accu_left=accu_subj_left;
		% accu_left.img=accu_subj_left.img.*((accu_subj_left.img>0)-imerode(accu_subj_left.img>0,se));
		clear accu_subj_left

		subthal_subj_left=aseg;
		subthal_subj_left.img=aseg.img*0;
		subthal_subj_left.img(aseg.img==28)=1;
		temp=sum(sum(subthal_subj_left.img));
		z_max=max(find(temp>0));
		z_min=min(find(temp>0));
		subthal_subj_left.img(:,:,1:(ceil(z_min+(z_max-z_min)/2)))=0;
		% subthal_subj_left.img=imerode(imerode(subthal_subj_left.img,se),se);
		subthal_subj_left.img=imerode(subthal_subj_left.img,se);
		subthal_left=subthal_subj_left;
		% subthal_left.img=subthal_subj_left.img.*((subthal_subj_left.img>0)-imerode(subthal_subj_left.img>0,se));
		clear subthal_subj_left

		hippo_subj_left=aseg;
		hippo_subj_left.img=aseg.img*0;
		hippo_subj_left.img(aseg.img==17)=1;
		hippo_left=hippo_subj_left;
		clear hippo_subj_left

		amygd_subj_left=aseg;
		amygd_subj_left.img=aseg.img*0;
		amygd_subj_left.img(aseg.img==18)=1;
		amygd_left=amygd_subj_left;
		clear amygd_subj_left



		%% create FINAL 'ROI_HR_th' dataset
		switch level
			case 500, offset=508;
			case 250, offset=250;
			case 125, offset=129;
			case 60,  offset=76;
			case 33,  offset=41;
			otherwise, error('Level not valid')
		end

		ROIs = ROIs_lh;
		ROIs_lh.img = ROIs_lh.img+offset;
		ROIs_lh.img(ROIs.img==0) = 0;
		ROIs.img = ROIs_rh.img+ROIs_lh.img;

		overlap = (ROIs_lh.img>0).*(ROIs_rh.img>0);% overlaping areas = 1
		if nnz(overlap(:))
			fprintf('   Number of removed voxels because of hemispheres overlap = %d\n',nnz(overlap(:)));
			rnd_N=round(rand(size(ROIs.img)));
			idx=logical(rnd_N.*overlap);
			ROIs_rh.img=ROIs_rh.img.*rnd_N.*overlap;
			ROIs.img(idx)=ROIs_rh.img(idx);
			ROIs_lh.img=ROIs_lh.img.*(~rnd_N).*overlap;
			idx2=logical(~rnd_N.*overlap);
			ROIs.img(idx2)=ROIs_lh.img(idx2);
		end


		switch level

			case 33
				ROIs.img(thalam_right.img>0)	= 34;
				ROIs.img(caudate_right.img>0)	= 35;
				ROIs.img(putam_right.img>0)		= 36;
				ROIs.img(palli_right.img>0)		= 37;
				ROIs.img(accu_right.img>0)		= 38;
				ROIs.img(subthal_right.img>0)	= 39;
				ROIs.img(hippo_right.img>0)		= 40;
				ROIs.img(amygd_right.img>0)		= 41;

				ROIs.img(thalam_left.img>0)		= 75;
				ROIs.img(caudate_left.img>0)	= 76;
				ROIs.img(putam_left.img>0)		= 77;
				ROIs.img(palli_left.img>0)		= 78;
				ROIs.img(accu_left.img>0)		= 79;
				ROIs.img(subthal_left.img>0)	= 80;
				ROIs.img(hippo_left.img>0)		= 81;
				ROIs.img(amygd_left.img>0)		= 82;

				ROIs.img(aseg.img==16)			= 83;

			case 60
				ROIs.img(thalam_right.img>0)	= 69;
				ROIs.img(caudate_right.img>0)	= 70;
				ROIs.img(putam_right.img>0)		= 71;
				ROIs.img(palli_right.img>0)		= 72;
				ROIs.img(accu_right.img>0)		= 73;
				ROIs.img(subthal_right.img>0)	= 74;
				ROIs.img(hippo_right.img>0)		= 75;
				ROIs.img(amygd_right.img>0)		= 76;

				ROIs.img(thalam_left.img>0)		= 142;
				ROIs.img(caudate_left.img>0)	= 143;
				ROIs.img(putam_left.img>0)		= 144;
				ROIs.img(palli_left.img>0)		= 145;
				ROIs.img(accu_left.img>0)		= 146;
				ROIs.img(subthal_left.img>0)	= 147;
				ROIs.img(hippo_left.img>0)		= 148;
				ROIs.img(amygd_left.img>0)		= 149;

				ROIs.img(aseg.img==16)			= 150;

			case 125
				ROIs.img(thalam_right.img>0)	= 122;
				ROIs.img(caudate_right.img>0)	= 123;
				ROIs.img(putam_right.img>0)		= 124;
				ROIs.img(palli_right.img>0)		= 125;
				ROIs.img(accu_right.img>0)		= 126;
				ROIs.img(subthal_right.img>0)	= 127;
				ROIs.img(hippo_right.img>0)		= 128;
				ROIs.img(amygd_right.img>0)		= 129;

				ROIs.img(thalam_left.img>0)		= 250;
				ROIs.img(caudate_left.img>0)	= 251;
				ROIs.img(putam_left.img>0)		= 252;
				ROIs.img(palli_left.img>0)		= 253;
				ROIs.img(accu_left.img>0)		= 254;
				ROIs.img(subthal_left.img>0)	= 255;
				ROIs.img(hippo_left.img>0)		= 256;
				ROIs.img(amygd_left.img>0)		= 257;

				ROIs.img(aseg.img==16)			= 258;

			case 250
				ROIs.img(thalam_right.img>0)	= 243;
				ROIs.img(caudate_right.img>0)	= 244;
				ROIs.img(putam_right.img>0)		= 245;
				ROIs.img(palli_right.img>0)		= 246;
				ROIs.img(accu_right.img>0)		= 247;
				ROIs.img(subthal_right.img>0)	= 248;
				ROIs.img(hippo_right.img>0)		= 249;
				ROIs.img(amygd_right.img>0)		= 250;

				ROIs.img(thalam_left.img>0)		= 492;
				ROIs.img(caudate_left.img>0)	= 493;
				ROIs.img(putam_left.img>0)		= 494;
				ROIs.img(palli_left.img>0)		= 495;
				ROIs.img(accu_left.img>0)		= 496;
				ROIs.img(subthal_left.img>0)	= 497;
				ROIs.img(hippo_left.img>0)		= 498;
				ROIs.img(amygd_left.img>0)		= 499;

				ROIs.img(aseg.img==16)			= 500;

			case 500
				ROIs.img(thalam_right.img>0)	= 501;
				ROIs.img(caudate_right.img>0)	= 502;
				ROIs.img(putam_right.img>0)		= 503;
				ROIs.img(palli_right.img>0)		= 504;
				ROIs.img(accu_right.img>0)		= 505;
				ROIs.img(subthal_right.img>0)	= 506;
				ROIs.img(hippo_right.img>0)		= 507;
				ROIs.img(amygd_right.img>0)		= 508;

				ROIs.img(thalam_left.img>0)		= 1007;
				ROIs.img(caudate_left.img>0)	= 1008;
				ROIs.img(putam_left.img>0)		= 1009;
				ROIs.img(palli_left.img>0)		= 1010;
				ROIs.img(accu_left.img>0)		= 1011;
				ROIs.img(subthal_left.img>0)	= 1012;
				ROIs.img(hippo_left.img>0)		= 1013;
				ROIs.img(amygd_left.img>0)		= 1014;

				ROIs.img(aseg.img==16)			= 1015;

		end


		% save the final dataset as int16 (to save space)
		ROIs.hdr.dime.datatype = 4;
		ROIs.hdr.dime.bitpix = 16;
		ROIs.img = int16(ROIs.img);
		save_untouch_nii( ROIs, fullfile(DATA_path,MY_SUBJECT,MY_TP, ['4__CMT/fs_output/registred/HR/scale' num2str(level) ], 'ROI_HR_th.nii') );
		delete( fullfile( DATA_path,MY_SUBJECT,MY_TP, ['4__CMT/fs_output/registred/HR/scale' num2str(level) ], ['ROI_lh.nii']) );
		delete( fullfile( DATA_path,MY_SUBJECT,MY_TP, ['4__CMT/fs_output/registred/HR/scale' num2str(level) ], ['ROI_rh.nii']) );
		fprintf('   Max label in final ''ROI_HR_th'' dataset = %d\n\n', max(ROIs.img(:)))
	end


end

function fillHolesInLabels( INPUT_path, gfa_GM_lb, gfa_WM_lb )

fprintf('\n-> Basepath for labels to be fixed: ''%s''\n', INPUT_path)



%% load GFA and WM datasets (GFA must be provided in 1x1x1 mm^3 resolution)
fprintf('\n-> Loading ''GFA_1x1x1.nii'' mask...\n')
	niiGFA = load_untouch_nii( fullfile(INPUT_path,'GFA_1x1x1.nii') );
fprintf('   [ OK ]\n')


fprintf('\n-> Loading ''WM.nii'' mask...\n')
	niiWM = load_untouch_nii( fullfile(INPUT_path,'WM.nii') );
	niiWM.img = abs(niiWM.img);
fprintf('   [ OK ]\n')


%% fill holes in WM based on GFA information
fprintf('\n-> Working on''WM.nii'' dataset...\n')

	% fill gaps
	fprintf('   * INCLUDING voxels with GFA >= %.2f and REMOVING voxels with GFA < %.2f...',gfa_WM_lb,gfa_GM_lb)

	[X Y Z] = ind2sub( niiWM.hdr.dime.dim(2:4), find(imdilate(niiWM.img,ones(3,3,3)) - imerode(niiWM.img,ones(3,3,3))) );
	for i = 1:length(X)
		if ( niiGFA.img( X(i),Y(i),Z(i) ) >= gfa_WM_lb )
			niiWM.img( X(i), Y(i), Z(i) ) = 1;
		end
		if ( niiGFA.img( X(i),Y(i),Z(i) ) < gfa_GM_lb )
			niiWM.img( X(i), Y(i), Z(i) ) = 0;
		end
	end
	clear X Y Z se

	fprintf(' [ OK ]\n')


	% save filled dataset
	fprintf('   * Saving dataset as ''WM__DILATED.nii''...')

	save_untouch_nii(niiWM,fullfile(INPUT_path,'WM__DILATED.nii'));

	fprintf(' [ OK ]\n')
fprintf('   [ OK ]\n')





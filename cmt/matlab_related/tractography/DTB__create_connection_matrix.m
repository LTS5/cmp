function script_connection_matrix( INPUT_path )

[tmp,tmp] = mkdir(INPUT_path,'/fibers/matrices');

fprintf('   * Loading fibers endpoints... ')
[ENDPOINTS LEN] = DTB__load_endpoints_from_trk( sprintf('%s/fibers/streamline.trk', INPUT_path) );
fprintf(' [ OK ]\n\n')

RESOLUTIONs  = [33 60 125 250 500];

for N = RESOLUTIONs
	fprintf('   * working on resolution = %d... ', N)

	niiROI 	= load_untouch_nii( sprintf('%s/fs_output/registred/HR__registered-TO-b0/scale%d/ROI_HR_th.nii', INPUT_path,N) );
	matrix 	= DTB__fibers2cmat(ENDPOINTS, LEN, niiROI);

	% apply mask filter
	load mat_mask.mat
	load roi_index

	for i = 1:matrix.datainfo.resolution
		for j = i:matrix.datainfo.resolution
			MODEi = mode(roi_index(roi_index(:,1)==i,1));
			MODEj = mode(roi_index(roi_index(:,1)==j,1));

			if ~isnan(MODEi) && ~isnan(MODEj) && mat_mask(MODEi,MODEj)==0
				matrix.density(i,j)=0;
				matrix.density(j,i)=0;
				matrix.length(i,j)=0;
				matrix.length(j,i)=0;
			end
		end
	end

	filename = sprintf('%s/fibers/matrices/matrix%d.mat', INPUT_path,N);
	save(filename,'matrix');
	fprintf(' [ "matrix%d.mat" ]\n', N)
end

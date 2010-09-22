function roi_creation( MY_SUBJECT, MY_TP )

fprintf('\n * Resolution: 35...');
roi_creation_level(MY_SUBJECT,MY_TP,35,'rh')
roi_creation_level(MY_SUBJECT,MY_TP,35,'lh')
fprintf(' [OK]\n');

fprintf('\n * Resolution: 60...');
roi_creation_level(MY_SUBJECT,MY_TP,60,'lh')
roi_creation_level(MY_SUBJECT,MY_TP,60,'rh')
fprintf(' [OK]\n');

fprintf('\n * Resolution: 125...');
roi_creation_level(MY_SUBJECT,MY_TP,125,'rh')
roi_creation_level(MY_SUBJECT,MY_TP,125,'lh')
fprintf(' [OK]\n');

fprintf('\n * Resolution: 250...');
roi_creation_level(MY_SUBJECT,MY_TP,250,'rh')
roi_creation_level(MY_SUBJECT,MY_TP,250,'lh')
fprintf(' [OK]\n');

fprintf('\n * Resolution: 500...');
roi_creation_level(MY_SUBJECT,MY_TP,500,'rh')
roi_creation_level(MY_SUBJECT,MY_TP,500,'lh')
fprintf(' [OK]\n');


	%---------------------------
	% nested function
	%---------------------------
	function roi_creation_level( MY_SUBJECT,MY_TP, level,hemi )

	CMT_HOME		= getenv('CMT_HOME');
    if isempty(CMT_HOME), error('Env variable "CMT_HOME" not set!'), end
	DATA_path		= getenv('DATA_path');
    if isempty(DATA_path), error('Env variable "DATA_path" not set!'), end
    
	SUBJECTS_DIR	= [DATA_path '/' MY_SUBJECT '/' MY_TP];

	cd(strcat(SUBJECTS_DIR,'/3__FREESURFER/label/regenerated_',hemi,'_',num2str(level)))


	list = load([CMT_HOME,'/matlab_related/ordred_33parcels.mat']); list = list.list;
	new_order = load([CMT_HOME,'/matlab_related/new_order_mai.mat']);
	if hemi=='rh'
		new_order=new_order.new_order_rh;
	else
		new_order=new_order.new_order_lh;
	end


	cpt=1;
	Rois=zeros(256,256,256);
	delete( '*.nii' );
	for i=1:33
%        [CMT_HOME '/one_label_script.sh ' hemi '.' list{i} ' ' strcat(SUBJECTS_DIR,'/3__FREESURFER')]
		%eval(strcat(['!env LD_LIBRARY_PATH= sh ',CMT_HOME,'/one_label_script.sh ',hemi,'.',list{i}]));
		%system( [CMT_HOME '/one_label_script.sh ' hemi '.' list{i} ' ' strcat(SUBJECTS_DIR,'/3__FREESURFER') ] );
		
        
		file_numbers = size( dir(strcat(hemi,'.',list{i},'*.nii')) ,1);
		if (level==500)
			file_numbers=file_numbers-1;
		end
		 cpt2=0;
		 for j=1:file_numbers

			if level==35
				label_file_name=strcat(hemi,'.',list{i},'.label');
				cpt2=cpt2+1;
			else
				if level==500
					label_file_name=strcat(hemi,'.',new_order{cpt},'.label');
				else
					label_file_name=strcat(hemi,'.',list{i},'_',num2str(j),'.label');
				end
				cpt2=cpt2+1;
			end


			label = load_untouch_nii( [label_file_name '.nii'] );
			Rois(find(label.img))=cpt;
			cpt=cpt+1;

		end
		if cpt2==j
		
			disp('[ERROR] cpt <> j   --> %f <> %f');
            disp(cpt2);
            disp(j);
			return
		end

		delete(strcat(hemi,'.',list{i},'*.nii'))
	end

	label.img = Rois;
	save_untouch_nii(label, strcat('ROI_',hemi,'.nii'))

	cd([CMT_HOME,'/']);
	end


end

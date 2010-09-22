function Roi_creation(MY_SUBJECT,MY_TP, level,hemi)

CMT_HOME		= getenv('CMT_HOME');
DATA_path		= getenv('DATA_path');
SUBJECTS_DIR	= [DATA_path '/' MY_SUBJECT '/' MY_TP];

load([CMT_HOME,'/matlab_related/ordred_33parcels.mat']);
load([CMT_HOME,'/matlab_related/new_order_mai.mat']);


cd(strcat(SUBJECTS_DIR,'/3__FREESURFER/label/regenerated_',hemi,'_',num2str(level)))

cpt=1;
Rois=zeros(256,256,256);

if hemi=='rh'
    new_order=new_order_rh;
else
    new_order=new_order_lh;
end

delete( '*.nii' );

for i=1:33
    eval(strcat(['!env LD_LIBRARY_PATH= sh ',CMT_HOME,'/one_label_script.sh ',hemi,'.',list{i}]));
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
    else
        fprintf('[ERROR] cpt <> j   --> %f <> %f',cpt2,j);
        return
    end

    delete(strcat(hemi,'.',list{i},'*.nii'))
end

label.img = Rois;
save_untouch_nii(label, strcat('ROI_',hemi,'.nii'))

cd([CMT_HOME,'/']);


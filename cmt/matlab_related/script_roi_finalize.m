
cd([getenv('DATA_path'),'/',getenv('MY_SUBJECT'),'/',getenv('MY_TP'),'/4__CMT/fs_output/registred/HR/']);
mask = load_untouch_nii( 'fsmask_1mm.nii' );

for n=[33,60,125,250,500]
    cd(['scale',num2str(n)]);
    ROI = load_untouch_nii( 'ROI_HR_th.nii' );
    ROI.img(ROI.img>0 & mask.img~=0)=0;
    save_untouch_nii( ROI, 'ROI_HR_th.nii' );
    cd ..
end

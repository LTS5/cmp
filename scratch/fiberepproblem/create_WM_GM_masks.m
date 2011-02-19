function create_WM_GM_masks( SUBJECT, TP )

DATA_path		= getenv('DATA_path');
if isempty(DATA_path), error('Env variable "DATA_path" not set!'), end
MRI_path = fullfile(DATA_path,SUBJECT,TP,'/3__FREESURFER/mri');


%% open 'aparc+aseg.nii' file
%  --------------------------
niiAPARC  = load_untouch_nii( fullfile(MRI_path,'aparc+aseg.nii') );


%% label mapping
%  -------------
CORTICAL{1} = [ 1  2  3  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34];
CORTICAL{2} = [31 13  9 21 27 25 19 29 15 23  1 24  4 30 26 11  6  2  5 22 16 14 10 20 12  7  8 18 30 17  3 28 33];

SUBCORTICAL{1} = [48 49 50 51 52 53 54 58 59 60    9 10 11 12 13 17 18 26 27 28];
SUBCORTICAL{2} = [34 34 35 36 37 40 41 38 39 39   75 75 76 77 78 81 82 79 80 80];

OTHER{1} = [16 251 252 253 254 255 86 1004 2004];
OTHER{2} = [83  84  84  84  84  84 84   84   84];

WM = [2 29 32 41 61 64 77:86 100:117 155:158 195:196 199:200 203:204 212 219 223 250:255];


%% create WM mask
%  --------------
niiWM = niiAPARC;
niiWM.hdr.dime.datatype = 2; % uint8
niiWM.hdr.dime.bitpix   = 8;
niiWM.img = uint8( niiAPARC.img .* 0 );

% labels given by Cristina
for i = 1:length(WM)
	niiWM.img( niiAPARC.img == WM(i) ) = 1;
end
% we include SUBCORTICAL ROIs to WM as well...
for i = 1:length(SUBCORTICAL{1})
	niiWM.img( niiAPARC.img == SUBCORTICAL{1}(i) ) = 1;
end


%% create GM mask (CORTICAL+SUBCORTICAL)
%  -------------------------------------
niiGM = niiAPARC;
niiGM.hdr.dime.datatype = 4; % int16
niiGM.hdr.dime.bitpix   = 16;
niiGM.img = int16(niiGM.img .* 0);

% 33 cortical regions (stored in the order of "parcel33")
for i = 1:length(CORTICAL{1})
	niiGM.img( niiAPARC.img == (2000+CORTICAL{1}(i)) ) = CORTICAL{2}(i);		% RIGHT
	niiGM.img( niiAPARC.img == (1000+CORTICAL{1}(i)) ) = CORTICAL{2}(i) + 41;	% LEFT
end

% subcortical nuclei
for i = 1:length(SUBCORTICAL{1})
	niiGM.img( niiAPARC.img == SUBCORTICAL{1}(i) ) = SUBCORTICAL{2}(i);
end

% other region to account for in the GM
for i = 1:length(OTHER{1})
	niiGM.img( niiAPARC.img == OTHER{1}(i) ) = OTHER{2}(i);
end


%% save datasets
%  -------------
save_untouch_nii( niiGM, fullfile(MRI_path,'GM.nii') );
save_untouch_nii( niiWM, fullfile(MRI_path,'WM.nii') );

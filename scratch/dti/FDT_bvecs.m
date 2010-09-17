

% reading bvecs from dicom files for FDT/FSL analysis
% Extracting bvects and bvals for dicom images

%*******************************CommentBegin*************************
% Author:              Elda Fischi, ITS/EPFL
% Created:             09/2010
% 
%*******************************CommentEnd***************************

my_subject='chuv6y_1'

folder=strcat('/Users/elda/Data/FDT','/',my_subject);
cd(folder)

% if isequal(filename(end-3:end),'.dcm')
%    filename=filename(1:end-5);
% end

dicom_data=dir('*.dcm');
bvecs=zeros(31,3);
bvals=zeros(31,1);
for i=1:numel(dicom_data)
    filename=dicom_data(i).name;
    hdr=dicominfo(filename);
    if i==1
       for j=1:3
           bvecs(i,j)=0;
       end
       bvals(i)=hdr.Private_0019_100c;
    elseif i>1
       bvecs(i,:)=hdr.Private_0019_100e;
       bvals(i)=hdr.Private_0019_100c;
    end
end

   
save bvecs.mat bvecs
save bvals.mat bvals

load bvecs.mat
load bvals.mat

save('bvecs.txt',bvecs{:},'-ascii')




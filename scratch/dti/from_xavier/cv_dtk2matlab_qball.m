function [b0,stixv,t1] = cv_dtk2matlab_qball(name,dirlist)

% \manchap
%
%   Import data obtained with the Diffusion Toolkit into Matlab
%
% \mansecSyntax
%
%   [adc,b0,dwi,fa,stixv] = cv_dtk2matlab(name,dirlist)
%
% \mansecDescription
%
%   cv_dtk2matlab imports data obtained with the Diffusion Toolkit into
%   Matlab
%
% \mansubsecInputData
%
%   \begin{description}
%   \item[NAME] [STRING]: Common name for the file (ex: dsi).
%   \item[DIRLIST] [ARRAY]: List of the directions used in DTK, see
%   cv/utils.
%   \end{description} 
%
% \mansubsecOutputData
%
%   \begin{description}
%   \item[ADC] [STRUCTURE]: structure containing the ADC volume.
%   \item[B0] [STRUCTURE]: structure containing the B0 volume.
%   \item[DWI] [STRUCTURE]: structure containing the DWI volume.
%   \item[FA] [STRUCTURE]: structure containing the FA volume.
%   \item[STIXV] [STRUCTURE]: structure containing the stix volume.
%   \end{description} 
%
% \mansecLicense
%
% This file is part of Dimaging Toolbox
% Copyright (C) 2001, the Dimage Team (see the file AUTHORS distributed
% with this library) (See the notice at the end of the file.) 
%

%*******************************CommentBegin*************************
% Author:              Xavier Gigandet, ITS/EPFL
% Created:             09/2008
% $Id: cv_dtk2matlab.m,
%*******************************CommentEnd***************************  

%load scalar maps
T1_name=strcat(name,'_T1_resampled.nii');
[t1,hdr]=cv_nifti2sv(T1_name,'l');
t1.descrip=strcat(name,' T1');
for i=1:size(t1.data,3)
    t1.data(:,:,i)=fliplr(flipud(t1.data(:,:,i)));
end


b0_name=strcat(name,'_b0.nii');
[b0,hdr]=cv_nifti2sv(b0_name,'l');
b0.descrip=strcat(name,' b0');
for i=1:size(b0.data,3)
    b0.data(:,:,i)=fliplr(flipud(b0.data(:,:,i)));
end


%load max file
max_name=strcat(name,'_max.nii');
[max,hdr]=cv_nifti2sv(max_name,'l');
max.descrip=strcat(name,' max');
max.data=logical(max.data);
for i=1:size(max.data,1)
    for j=1:size(max.data,4)
        max.data(i,:,:,j)=fliplr(flipud(squeeze(max.data(i,:,:,j))));
    end
end

% load odf file
odf_name=strcat(name,'_odf.nii');
[odfv_dtk,hdr]=cv_nifti2sv(odf_name,'l');
odfv_dtk.descrip=strcat(name,' odfv_dtk');
odfv_dtk.format='odfv_dtk';
for i=1:size(odfv_dtk.data,1)
    for j=1:size(odfv_dtk.data,4)
        odfv_dtk.data(i,:,:,j)=fliplr(flipud(squeeze(odfv_dtk.data(i,:,:,j))));
    end
end
odfv_dtk.datainfo.pixdim=b0.datainfo.pixdim;

% find idx of stix
stix_idx=cell(size(max.data,2),size(max.data,3),size(max.data,4));
for x=1:size(max.data,2)
    for y=1:size(max.data,3)
        for z=1:size(max.data,4)
            stix_idx{x,y,z}=find(max.data(:,x,y,z));
        end
    end
end

% creates stix volume
stixv.descrip=strcat(name,' stixv');
stixv.datainfo=b0.datainfo;
stixv.format='stix';
stixv.data=cell(size(max.data,2),size(max.data,3),size(max.data,4));
for x=1:size(max.data,2)
    for y=1:size(max.data,3)
        for z=1:size(max.data,4)
            stixv.data{x,y,z}=dirlist(stix_idx{x,y,z},:).*repmat(odfv_dtk.data(stix_idx{x,y,z},x,y,z),[1 3]);
            stixv.data{x,y,z}(:,1:2)=-stixv.data{x,y,z}(:,1:2);
		
        end
    end
end

% This program is free software; you can redistribute it and/or modify
% it under the terms of the GNU General Public License as published by
% the Free Software Foundation; either version 2 of the License, or
% any later version.
%
% This program is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU General Public License for more details.
%
% You should have received a copy of the GNU General Public License
% along with this program; if not, write to the Free Software
% Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA






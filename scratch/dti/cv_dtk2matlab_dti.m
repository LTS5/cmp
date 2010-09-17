function [adc,b0,dwi,fa,stixv,t1] = cv_dtk2matlab_dti(name,dirlist)

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

adc_name=strcat(name,'_adc.nii');
[adc,hdr]=cv_nifti2sv(adc_name,'l');
adc.descrip=strcat(name,' adc');
for i=1:size(adc.data,3)
    adc.data(:,:,i)=fliplr(flipud(adc.data(:,:,i)));
end

b0_name=strcat(name,'_b0.nii');
[b0,hdr]=cv_nifti2sv(b0_name,'l');
b0.descrip=strcat(name,' b0');
for i=1:size(b0.data,3)
    b0.data(:,:,i)=fliplr(flipud(b0.data(:,:,i)));
end

dwi_name=strcat(name,'_dwi.nii');
[dwi,hdr]=cv_nifti2sv(dwi_name,'l');
dwi.descrip=strcat(name,' dwi');
for i=1:size(dwi.data,3)
    dwi.data(:,:,i)=fliplr(flipud(dwi.data(:,:,i)));
end

fa_name=strcat(name,'_fa.nii');
[fa,hdr]=cv_nifti2sv(fa_name,'l');
fa.descrip=strcat(name,' fa');
for i=1:size(fa.data,3)
    fa.data(:,:,i)=fliplr(flipud(fa.data(:,:,i)));
end

stixv=cv_nifti2vv(strcat(name,'_v1.nii'),'l');
for i=1:size(stixv.data,1)
	for j=1:size(stixv.data,2)
		for k=1:size(stixv.data,3)
			if ~isempty(stixv.data{i,j,k})
				if sum(stixv.data{i,j,k}.^2)==0
					stixv.data{i,j,k}=[];
				end
			end
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






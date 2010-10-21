function [img1, hdr] = cv_nifti2vv(fileName,byteOrder)

% Definition of the type of hdr
%----------------------------------------------------------------------
header_key = struct('sizeof_hdr',0,...
	'data_type',{' '},...
	'db_name',{' '},...
	'extents',0,...
	'session_error',0,...
 	'regular',{' '},...
	'hkey_un0',{' '});
image_size = struct('dim',[0 0 0 0 0 0 0 0],...
	'unused8',0,...
	'unused9',0,...
	'unused10',0,...
	'unused11',0,...
	'unused12',0,...
	'unused13',0,...
	'unused14',0,...
	'datatype',0,...
	'bitpix',0,...
	'dim_un0',0,...
	'pixdim',[0 0 0 0 0 0 0 0],...
	'vox_offset',0,...
	'scale_fact',0,...
	'funused10',0,...
	'funused11',0,...
	'funused12',0,...
	'funused13',0,...
	'compressed',0,...
	'verified',0,...
	'glmax',0,...
	'glmin',0);
data_histo = struct('descrip',{' '},...
	'aux_file',{' '},...
	'orient',{' '},...
	'originator',{' '},...
	'generated',{' '},...
	'scannum',{' '},...
	'patient_id',{' '},...
	'exp_date',{' '},...
	'exp_time',{' '},...
   'hist_un0',{' '},...
   'views',0,...
	'vols_added',0,...
 	'start_field',0,...
	'field_skip',0,...
	'omax',0,...
	'omin',0,...
	'smax',0,...
   'smin',0);
hdr = struct('hk',header_key,...
   'dime',image_size,...
   'hist',data_histo);
clear header_key image_size data_histo;

%----------------------------------------------------------------------
% open file
%----------------------------------------------------------------------

file=fopen(fileName,'r',byteOrder);

%----------------------------------------------------------------------
% read header_key
%----------------------------------------------------------------------

hdr.hk.sizeof_hdr = fread(file,1,'int32');
hdr.hk.data_type = char(fread(file,[1 10],'uchar'));
hdr.hk.db_name = char(fread(file,[1 18],'char'));
hdr.hk.extents = fread(file,1,'int32');
hdr.hk.session_error = fread(file,1,'int16');
hdr.hk.regular = char(fread(file,1,'char'));
hdr.hk.hkey_un0 = fread(file,1,'uchar');

% read image_dimension
%----------------------------------------------------------------------
hdr.dime.dim = fread(file,[1 8],'int16');
hdr.dime.unused8 = char(fread(file,[1 2],'uchar'));
%hdr.dime.unused8 = (fread(file,1,'int16'));
hdr.dime.unused9 = fread(file,1,'int16');
hdr.dime.unused10 = fread(file,1,'int16');
hdr.dime.unused11 = fread(file,1,'int16');
hdr.dime.unused12 = fread(file,1,'int16');
hdr.dime.unused13 = fread(file,1,'int16');
hdr.dime.unused14 = fread(file,1,'int16');
hdr.dime.datatype = fread(file,1,'int16');
hdr.dime.bitpix = fread(file,1,'int16');
hdr.dime.dim_un0 = fread(file,1,'int16');
hdr.dime.pixdim = fread(file,[1 8],'float32');
hdr.dime.vox_offset = fread(file,1,'float32');
hdr.dime.scale_fact = fread(file,1,'float32');
hdr.dime.funused10 = fread(file,1,'float32');
hdr.dime.funused11 = fread(file,1,'float32');
hdr.dime.funused12 = fread(file,1,'float32');
hdr.dime.funused13 = fread(file,1,'float32');
hdr.dime.compressed = fread(file,1,'float32');
hdr.dime.verified = fread(file,1,'float32');
hdr.dime.glmax = fread(file,1,'int32');
hdr.dime.glmin = fread(file,1,'int32');

% read data_history
%----------------------------------------------------------------------
hdr.hist.descrip = char(fread(file,[1 80],'uchar'));
hdr.hist.aux_file = char(fread(file,[1 24],'uchar'));
hdr.hist.orient = char(fread(file,1,'uchar'));
hdr.hist.originator = char(fread(file,[1 10],'uchar'));
%hdr.hist.originator = fread(file,[1 10],'uchar');
hdr.hist.generated = char(fread(file,[1 10],'uchar'));
hdr.hist.scannum = char(fread(file,[1 10],'uchar'));
hdr.hist.patient_id = char(fread(file,[1 10],'uchar'));
hdr.hist.exp_date = char(fread(file,[1 10],'uchar'));
hdr.hist.exp_time = char(fread(file,[1 10],'uchar'));
hdr.hist.hist_un0 = char(fread(file,[1 3],'uchar'));
hdr.hist.views = fread(file,1,'int32');
hdr.hist.vols_added = fread(file,1,'int32');
hdr.hist.start_field = fread(file,1,'int32');
hdr.hist.field_skip = fread(file,1,'int32');
hdr.hist.omax = fread(file,1,'int32');
hdr.hist.omin = fread(file,1,'int32');
hdr.hist.smax = fread(file,1,'int32');
hdr.hist.smin = fread(file,1,'int32');
hdr.hk.sizeof_hdr;
temp=fread(file,1,'float');

% Initialization of volumes. img1 will contain the data in the usual
% toolbox referential.
img1.descrip = hdr.hk.db_name;
img1.format = 'tv';
img1.datainfo.dimunits = hdr.dime.unused8;
img1.datainfo.pixdim = hdr.dime.pixdim(2:4);
img1.datainfo.arraytype = 'mat';
img1.data = zeros(hdr.dime.dim(2),hdr.dime.dim(3),hdr.dime.dim(4),3, ...
	    hdr.dime.dim(5));

% Determination of datatype, reading in the header.
switch hdr.dime.datatype
 case 0
  mode = '';   % There is no implementation to read UNKNOWN format
  error([' ERROR: THIS FILE IS OF "UNKNOWN" DATAYPE, WHICH IS NOT' ...
	  ' IMPLEMENTED BY THIS READER!']);
 case 1
  mode = 'ubit1';			
  if(hdr.dime.bitpix ~= 1)
    error(' ERROR IN DATA TYPE IN THE HEADER FILES');
  end
 case 2
  mode = 'uchar';
  if(hdr.dime.bitpix ~= 8)
    error(' ERROR IN DATA TYPE IN THE HEADER FILES');
  end
 case 4
  mode = 'int16';
  if(hdr.dime.bitpix ~= 16)
    error(' ERROR IN DATA TYPE IN THE HEADER FILES');
  end
 case 8
  mode = 'int32';
  if(hdr.dime.bitpix ~= 32)
    error(' ERROR IN DATA TYPE IN THE HEADER FILES');
  end
 case 16
  mode = 'float32';
  if(hdr.dime.bitpix ~= 32)
    error(' ERROR IN DATA TYPE IN THE HEADER FILES');
  end
 case 32
  mode = '';	% There is no implementation to read COMPLEX format
  error([' ERROR: THIS FILE IS OF "COMPLEX" DATAYPE IS NOT IMPLEMENTED' ...
	' IN THE READER!']);
  if(hdr.dime.bitpix ~= 64)
    error(' ERROR IN DATA TYPE IN THE HEADER FILES');
  end
 case 64
  mode = 'float64';
  if(hdr.dime.bitpix ~= 64)
    error(' ERROR IN DATA TYPE IN THE HEADER FILES');
  end
 case 128
  mode = '';	% There is no implementation to read RGB format
  error([' ERROR: THIS FILE IS OF "RGB" DATAYPE IS NOT IMPLEMENTED IN' ...
	 ' THE READER!']);
  if(hdr.dime.bitpix ~= 128)
    error(' ERROR IN DATA TYPE IN THE HEADER FILES');
  end
 otherwise
  error(' ERROR IN DATA TYPE IN THE HEADER FILES');
end
   
% Reading the dataset from the file.
for j = 1:hdr.dime.dim(4)
      img = fread(file,[hdr.dime.dim(2),hdr.dime.dim(3)], ...
			    mode );
      img1.data(:,:,j,1) = img;
end
for j = 1:hdr.dime.dim(4)
      img = fread(file,[hdr.dime.dim(2),hdr.dime.dim(3)], ...
			    mode );
      img1.data(:,:,j,2) = img;
end
for j = 1:hdr.dime.dim(4)
      img = fread(file,[hdr.dime.dim(2),hdr.dime.dim(3)], ...
			    mode );
      img1.data(:,:,j,3) = img;
end

for i=1:size(img1.data,3)
for j=1:size(img1.data,4)
img1.data(:,:,i,j)=fliplr(flipud(img1.data(:,:,i,j)));
end
end

img2=img1;
img2.data=cell(size(img1.data,1),size(img1.data,2),size(img1.data,3));
for i=1:size(img1.data,1)
for j=1:size(img1.data,2)
for k=1:size(img1.data,3)
img2.data{i,j,k}=squeeze(img1.data(i,j,k,:))';
img2.data{i,j,k}(1:2)=-img2.data{i,j,k}(1:2);
end
end
end
img1=img2;


fclose(file);

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

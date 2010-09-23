function [endpoints len] = DTB__load_endpoints_from_trk( TRK_filename )

file=fopen(TRK_filename,'r','l');

%----------------------------------------------------------------------
% read header
%----------------------------------------------------------------------

hdr.id_string = uint8(fread(file,[1 6],'*uint8'));
hdr.dim = fread(file,[1 3],'*int16');
hdr.voxel_size = fread(file,[1 3],'*float32');
hdr.origin = fread(file,[1 3],'*float32');
hdr.n_scalars = fread(file,1,'*int16');
hdr.scalar_name = uint8(fread(file,[10 20],'*uint8'));
hdr.n_properties = fread(file,1,'*int16');
hdr.property_name = uint8(fread(file,[10 20],'*uint8'));
hdr.vox_to_ras = fread(file,[4 4],'*float32');
hdr.reserved = uint8(fread(file,[1 444],'*uint8'));
hdr.voxel_order = uint8(fread(file,[1 4],'*uint8'));
hdr.pad2 = uint8(fread(file,[1 4],'*uint8'));
hdr.image_orientation_patient = fread(file,[1 6],'*float32');
hdr.pad1 = uint8(fread(file,[1 2],'*uint8'));
hdr.invert_x = uint8(fread(file,1,'*uint8'));
hdr.invert_y = uint8(fread(file,1,'*uint8'));
hdr.invert_z = uint8(fread(file,1,'*uint8'));
hdr.swap_xy = uint8(fread(file,1,'*uint8'));
hdr.swap_yz = uint8(fread(file,1,'*uint8'));
hdr.swap_zx = uint8(fread(file,1,'*uint8'));
hdr.n_count = fread(file,1,'*int32');
hdr.version = fread(file,1,'*int32');
hdr.hdr_size = fread(file,1,'*int32');


%----------------------------------------------------------------------
% Read fibers
%----------------------------------------------------------------------
endpoints   = zeros(hdr.n_count,2);
len         = zeros(hdr.n_count,1);
data        = zeros(3,1000);

%h=waitbar(0,'Loading trajectory endpoints from .trk file...');

for n = 1:hdr.n_count
   M = fread(file,1,'int32');
   for m = 1:M
      data(:,m) = fread(file,[3 1],'float');
      if hdr.n_scalars~=0
          temp=fread(file,hdr.n_scalars,'float');
      end
   end
   data = data(:,[1 M]);	% keep only first and last

	v = zeros(3,2);
	v(1,1) = round( data(1,1) / hdr.voxel_size(1) - 0.5 ) + 1;
	v(2,1) = round( data(2,1) / hdr.voxel_size(2) - 0.5 ) + 1;
	v(3,1) = round( data(3,1) / hdr.voxel_size(3) - 0.5 ) + 1;
	v(1,2) = round( data(1,2) / hdr.voxel_size(1) - 0.5 ) + 1;
	v(2,2) = round( data(2,2) / hdr.voxel_size(2) - 0.5 ) + 1;
	v(3,2) = round( data(3,2) / hdr.voxel_size(3) - 0.5 ) + 1;

	v( v<1 ) = 1;
	if v(1,1)>hdr.dim(1), v(1,1)=hdr.dim(1); end
	if v(1,2)>hdr.dim(1), v(1,2)=hdr.dim(1); end
	if v(2,1)>hdr.dim(2), v(2,1)=hdr.dim(2); end
	if v(2,2)>hdr.dim(2), v(2,2)=hdr.dim(2); end
	if v(3,1)>hdr.dim(3), v(3,1)=hdr.dim(3); end
	if v(3,2)>hdr.dim(3), v(3,2)=hdr.dim(3); end

   endpoints(n,:)   = [ sub2ind(hdr.dim, v(1,1),v(2,1),v(3,1)) sub2ind(hdr.dim, v(1,2),v(2,2),v(3,2)) ];
   len(n)           = M-1;

   % discard properties/scalars
   if hdr.n_properties~=0
      temp=fread(file,hdr.n_properties,'float');
   end

%   PERC = double(n) / double(hdr.n_count);
%   if ( mod(n,1000)==0 )
% 	  waitbar(PERC,h, sprintf('%d%% loaded...', int32(PERC*100)));
%   end
end

%close(h);
fclose(file);

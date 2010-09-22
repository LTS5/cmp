function [ matrix ] = DTB__fibers2cmat(ENDPOINTS, LEN, niiROI)

N = max( niiROI.img(:) );

% find roi_size
I = find( niiROI.img(:)~=0 );
roi_size = zeros(1,N);
for i = 1:length(I)
    roi_size(niiROI.img(I(i))) = roi_size(niiROI.img(I(i)))+1;
end

% creation of the matrices
matrix.datainfo.resolution 	= N;
matrix.density				= zeros(N,N);
matrix.length				= zeros(N,N);

temp_length					= cell(N,N);

% for each fiber
for j = 1:size(ENDPOINTS,1)
    b1 = ENDPOINTS(j,1); % fiber starting points
    e1 = ENDPOINTS(j,2); % fiber endpoints

    lb = niiROI.img(b1);
    le = niiROI.img(e1);

    if (lb~=0 && le~=0 && LEN(j) >= 3)
        MIN = min([lb le]);
        MAX = max([lb le]);
        temp_length{MIN,MAX} = [temp_length{MIN,MAX} ; LEN(j)]; % store length of fiber
    end
end

for k = 1:N
    for m = k:N % for each matrix element
        if ~isempty(temp_length{k,m})
            matrix.density(k,m) = sum(1./temp_length{k,m});  % computation of the connection probability
            matrix.density(m,k) = matrix.density(k,m);

            matrix.length(k,m) = mean(temp_length{k,m});
            matrix.length(m,k) = matrix.length(k,m);
        end
    end
end
